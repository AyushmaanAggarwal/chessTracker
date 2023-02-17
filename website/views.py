import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Players, Games
from . import db
import numpy as np
import json

views = Blueprint('views', __name__)

@views.route('/')
def home():
    players_lst = Players.query.order_by(Players.ranking.desc()).all()
    return render_template("players.html", players=players_lst, user=current_user)

@views.route('/add-player', methods=['POST', 'GET'])
@login_required
def add_player():
    if request.method == 'POST':
        playername = request.form.get('playerName')

        existingPlayer = Players.query.filter_by(name=playername).first()
        if existingPlayer:
            flash("Player already exists.", category='error')
        elif len(playername) == 0:
            flash("Please add a name.", category='error')
        else:
            new_player = Players(name=playername, ranking=2000, gamesplayed=0, gamesIds=0, rankingHistory=0)
            db.session.add(new_player)
            db.session.commit()
            flash("New Loth Master created!", category='success')
            return redirect(url_for('views.home'))
    return render_template("new_player.html", user=current_user)

@views.route('/games')
def game():
    games_lst = Games.query.order_by(Games.date.desc()).all()
    return render_template("games.html", games=games_lst, user=current_user)
def expected_score(elo1, elo2):
    return 1/(1 + 10**((elo2 - elo1)/400))
def computeElo(player1, player2, winner, type):
    # Compute the expected value for each player
    E1 = expected_score(player1.ranking, player2.ranking)
    E2 = expected_score(player2.ranking, player1.ranking)

    if winner == '½ - ½':
        delta1 = .5 - E1
        delta2 = .5 - E2
    elif winner == '1 - 0':
        delta1 = 1 - E1
        delta2 = 0 - E2
    elif winner == '0 - 1':
        delta1 = 0 - E1
        delta2 = 1 - E2

    k = 16
    if "Classic" in type:
        k *= 2
    elif "Rapid" in type:
        k *= 1.5
    elif "Bullet" in type:
        k *= 1.25

    deltaElo1 = np.round(delta1*k)
    deltaElo2 = np.round(delta2*k)

    return deltaElo1, deltaElo2

@views.route('/add-game', methods=['POST', 'GET'])
@login_required
def add_game():
    players_lst = Players.query.order_by(Players.gamesplayed.desc()).all()

    if request.method == 'POST':
        type = request.form.get('format')
        player1 = request.form.get('player1')
        player2 = request.form.get('player2')
        winner = request.form.get('winner')
        if type=="invalid":
            flash("Please select a type of game (Classic means no time limit)", category="error")
        elif player1=="invalid" or player2=="invalid":
            flash("Select both players before continuing", category="error")
        elif winner=="invalid":
            flash("Please select a winner", category="error")
        else:
            player1 = Players.query.filter_by(name=player1).first()
            player2 = Players.query.filter_by(name=player2).first()

            delta1, delta2 = computeElo(player1, player2, winner, type)
            new_game = Games(type=type, date=datetime.datetime.now().date(), player1=player1.name, player1elo=player1.ranking, player1elodelta=delta1,
                             player2=player2.name, player2elo=player2.ranking, player2elodelta=delta2, winner=winner)
            player1.ranking += delta1
            player2.ranking += delta2
            player1.gamesplayed += 1
            player2.gamesplayed += 1
            #player1.rankingHistory.append(player1.ranking)
            #player2.rankingHistory.append(player2.ranking)
            #player1.gamesIds.append(new_game.id)
            #player2.gamesIds.append(new_game.id)
            db.session.add(new_game)
            db.session.commit()
            flash("New game added!", category='success')
            return redirect(url_for('views.game'))
    return render_template("new_game.html", user=current_user, players=players_lst)