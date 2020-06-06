import socket
from dnslib import DNSError, DNSRecord

from work_with_cache import *


SERVER = "ns1.e1.ru"


def send_response(response, addr):
    sock.connect(addr)
    sock.sendall(response)
    sock.close()


def work_loop():
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 53))
    # привязали сокет к порту

    try:
        while True:
            data, addr = sock.recvfrom(2048)

            if database:
                clear_old_cash(database)

            try:
                dns_record = DNSRecord.parse(data)
                # print(dns_record)
            except DNSError:
                print('error parse')
                continue

            add_records(dns_record, database)
            if not dns_record.header.qr:
                response = get_response_from_cache(dns_record, database)
                try:
                    if response:
                        print(response)
                        send_response(response.pack(), addr)
                        if database:
                            save_cache(database)
                    else:
                        resp = dns_record.send(SERVER)
                        add_records(DNSRecord.parse(resp), database)
                        send_response(resp, addr)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind(("", 53))
                    if database:
                        save_cache(database)
                except (OSError, DNSError):
                    print("can not ask server " + SERVER +
                          " time: " + str(datetime.now()))
    except:
        print('server error')


print('server started')

global database

database = load_cache()

try:
    work_loop()
finally:
    if database:
        save_cache(database)
    print('server stop')
