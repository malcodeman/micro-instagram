from flask import Flask
from flask import jsonify
from flask import render_template
from flask import abort

import users

app = Flask(__name__)


@app.route("/users/<string:user>")
def get_user(user):
    return jsonify(users.get_user(user))


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
