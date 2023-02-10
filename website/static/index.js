function increaseCounter(counterId, increase) {
    fetch("/increase-counter", {
        method: 'POST',
        body: JSON.stringify({ counterId: counterId, increase: increase }),
    }).then((_res) => {
        window.location.href = "/counter";
    });
}

function deleteCounter(counterId) {
    fetch("/delete-counter", {
        method: 'POST',
        body: JSON.stringify({ counterId: counterId }),
    }).then((_res) => {
        window.location.href = "/counter";
    });
}

function addMovie(movieList) {
    fetch("/add-movie", {
        method: 'POST',
        body: JSON.stringify({ movie: movieList }),
    }).then((_res) => {
        window.location.href = "/movies";
    });
}

function likeMovie(movieId, increase) {
    fetch("/like-movie", {
        method: 'POST',
        body: JSON.stringify({ movieId: movieId, increase: increase }),
    }).then((_res) => {
        window.location.href = "/movies";
    });
}

function addBook(bookList) {
    fetch("/add-book", {
        method: 'POST',
        body: JSON.stringify({ book: bookList }),
    }).then((_res) => {
        window.location.href = "/books";
    });
}

function likeBook(bookId, increase) {
    fetch("/like-book", {
        method: 'POST',
        body: JSON.stringify({ bookId: bookId, increase: increase }),
    }).then((_res) => {
        window.location.href = "/books";
    });
}

function markHere(latenessId, here) {
    fetch("/mark-here", {
        method: 'POST',
        body: JSON.stringify({ latenessId: latenessId, here: here }),
    }).then((_res) => {
        window.location.href = "/lateness-tracker";
    });
}

window.onload = displayClock();
function displayClock(){
    var display = new Date().toLocaleTimeString();
    document.getElementById("time").textContent = display
    setTimeout(displayClock, 1000);
}

window.onload = displayCountdown();
function displayCountdown(){
    var date1 = new Date();
    var date2 = new Date('02/10/2023 08:00:00');
    var diffTime = Math.abs(date2 - date1);
    var diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    diffTime = Math.ceil((diffTime % (1000 * 60 * 60 * 24))/1000);
    document.getElementById("countdown").textContent = "There are "+diffDays+" days and "+diffTime+" seconds remaining until the top two people will have to .... At that point, everyone's score will be halved, except for the top two people whose scores will be reset to 0."
    setTimeout(displayCountdown, 1000);
}