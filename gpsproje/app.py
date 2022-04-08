
from http import client
from multiprocessing.connection import Client
from pymongo import MongoClient


from asyncio.windows_events import NULL
from contextlib import nullcontext
import datetime as dt #n
from tokenize import String
from flask import Flask, flash, render_template,request,redirect,url_for,session,jsonify
import sqlite3 as sql
import zmq
from datetime import timedelta
import json


cluster=MongoClient('localhost',27017)
print(cluster.list_database_names())
db=cluster['cardb']
coll=db['carcollection']
entrycoll=db['entrycollection']


context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5559")

arac_id_gecmis=""
date_web_app=""
clock_web_app=""
current_time ="2018-10-02 17:06"
hangiaracc = 0
emailogin=""
hata=1

db= sql.connect("customerdb.sqlite3")
cursor=db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS customertable (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    password TEXT,
    car1 TEXT,
    car2 TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS timetable (
    name TEXT,
    time TEXT)""") #

cursor.execute("""CREATE TABLE IF NOT EXISTS exittable (
    name TEXT,
    time TEXT)""") # 

#cursor.execute("INSERT INTO customertable VALUES (1, 'ahmet',  'ahmet@hotmail.com', '1ahmet', '1', '2')")
#cursor.execute("INSERT INTO customertable VALUES (2, 'berk',  'berk@hotmail.com', 'berk123', '3', '4')")


db.commit()
db.close()


app= Flask(__name__)
@app.route("/")
def index():
    return render_template("View.html")

@app.route('/exit',methods=["POST"])
def exit():
    if request.method == "POST":
     global emailogin
     current=dt.datetime.now() #n
     db= sql.connect("customerdb.sqlite3")
     cr=db.cursor()

     strcurrent=str(current) 
     print(current)

     strmail=str(emailogin)
     cr.execute("INSERT INTO exittable VALUES (?, ?)",(strmail, strcurrent))
     db.commit()
     db.close()   
     return render_template("View.html")



@app.route('/account',methods=["POST"])
def login():
    if request.method == "POST":
        global emailogin
        emailogin = request.form.get("emailogin")
        passlogin = request.form.get("passlogin")
        passlogin="('"+passlogin+"',)"
        db= sql.connect("customerdb.sqlite3")
        cursor=db.cursor()
        cursor.execute("SELECT password FROM customertable WHERE email =?",(emailogin,))
        rows = cursor.fetchone()
        print(rows)
        print(passlogin)
        global hata


        if passlogin == str(rows):
           print(passlogin==str(rows))
           global arac_id_gecmis
           db= sql.connect("customerdb.sqlite3")
           cursor=db.cursor()
            
           cursor.execute("SELECT car1 FROM customertable WHERE email =?",(emailogin,))
           rows = cursor.fetchone()
           arac_id_gecmis = str(rows).replace('(','').replace(')','').replace('\'','').replace(',','')
            
           db.close()




           current=dt.datetime.now() #n
           db= sql.connect("customerdb.sqlite3")
           cr=db.cursor()

           strcurrent=str(current) 
           print(current)


           strmail=str(emailogin)
           cr.execute("INSERT INTO timetable VALUES (?, ?)",(strmail, strcurrent))
           db.commit()
           db.close()

           return render_template("View2.html")
        elif hata < 3:
            hata=hata+1
            print(hata)
            return redirect(request.referrer)
        else:
           print(passlogin==str(rows))
           
           return render_template("View3.html")
    

        
def langlat(id):
    
    my__string = bytes(id, encoding='utf-8')
    socket.send(my__string)
    message = socket.recv_string()
    return message;        








@app.route('/getdata',methods=["GET","POST"])
def getdata():
   
        
        db= sql.connect("customerdb.sqlite3")
        cursor=db.cursor()
        rows = ''
        
        if(str(hangiaracc) == '1'):
            cursor.execute("SELECT car1 FROM customertable WHERE email =?",(emailogin,))
            rows = cursor.fetchone()
        
        elif(str(hangiaracc) == '2'):
            cursor.execute("SELECT car2 FROM customertable WHERE email =?",(emailogin,))
            rows = cursor.fetchone()
        else:
            cursor.execute("SELECT car1 FROM customertable WHERE email =?",(emailogin,))
            rows = cursor.fetchone()
        
        print(rows)
        arac_id = str(rows).replace('(','').replace(')','').replace('\'','').replace(',','')
        latitude_web, longitude_web, date_web, clock_web = langlat(arac_id).split()
        print(f"latitude: {latitude_web} longitude: {longitude_web}")

        global current_time
        global date_web_app
        global clock_web_app
        global arac_id_gecmis
        arac_id_gecmis = arac_id
        date_web_app = date_web
        clock_web_app = clock_web
        current_time = date_web + " " + clock_web
        mydict = { "date": current_time, "x": latitude_web, "y": longitude_web, "id": arac_id}
        entrycoll.insert_one(mydict)

        return jsonify(lat=latitude_web,lng=longitude_web,tarih=date_web,saat=clock_web)
   
        
        
        



@app.route('/hangiarac',methods=["POST"])
def hangiarac():
    global hangiaracc
    hangiaracc = request.form.get('sayi')
    return ('', 204)



@app.route("/zaman", methods=['POST','GET'])
def hesapla():
    if request.method == 'POST':
        sayi = request.form.get('saatx') 
        global current_time
        global arac_id_gecmis
        date_time_obj = dt.datetime.strptime(current_time, '%Y-%m-%d %H:%M')
        final_time = date_time_obj + timedelta(hours=-float(sayi))
        final_time_str = final_time.strftime('%Y-%m-%d %H:%M')

        date_time_obj = dt.datetime.strptime(current_time, '%Y-%m-%d %H:%M')
        final_current_time = date_time_obj + timedelta(minutes=+1)
        current_time_str = final_current_time.strftime('%Y-%m-%d %H:%M')


        
        a=coll.find({"id": arac_id_gecmis, "date" : { "$gt" :  final_time_str, "$lt" : current_time_str}}, {"x":1, "y":1, "_id":False})
        cordsjason = []

        for element in a:
            cordsjason.append(element)
        print(cordsjason)
        return jsonify(cordsjason)


    else:
        return "error"


if __name__ == "__main__":
    app.run(debug=True)





