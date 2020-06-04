from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class MqttClient(QtCore.QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2

    MQTT_3_1 = mqtt.MQTTv31
    MQTT_3_1_1 = mqtt.MQTTv311

    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()

    stateChanged = QtCore.pyqtSignal(int)
    hostnameChanged = QtCore.pyqtSignal(str)
    portChanged = QtCore.pyqtSignal(int)
    keepAliveChanged = QtCore.pyqtSignal(int)
    cleanSessionChanged = QtCore.pyqtSignal(bool)
    protocolVersionChanged = QtCore.pyqtSignal(int)

    messageSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MqttClient, self).__init__(parent)

        self.m_hostname = ""
        self.m_port = 1883
        self.m_keepAlive = 60
        self.m_cleanSession = True
        self.m_protocolVersion = MqttClient.MQTT_3_1

        self.m_state = MqttClient.Disconnected

        self.m_client =  mqtt.Client(clean_session=self.m_cleanSession,
            protocol=self.protocolVersion)

        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect


    @QtCore.pyqtProperty(int, notify=stateChanged)
    def state(self):
        return self.m_state

    @state.setter
    def state(self, state):
        if self.m_state == state: return
        self.m_state = state
        self.stateChanged.emit(state) 

    @QtCore.pyqtProperty(str, notify=hostnameChanged)
    def hostname(self):
        return self.m_hostname

    @hostname.setter
    def hostname(self, hostname):
        if self.m_hostname == hostname: return
        self.m_hostname = hostname
        self.hostnameChanged.emit(hostname)

    @QtCore.pyqtProperty(int, notify=portChanged)
    def port(self):
        return self.m_port

    @port.setter
    def port(self, port):
        if self.m_port == port: return
        self.m_port = port
        self.portChanged.emit(port)

    @QtCore.pyqtProperty(int, notify=keepAliveChanged)
    def keepAlive(self):
        return self.m_keepAlive

    @keepAlive.setter
    def keepAlive(self, keepAlive):
        if self.m_keepAlive == keepAlive: return
        self.m_keepAlive = keepAlive
        self.keepAliveChanged.emit(keepAlive)

    @QtCore.pyqtProperty(bool, notify=cleanSessionChanged)
    def cleanSession(self):
        return self.m_cleanSession

    @cleanSession.setter
    def cleanSession(self, cleanSession):
        if self.m_cleanSession == cleanSession: return
        self.m_cleanSession = cleanSession
        self.cleanSessionChanged.emit(cleanSession)

    @QtCore.pyqtProperty(int, notify=protocolVersionChanged)
    def protocolVersion(self):
        return self.m_protocolVersion

    @protocolVersion.setter
    def protocolVersion(self, protocolVersion):
        if self.m_protocolVersion == protocolVersion: return
        if protocolVersion in (MqttClient.MQTT_3_1, MQTT_3_1_1):
            self.m_protocolVersion = protocolVersion
            self.protocolVersionChanged.emit(protocolVersion)

    #################################################################
    @QtCore.pyqtSlot()
    def connectToHost(self):
        if self.m_hostname:
            self.m_client.connect(self.m_hostname, 
                port=self.port, 
                keepalive=self.keepAlive)

            self.state = MqttClient.Connecting
            self.m_client.loop_start()

    @QtCore.pyqtSlot()
    def disconnectFromHost(self):
        self.m_client.disconnect()

    def subscribe(self, path):
        if self.state == MqttClient.Connected:
            self.m_client.subscribe(path)

    #################################################################
    # callbacks
    def on_message(self, mqttc, obj, msg):
        mstr = msg.payload.decode("ascii")
        self.messageSignal.emit(mstr)

    def on_connect(self, *args):
        self.state = MqttClient.Connected
        self.connected.emit()

    def on_disconnect(self, *args):
        self.state = MqttClient.Disconnected
        self.disconnected.emit()

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Client")

        self.resize(402, 302)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 10, 101, 16))
        self.label.setObjectName("label")
        self.label.setText("Send Message")
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(10, 30, 281, 31))
        self.textEdit.setObjectName("textEdit")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 91, 16))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Receive Messages")
        self.bSend = QtWidgets.QPushButton(self)
        self.bSend.setGeometry(QtCore.QRect(310, 20, 75, 23))
        self.bSend.setObjectName("bSend")
        self.bSend.setText("Send")
        self.bWater = QtWidgets.QPushButton(self)
        self.bWater.setGeometry(QtCore.QRect(310, 50, 75, 23))
        self.bWater.setObjectName("bWater")
        self.bWater.setText("Water")
        self.textEdit_2 = QtWidgets.QTextEdit(self)
        self.textEdit_2.setGeometry(QtCore.QRect(10, 100, 381, 181))
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setObjectName("textEdit_2")
        self.bSend.clicked.connect(self.on_buttonPress)
        self.bWater.clicked.connect(self.on_buttonPressWater)


        self.client = MqttClient(self)
        self.client.stateChanged.connect(self.on_stateChanged)
        self.client.messageSignal.connect(self.on_messageSignal)

        self.client.hostname = "mqtt.eclipse.org"
        self.client.connectToHost()

    @QtCore.pyqtSlot(bool)
    def on_buttonPress(self):
        msg = self.textEdit.toPlainText()
        publish.single("Vin/ToServer", msg, hostname= "mqtt.eclipse.org")
        self.textEdit.clear()

    @QtCore.pyqtSlot(bool)
    def on_buttonPressWater(self):
        publish.single("Vin/ToServer", "Water please!", hostname= "mqtt.eclipse.org")
        

    @QtCore.pyqtSlot(int)
    def on_stateChanged(self, state):
        if state == MqttClient.Connected:
            #print(state)
            self.client.subscribe("Vin/ToClient")

    @QtCore.pyqtSlot(str)
    def on_messageSignal(self, msg):
            msg = str(msg)
            self.textEdit_2.append(msg)
        
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
