#!/usr/bin/env python3

import sqlite3
import xml.etree.ElementTree as ET
import requests

def fetch_grantees():
    r = requests.get('https://fcc.io/grantees')
    print(dir(r))
    print(r.headers['content-type'])
    print(r.encoding)
    # print(r.text)

attributes = [
    'grantee_code',
    'grantee_name',
    'mailing_address',
    'po_box',
    'city',
    'state',
    'country',
    'zip_code',
    'contact_name',
    'date_received',
]

def parse_grantees():
    global attributes
    rows = []
    tree = ET.parse('grantees.xml')
    root = tree.getroot()
    for row in root.iter('Row'):
        rows.append(dict())
        for attribute in attributes:
            x = row.find(attribute)
            if hasattr(x, 'text'):
                rows[-1][attribute] = x.text
    print("Found %d grantees" % len(rows))

def write_db():
    conn = sqlite3.connect('/tmp/example')
    c = conn.cursor()

    c.execute("""drop table if exists grantees""")

    conn.commit()

    c.execute("""create table towns (
            tid int primary key not NULL ,
            name text,
            postcode text)""")

    c.execute("""create table hotels (
            hid int primary key not NULL ,
            tid int,
            name text,
            address text,
            rooms int,
            rate float)""")

    c.execute("""insert into towns values (1, "Melksham", "SN12")""")
    c.execute("""insert into towns values (2, "Cambridge", "CB1")""")
    c.execute("""insert into towns values (3, "Foxkilo", "CB22")""")

    c.execute("""insert into hotels values (1, 2, "Hamilkilo Hotel", "Chesterton Road", 15, 40.)""")
    c.execute("""insert into hotels values (2, 2, "Arun Dell", "Chesterton Road", 60, 70.)""")
    c.execute("""insert into hotels values (3, 2, "Crown Plaza", "Downing Street", 100, 105.)""")
    c.execute("""insert into hotels values (4, 1, "Well House Manor", "Spa Road", 5, 80.)""")
    c.execute("""insert into hotels values (5, 1, "Beechfield House", "The Main Road", 26, 110.)""")

    conn.commit()

    c.execute ("""select * from towns left join hotels on towns.tid = hotels.tid""")

    for row in c:
        print (row)

    c.close()

if __name__ == "__main__":
    parse_grantees()
