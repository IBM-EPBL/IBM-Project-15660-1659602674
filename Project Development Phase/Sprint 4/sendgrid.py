from sendgrid import SendGridAPIClient, Mail
import os
from dotenv import load_dotenv
import ibm_db

load_dotenv()

def mailto(email, subject, content):
    message = Mail(from_email='servo.inventory@gmail.com', to_emails=email,
                   subject=subject, html_content='<strong> {} </strong>'.format(content))
    try:
        sg = SendGridAPIClient(os.getenv('SendGrid_API_Key'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def checkstatus(userDB, email, username):
        sql = "SELECT th_value FROM threshold_value WHERE email='{}'".format(email)
        stmt = ibm_db.exec_immediate(userDB, sql)
        res = ibm_db.fetch_assoc(stmt)
        th_value = int(res['TH_VALUE'])
        sql = "SELECT * FROM USERPRODUCTS WHERE username='{}'".format(username)
        stmt = ibm_db.exec_immediate(userDB, sql)
        res = ibm_db.fetch_assoc(stmt)
        while res != False:
            curr_stocks = int(res['AVAILABLESTOCK'])
            if curr_stocks < th_value:
                pid = res['PRODUCTID']
                sql = "SELECT productname FROM PRODUCTS WHERE productid='{}'".format(pid)
                stmt = ibm_db.exec_immediate(userDB, sql)
                res = ibm_db.fetch_assoc(stmt)
                prod_name = res['PRODUCTNAME']
                mailto(email, "Threshold Limit Alert", "Alert! product '{0}' available stocks had dropped below the threshold limit '{1}'".format(prod_name, th_value))
            res = ibm_db.fetch_assoc(stmt)

def getProductsBelowThValue(userDB, email, username):
        prodList = []
        sql = "SELECT th_value FROM threshold_value WHERE email='{}'".format(email)
        stmt = ibm_db.exec_immediate(userDB, sql)
        res = ibm_db.fetch_assoc(stmt)
        th_value = res['TH_VALUE']
        sql = "SELECT * FROM USERPRODUCTS WHERE username='{}'".format(username)
        stmt = ibm_db.exec_immediate(userDB, sql)
        res = ibm_db.fetch_assoc(stmt)
        while res != False:
            curr_stocks = int(res['AVAILABLESTOCK'])
            if curr_stocks < th_value:
                pid = res['PRODUCTID']
                sql = "SELECT productname FROM PRODUCTS WHERE productid='{}'".format(pid)
                stmt = ibm_db.exec_immediate(userDB, sql)
                res = ibm_db.fetch_assoc(stmt)
                prod_name = res['PRODUCTNAME']
                prodList.append(prod_name)
            res = ibm_db.fetch_assoc(stmt)

        return prodList