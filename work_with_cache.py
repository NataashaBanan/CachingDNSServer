import pickle
from datetime import datetime, timedelta


class Packet:
    def __init__(self, rr, create_time):
        self.resource_record = rr
        self.create_time = create_time


def get_response_from_cache(dns_record, database):
    print("get cache answer")
    key = (str(dns_record.q.qname).lower(), dns_record.q.qtype)
    if key in database and database[key]:
        reply = dns_record.reply()
        reply.rr = [p.resource_record for p in database[key]]
        return reply


def check_cache(packet):
    return datetime.now() - packet.create_time >\
           timedelta(seconds=packet.resource_record.ttl)


def clear_old_cash(database):
    cache_delta = 0
    for key, value in database.items():
        old_length = len(value)
        database[key] = \
            set(packet for packet in value if not check_cache(packet))
        cache_delta += old_length - len(database[key])
    if cache_delta > 0:
        print(str(datetime.now()) + " - cleared " +
              str(cache_delta) + " resource records")


def add_records(dns_record, database):
    for r in dns_record.rr + dns_record.auth + dns_record.ar:
        print(r)
        date_time = datetime.now()
        add_record(r, date_time, database)


def add_record(rr, date_time, database):
    k = (str(rr.rname).lower(), rr.rtype)
    if k in database:
        database[k].add(Packet(rr, date_time))
    else:
        database[k] = {Packet(rr, date_time)}


def load_cache():
    try:
        with open('data.pickle', 'rb') as f:
            data = pickle.load(f)
        print('history cache')
    except FileNotFoundError:
        print('cache not exist')
        return {}
    return data


def save_cache(data):
    try:
        with open('data.pickle', 'wb') as f:
            pickle.dump(data, f)
        print('save cache done')
    except FileNotFoundError:
        print('save cache error')
