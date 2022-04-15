from flask import Flask, render_template, request,url_for, jsonify, json
from socket import socket, AF_INET, SOCK_STREAM
import pickle
import random

app = Flask(__name__)

sock = socket(AF_INET, SOCK_STREAM)

# route tells flask what URL should trigger our function
# This will trigger localhost


colours = ['rgb(255, 0, 0)', 'rgb(255, 0, 255)', 'rgb(0, 0, 255)', 'rgb(0, 255, 0)',
           'rgb(102, 51, 0)', 'rgb(153, 204, 255)', 'rgb(255, 204, 229)', 'rgb(0, 0, 0)']


def update():
    """
    Updates all the datapoints in the graph
    """
    global sock
    sock.send(b'get-data')
    # Receive data
    data = sock.recv(4096)
    while data[-3:] != b'EOF':
        data += sock.recv(4096)

    data = data[:-3]  # Remove poison-pill from message

    if data == b'error':
        print("Server responded with error.")
        return None

    dic = pickle.loads(data)

    l = list()

    i = 0
    for station_id, info in dic.items():
        d = dict()
        d["station_id"] = station_id
        temp, rain = [], []
        for t, r in info:
            temp.append(t)
            rain.append(r)
        d["temp"] = temp
        d["rain"] = rain
        d["hours"] = [i for i in range(len(info))]
        d["color"] = colours[i % 8]
        i += 1
        l.append(d)
    return l




@app.route("/")
def homepage():
    return render_template("home.html")


# displays rain data
@app.route('/display_rain')
def display_rain():
    return render_template("rain.html")


@app.route('/display_rain/update', methods=["GET"])
def update_rain():
    """
    Updates rain data
    """
    l = update()
    return jsonify(json.dumps(l))


# displays temp data
@app.route('/display_temp')
def display_temp():
    """
    Starts the html file and displays it in the web
    """
    return render_template("temp.html")


# displays temp data
@app.route('/display_temp/update', methods=["GET"])
def update_temp():
    l = update()
    return jsonify(json.dumps(l))


def run(addr):
    global sock
    sock.connect(addr)
    sock.send(b'gib')
    app.run(host='0.0.0.0', port=5000)
