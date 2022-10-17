from flask import Blueprint, flash, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", category="success")
        return redirect(url_for("views.home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):

                flash("Loggin success", category="Success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password", "error")
        else:
            flash("User does not exits please register")

    return render_template("login.html", page="login", user=current_user)


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():

    if current_user.is_authenticated:

        flash("Logout to register new user!", category="error")
        return redirect(url_for("views.home"))

    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("first-name")
        lastName = request.form.get("last-name")
        contact = request.form.get("contact")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists!", category="error")

        elif len(firstName) < 2:
            flash("Enter a vaild First Name", category="error")

        elif len(lastName) == 0:
            flash("Enter a vaild Last Name", category="error")

        elif len(email) < 4:
            flash("Enter a vaild email", category="error")

        elif len(contact) < 10:
            flash("Enter a vaild contact number (10 digits)", category="error")

        else:

            user = User(
                email=email,
                firstName=firstName,
                lastName=lastName,
                contact=contact,
                password=generate_password_hash(password, method="sha256"),
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration success!", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", page="sign-up", user=current_user)
