# import sqlite3
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from website.models import User


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    users = User.query.all()
    return render_template("home.html", page="home", user=current_user, data=users)


@views.route("/user-info/<int:id>", methods=["GET", "POST"])
@login_required
def userInfo(id):
    user = User.query.filter_by(id=id).first()
    return render_template("user-info.html", page="home", user=user)


@views.route("/about", methods=["GET", "POST"])
@login_required
def about():
    return render_template("about.html", page="about", user=current_user)
