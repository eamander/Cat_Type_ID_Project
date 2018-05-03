from flask import Flask, render_template
from flask_socketio import SocketIO
import Algorithmia
# import simplejson as json
import os

app = Flask(__name__)

keys = dict()
keys['ALGO_KEY'] = os.environ['ALGO_KEY']

socketio = SocketIO(app)


@socketio.on('algo')
def handle_algo_event(json_data):
    # client = Algorithmia.client(keys['ALGO_KEY'])
    # algo = client.algo('eamander/Felindex/')
    # resp = algo.pipe(json_data).result  # Send this back to the client
    # socketio.send(resp, json=True)
    # return resp
    return json_data


@socketio.on('connect')
def connect_event():
    pass


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 33507))
    socketio.run(app, host='0.0.0.0', port=port)
