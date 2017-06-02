#!/usr/bin/env python3

import sqlite3
import xml.etree.ElementTree as ET
import requests

def fetch_grantees():
    r = requests.get('https://fcc.io/grantees')
    print(dir(r))
    print(r.headers['content-type'])
    print(r.encoding)

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
        grantee = []
        for attribute in attributes:
            x = row.find(attribute)
            if hasattr(x, 'text'):
                grantee.append(x.text)
        rows.append(grantee)
    print("Found %d grantees" % len(rows))
    return rows

def write_db(granteeTest):
    conn = sqlite3.connect('FCCgrantees.db')
    c = conn.cursor()

    c.execute("""drop table if exists grantees""")
    conn.commit()

    c.execute('''CREATE TABLE grantees
                (grantee_code int primary key not NULL,  
                grantee_name text,
                mailing_address text,
                po_box text,
                city text,
                state text,
                country text,
                zip_code text,
                contact_name text,
                date_received text)''')

    c.executemany('INSERT INTO grantees VALUES (?,?,?,?,?,?,?,?,?,?)', granteeTest)
    conn.commit()

    for row in c:
        print(row)

    c.close()
    print("Table Created")


if __name__ == "__main__":
    grantees = parse_grantees()
    write_db(grantees)
    