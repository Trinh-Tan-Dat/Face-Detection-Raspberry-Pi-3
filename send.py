import cv2
import zmq
import base64
import paho.mqtt.client as paho
from paho import mqtt



mqtt_broker = "hbjaiwnamsawhqjdwncssjfsadkjkdwweh.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "iot/result"
mqtt_username = "trinhdat"
mqtt_password = "trinhdat"
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
def on_message(client, userdata, msg):
    print(str(msg.payload.decode()))

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv311)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_broker, mqtt_port)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish
client.subscribe(mqtt_topic)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://127.0.0.1:5555") 


cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    x = 1
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    socket.send(jpg_as_text)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
socket.close()
cv2.destroyAllWindows()


