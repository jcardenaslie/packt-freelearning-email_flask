
from flask import Flask

app = Flask(__name__)

# ROUTES ############################################################

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/freelearning')
def freeLearning():
    return "Free Learning"

# RUN ############################################################

if __name__ == '__main__':
    app.run(
        debug = True, 
        use_reloader=False
        )