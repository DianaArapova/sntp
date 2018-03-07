import struct
import time
import sys


class SNTPPacket:
    MODE = {'client': 3, 'server': 4}

    def __init__(self, delay=0, stratum=3, version=4, mode=4, originate_time=0, recive_time=0):
        self.delay = delay
        self.leap = 0
        self.version = version
        self.mode = mode
        self.stratum = stratum
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = 0
        self.ref_timestamp = 0
        self.originate_timestamp = originate_time
        self.recive_timestamp = recive_time
        self.transmit_timestamp = 0

    def to_data(self):
        beginning_of_packet = self.num_to_bin(self.leap).rjust(2, '0') \
            + self.num_to_bin(self.version).rjust(3, '0') \
            + self.num_to_bin(self.mode).rjust(3, '0')
        first_byte = int(beginning_of_packet, 2)
        self.ref_timestamp = self.get_time_in_sntp_format(time.time() + self.delay)
        self.transmit_timestamp = time.time() + self.delay

        packet = struct.pack('!4B3L2LQ4L', first_byte,
                             self.stratum, self.poll, self.precision, self.root_delay,
                             self.root_dispersion, self.ref_id, *self.ref_timestamp,
                             self.originate_timestamp,
                             *(self.get_time_in_sntp_format(self.recive_timestamp)
                               + self.get_time_in_sntp_format(self.transmit_timestamp)))
        return packet

    def from_packet_to_data(self, data):
        try:
            unpacked = struct.unpack('!4B3L4Q', data[0:struct.calcsize('!4B3L4Q')])
            self.leap, self.version, self.mode = self.int_to_bin(unpacked[0])
            self.transmit_timestamp = struct.unpack('!Q', data[40:48])[0]
        except BaseException:
            print('Invalid SNTP-packet format', file=sys.stderr)

    @staticmethod
    def num_to_bin(num):
        return bin(num)[2:]

    @staticmethod
    def int_to_bin(num):
        num = bin(num)[2:].rjust(8, '0')
        leap = int(num[:2], 2)
        version = int(num[2:5], 2)
        mode = int(num[5:], 2)
        return leap, version, mode

    @staticmethod
    def get_time_in_sntp_format(time):
        second_in_70_years = 2208988800
        sec, mill_sec = str(time + second_in_70_years).split('.')
        mill_sec = float('0.{}'.format(mill_sec)) * 2 ** 32
        return int(sec), int(mill_sec)
