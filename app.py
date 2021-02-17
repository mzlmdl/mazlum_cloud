from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exams.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class Exams(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    count = db.Column(db.Integer)
    questions = db.relationship('Questions',backref='exam',lazy=True)
    
    def __init__(self, name, count):
        self.name = name
        self.count = count

class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question_description = db.Column(db.String(150),nullable=False)
    right_answer = db.Column(db.String(30),nullable=False)
    wrong_answer1 = db.Column(db.String(30),nullable=False)
    wrong_answer2 = db.Column(db.String(30),nullable=False)
    wrong_answer3 = db.Column(db.String(30),nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    
    def __init__(self,question_description,right_answer,wrong_answer1,wrong_answer2,wrong_answer3,exam_id):
        self.question_description = question_description
        self.right_answer = right_answer
        self.wrong_answer1 = wrong_answer1
        self.wrong_answer2 = wrong_answer2
        self.wrong_answer3 = wrong_answer3
        self.exam_id = exam_id

idtemp = 0
count = 0
key=0

@app.route('/show', methods = ['GET', 'POST'])
def show():
    return render_template('show.html', e = Exams.query.all())


@app.route('/new', methods = ['GET', 'POST'])
def new():
    global idtemp
    global count
    if request.method == 'POST':
        if not request.form['name'] or not request.form['count']:
            flash('Please enter all the fields', 'error')
        else:
            exam = Exams(request.form['name'],request.form['count'])
            db.session.add(exam)
            db.session.commit()
            idtemp = exam.id
            count = exam.count
            flash('Record was successfully added')
            return redirect(url_for('question'))
    return render_template('new.html')

@app.route('/question', methods=['GET', 'POST'])
def question():

    global idtemp
    global count
    exam = Exams.query.filter_by(id=idtemp).first()
    if request.method == 'POST':
            if not request.form['description'] or not request.form['right'] or not request.form['wrong1'] or not request.form['wrong2'] or not request.form['wrong3']:
                flash('Please enter all the fields', 'error')
            else:
                questions = Questions(request.form['description'], request.form['right'], request.form['wrong1'],
                                      request.form['wrong2'], request.form['wrong3'], exam.id)
                db.session.add(questions)
                exam.questions.append(questions)
                db.session.commit()
                count = count-1
                if count != 0:
                    flash('Record was successfully added')
                    return redirect(url_for('question'))
                else:
                    return redirect(url_for('show'))
    return render_template('question.html')
    

questionsList = {}
exam = Exams.query.filter_by(id=1).first()
question = Questions.query.filter_by(exam_id=exam.id).all()
for i in range(exam.count):
    questionsList[question[i].question_description] = [question[i].right_answer, question[i].wrong_answer1,
                                                                question[i].wrong_answer2, question[i].wrong_answer3]


@app.route('/')
def home():
    global questionsList

    if not session.get('logged_in'):
        return render_template('login.html')
    elif key==1:
        session['logged_in'] = False
        return render_template('quiz_student.html', question = questionsList)
    elif key==2:
        session['logged_in'] = False
        return render_template('show.html', e = Exams.query.all())

@app.route('/quiz', methods=['POST'])
def quiz_answers():
    global questionsList
    correct = 0

    for i in questionsList.keys():
        answered = request.form[i]
        print(answered)
  
        if questionsList[i][0] == answered:
            correct = correct+1
    return '<h1>Correct Answers: <u>'+str(correct)+'</u></h1>'

@app.route('/login', methods=['POST'])
def login():
    global key
    if request.form['password'] == 'password' and request.form['username'] == 'student':
        session['logged_in'] = True
        key = 1
    elif request.form['password'] == 'password' and request.form['username'] == 'teacher':
        session['logged_in'] = True
        key = 2
    else:
        flash('wrong password!')
    return home()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    db.create_all()
    app.run()