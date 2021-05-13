from flask import Flask, render_template, request, make_response
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy("sqlite:///db.sqlite")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False)
    text = db.Column(db.String, unique=False)


db.create_all()


@app.route("/", methods=["GET"])
def index():
    is_logged_in = request.cookies.get("is_logged_in")
    user_name = "Gregor"
    articles = ["My first article", "It's fun to learn"]
    return render_template(
        "index.html",
        name=user_name,
        articles=articles,
        is_logged_in=is_logged_in
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # TODO: Store user to database

        response = make_response(render_template(
            "register_success.html",
            first_name=first_name,
            email=email,
            is_logged_in=True
        ))
        response.set_cookie("is_logged_in", "true")

        return response


@app.route("/profile")
def profile():
    is_logged_in = True
    return render_template("profile.html", is_logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(use_reloader=True)
