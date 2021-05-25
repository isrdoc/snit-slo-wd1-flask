from flask import Flask, render_template, request, make_response, redirect, url_for, g
from sqla_wrapper import SQLAlchemy
import uuid
import hashlib
from functools import wraps

app = Flask(__name__)
db = SQLAlchemy("sqlite:///db.sqlite")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False, nullable=False)
    text = db.Column(db.String, unique=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False)
    session_token = db.Column(db.String, unique=True)
    is_admin = db.Column(db.Boolean, nullable=True)
    is_deleted = db.Column(db.Boolean, nullable=True)
    undelete_token = db.Column(db.String, unique=True)


db.create_all()


def get_user():
    if 'user' not in g:
        session_token = request.cookies.get("session_token")
        user = None
        if session_token:
            user = db.query(User).filter_by(session_token=session_token).first()
        g.user = user

    return g.user


@app.context_processor
def inject_user():
    user = get_user()

    return dict(user=user)


def auth_guard(handler):
    @wraps(handler)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if not user:
            return redirect(url_for('login'))

        return handler(*args, **kwargs)
    return decorated_function


def with_email_and_pass(handler):
    @wraps(handler)
    def decorated_function(*args, **kwargs):
        if request.method == "GET":
            return handler(*args, **kwargs)

        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("missing_login_data.html", email=email, password=password)

        return handler(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["GET"])
def index():
    articles = ["My first article", "It's fun to learn"]

    return render_template("index.html", articles=articles)


@app.route("/profile")
@auth_guard
def profile():
    user = get_user()

    # print(user.admin)

    # if user.admin:
    #     return render_template("profile_admin.html")

    return render_template("profile.html")


@app.route("/profile/edit", methods=["GET", "POST"])
@auth_guard
def profile_edit():
    if request.method == "GET":
        return render_template("profile_edit.html")

    if request.method == "POST":
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        user = get_user()

        if first_name:
            user.first_name = first_name
        if email:
            user.email = email
        if password and password_confirm and password == password_confirm:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user.password = hashed_password

        user.save()

        # TODO: add current values to edit form
        # TODO: return feedback to user if password was not changed due to missing password_confirm

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
@auth_guard
def profile_delete():
    if request.method == "GET":
        return render_template("profile_delete.html")

    if request.method == "POST":
        user = get_user()

        user.is_deleted = True
        user.save()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", "")
        return response


@app.route("/profile/undelete", methods=["GET", "POST"])
def profile_undelete():
    undelete_token = request.cookies.get("undelete_token")
    if not undelete_token:
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template("profile_undelete.html")

    if request.method == "POST":
        user = db.query(User).filter_by(undelete_token=undelete_token).first()
        print(user)
        if not user:
            return redirect(url_for('login'))

        user.is_deleted = False

        session_token = str(uuid.uuid4())
        user.session_token = session_token
        user.save()

        response = make_response(redirect(url_for('profile')))
        response.set_cookie("session_token", session_token)
        return response


@app.route("/chat", methods=["GET", "POST"])
@auth_guard
def chat():
    if request.method == "GET":
        messages = db.query(Message).all()

        return render_template("chat.html", messages=messages)

    if request.method == "POST":
        user = get_user()
        message_text = request.form.get("message_text")

        message = Message(author=user.first_name, text=message_text)
        message.save()

        messages = db.query(Message).all()

        return render_template("chat.html", messages=messages)


@app.route("/login", methods=["GET", "POST"])
@with_email_and_pass
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(User).filter_by(email=email).first()
        if not user:
            return render_template("login.html", did_login_fail=True)

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        are_passwords_same = user.password == hashed_password
        if not are_passwords_same:
            return render_template("login.html", did_login_fail=True)

        if user.is_deleted:
            undelete_token = str(uuid.uuid4())
            user.undelete_token = undelete_token
            user.save()

            response = make_response(redirect(url_for('profile_undelete')))
            response.set_cookie("undelete_token", undelete_token)
            return response

        session_token = str(uuid.uuid4())
        user.session_token = session_token
        user.save()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token)
        return response


@app.route("/logout", methods=["GET"])
def logout():
    user = get_user()
    BLANK_SESSION_TOKEN = ""

    if user:
        user.session_token = BLANK_SESSION_TOKEN
        user.save()

    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", BLANK_SESSION_TOKEN)
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("register.html")

        session_token = str(uuid.uuid4())
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User(
            first_name=first_name,
            email=email,
            password=hashed_password,
            session_token=session_token
        )

        # TODO: Gracefully handle errors from db (such as duplicate user)
        db.add(user)
        db.commit()

        response = make_response(render_template("register_success.html", user=user))
        response.set_cookie("session_token", session_token)

        return response


if __name__ == '__main__':
    app.run(use_reloader=True)
