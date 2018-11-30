import Domoticz
import json
import math

class Device():
    def __init__(self, domoticz_devices, mqtt_base_topic, device):
        self.devices = domoticz_devices
        self.topic = mqtt_base_topic + '/' + device['mac']
        self._register(device)

    def get_first_available_unit(self):
        for i in range(1, 255):
            if i not in self.devices:
                return i

    def get_device(self, address, alias):
        device_id = address + '_' + alias

        for unit, device in self.devices.items():
            if device.DeviceID == device_id:
                return device

    def _register(self, device):
        address = device['mac']
        name = device['name'].strip()

        if self.get_device(address, 'switch') == None:
            device_id = address + '_switch'
            Domoticz.Debug('Creating domoticz device to handle on/off state')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Switch', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'turbo') == None:
            device_id = address + '_turbo'
            Domoticz.Debug('Creating domoticz device to handle Turbo mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Turbo Mode', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'quiet') == None:
            device_id = address + '_quiet'
            Domoticz.Debug('Creating domoticz device to handle Quiet mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Quiet Mode', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'sleep') == None:
            device_id = address + '_sleep'
            Domoticz.Debug('Creating domoticz device to handle Sleep mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Sleep Mode', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'health') == None:
            device_id = address + '_health'
            Domoticz.Debug('Creating domoticz device to handle Health (Cold plasma) mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Cold Plasma', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'economy') == None:
            device_id = address + '_economy'
            Domoticz.Debug('Creating domoticz device to handle Energy saving mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Energy Saving', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'display') == None:
            device_id = address + '_display'
            Domoticz.Debug('Creating domoticz device to handle visibility of display indicators')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Display', TypeName="Switch", Image=9).Create()

        if self.get_device(address, 'temp') == None:
            device_id = address + '_temp'
            Domoticz.Debug('Creating domoticz device to handle temperature')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Temperature', Type=242, Subtype=1).Create()

        if self.get_device(address, 'mode') == None:
            device_id = address + '_mode'
            options = {}
            options['LevelActions'] = ''
            options['LevelNames'] = '|'.join(['Auto', 'Cool', 'Dry', 'Fan', 'Heat'])
            options['SelectorStyle'] = '0'
            Domoticz.Debug('Creating domoticz device to handle device mode')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Mode', TypeName="Selector Switch", Options=options, Image=15).Create()

        if self.get_device(address, 'blades') == None:
            device_id = address + '_blades'
            options = {}
            options['LevelActions'] = ''
            options['LevelNames'] = '|'.join([
                'Default', 
                'Swing in full range', 
                'Fixed in the upmost position (1/5)', 
                'Fixed in the middle-up position (2/5)', 
                'Fixed in the middle position (3/5)', 
                'Fixed in the middle-low position (4/5)',
                'Fixed in the lowest position (5/5)',
                'Swing in the downmost region (5/5)',
                'Swing in the middle-low region (4/5)',
                'Swing in the middle region (3/5)',
                'Swing in the middle-up region (2/5)',
                'Swing in the upmost region (1/5)'
            ])
            options['SelectorStyle'] = '1'
            Domoticz.Debug('Creating domoticz device to handle blades position')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Blades', TypeName="Selector Switch", Options=options, Image=9).Create()

        if self.get_device(address, 'fan') == None:
            device_id = address + '_fan'
            options = {}
            options['LevelActions'] = ''
            options['LevelNames'] = '|'.join(['Auto', 'Low', 'Medium-low', 'Medium', 'Medium-high', 'High'])
            options['SelectorStyle'] = '1'
            Domoticz.Debug('Creating domoticz device to handle device fan speed')
            Domoticz.Device(Unit=self.get_first_available_unit(), DeviceID=device_id, Name=name + ' - Fan Speed', TypeName="Selector Switch", Options=options, Image=7).Create()

        self.device = device

    def _update_state(self, state):
        address = self.device['mac']
        Domoticz.Debug(json.dumps(state))

        if "Pow" in state:
            power_device = self.get_device(address, 'switch')
            mode_device = self.get_device(address, 'mode')
            fan_device = self.get_device(address, 'fan')
            blades_device = self.get_device(address, 'blades')

            power_device.Update(nValue=int(state['Pow']), sValue=str(state['Pow']))
            mode_device.Update(nValue=power_device.nValue, sValue=mode_device.sValue)
            fan_device.Update(nValue=power_device.nValue, sValue=fan_device.sValue)
            blades_device.Update(nValue=power_device.nValue, sValue=blades_device.sValue)

        if "Tur" in state:
            self.get_device(address, 'turbo').Update(nValue=int(state['Tur']), sValue=str(state['Tur']))

        if "Quiet" in state:
            self.get_device(address, 'quiet').Update(nValue=int(state['Quiet']), sValue=str(state['Quiet']))

        if "Health" in state:
            self.get_device(address, 'health').Update(nValue=int(state['Health']), sValue=str(state['Health']))

        if "SwhSlp" in state:
            self.get_device(address, 'sleep').Update(nValue=int(state['SwhSlp']), sValue=str(state['SwhSlp']))

        if "Lig" in state:
            self.get_device(address, 'display').Update(nValue=int(state['Lig']), sValue=str(state['Lig']))

        if "SvSt" in state:
            self.get_device(address, 'economy').Update(nValue=int(state['SvSt']), sValue=str(state['SvSt']))

        if "SetTem" in state and "TemRec" in state:
            temperature = state['SetTem'] + (0.5 if state['TemRec'] == 1 else 0)
            self.get_device(address, 'temp').Update(nValue=0, sValue=str(temperature))

        if "Mod" in state:
            n_value = self.get_device(address, 'switch').nValue
            s_value = str(state["Mod"] * 10)
            self.get_device(address, 'mode').Update(nValue=n_value, sValue=s_value)

        if "WdSpd" in state:
            n_value = self.get_device(address, 'switch').nValue
            s_value = str(state["WdSpd"] * 10)
            self.get_device(address, 'fan').Update(nValue=n_value, sValue=s_value)

        if "SwUpDn" in state:
            n_value = self.get_device(address, 'switch').nValue
            s_value = str(state["SwUpDn"] * 10)
            self.get_device(address, 'blades').Update(nValue=n_value, sValue=s_value)

    def handle_message(self, topic, message):
        if topic == self.topic + '/status':
            self._update_state(message)

    def handle_command(self, alias, command, level, color):
        cmd = command.upper()
        commands = {}

        Domoticz.Debug('Command "' + command + ' (' + str(level) + ')" from device "' + self.device['name'] + '" alias: ' + alias)

        if alias == 'switch' and (cmd == 'ON' or cmd == 'OFF'):
            commands['Pow'] = 1 if cmd == 'ON' else 0

        if alias == 'turbo' and (cmd == 'ON' or cmd == 'OFF'):
            commands['Tur'] = 1 if cmd == 'ON' else 0

        if alias == 'quiet' and (cmd == 'ON' or cmd == 'OFF'):
            commands['Quiet'] = 1 if cmd == 'ON' else 0

        if alias == 'health' and (cmd == 'ON' or cmd == 'OFF'):
            commands['Health'] = 1 if cmd == 'ON' else 0

        if alias == 'sleep' and (cmd == 'ON' or cmd == 'OFF'):
            commands['SwhSlp'] = 1 if cmd == 'ON' else 0

        if alias == 'economy' and (cmd == 'ON' or cmd == 'OFF'):
            commands['SvSt'] = 1 if cmd == 'ON' else 0

        if alias == 'display' and (cmd == 'ON' or cmd == 'OFF'):
            commands['Lig'] = 1 if cmd == 'ON' else 0

        if alias == 'temp' and cmd == 'SET LEVEL':
            commands['TemUn'] = 0
            commands['SetTem'] = math.floor(level)
            commands['TemRec'] = 1 if (level - math.floor(level)) > 0 else 0

        if alias == 'mode':
            commands['Mod'] = level / 10

        if alias == 'fan':
            commands['WdSpd'] = level / 10

        if alias == 'blades':
            commands['SwUpDn'] = level / 10

        return commands

        