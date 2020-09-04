import pika
import requests
import json
import urllib.request
import ZODB, ZODB.FileStorage
import persistent
import transaction
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

from flask import Flask
from flask import request

#log files have different names

class Student(persistent.Persistent):
    studentName, secondName, studentID = '', '', ''
    
    
    def setStudentName(self, sName):
        self.studentName = sName
    def getStudentName(self):
        return self.studentName
    
    def setSecondName(self, ssName):
        self.secondName = ssName
    def getSecondName(self):
        return self.secondName
    
    def setStudentID(self, sId):
        self.studentID = sId
    def getstudentID(self):
        return self.studentID
        


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/insert')
def insertRecord():
    #get the values from the url
    firstname = request.args.get('firstname')
    secondname = request.args.get('secondname')#secondname is what i used for lastname
    studentid = request.args.get('studentid')

    #connect to the database
    storage = ZODB.FileStorage.FileStorage('mydata.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root
    #saving the data
    root.s1 = Student()

    # set the data into the node
    root.s1.setStudentName(firstname)
    root.s1.setSecondName(secondname)
    root.s1.setStudentID(studentid)
    

    # save the changes!
    transaction.commit()
    db.close()
    return 'All ok' + firstname +secondname +studentid

@app.route('/insertStudent1')
def insert_student():
    fn = request.args.get('firstname', '')
    secondname = request.args.get('secondname', '')
    studentid = request.args.get('studentid', '')
    return 'Inserting new student: ' + fn + secondname +studentid

    #http://localhost:5000/insertStudent?firstname=Matt
    
@app.route('/justweather')
def just_weather():

    with urllib.request.urlopen('http://kylegoslin.pythonanywhere.com/') as f:
        content = f.read().decode('utf-8')

    print(content)
    var = json.loads(content)
    forecast = var['forecast']
    
    return '{forecast:"' +forecast+ '"}'

#    output += '{' + forecast + '}'
#    return output # send it all back as JSON
    

@app.route('/updates')
def get_weather():
    output = ''
    
    
    
    f = open('updates.txt', 'r')
    x = f.readlines()

    '''
    This for loop will run over the lines in the file and print them to the console.

    '''

    output = '{'

    print(type(x))
    print(x)

    for item in x:
        #   "line1": "item1",
        output = output + '"line": "'+item + '",'
    f.close()

    output = output[:-1]

    output = output + '}'
        
    
    
    
    
    
    #1 todays date
    #2 weather
    with urllib.request.urlopen('http://kylegoslin.pythonanywhere.com/') as f:
        content = f.read().decode('utf-8')
    
    print(content)
    var = json.loads(content)
    forecast = var['forecast']
	
    output += '{' + forecast + '}'
   
    #3 context from text file

    return output # send it all back as JSON




    
@app.route('/ping')
def new_ping():
    return 'pong'


@app.route('/callClient')
def callClient():
    with xmlrpc.client.ServerProxy("http://localhost:8001/") as proxy:
        return "result: %s" % str(proxy.ctw(3))


    
@app.route('/rabbit')
def weather_hello():


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='weather')

    channel.basic_publish(exchange='',
                          routing_key='weather',
                          body='weather-rainy')
    print(" [x] Sent 'weather-rainy'")


    connection.close()
    return 'sent message to Q'

#url for students sent back to graphql
@app.route('/students')
def student_hello():


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='student')

    channel.basic_publish(exchange='',
                          routing_key='student',
                          body='all-students',
                          firstname='sam',
                          secondname='ade',
                          studentid='1')
    print(" [x] Sent 'all-students'" + firstname)


    connection.close()
    return 'sent message to Q'

    #http://localhost:5000/insert?firstname=sam&secondname=fdfsdf&studentid=1