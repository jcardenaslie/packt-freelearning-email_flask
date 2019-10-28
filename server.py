from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import requests
from datetime import date, timedelta, datetime
import dateutil.parser as parser
import json
from bs4 import BeautifulSoup
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# FUNCTIONS ############################################################
def SendEmail(**args):
    port = 465  # For SSL
    # password = input("Type your password and press enter: ")
    fromEmail = "jcardenas.lie@gmail.com"
    toEmail = "jcardenas.lie@gmail.com"
    password = "cafetortugascott"

    # Create a secure SSL context
    context = ssl.create_default_context()

    sender_email = fromEmail
    receiver_email = toEmail

    message = MIMEMultipart("alternative")
    message["Subject"] = "Today's book at Packt"
    message["From"] = sender_email
    message["To"] = receiver_email

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

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def DateToISO(date):
    date = date.strftime("%c").split(" ")
    print(date)
    newDate = date[0] + ', ' + date[2] + " " + date[1] + " " +date[4] + " " + date[3]
    date = datetime.strptime(newDate, '%a, %d %b %Y %H:%M:%S')
    return date.isoformat().split("T")[0]

def TodaysBook():
    
    today = datetime.now() + timedelta(hours=5)
    
    tomorrow = today + timedelta(days=1)
    
    t1 = DateToISO( today ) 
    
    t2 = DateToISO( tomorrow )

    url = "https://services.packtpub.com/free-learning-v1/offers?dateFrom={}T00:00:00.000Z&dateTo={}T00:00:00.000Z".format(t1, t2)
    
    response = requests.get(url)

    product_id = json.loads(response.content)['data'][0]['productId']; print(product_id)

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
    # print(data)

    SendEmail(**data)

    return response.content

def sensor():
    """ Function for test purposes. """
    TodaysBook()
    print("Email Send")

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval', days=1)
sched.start()

# ROUTES ############################################################
@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/freelearning')
def freeLearning():
    return TodaysBook()

# RUN ############################################################
if __name__ == '__main__':
    app.run(debug = True)