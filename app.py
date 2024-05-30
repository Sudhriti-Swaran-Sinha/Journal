from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import Form, ValidationError, DateField, StringField, validators, PasswordField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String, Date

app = Flask(__name__)
app.secret_key = "12345000"

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///<journal_database>.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

#Creating a table

class Journal(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    db_date: Mapped[str] = mapped_column(String, nullable=False)
    db_purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    db_notes: Mapped[str] = mapped_column(String(250), nullable=False)

    def __repr__(self):
        return f"<Journal {self.db_date} - {self.db_purpose} : {self.db_notes}>"


with app.app_context():
    db.create_all()




class MyForm(FlaskForm):
    username = StringField(label="Username", validators=[validators.data_required()])
    password = PasswordField(label="Password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")

class JournalForm(FlaskForm):
    date = StringField(label="Date", validators=[validators.data_required()])
    purpose = StringField(label="Purpose", validators=[validators.data_required()])
    notes = StringField(label="Notes", validators=[validators.data_required()])
    save = SubmitField(label="Save Journal")

@app.route('/create', methods=['GET', 'POST'])
def create():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    form = JournalForm()
    if form.validate_on_submit():
        date = form.date.data
        purpose = form.purpose.data
        notes = form.notes.data

        #creating a record in database
        with app.app_context():
            new_journal = Journal(db_date=date, db_purpose=purpose, db_notes=notes)
            db.session.add(new_journal)
            db.session.commit()

        return redirect(url_for('create'))
    else:
        print(form.errors)
    return render_template("new_journal.html", form=form)


@app.route("/delta")
def alpha():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    return render_template("alpha.html")



@app.route("/", methods=['GET', 'POST'])
def home():
    home_form = MyForm()
    if home_form.validate_on_submit():
        if home_form.username.data == "Sudhriti" and home_form.password.data == "12345":
            session['logged_in'] = True
            return render_template("alpha.html")
        else:
            return render_template("denied.html")

    return render_template("index.html", home_form=home_form)

@app.route("/all")
def all_journals():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    with app.app_context():
        result = db.session.execute(db.select(Journal).order_by(Journal.db_purpose))
        data = result.scalars().all()

    return render_template("all_journals.html", journals=data)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0' )
