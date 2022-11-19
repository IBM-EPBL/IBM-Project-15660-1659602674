from flask import Flask,render_template, request,url_for 
app=Flask(__name__)
@app.route('/') 
def home(): 
    return render_template("index.html") 
@app.route('/postjob') 
def postjob(): 
    return render_template("postjob.html")    
if(__name__=='__main__'):
    app.run(debug=True)