from flask import Flask, render_template

app = Flask(__name__)


@app.context_processor
def add_global_variables():
    return dict(surname="Novak")


@app.route("/")
def index():
    user_name = "Gregor"
    articles = ["My first article", "It's fun to learn"]
    is_logged_in = False
    return render_template(
        "index.html",
        name=user_name,
        articles=articles,
        is_logged_in=is_logged_in
    )


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/profile")
def profile():
    is_logged_in = True
    return render_template("profile.html", is_logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(use_reloader=True)
