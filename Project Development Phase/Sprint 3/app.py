from flask import Flask, render_template,request,url_for,flash,redirect,session;
from flask_session import Session
import sqlite3,random,ibm_db
from datetime import date,timedelta


app = Flask(__name__)


app.config["SESSION_PERMANENT"]=False 
app.config["SESSION_TYPE"]="filesystem"
Session(app)
app.secret_key = "7358543180"

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=snx86674;PWD=iTqZUz2Ytf3yQKNd",'','')


#---------------------------- common functionss ---------------------------------------------------

def calcstreak(userid,curdate):
    streaks=0

    
    prevdate=curdate - timedelta(days=1)
    
    try:
        query="select date,streak from userexpenses where userid='"+userid+"' and date='"+str(prevdate)+"'"
        streakss=ibm_db.exec_immediate(conn,query)
        streak=ibm_db.fetch_assoc(streakss)
        while streak:
            streaks=int(streak["STREAK"])
            streak=ibm_db.fetch_assoc(streakss)
        streaks+=1
    except:
        streaks=1
    
    query="update userecons set streak=(?) where userid =(?)"
    prep_stmt=ibm_db.prepare(conn,query)

    ibm_db.bind_param(prep_stmt,1,streaks)
    ibm_db.bind_param(prep_stmt,2,userid)

    ibm_db.execute(prep_stmt)
    return streaks

def getstreak(userid):


    query="select streak from userecons where userid ='"+userid+"'"
    streakss=ibm_db.exec_immediate(conn,query)
    streaks=ibm_db.fetch_assoc(streakss)

    return streaks['STREAK']

def insertsql(tablename, fields, values):
    query="Insert into "+tablename+"("

    for i in fields:
        query+=str(i)+","
    query=query[:-1]+") Values ("
    for i in range(len(fields)):
        query+="?,"
    query=query[:-1]+")"


    prep_stmt=ibm_db.prepare(conn,query)

    for i in range(len(values)):
        ibm_db.bind_param(prep_stmt,i+1,values[i])

    ibm_db.execute(prep_stmt)




#---------------------------- authentication open --------------------------------------------------


@app.route("/")
def home():
    try:
        if session["userid"]:
            streaks=getstreak(session["userid"])
            return render_template("home.html",userid=session["userid"],streaks=streaks)
    except:
        return redirect(url_for("login"))
    return redirect(url_for("login"))

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form["email"]
        password=request.form["password"]

        query= ibm_db.exec_immediate(conn,"select * from userauth")

        userdetails=ibm_db.fetch_assoc(query)

        
        flag=0
        while userdetails!=False:
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

            #userid generation
            ran=random.randint(100,999)
            userid=fname[:3]+str(ran)+str(ran+(int(mobileno)%100))

            
            userdetails=[fname,lname,userid,email,mobileno,password]
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
        return render_template("signupincomesection.html",numberofincomes=numberofincomes)
    
    signupusertodatabase()
    signupexpensetodatabase()

    session["userid"]=str(session["userdetails"][2])
    session["userdetails"]=None
    session["numberofincomes"]=None
    session["expenses"]=None
    return redirect(url_for("home"))

@app.route("/logout",methods=('POST','GET'))
def logout():
    session['userid']=None 
    return redirect(url_for("login"))


def signupusertodatabase():
    userdetails=session["userdetails"]
    
    fields=["firstname", "lastname", "userid", "email","mobileno","passwordd"]
    insertsql("userauth",fields,userdetails)

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





#---------------------------- authentication close --------------------------------------------------


#---------------------------- expense open --------------------------------------------------

@app.route("/myexpense")
def myexpense():

    userid=str(session['userid'])
    query="select * from userecons where userid='"+userid+"' "
    
    usereconn=ibm_db.exec_immediate(conn,query)
  
    userecon=ibm_db.fetch_assoc(usereconn)
    userecons=[]

    while userecon:
        for j in str(userecon["EXPENSES"]).split(";"):
            userecons.append(j)
        userecon=ibm_db.fetch_assoc(usereconn)
    

    expenselog=getexpenselog()    
    streaks=getstreak(session["userid"])
    return render_template("expenses/expense.html",userecons=userecons,expenselog=expenselog,streaks=streaks)

@app.route("/addexpense",methods=['GET','POST'])
def addexpense():
    if request.method=="POST":
        userid=session["userid"]
        allexpenses=request.form['allexpenses']
        curdate=date.today()
        expenses=seperatenaemandamount(allexpenses)  
        expensenamest,expenseamountst=expenses[0],expenses[1]
        totalexpense=sum(expenseamountst)
        expenseamounts,expensenames="",""

        for i in expenseamountst:
            expenseamounts+=str(i)
            expenseamounts+=";" 
        for i in expensenamest:
            expensenames+=i;expensenames+=";"
        expensenames=expensenames[:-1]
        expenseamounts=expenseamounts[:-1]

        
        query="select date from userexpenses where userid='"+session['userid']+"'"
        datess=ibm_db.exec_immediate(conn,query)
        dates=ibm_db.fetch_assoc(datess)
        flag=0
        while dates:
            if dates['DATE']==str(curdate):
                flag=1;break
            dates=ibm_db.fetch_assoc(datess)

        
        streaks=calcstreak(userid,curdate)
        if flag==0:
            
            fields=["userid", "streak" , "date" , "expenses", "expenses_amount", "total_expense"]
            values=[userid,streaks,curdate,expensenames,expenseamounts,totalexpense]
            
            insertsql("userexpenses",fields,values)
            
        else:
            query="select expenses,expenses_amount,total_expense from userexpenses where userid ='"+userid+" ' and date = '"+str(curdate)+"'"
            
            userexpensess=ibm_db.exec_immediate(conn,query)

            userexpenses=ibm_db.fetch_assoc(userexpensess)

            expensenamestt=[]
            expenseamountstt=[]
            while userexpenses:
                for j in str(userexpenses['EXPENSES']).split(";"):
                    expensenamestt.append(j)
                for j in str(userexpenses['EXPENSES_AMOUNT']).split(";"):
                    expenseamountstt.append(j)
                userexpenses=ibm_db.fetch_assoc(userexpensess)
            expensest={}
            
            for i in range(len(expensenamestt)):
                expensest[expensenamestt[i]]=expenseamountstt[i]
            
            for i in range(len(expensenamest)):
                expensest[expensenamest[i]]=expenseamountst[i]
            
            
            expensenames="";expenseamounts="";totalexpense=0
            
            for i in expensest:
                if expensest[i]!='':
                    expensenames+=(i+";")
                    expenseamounts+=str(expensest[i])+";"
                    totalexpense+=int(expensest[i])
            
            query="update userexpenses set expenses= (?) ,expenses_amount = (?), total_expense = (?) where userid = '"+userid+"' and date = '"+str(curdate)+"'"
             
            prep_stmt=ibm_db.prepare(conn,query)
        
            ibm_db.bind_param(prep_stmt,1,expensenames)
            ibm_db.bind_param(prep_stmt,2,expenseamounts)
            ibm_db.bind_param(prep_stmt,3,totalexpense)
            
            ibm_db.execute(prep_stmt)

            flash("Expense updated successfully")
        


    
    
    return redirect(url_for("myexpense"))


def seperatenaemandamount(allexpenses):
    expenseamounts,expensenames=[],[]
    for i in str(allexpenses).split(","):
        if i!="":
            expensename,expenseamount=i.split("|")
            expensenames.append(expensename)
            expenseamounts.append(int(expenseamount))

    return [expensenames,expenseamounts]

def getexpenselog():

    query="select DATE, EXPENSES, EXPENSES_AMOUNT, TOTAL_EXPENSE from userexpenses where userid='"+session['userid']+"'"
    stmt=ibm_db.exec_immediate(conn,query)
    expenselogg=ibm_db.fetch_assoc(stmt)
    expenselog=[]
    while expenselogg:
        expenses,expenses_amount=[],[]
        for i in str(expenselogg['EXPENSES']).split(";"):
            if i!="" and i!=" ":
                expenses.append(i)
        for i in str(expenselogg['EXPENSES_AMOUNT']).split(";"):
            if i!='' and i!=" ":
                expenses_amount.append(i)
        expenselogg['EXPENSES']=expenses
        expenselogg['EXPENSES_AMOUNT']=expenses_amount
        expenselogg['NUMBEROFEXPENSES']=len(expenses)
        expenselog.append(expenselogg)
        print(expenselog)
        expenselogg=ibm_db.fetch_assoc(stmt)

    return expenselog[::-1]
  

#---------------------------- expense close --------------------------------------------------

#---------------------------- income open --------------------------------------------------


@app.route("/myincome")
def myincome():

    
    userid=str(session['userid'])
    query="select * from userecons where userid='"+userid+"' "
    
    usereconn=ibm_db.exec_immediate(conn,query)
  
    userecon=ibm_db.fetch_assoc(usereconn)
    userecons=[]
   

    while userecon:
        for j in str(userecon["INCOMES"]).split(";"):
            userecons.append(j)
        userecon=ibm_db.fetch_assoc(usereconn)
    

    incomelog=getincomelog()
    streaks=getstreak(session["userid"])
    return render_template("incomes/income.html",userecons=userecons,incomelog=incomelog,streaks=streaks)

@app.route("/addincome",methods=['GET','POST'])
def addincome():
    if request.method=="POST":
        userid=session["userid"]
        allincomes=request.form['allincomes']
        curdate=date.today()
        incomes=seperatenaemandamount(allincomes)  
        incomenamest,incomeamountst=incomes[0],incomes[1]
        totalincome=sum(incomeamountst)
        incomeamounts,incomenames="",""

        for i in incomeamountst:
            incomeamounts+=str(i)
            incomeamounts+=";" 
        for i in incomenamest:
            incomenames+=i;incomenames+=";"
        incomenames=incomenames[:-1]
        incomeamounts=incomeamounts[:-1]

        
        query="select date from userincomes where userid='"+session['userid']+"'"
        datess=ibm_db.exec_immediate(conn,query)
        dates=ibm_db.fetch_assoc(datess)
        flag=0
        while dates:
            if dates['DATE']==str(curdate):
                flag=1;break
            dates=ibm_db.fetch_assoc(datess)

        
        if flag==0:
            
            fields=["userid" , "date" , "incomes", "incomes_amount", "total_income"]
            values=[userid,curdate,incomenames,incomeamounts,totalincome]
            
            insertsql("userincomes",fields,values)
            
        else:
            query="select incomes,incomes_amount,total_income from userincomes where userid ='"+userid+" ' and date = '"+str(curdate)+"'"
            
            userincomess=ibm_db.exec_immediate(conn,query)

            userincomes=ibm_db.fetch_assoc(userincomess)

            incomenamestt=[]
            incomeamountstt=[]
            while userincomes:
                for j in str(userincomes['INCOMES']).split(";"):
                    incomenamestt.append(j)
                for j in str(userincomes['INCOMES_AMOUNT']).split(";"):
                    incomeamountstt.append(j)
                userincomes=ibm_db.fetch_assoc(userincomess)
            incomest={}
            
            for i in range(len(incomenamestt)):
                incomest[incomenamestt[i]]=incomeamountstt[i]
            
            for i in range(len(incomenamest)):
                incomest[incomenamest[i]]=incomeamountst[i]
            
            
            incomenames="";incomeamounts="";totalincome=0
            
            for i in incomest:
                if incomest[i]!='':
                    incomenames+=(i+";")
                    incomeamounts+=str(incomest[i])+";"
                    totalincome+=int(incomest[i])
            
            query="update userincomes set incomes= (?) ,incomes_amount = (?), total_income = (?) where userid = '"+userid+"' and date = '"+str(curdate)+"'"
             
            prep_stmt=ibm_db.prepare(conn,query)
        
            ibm_db.bind_param(prep_stmt,1,incomenames)
            ibm_db.bind_param(prep_stmt,2,incomeamounts)
            ibm_db.bind_param(prep_stmt,3,totalincome)
            
            ibm_db.execute(prep_stmt)

    return redirect(url_for("myincome"))
        
def getincomelog():

    query="select DATE, INCOMES, INCOMES_AMOUNT, TOTAL_INCOME from userincomes where userid='"+session['userid']+"'"
    stmt=ibm_db.exec_immediate(conn,query)
    incomelogg=ibm_db.fetch_assoc(stmt)
    incomelog=[]
    while incomelogg:
        incomes,incomes_amount=[],[]
        for i in str(incomelogg['INCOMES']).split(";"):
            if i!="" and i!=" ":
                incomes.append(i)
        for i in str(incomelogg['INCOMES_AMOUNT']).split(";"):
            if i!='' and i!=" ":
                incomes_amount.append(i)
        incomelogg['INCOMES']=incomes
        incomelogg['INCOMES_AMOUNT']=incomes_amount
        incomelogg['NUMBEROFINCOMES']=len(incomes)
        incomelog.append(incomelogg)
        print(incomelog)
        incomelogg=ibm_db.fetch_assoc(stmt)

    return incomelog[::-1]

    
    
    





#---------------------------- income close --------------------------------------------------
