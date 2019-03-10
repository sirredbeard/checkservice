from random import randint
from time import strftime, sleep
from datetime import datetime
from dateutil.parser import parse
from flask import Flask, render_template, flash, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from py3270 import Emulator
from credentials import MainframeLocation, MainframeUsername, MainframePassword

DEBUG = False
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '9eBBtQ8IqUX1mWfZ31s9YC1lCRlFLTw4Tcg9cm2'
limiter = Limiter(app, key_func=get_remote_address)
em = Emulator()
connected = 0

class ReusableForm(Form):
    global message
    court = TextField('Court:', validators=[validators.required(),validators.length(min=2,max=2)])
    caseyear = TextField('Case Year:', validators=[validators.required(),validators.length(min=2,max=4)])
    casetype = TextField('Case Type:', validators=[validators.required(),validators.length(min=2,max=2)])
    casenumber = TextField('Case Number:', validators=[validators.required(),validators.length(min=1,max=4)])

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

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
    global plaintiffname
    global defendantname
    global connected
    global casedescription
    global resultcode

    court = court.upper()
    casetype = casetype.upper()
    
    if caseyear == "0":
        caseyear = "2000"

    if not caseyear.startswith("20"):
        caseyear = ''.join(('20',caseyear))

    if connected == 0:
        em.connect(MainframeLocation)
        sleep(0.2)
        em.fill_field(20, 21, 'B', 1)
        em.send_enter()
        sleep(0.2)
        em.send_string(MainframeUsername)
        em.send_enter()
        em.send_string(MainframePassword)
        em.send_enter()
        sleep(0.2)
        em.send_string('1')
        em.send_enter()
        sleep(0.2)
    else:
        em.send_pf7()
        em.send_pf7()
        em.send_string('1')
        em.send_enter()
        sleep(0.5)
    
    em.send_string('Q')
    em.send_string('DCKT')
    em.send_enter()
    em.send_string(court, ypos=10, xpos=47)
    em.send_string(caseyear, ypos=12, xpos=47)
    em.send_string(casetype, ypos=14, xpos=47)
    em.send_string(casenumber, ypos=16, xpos=47)
    em.send_enter()
    resultcode = 0

    judgename = ""
    fileddate = ""
    servicedate = ""
    plaintiffname = ""
    defendantname = ""
    casedescription = ""

    if em.string_found(24,15,'INVALID COURT ENTERED'):
        result = 'Invalid Court Entered ⚠️'
        resultcode = 1
    
    if em.string_found(24,15,'INVALID CASE TYPE ENTERED'):
        result = 'Invalid Case Type Entered ⚠️'
        resultcode = 1

    if em.string_found(24,15,'CASE NOT ON FILE'):
        result = 'Case Not Found ⚠️'
        resultcode = 1
        
    if resultcode == 0:
        result = 'Search Ran 👍'
        
        if casetype == "CR":
            judgename = em.string_get(5, 15, 20)
            servicedate = em.string_get(8, 67, 10)
            fileddate = em.string_get(18, 29, 10)
            casedescription = em.string_get(4, 58, 15)
            plaintiffname = "STATE OF GEORGIA 🚓"
            em.send_enter()
            em.send_string('Q')
            em.send_enter()
            sleep(0.2)
            defendantname = em.string_get(7, 30, 30)

            if fileddate == "          ":
                fileddate = "Unavailable 🤷"

            if servicedate == "00000000" or servicedate == "          " or is_date(servicedate) == False:
                servicedate = "Unavailable 🤷"
            else:
                servicedate = datetime.strptime(str(servicedate), '%M/%d/%Y').strftime('%m-%d-%y')

        else:
            judgename = em.string_get(7, 14, 20)
            em.send_enter()
            fileddate = em.string_get(8, 30, 8)
            casedescription = em.string_get(8, 49, 14)
            em.send_string('Q')
            em.send_enter()
            sleep(0.2)
            servicedate = em.string_get(9, 25, 8)
            
            if servicedate == "00000000" or servicedate == "          " or servicedate == "          " or servicedate == "" or is_date(servicedate) == False:
                servicedate = "Unavailable 🤷"
            else:    
                servicedate = datetime.strptime(str(servicedate),'%Y%m%d').strftime('%m-%d-%y')

                if servicedate.startswith('0') == True:
                    servicedate = servicedate.strip('0')
            
            em.send_enter()
            em.send_enter()
            sleep(0.2)
            
            for x in range(9, 20):
                checkparty = em.string_get(x, 2, 1)
                if checkparty == "D":
                    defendantname = em.string_get(x, 38, 30)

            for x in range(9, 20):
                checkparty = em.string_get(x, 2, 1)
                if checkparty == "P":
                    plaintiffname = em.string_get(x, 38, 30)
    em.send_pf7()
    em.send_pf7()
    
    return

@app.route("/", methods=['GET', 'POST'])
@limiter.limit("200/day;50/hour;20/minute")
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
            flash('Searched: 🔎 {}-{}-{}-{}'.format(court, caseyear, casetype, casenumber))
            flash('Result: {}'.format(result))
            connected = 1

            if resultcode == 0:
                flash('Plaintiff/Complaintant: {}'.format(plaintiffname))
                flash('Defendant/Respondant: {}'.format(defendantname))
                flash('Description: {}'.format(casedescription))
                flash('Assigned Judge ⚖️: {}'.format(judgename))
                flash('Filed Date 📅: {}'.format(fileddate))
                flash('Service/Arraignment Date 📮: {}'.format(servicedate))

        else:
            flash("Invalid search criteria. ⚠️")

    return render_template('index.html', form=form)

@app.errorhandler(500)
def internal_error(error):
    global connected
    form = ReusableForm(request.form)

    flash("Something  went horribly wrong. ⚠️ Please try again.")
    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()