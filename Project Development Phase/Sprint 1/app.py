from flask import Flask, render_template,request,url_for,flash,redirect,session;
from flask_session import Session
import sqlite3,random,ibm_db

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=snx86674;PWD=iTqZUz2Ytf3yQKNd",'','')



app = Flask(__name__)
app.config["SESSION_PERMANENT"]=False 
app.config["SESSION_TYPE"]="filesystem"
Session(app)
app.secret_key = "7358543180"


def insertsql(tablename, fields, values):
    query="Insert into "+tablename+"("
    # query="INSERT INTO userauth (firstname, lastname, userid, email,mobileno,passwordd) VALUES (?,?,?,?,?,?)"

    for i in fields:
        query+=str(i)+","
    query=query[:-1]+") Values ("
    for i in range(len(fields)):
        query+="?,"
    query=query[:-1]+")"

    print(query)

    prep_stmt=ibm_db.prepare(conn,query)

    for i in range(len(values)):
        ibm_db.bind_param(prep_stmt,i+1,values[i])

    ibm_db.execute(prep_stmt)




@app.route("/")
def home():
    try:
        if session["userid"]:
            return render_template("home.html",userid=session["userid"])
    except:
        return redirect(url_for("login"))


@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form["email"]
        password=request.form["password"]

        query= ibm_db.exec_immediate(conn,"select * from userauth")

        userdetails=ibm_db.fetch_assoc(query)

        # print(userdetails)
        
        flag=0
        while userdetails!=False:
            print(userdetails['EMAIL'],email,userdetails['PASSWORDD']==password)
            if userdetails['EMAIL']==email and userdetails["PASSWORDD"]==password.strip():
                flag=2;session["userid"]=userdetails["USERID"];break
            elif userdetails["EMAIL"]==email and userdetails["PASSWORDD"]!=password.strip():
                flag=1;break
            userdetails=ibm_db.fetch_assoc(query)
        if flag==0:
            flash("User doesn't exist")
        elif flag==1:
            flash("Password is incorrect")
        else:
            return redirect(url_for("home")) 

    return render_template("login.html")



@app.route("/signup")
def signupgeneral():
    session["userdetails"]=None
    session["numberofincomes"]=None
    session["expenses"]=None
    return render_template("signupgeneral.html")


@app.route("/addnoofincome",methods=['POST','GET'])
def addnoofincome():
    session['numberofincomes']=request.form.get('noofincomes',type=int)
    session["balance"]=request.form['balance']
    return redirect(url_for("signupincome"))


@app.route("/signupincome")
def signupincome():
    print(session["userdetails"],session["expenses"])
    if not session["numberofincomes"]:
        numberofincomes=0
    else:
        numberofincomes=(int)(session["numberofincomes"])
    return render_template("signupincomesection.html",numberofincomes=numberofincomes)


@app.route("/signupexpense/")
def signupexpense():
    return render_template("signupexpensesection.html")

@app.route("/createaccount",methods=('GET','POST'))
def createaccount():
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        mobileno=request.form['mobileno']
        password=request.form['password']
        cpassword=request.form['cpassword']
        if not fname:
            flash("Please enter your name")
        elif not email:
            flash("Please enter your email id")
        elif not mobileno:
            flash("Please enter your Mobile number")
        elif not password:
            flash("Please enter a password")
        elif password!=cpassword:
            flash("Password didn't match")
        else:
            if not lname:
                lname=" "
            ran=random.randint(100,999)
            userid=fname[:3]+str(ran)+str(ran+(int(mobileno)%100))
            userdetails=[fname,lname,userid,email,mobileno,password]
            print(userdetails)
            session["userdetails"]=userdetails
            return redirect(url_for("signupexpense"))
    return redirect(url_for("signupgeneral"))
        
            

@app.route("/addexpensedetails",methods=('GET','POST'))
def addexpensedetails():
    if request.method=="POST":
        expenses=request.form["expenses"]
        filteredexpenses=""
        for expense in expenses.strip().split(","):
            filteredexpenses+=expense
            filteredexpenses+=";"
        session["expenses"]=filteredexpenses[:-1]
        session["incomes"]=[]
    return redirect(url_for("signupincome"))



@app.route("/addincomedetails",methods=('GET','POST'))
def addincomedetails():
    if request.method=="POST":
        incomename=request.form["incomename"]
        incometype=request.form["incometype"]
        utime=request.form["utime"]
        uinterval="-1"

        if incometype!="daily":
            uinterval=request.form["uinterval"]
        if uinterval=="select" and incometype=="weekly":
            uinterval="monday"
        if uinterval=="select" and incometype=="monthly":
            uinterval="1"

        incomedetails=list(session["incomes"])
        incomedetails.append([incomename,incometype,utime,uinterval])
        session["incomes"]=incomedetails

    session["numberofincomes"]=(int)(session["numberofincomes"])-1
    while session["numberofincomes"]!=0:
        numberofincomes=session["numberofincomes"]
        print(session["incomes"])
        return render_template("signupincomesection.html",numberofincomes=numberofincomes)
    
    signupusertodatabase()
    signupexpensetodatabase()
 
    session["userid"]=session["userdetails"][2]
    session["userdetails"]=None
    session["numberofincomes"]=None
    session["expenses"]=None
    return redirect(url_for("home"))


def signupusertodatabase():
    userdetails=session["userdetails"]
    
    # query="INSERT INTO userauth (firstname, lastname, userid, email,mobileno,passwordd) VALUES (?,?,?,?,?,?)"
    fields=["firstname", "lastname", "userid", "email","mobileno","passwordd"]
    insertsql("userauth",fields,userdetails)
    # prep_stmt=ibm_db.prepare(conn,query)

    # ibm_db.bindparam(1,userdetails[0])
    # ibm_db.bindparam(2,userdetails[1])
    # ibm_db.bindparam(3,userdetails[2])
    # ibm_db.bindparam(4,userdetails[3])
    # ibm_db.bindparam(5,userdetails[4])
    # ibm_db.bindparam(6,userdetails[5])

    # ibm_db.execute(prep_stmt)
    

    

def signupexpensetodatabase():
    userdetails=session["userdetails"]
    expenses=session["expenses"]
    balance=session["balance"]
    incomelist=session["incomes"]
    incomes=""
    for i in incomelist:
        incomes+=i[0]
        incomes+=";"
    incomes=incomes[:-1]
    fields=["userid","email","mobileno","balance","expenses","incomes","streak"]
    values=[userdetails[2],userdetails[3],str(userdetails[4]),balance,expenses,incomes,0]
    insertsql("userecons",fields,values)
    
    # cur.execute("INSERT INTO userecons (userid,email,mobileno,balance,expenses,incomes) VALUES (?,?,?,?,?,?)",
    # (userdetails[2],userdetails[3],userdetails[4],balance,expenses,incomes))
    




@app.route("/databasecheck")
def databasecheck():
    conn=sqlite3.connect("kanakkardatabase.db")
    conn.row_factory=sqlite3.Row


    cur=conn.cursor()
    cur.execute("select * from userauth")

    userrows=cur.fetchall()
    cur.close()


    cur=conn.cursor()
    cur.execute("select * from userecons")

    userecons=cur.fetchall()
    cur.close()


    cur=conn.cursor()
    cur.execute("select * from Gok329409")

    usertable=cur.fetchall()
    cur.close()


    conn.close()

    # print(userrows[0])
    return render_template("databasecheck.html",userdetails=userrows,userecons=userecons,usertable=usertable)


#---------------------------- authentication close --------------------------------------------------


#---------------------------- expense open --------------------------------------------------

@app.route("/myexpense")
def myexpense():
    return render_template("expense.html")