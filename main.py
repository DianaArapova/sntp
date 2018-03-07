import socket
import threading
import sys
import argparse
from server import serverSNTP


def main(delay, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
        sock.settimeout(3)
    except BaseException:
        print("!!!Error", file=sys.stderr)
        sys.exit(-1)

    sntp = serverSNTP(sock, delay)

    try:
        t1 = threading.Thread(target=sntp.listener)
        t1.start()
        t2 = threading.Thread(target=sntp.make_responses_to_client)
        t2.start()
    except BaseException:
        print("!!!Error", file=sys.stderr)
        sock.close()
        sys.exit(-1)

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', help='delay to time in server', default=0)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    args = parse_argument()
    main(int(args['delay']), port=123)