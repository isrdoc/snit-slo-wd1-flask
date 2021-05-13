from flask import Flask, render_template, request, make_response, redirect, url_for
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy("sqlite:///db.sqlite")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False)
    text = db.Column(db.String, unique=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False)


db.create_all()


@app.route("/", methods=["GET"])
def index():
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()

    articles = ["My first article", "It's fun to learn"]

    return render_template(
        "index.html",
        user=user,
        articles=articles
    )


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        messages = db.query(Message).all()

        return render_template("chat.html", messages=messages)

    if request.method == "POST":
        first_name = request.form.get("first_name")
        message_text = request.form.get("message_text")

        message = Message(author=first_name, text=message_text)
        message.save()

        messages = db.query(Message).all()

        return render_template("chat.html", messages=messages)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(User).filter_by(email=email).first()
        if not user:
            return render_template("login.html", did_login_fail=True)

        are_passwords_same = user.password == password
        if not are_passwords_same:
            return render_template("login.html", did_login_fail=True)

        response = make_response(redirect(url_for('index')))
        response.set_cookie("email", email)
        return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # TODO: Check valid email and password

        user = User(first_name=first_name, email=email, password=password)

        db.add(user)
        db.commit()

        response = make_response(render_template(
            "register_success.html",
            first_name=first_name,
            email=email,
            is_logged_in=True
        ))
        response.set_cookie("email", email)

        return response


@app.route("/profile")
def profile():
    is_logged_in = True
    return render_template("profile.html", is_logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(use_reloader=True)
