# Uses pi_switch from https://github.com/lexruee/pi-switch-python
# See pi_switch readme for details on setup

from pi_switch import RCSwitchReceiver
import time
import paho.mqtt.client as mqtt

receiver = RCSwitchReceiver()
receiver.enableReceive(2)

def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
#    client.subscribe("Home/#")

def publish_message():
    # Initialize the client that should connect to the Mosquitto broker
    client = mqtt.Client()
    client.on_connect = on_connect
    connOK=False
    while(connOK == False):
        try:
            print("try connect")
            client.connect("192.168.1.16", 1883, 60)
            connOK = True
        except:
            connOK = False
        time.sleep(2)

    client.publish("Home/Frontdoor/Opened","1.0")
    time.sleep(5)
    client.disconnect()

acceptedTypes = { 1 : "Light", 2 : "Temp [C]", 3: "Humidity [%]", 4: "Door open" }
prev_value = 0L
while True:
    if receiver.available():
        value = receiver.getReceivedValue()

        if value == prev_value:
            # we have already seen this measurement, so ignore it
            continue
        
        # decode byte3
        byte3 = (0xFF000000 & value) >> 24
        typeID = int((0xF0 & byte3) >> 4)
        seqNum = int((0x0F & byte3))

        # decode byte2 and byte1
        data = int((0x00FFFF00 & value) >> 8)

        # decode byte0
        checkSum = int((0x000000FF & value))

        calculatedCheckSum = 0xFF & (typeID + seqNum + data)

        # Sanity checks on received data
        correctData = True
        if calculatedCheckSum != checkSum:
            correctData = False
        elif data > 1023:
            correctData = False
        elif typeID not in acceptedTypes:
            correctData = False
        elif seqNum > 15:
            correctData = False

        if correctData:
            print(str.format("{0}: {1}={2} SeqNum={3}",time.ctime(),acceptedTypes[typeID],data,seqNum))
            prev_value = value
            if (typeID == 0x04):
                publish_message()

        receiver.resetAvailable()
        
