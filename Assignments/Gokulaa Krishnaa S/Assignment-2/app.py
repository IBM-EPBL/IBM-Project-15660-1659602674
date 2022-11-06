from flask import Flask, render_template,request,url_for,flash,redirect;
import sqlite3


app = Flask(__name__)


app.secret_key = "secret key"


@app.route("/")
def login():
    return render_template("login.html")
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/create/',methods=('GET','POST'))
def create():
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        cpassword=request.form['cpassword']
        if not name:    
            flash('Name required')

        elif not email:
            flash('Email required')

        elif not password:
            flash('Password is required')
        
        elif not cpassword:
            flash('Password is required')

        elif password!=cpassword:
            flash('Password did not match')

        else:
            try:
                con= sqlite3.connect("auth.db")

                cur=con.cursor()
                cur.execute("Insert into clients (name,mailid,password) values (?,?,?)",(name,email,password))
                print("success")
                flash("Inserted successfully!")
                cur.close()
                con.commit()
            except:
                flash("connection error")
                print("connection error!!")
                con.rollback()
            finally:
                
                con.close()
                return render_template("login.html")
                
    return  redirect(url_for("signup"))

@app.route('/signin/',methods=('GET','POST'))
def signin():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']

        if not email:
            flash('Name required')

        elif not password:
            flash('Email required')
        else:
            conn=sqlite3.connect("auth.db")
            cur=conn.cursor()
            cur.execute("select * from clients")
            users=cur.fetchall()
            # print(users)
            flag=1
            for user in users:
                if flag==1 and user[1]==email and user[2]==password:
                    flag=0
                    break
                elif flag==1 and user[1]==email and user[2]!=password:
                    flag=2
                    break
            cur.close()
            conn.close()
            if flag==0:
                return redirect(url_for("home"))
            elif flag==1:
                flash("User doesn't exist")
            else:
                flash("Password is not matching")
            
    return  redirect(url_for("login"))

@app.route("/home")
def home():
    con= sqlite3.connect("auth.db")
    con.row_factory=sqlite3.Row

    cur=con.cursor()
    cur.execute("Select * from clients")

    rows=cur.fetchall()
    cur.close()
    con.close()
    for i in rows:
        print(i)
    return render_template("home.html",rows=rows)

