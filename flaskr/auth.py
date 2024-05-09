from for_model import model_pred
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json
import sqlite3
import os
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,Flask
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

@bp.route('/main')
def main():
    return render_template('auth/main.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        username2 = request.args.get('username2')
        password2 = request.args.get('pwd2')
        email2 = request.args.get('email2')

        if username2 and password2 and email2:
            with sqlite3.connect(db_path) as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO user_info (username, pwd, email) VALUES (?, ?, ?)",
                    (username2, password2, email2),
                )
                con.commit()
                return redirect(url_for("auth.login"))
        else:
            error = '모든 데이터를 입력해주세요'
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM user_info WHERE email = ?', (email,)
        )

        result = cursor.fetchone()  

        if result:
            return redirect(url_for('auth.enter'))
        
        else:
            error = 'Incorrect email.'
            flash(error)

    return render_template('auth/login.html')

@bp.route('/enter')
def enter():
    return render_template('auth/enter.html')

@bp.route('/manage',methods=('GET','POST'))
def manage():   
    if request.method == 'POST':
        names = request.form['names']
        numbers = request.form['numbers']

        error = None

        if not names:
            error = 'Username is required.'
        elif not numbers:
            error = 'UserNumber is required.'

        if error is None:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
            'SELECT distinct consult_day, positive FROM consult_info where student_name = ? order by consult_day', (names,)
            )

            result = cursor.fetchall()

            r = [[names],[str(i[0]) for i in result],[float(i[1]) for i in result]]
            return render_template('auth/manage.html', data = r)

        flash(error)
    
    return render_template('auth/manage.html')

@bp.route('/consulting',methods=('GET','POST'))
def consulting():
    if request.method == 'POST':
        name = request.form['student_name']
        num = request.form['student_num']
        date = request.form['consult_date']
        sub = request.form['subject']
        consulting_text = request.form['consultation']

        error = None

        if not name:
            error = 'Not email'
        elif not num:
            error = 'Not password'
        elif not date:
            error = 'Not date'
        elif not sub:
            error = 'Not category'
        elif not consulting_text:
            error = 'Not text'

        with open('for_korean.json', 'r') as f:
            word_index = json.load(f)

        okt = Okt()
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
        tokenizer = Tokenizer()

        tokenizer.word_index = word_index

        loaded_model = load_model('best_model.h5')

        pred = model_pred(consulting_text)

        if name and num and date:
            with sqlite3.connect(db_path) as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO consult_info (student_name, student_num, consult_day, consult_type,consult_text, positive) VALUES (?, ?, ?, ?, ?, ?)",
                    (name,num,date, sub, consulting_text, pred),
                )
                con.commit()
            return redirect(url_for("auth.enter"))
        else:
            error = '모든 데이터를 입력해주세요'
            flash(error)
        
    return render_template('auth/consulting.html')

@bp.route('/schedule')
def schedule():
    error = None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schedule_info = cursor.execute(
    'SELECT distinct * FROM my_schedule order by schedule_date;'
    )

    schedule_info = cursor.fetchall()

    schedule_date = request.args.get('schedule_date')
    schedule_time = request.args.get('schedule_time')
    about_schedule = request.args.get('schedule_info')

    if schedule_date and schedule_time and about_schedule:
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO my_schedule (schedule_date, schedule_time, about_schedule) VALUES (?,?,?)",
                (schedule_date, schedule_time, about_schedule),
            )
            con.commit()
            return redirect(url_for("auth.enter"))
    
    else:
        error = '빈칸이 존재합니다'
        flash(error)

    return render_template('auth/schedule.html', data = schedule_info)