
# python dependencies: flask, wtforms, py3720
# system dependencies: s3270

from random import randint
from time import strftime
from datetime import datetime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from py3270 import Emulator
from credentials import MainframeLocation, MainframeUsername, MainframePassword

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '9eBBtQ8IqUX1mWfZ31s9YC1lCRlFLTw4Tcg9cm2'
em = Emulator()
connected = 0

class ReusableForm(Form):
    court = TextField('Court:', validators=[validators.required()])
    caseyear = TextField('Case Year:', validators=[validators.required()])
    casetype = TextField('Case Type:', validators=[validators.required()])
    casenumber = TextField('Case Number:', validators=[validators.required()])

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(court, caseyear, casetype, casenumber):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Court={}, CaseYear={}, CaseType={}, CaseNumber={} \n'.format(timestamp, court, caseyear, casetype, casenumber))
    data.close()

def search(court, caseyear, casetype, casenumber):
    global result
    global judgename
    global servicedate
    global fileddate
    global connected

    if connected == 0:
        em.connect(MainframeLocation)
        em.wait_for_field()
        em.fill_field(20, 21, 'B', 1)
        em.send_enter()
        em.wait_for_field()
        em.send_string(MainframeUsername)
        em.send_enter()
        em.send_string(MainframePassword)
        em.send_enter()
        em.wait_for_field()
        em.send_string('1')
        em.send_enter()
        em.wait_for_field()
    else:
        em.send_pf7()
        em.send_pf7()
        em.wait_for_field()
        em.send_string('1')
        em.send_enter()
        em.wait_for_field()
    
    em.send_string('Q')
    em.send_string('DCKT')
    em.send_enter()
    em.send_string(court, ypos=10, xpos=47)
    em.send_string(caseyear, ypos=12, xpos=47)
    em.send_string(casetype, ypos=14, xpos=47)
    em.send_string(casenumber, ypos=16, xpos=47)
    em.send_enter()
    resultcode = 0

    judgename = "N/A"
    fileddate = "N/A"
    servicedate = "N/A"

    if em.string_found(24,15,'INVALID COURT ENTERED'):
        result = 'Invalid Court Entered'
        resultcode = 1
    
    if em.string_found(24,15,'INVALID CASE TYPE ENTERED'):
        result = 'Invalid Case Type Entered'
        resultcode = 1

    if em.string_found(24,15,'CASE NOT ON FILE'):
        result = 'Case Not Found'
        resultcode = 1
        
    if resultcode == 0:
        result = 'Search Run'
        
        if casetype == "CR":
            judgename = em.string_get(5, 15, 15)
            servicedate = em.string_get(8, 67, 10)
            fileddate = em.string_get(18, 29, 10)
        else:
            judgename = em.string_get(7, 14, 15)
            em.send_enter()
            fileddate = em.string_get(8, 30, 8)
            em.send_string('Q')
            em.send_enter()
            servicedate = em.string_get(9, 25, 8)
            servicedate = datetime.strptime(str(servicedate), '%Y%m%d').strftime('%m-%d-%Y')

    return

@app.route("/", methods=['GET', 'POST'])
def hello():
    global connected
    form = ReusableForm(request.form)

    #print(form.errors)
    if request.method == 'POST':
        court=request.form['court']
        caseyear=request.form['caseyear']
        casetype=request.form['casetype']
        casenumber=request.form['casenumber']

        if form.validate():
            write_to_disk(court, caseyear, casetype, casenumber)
            search(court, caseyear, casetype, casenumber)
            flash('Searched: {}-{}-{}-{}'.format(court, caseyear, casetype, casenumber))
            flash('Result Code: {}'.format(result))
            flash('Assigned Judge: {}'.format(judgename))
            flash('Filed Date: {}'.format(fileddate))
            flash('Service/Arraignment Date: {}'.format(servicedate))
            connected = 1
        else:
            flash('Error. All fields are required.')

    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()