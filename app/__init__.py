from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app.errors import bp as errors_bp
from app.auth import bp as auth_bp
from app.main import bp as main_bp

app.register_blueprint(errors_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        secure = None

        if app.config['MAIL_USE_TLS']:
            secure = ()

        # to handle error reports (mail)
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='noreply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMIN_ADDR'],
            subject='Blog failure',
            credentials=auth,
            secure=secure
        )

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/blog.log', maxBytes=10240, backupCount=10)   # rotates the logs, ensuring that the log files do not grow too large
    file_handler.setFormatter(logging.Formatter
                              ('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                               ))
    
    # includes the timestamp, the logging level, the message and the source file and line number from where the log entry originated.
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('BlogPost Logs')


from app import models
