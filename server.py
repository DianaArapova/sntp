import time
import select
import queue
from packet import SNTPPacket

#Kerberos AD
class serverSNTP:
    def __init__(self, sock, delay=0):
        self.sock = sock
        self.delay = delay
        self.tasks = queue.Queue()

    def make_tasks(self, ready_to_read):
        for client_sntp in ready_to_read:
            packet_sntp, addr = client_sntp.recvfrom(1024)
            print('Connected to address:', addr[0])
            self.tasks.put((packet_sntp, addr, time.time()))

    def listener(self):
        while True:
            ready_to_read, _, _ = select.select([self.sock], [], [], 5)
            print("I listen port 123 in localhost")
            if ready_to_read:
                self.make_tasks(ready_to_read)

    def make_response_packet(self, client_message, recive_time):
        return SNTPPacket(self.delay, stratum=3, version=client_message.version,
                          mode=SNTPPacket.MODE['server'], originate_time=client_message.transmit_timestamp,
                          recive_time=recive_time + self.delay)

    def make_responses_to_client(self):
        while True:
            try:
                print("I make responese to client")
                client_packet, addr, recive_time = self.tasks.get(timeout=1)
                client_message = SNTPPacket()
                client_message.from_packet_to_data(client_packet)
                server_response_packet = self.make_response_packet(client_message, recive_time)
                self.sock.sendto(server_response_packet.to_data(), addr)
            except queue.Empty:
                continue