from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from flask import Flask
import requests
from datetime import date, timedelta, datetime
import dateutil.parser as parser
import json
from bs4 import BeautifulSoup
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import importlib
spam_spec = importlib.util.find_spec("config")
found = spam_spec is not None

if found:
    import config
    print("Using config file")
    SENDGRID_API_KEY = config.SENDGRID_API_KEY
    SENDGRID_API_NAME = config.SENDGRID_API_NAME
else:
    import os
    print("Using env")
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
    SENDGRID_API_NAME = os.environ['SENDGRID_API_NAME']
        

app = Flask(__name__)

# FUNCTIONS ############################################################

def CreateMessage(subject, sender, receiver, **args):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver
    # Create the plain-text and HTML version of your message
    text = '''\
        Image: {image}
        Title: {title}
        Pages: {pages}
        Length: {length}
        About: {about}
        Features: {features}
        View at: https://www.packtpub.com/free-learning
    '''.format(
        title = args.get("title"),
        image = args.get("image"),
        pages = args.get("pages"),
        length = args.get("length"),
        about = args.get("about"),
        features = args.get("features")
     )

    html = '''\
        <html>
            <head>
            </head>
            <body>
                <p>Hi,<br>
                How are you?<br>
                A new book is available at <a href="https://www.packtpub.com/free-learning">Packt</a>

                <br>
                <br>
                <img src={image} alt="Book Image"> Title: {title}
                <br> 
                Pages: {pages}
                <br>
                Length: {length}
                <br>
                About: {about}
                <br>
                Features: {features}

                <button style="
                    background-color: #008CBA;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                ">Get Book</button>
            </body>
        </html>
    '''.format(
        title = args.get("title"),
        image = args.get("image"),
        pages = args.get("pages"),
        length = args.get("length"),
        about = args.get("about"),
        features = args.get("features")
    )

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)
    
    return message

def SendSecureEmail(**args):
    
    # SMTP CONFIG #####################

    # port = 587  # For SSL
    port = 465  # For SSL
    
    # password = input("Type your password and press enter: ")
    # sender_email = "jcardenas.lie@gmail.com"
    sender_email = "jcardenas.lie@gmail.com"

    # password = "9C5afg6k2D0AUnN1"
    # password = "cafetortugascott"
    # password = "cafetortugascott"

    server = "smtp.sendgrid.net"
        
    # EMAIL CONFIG #####################

    receiver_email = "jcardenas.lie@gmail.com"

    subject = "Today's book at Packt"

    # Create a secure SSL context
    context = ssl.create_default_context()

    message = CreateMessage(subject, sender_email, receiver_email, **args)
    print( SENDGRID_API_KEY, SENDGRID_API_NAME )
    with smtplib.SMTP_SSL(server, port, context=context) as server:
        server.login(SENDGRID_API_NAME, SENDGRID_API_KEY )
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def SendUnsecuredEmail(**args):
    # smtp_server = "smtp-relay.sendinblue.com"
    smtp_server = "smtp.gmail.com"
    # smtp_server = "smtp-mail.outlook.com"

    port = 587  # For starttls

    sender_email = "jcardenas.lie@gmail.com"
    # sender_email = "jquin_cardenas@hotmail.com"
    
    password = "c4f3t0rtug4sc0tt"
    # password = "9C5afg6k2D0AUnN1"
    # # password = "cafetortugascott"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        
        receiver_email = "jcardenas.lie@gmail.com"

        subject = "Today's book at Packt"
        
        message = CreateMessage(subject, sender_email, receiver_email, **args)

        server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 

def DateToISO(date):
    
    date = date.strftime("%c").split(" ")
    
    if date[2] == '':
        newDate = date[0] + ', ' + date[3] + " " + date[1] + " " +date[5] + " " + date[4]
    elif date[2] != '':
        newDate = date[0] + ', ' + date[2] + " " + date[1] + " " +date[4] + " " + date[3]

    print(date)
    print(newDate)
    
    date = datetime.strptime(newDate, '%a, %d %b %Y %H:%M:%S')
    
    return date.isoformat().split("T")[0]

def TodaysBook():
    
    today = datetime.now() + timedelta(hours=5)
    
    tomorrow = today + timedelta(days=1)
    
    t1 = DateToISO( today ) 
    
    t2 = DateToISO( tomorrow )

    url = "https://services.packtpub.com/free-learning-v1/offers?dateFrom={}T00:00:00.000Z&dateTo={}T00:00:00.000Z".format(t1, t2)
    
    response = requests.get(url)

    product_id = json.loads(response.content)['data'][0]['productId']

    url = "https://static.packt-cdn.com/products/{}/summary".format(product_id)
    
    response = requests.get(url)

    book = json.loads(response.content)
    
    data = {
        'title': book['title'],
        'image' : book['coverImage'],
        'pages': book['pages'],
        'length': book['length'],
        'about': book['about'],
        'features' : book['features']
    }
    
    print('Send Email! The time is: %s' % datetime.now())

    SendSecureEmail(**data)
    # SendUnsecuredEmail(**data)

    return response.content

# SCHEDULER ############################################################

def sensor():
    TodaysBook()
    # print("Email Send")

def tick():
    print('Tick! The time is: %s' % datetime.now())

sched = BackgroundScheduler(daemon=True)
# sched.add_job(tick,'interval', seconds=10)
sched.add_job(sensor,'interval', seconds=30)
# sched.add_job(sensor_test, 'cron', day_of_week='mon-sun', hour=11, minute=30)
sched.start()

atexit.register(lambda: sched.shutdown())

# ROUTES ############################################################

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/freelearning')
def freeLearning():
    return TodaysBook()

# RUN ############################################################

if __name__ == '__main__':
    app.run(
        debug = True, 
        use_reloader=False
        )