
import cv2
import numpy as np
import os 
import zmq
import cv2
import base64
import paho.mqtt.client as paho
from paho import mqtt
import time
import threading

mqtt_broker = "hbjaiwnamsawhqjdwncssjfsadkjkdwweh.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "iot/result"
mqtt_username = "trinhdat"
mqtt_password = "trinhdat"
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv311)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_broker, mqtt_port)
client.on_subscribe = on_subscribe

client.subscribe(mqtt_topic)

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind("tcp://*:5555")  
socket.setsockopt_string(zmq.SUBSCRIBE, '')


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

id = 0

names = [ 'Dat',"Unknown"]

def sendMq(topic, id, time,confi):
    client.publish(topic, payload=f"Phát hiện: {id} , thời gian phát hiện {(time):.4f}, độ chính xác {confi}")


while True:
    jpg_as_text = socket.recv()
    start_time = time.time()
    jpg_original = base64.b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    img = cv2.flip(img, 1) 
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(0.1 * img.shape[1]), int(0.1 * img.shape[2])),
       )
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        if (confidence < 40):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "Unknown"
            confidence = "  {0}%".format(round(confidence))
        end_time = time.time()
        client.publish(mqtt_topic, payload=f"Phat hien: {id} , thoi gian phat hien {(end_time-start_time):.4f}, độ chính xác {confidence}")
        if (id != "Unknown"):
            cv2.putText(img, str(id) +' '+ str(confidence), (x+5,y-5), font, 1, (0,0,255), 2)
        else:             
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
    cv2.imshow('camera',img) 
    k = cv2.waitKey(10) & 0xff
    if k == 27 :
        break

print("\n [INFO] Exiting Program and cleanup stuff")
socket.close()
cv2.destroyAllWindows()
