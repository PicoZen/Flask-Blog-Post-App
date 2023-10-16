from flask_mail import Message
from threading import Thread
from app import mail


def send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, sender, recipients, text_body, html_body):
    message = Message(subject, sender=sender, recipients=recipients)
    message.body = text_body
    message.html = html_body
    Thread(target=send_async_mail, args=(app, message)).start()







