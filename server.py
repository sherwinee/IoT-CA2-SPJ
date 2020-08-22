from flask import Flask, render_template, jsonify,request

app = Flask(__name__)

import json
import dynamodb
import jsonconverter as jsonc
import pandas as pd
import ml


import simpleaudio as sa

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import datetime as datetime

counter = 0
result_df = pd.DataFrame()

@app.route("/api/getdata",methods=['POST','GET'])
def apidata_getdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            #jsonc.data_to_json(
            data = {'chart_data': json.loads(jsonc.data_to_json(dynamodb.get_data_from_dynamodb())), 
             'title': "IOT Data"}            
            #data = data.replace("\"","'")
            print("before json loads")
            global counter
            global result_df

            # Convert to dataframe, dropping dynamoDB id column
            df = pd.DataFrame(data['chart_data'], dtype=float).drop(['id', 'speedkmhour', 'datetime_value'], axis=1)
            result_df = ml.predict_danger(df)
            print('RESULT DF')
            print(result_df)

            #dataj = json.loads(data)
            print()
            print("after json loads")
            #print(dataj)
            #return data
            return jsonify(data)
            #return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

@app.route("/predict", methods=['POST', 'GET'])
def predict():
    global result_df
    result_dict = result_df.set_index('bookingID')['label'].to_dict()
    return jsonify(result_dict)

@app.route("/brake", methods=['POST'])
def brake():
    def force_slow_down(bookingid):
        # This function simulates an api that slows the car given the booking id
        wave_obj = sa.WaveObject.from_wave_file("static/audio/brake.wav")
        play_obj = wave_obj.play()
        print(f"Car {bookingid} has been slown down.")
    
    bookingid = request.form["bookingid"]
    force_slow_down(bookingid)
    return ('', 204)

@app.route("/speedpub", methods=['POST'])
def speedpub():
    spd = request.form["speed"]
    # This function sounds a buzzer connected to the raspberry pi to signal the driver to slow down
    host = "a2mtg194yamduh-ats.iot.us-east-1.amazonaws.com"
    rootCAPath = "rootca.pem"
    certificatePath = "certificate.pem.crt"
    privateKeyPath = "private.pem.key"

    ca2_rpi = AWSIoTMQTTClient("CA2_webapp_Pub")
    ca2_rpi.configureEndpoint(host, 8883)
    ca2_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    ca2_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    ca2_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
    ca2_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
    ca2_rpi.configureMQTTOperationTimeout(5)  # 5 sec

    message = {}								# publish to dynamodb using mqtt
    message["deviceid"] = "deviceid_CA2_1"	
    now = datetime.datetime.now()
    message["datetimeid"] = now.isoformat()      
    message["speed"] = spd
    # ca2_rpi.publish("/sensors/speed/overspeed", json.dumps(message), 1) # is not able to publish but will crash the subscriber on the raspberry pi
    return ('', 204)

@app.route("/")
def home():
    return render_template("index.html")

app.run(debug=True,host="0.0.0.0", port=80)
