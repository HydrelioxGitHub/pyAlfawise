from voluptuous import Schema
import socket
import json
import logging
import netaddr


class AlfawiseError(Exception):
    def __init__(self, arg):
        Exception.__init__(self, "Alfawaise device can't be reached using this ip :" + str(arg))


class Alfawise:
    """
     TODO : Find some method to read properties from the device

    """

    COMMAND_POWER = 'comm6'
    POWER_OFF = '0'
    POWER_ON = '1'

    COMMAND_SPEED = 'comm103'
    OFF = '0'
    LOW = '1'
    HIGH = '2'

    COMMAND_TIMER = 'comm102'
    ONE_HOUR = '1'
    THREE_HOURS = '3'
    SIX_HOURS = '6'

    COMMAND_EFFECT = 'comm104'
    GRADIENT = '2'
    FLASH = '3'
    QUIET = '1'

    COMMAND_COLOR = 'comm101'

    OPTION_POWER = 'sa_ctrl'
    OPTION_SPEED = 'h_rank'
    OPTION_TIMER = 'countdown'
    OPTION_EFFECT = 'l_mode'
    OPTION_COLOR = 'l_color'
    OPTION_BRIGHTNESS = 'leave'

    def __init__(self, mac, ip='255.255.255.255'):
        self.ip = netaddr.IPAddress(ip)
        self.mac = netaddr.EUI(mac)
        self.port = 10002
        self.saved_color = "FFFFFF"
        self.property = dict.fromkeys([self.OPTION_POWER, self.OPTION_COLOR,
                                       self.OPTION_EFFECT, self.OPTION_TIMER,
                                       self.OPTION_SPEED])
        self._formatted_mac = self._format_mac(mac)
        self._update()

    def is_fan_on(self):
        return self.property[self.OPTION_SPEED] != self.OFF

    def is_fan_off(self):
        return self.property[self.OPTION_SPEED] == self.OFF

    def is_light_on(self):
        return self.property[self.OPTION_COLOR] != '000000'

    def is_light_off(self):
        return self.property[self.OPTION_COLOR] == '000000'

    def is_on(self):
        return self.property[self.OPTION_POWER] == self.POWER_ON

    def is_off(self):
        return self.property[self.OPTION_POWER] == self.POWER_OFF

    def get_property(self, property_name):
        try:
            return self.property[property_name]
        except KeyError:
            print("This property '{}' is not available".format(property_name))
            return None

    def get_all_properties(self):
        return self.property

    def set_rgb_color(self, hexvalue):
        """
            Set the color of the device using hex code.

            :param haxvalue: Color value in hexadecimal code

            :type hexvalue: str
        """
        # Input validation
        schema = Schema({'hexvalue': str})
        schema({'hexvalue': hexvalue})
        # Send command
        self._send_command(self.COMMAND_COLOR, self.OPTION_COLOR, hexvalue)
        # Update property
        self.saved_color = hexvalue
        self.property[self.OPTION_COLOR] = hexvalue

    def turn_on(self):
        """
        This method is used to switch on the device
        BUG : when you turn off and on the device, it starts with default
        color and fan speed. The data read from the device still the same so there no match between real state and
        data provided.
        """
        # Check state
        if self.is_off():
            # Send command
            self._send_command(self.COMMAND_POWER, self.OPTION_POWER, self.POWER_ON)
            self.property[self.OPTION_POWER] = self.POWER_ON

    def turn_off(self):
        """
            This method is used to switch off the device
        """
        # Check state
        if self.is_on():
            # Send command
            self._send_command(self.COMMAND_POWER, self.OPTION_POWER, self.POWER_OFF)
            self.property[self.OPTION_POWER] = self.POWER_OFF

    def toggle(self):
        """
            This method is used to toggle the device
        """
        # Update property
        if self.is_on():
            self.turn_off()
        elif self.is_off():
            self.turn_on()

    def turn_fan_on(self, speed=None):
        """
            This method is used to switch on the fan (mist)
        """
        # if no speed is provided, low speed will be send
        if speed is None:
            self.property[self.OPTION_SPEED] = self.LOW
        else:
            self.property[self.OPTION_SPEED] = speed
        # Send command
        self._send_command(self.COMMAND_SPEED, self.OPTION_SPEED, self.property[self.OPTION_SPEED])

    def turn_fan_off(self):
        """
            This method is used to switch off the fan (mist)
        """
        # Send command
        self._send_command(self.COMMAND_SPEED, self.OPTION_SPEED, self.OFF)
        self.property[self.OPTION_SPEED] = self.OFF

    def toggle_fan(self):
        """
            This method is used to toggle the fan (mist)
        """
        # Update property
        if self.is_fan_on():
            self.turn_fan_off()
        elif self.is_off():
            self.turn_fan_on()

    def turn_light_on(self, color=None):
        """
            This method is used to switch on the light
        """
        # if no speed is provided, the last saved color will be send
        if (color is None):
            self.property[self.OPTION_COLOR] = self.saved_color
        else:
            self.property[self.OPTION_COLOR] = color
        # Send command
        self._send_command(self.COMMAND_COLOR, self.OPTION_COLOR, self.property[self.OPTION_COLOR])

    def turn_light_off(self):
        """
            This method is used to switch off the light
        """
        # Send command
        self._send_command(self.COMMAND_COLOR, self.OPTION_COLOR, "000000")
        self.property[self.OPTION_COLOR] = "000000"

    def toggle_light(self):
        """
            This method is used to toggle the light
        """
        if self.is_light_on():
            self.turn_light_off()
        elif self.is_light_off():
            self.turn_light_on()

    def read(self):
        buffer_size = 1024
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)

        command = bytes(
            '{"command":"comm100","password":"1234","deviceid":"' + self._formatted_mac + '","modelid":"SJA-07-01S",'
                            '"phoneid":"020000000000","userid":""}',
            'UTF-8')
        sock.sendto(command, (str(self.ip), 10002))
        try:
            received_bytes, peer = sock.recvfrom(buffer_size)
            logging.debug("Read : %s from %s:%u" % (received_bytes.decode('utf8'), peer[0], peer[1]))
            sock.close()
        except socket.timeout:
            return None
        return json.loads(received_bytes.decode('utf8'))

    def _send_command(self, command_type, command_name, command_value):
        buffer_size = 1024
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)
        command = bytes(
            '{"command":"' + command_type + '", "' + command_name + '":"' + command_value + '","deviceid":"' + self._formatted_mac + '","modelid":"SJA-07-01S","phoneid":"020000000000","userid":""}',
            'UTF-8')
        logging.debug("Sent : %s" % command)
        sock.sendto(command, (str(self.ip), 10002))
        try:
            received_bytes, peer = sock.recvfrom(buffer_size)
            logging.debug("Response : %s from %s:%u" % (received_bytes.decode('utf8'), peer[0], peer[1]))
            sock.close()
        except socket.timeout:
            raise AlfawiseError(self.ip)

    def _update(self, already_polled=False):
        """
            Update properties from reading the device and parsing response
        """
        if already_polled is not False:
            data = already_polled
        else:
            data = self.read()

        if data is None:
            raise AlfawiseError(self.ip)

        for key in self.property:
            self.property[key] = (data[key])

    def _format_mac(self, mac_address):
        converted_mac = str(mac_address).replace("-", "")
        logging.debug("Converted mac : %s" % (converted_mac))
        return converted_mac
