import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def gmail_send_message(to_address, from_address, subject, message_text):

    with open("instance/pythonpass", 'r') as file:
        email_password = file.read()

    em = MIMEMultipart('alternative')
    em['From'] = from_address
    em['To'] = to_address
    em['Subject'] = subject
    part2 = MIMEText(message_text, 'html')
    em.attach(part2)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(from_address, email_password)
        smtp.sendmail(from_address, to_address, em.as_string())
    return "Email Sent!"