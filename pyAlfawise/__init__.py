from voluptuous import Schema


class Alfawise:
    """
     TODO :

    """

    POWER = 'comm6'
    OFF = '0'
    ON = '1'

    SPEED = 'comm103'
    LOW = '0'
    MEDIUM = '1'
    HIGH = '2'

    TIMER = 'comm102'
    ONE_HOUR = '1'
    THREE_HOURS = '3'
    SIX_HOURS = '6'

    EFFECT = 'comm104'
    GRADIENT = '2'
    FLASH = '3'
    QUIET = '1'

    COLOR = 'comm101'

    OPTION_POWER = 'sa_ctrl'
    OPTION_SPEED = 'h_rank'
    OPTION_TIMER = 'countdown'
    OPTION_EFFECT = 'l_mode'
    OPTION_COLOR = 'l_color'

    def __init__(self, mac, ip='255.255.255.255'):
        self.ip = ip
        self.mac = mac
        self.property = dict.fromkeys([self.OPTION_POWER, self.OPTION_COLOR,
                                       self.OPTION_EFFECT, self.OPTION_TIMER,
                                       self.OPTION_SPEED])
        self.refresh_property()

    def is_on(self):
        return self.property[self.OPTION_POWER] == self.ON

    def is_off(self):
        return self.property[self.OPTION_POWER] == self.OFF

    def get_property(self, property_name):
        try:
            return self.property[property_name]
        except KeyError:
            print("This property '{}' is not available".format(property_name))
            return None

    def get_all_properties(self):
        return self.property

    def refresh_property(self):
        return

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
        self._send_command(self.COLOR, self.OPTION_COLOR, hexvalue)
        # Update property
        self.property[self.OPTION_COLOR] = hexvalue

    def turn_on(self):
        """
            This method is used to switch on the device
        """
        # Check state
        if 1:
            # Send command
            self._send_command(self.POWER, self.OPTION_POWER, self.ON)
            # Update property
            self.property[self.OPTION_POWER] = self.ON

    def turn_off(self):
        """
            This method is used to switch off the device
        """
        # Check state
        if 1:
            # Send command
            self._send_command(self.POWER, self.OPTION_POWER, self.OFF)
            # Update property
            self.property[self.OPTION_POWER] = self.OFF

    def toggle(self):
        """
            This method is used to toggle the device
        """
        # Update property
        if self.is_on():
            self.turn_off()
        elif self.is_off():
            self.turn_on()

    def _send_command(self, command_type, command_name, command_value):
        bufferSize = 1024
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        command = bytes('{"command":"' + command_type + '", "' + command_name + '":"' + command_value + '","deviceid":"' + self.mac + '","modelid":"sj07","phoneid":"020000000000","userid":""}',
                        'UTF-8')
        sock.sendto(command, (self.ip, 10002))
        sock.close()
