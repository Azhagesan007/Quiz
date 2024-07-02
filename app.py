import random
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user,login_required, UserMixin, current_user


import question
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mitilence.db"
app.secret_key = 'ialzahnatgheasaamnizh'
db = SQLAlchemy(app)
questions = question.questions
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=False, nullable=False)
    mobile = db.Column(db.String, unique=False, nullable=False)
    score = db.Column(db.Integer, unique=False, nullable=False)
    index = db.Column(db.Integer, unique=False, nullable=False)
    completed = db.Column(db.Integer, unique=False, nullable=False)
    question = db.Column(db.String, unique=False, nullable=False)
    shuffled = db.Column(db.Integer, unique=False, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/quiz')
@login_required
def index():
    query = User.query.filter_by(email=current_user.email).first()
    if query.index >= len(questions):
        return redirect(url_for("result"))
    return render_template('contacts.html', question=questions[session['question_index']], q=questions[session['question_index']]["question"].split("\n"))

@app.route("/start")
@login_required
def start():
    global questions
    questions = question.questions
    random.shuffle(questions)
    query = User.query.filter_by(email=current_user.email).first()
    if query.completed == 1:
        return "Already Completed"
    with app.app_context():
        query.score = 0
        query.index = 0
        query.question = str(questions)
        query.shuffled = 1
        db.session.commit()
    session['score'] = 0
    session['question_index'] = 0
    return redirect(url_for("index"))

# Route for handling user responses
@app.route('/answer', methods=['POST'])
def answer():
    with app.app_context():
        query = User.query.filter_by(email=current_user.email).first()
        if "option" in request.form.to_dict():
            selected_option = request.form['option']
            correct_answer = questions[session['question_index']]['correct_answer']
            if selected_option == correct_answer:
                session['score'] += 1

                query.score += 1

        session['question_index'] += 1
        query.index += 1
        db.session.commit()
    if session['question_index'] < len(questions):
        return redirect(url_for('index'))
    else:
        return redirect(url_for('result'))



@app.route('/result')
@login_required
def result():
    final_score = current_user.score
    query = User.query.filter_by(email= current_user.email).first()
    with app.app_context():
        query.completed = 1
        db.session.commit()
    session.clear()
    return render_template('results.html', data={final_score: [current_user.name]}, des=[final_score])

@app.route("/registration_mitronce", methods=["POST", "GET"])
def registration():
    with app.app_context():
        query = User.query.all()
    if request.method == "GET":
        return render_template("registration.html", data=query)
    data = request.form.to_dict()
    user = User(name=data["name"], email=data["email"], mobile=data["mobile"], score=0, index=0, completed=0, question="", shuffled=0)
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        query = User.query.all()
    return render_template("registration.html", data=query)

@app.route("/result_all")
def result_all():
    with app.app_context():
        query = User.query.all()
    des = [i.score for i in query]
    des.sort(reverse=True)
    data = {i: [] for i in des}
    for i in query:
        data[i.score].append(i.name)
    return render_template("results.html", data=data, des=des)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", data="")
    data = request.form.to_dict()
    query = User.query.filter_by(email=data["email"]).first()
    if query:
        if int(query.mobile) == int(data["password"]):
            login_user(query)
            return redirect(url_for("start"))

    return render_template("login.html", data="Wrong credentials")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/codind/<int:data>")
def coding(data):
    d = {
        0:["Write a function reverse_string(s) that takes a string s as input and returns the reversed string.",
           'Input: "hello", Output: "olleh"', 'Input: "python", Output: "nohtyp"'],
        1:["Write a function count_vowels(s) that takes a string s as input and returns the number of vowels in the string",
           'Input: "hello", Output: 2', 'Input: "python", Output: 1'],
        2:["Write a function is_palindrome(s) that takes a string s as input and returns True if s is a palindrome, otherwise False.",
           'Input: "hello", Output: False', 'Input: "racecar", Output: True'],
        3:["Write a function find_max(arr) that takes a list of integers arr as input and returns the maximum value in the list",
           'Input: [1, 2, 3, 4, 5], Output: 5', 'Input: [-1, -2, -3, -4, -5], Output: -1'],
        4:[""]
    }

if __name__ == '__main__':
    app.run(debug=True, port=5678)
