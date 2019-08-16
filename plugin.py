"""
<plugin key="EwpeSmartMqtt" name="EwpeSmart Air Conditioners via MQTT" version="1.0.2">
    <description>
      Plugin to control EwpeSmart powered air conditioners via MQTT bridge including:
      <ul>
        <li>Gree series with WiFi: Smart, U-CROWN</li>
        <li>Cooper&amp;Hunter series with WiFi: Supreme, Vip Inverter, ICY II, Arctic, Alpha, Alpha NG, Veritas, Veritas NG, ...</li>
        <li><a href="https://www.ecoair.org/x-series-inverter-air-conditioning">EcoAir X series</a></li>
      </ul>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="MQTT Username" width="300px" required="false" default=""/>
        <param field="Password" label="MQTT Password" width="300px" required="false" default="" password="true"/>
        <param field="Mode1" label="EWPE Smart MQTT Topic" width="300px" required="true" default="ewpe-smart"/>
        <param field="Mode3" label="MQTT Client ID (optional)" width="300px" required="false" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="No" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import time
import re
from mqtt import MqttClient
from device import Device


class EwpeSmartOverMqttPlugin:
    mqttClient = None

    def onStart(self):
        self.debugging = Parameters["Mode6"]

        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)

        self.devices = {}
        self.base_topic = Parameters["Mode1"].strip()

        mqttserver_address = Parameters["Address"].strip()
        mqttserver_port = Parameters["Port"].strip()
        mqtt_client_id = Parameters["Mode3"].strip()

        self.mqttClient = MqttClient(mqttserver_address, mqttserver_port, mqtt_client_id,
                                     self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)

        Domoticz.Debug("onStart called")

    def onMQTTConnected(self):
        self.mqttClient.subscribe([self.base_topic + '/#'])
        self.mqttClient.publish(self.base_topic + '/devices/list', '')

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))

        if topic == self.base_topic + '/devices':
            Domoticz.Log('Received available devices list')
            self.devices = {}

            for item in message:
                mac = item['mac']
                Domoticz.Log('Device ' + item['name'].strip() + ' (MAC: ' + mac + ')')
                self.devices[mac] = Device(Devices, self.base_topic, item)
        else:
            for mac, device in self.devices.items():
                if topic.startswith(self.base_topic + '/' + mac):
                    Domoticz.Debug(self.base_topic + '/' + mac)
                    device.handle_message(topic, message)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand: " + Command + ", level (" + str(Level) + ") Color:" + Color)
        [mac, alias] = Devices[Unit].DeviceID.split('_')

        if mac in self.devices:
            state = self.devices[mac].handle_command(alias, Command, Level, Color)
            topic = '/'.join([self.base_topic, mac, 'set'])
            self.mqttClient.publish(topic, json.dumps(state))

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        self.mqttClient.onHeartbeat()


global _plugin
_plugin = EwpeSmartOverMqttPlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
