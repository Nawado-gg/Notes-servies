import os
import random
from cryptography.fernet import Fernet
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
sslify = SSLify(app)

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key = True)
    number = db.Column(db.Integer, unique = True, nullable = False)
    ciptext = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return f'<Note number: {self.number}'

class TextFrom(FlaskForm):
    text = TextAreaField('Введите текст',
                        validators = [DataRequired(), Length(1, 1000)])
                        
    submit = SubmitField('Создать')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Note': Note}


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = TextFrom()
    if form.validate_on_submit():
        key = Fernet.generate_key()
        str_key = key.decode('ascii')
        f = Fernet(key)
        bin_string = form.text.data.encode('utf-8')
        cipher_text = f.encrypt(bin_string)
        str_cipher_text = cipher_text.decode('ascii')
        rnumber = random.randint(1000000, 9999999)
        while True:
            n = Note.query.filter_by(number=rnumber).first()
            if n:
                rnumber = random.randint(1000000, 9999999)
                continue
            break
        cipger_note = Note(number = rnumber, ciptext = str_cipher_text)
        link = f'{app.config["SITE_URL"]}/{rnumber}/{str_key}'
        db.session.add(cipher_note)
        db.session.commit()
        return rander_template('complete.html', link = link)
    return render_template('index.html', form = form)

@app.route('/<rnumber>/<str_key>')
def question(rnumber, str_key):
    link = f'{app.config["SITE_URL"]}/decrypt/{rnumber}/{str_key}'
    return render_template('question.html', link=link)

@app.route('/decrypt/<int:rnumber>/<str_key>')
def decrypt(rnumber, str_key):
    cipher_note = Note.query.filter_by(number=rnumber).first_or_404()
    cipher_text = cipher_note.ciptext.encode('ascii')
    key = str_key.encode('ascii')
    try:
        f = Fernet(key)
        text = f.decrypt(cipher_text)
    except (ValueError, InvalidToken):
        return render_template('error.html')
    text = text.decode('utf-8')
    db.session.delete(cipher_note)
    db.session.commit()
    return render_template('decrypt.html', text=text)