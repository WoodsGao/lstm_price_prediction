from flask import Flask, session, abort, redirect, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
import os
import json
import time
from werkzeug.security import generate_password_hash, check_password_hash
from models import StockLSTM
from spiders import BitmexSpider, HuobiSpider

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = '32489r32hjd982h'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

stocks = ['btcusdt','ethusdt', 'eosusdt', 'neousdt', 'htusdt']

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    # read(unreadable)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # write
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,16)])
    submit = SubmitField('Log In')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', stocks=stocks)

@app.route('/predict/<string:stock>', methods=['GET'])
def predict(stock):
    stock = stock.lower()
    if stock not in stocks:
        abort(404)
    with open('now/%s' % stock, 'r') as f:
        now = json.loads(f.read())
    with open('pre/%s' % stock, 'r') as f:
        pre = json.loads(f.read())
    now_time = [i[0] for i in now]
    pre_time = [i[0] for i in pre]
    timestamps = now_time + pre_time
    timestamps = list(set(timestamps))
    timestamps.sort()
    now = [now[now_time.index(t)][1] if t in now_time else None for i, t in enumerate(timestamps)]
    pre = [pre[pre_time.index(t)][1] if t in pre_time else None for i, t in enumerate(timestamps)]
    now = json.dumps(now)
    pre = json.dumps(pre)
    timestamps = [str(time.strftime("%m-%d %H:%M", time.localtime(t))) for t in timestamps]
    timestamps = json.dumps(timestamps)
    return render_template('predict.html', stocks=stocks, stock=stock, now=now, pre=pre, timestamps=timestamps)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect('/')
        flash('Invalid username or password')
    return render_template('login.html', form=form, stocks=stocks)

@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    return 'wait for it'


if __name__ == "__main__":
    for s in stocks:
        t = HuobiSpider(s, 15*60)
        t.run()
        time.sleep(10)
    time.sleep(60)
    for s in stocks:
        t = StockLSTM(s, 2*60*60)
        t.run()
    app.run(host='0.0.0.0', port=15000)
    input()
    
