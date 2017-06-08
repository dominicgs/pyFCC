import sqlite3
import xml.etree.ElementTree as ET
import requests
import argparse

# saves all grantees from url to an xml file
def fetch_grantees_xml():
    r = requests.get('https://apps.fcc.gov/eas/GetEntityDownload.xml?type=G')
    with open('grantees.xml', 'w') as f:
        f.write(r.text)

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

    c.execute("""DROP TABLE IF EXISTS grantees""")
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

    #for row in c:
    #   print(row)

    c.close()
    print("Table Created in FCCgrantees.db")


if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--remote", help="Download grantee data from FCC website", action="store_true")
    parser.add_argument("-l", "--local", help="Create grantee database from local file", action="store_true")
    args = parser.parse_args()
    #if argv[1] == '-r':
    if args.remote:
        print("Downloading grantee data...")
        fetch_grantees_xml()
    if args.local:
        try:
            grantees = parse_grantees()
        except FileNotFoundError:
            print("No local xml file found.")
            print("Use argument --help for help")
            print("Downloading...")
            fetch_grantees_xml()
            grantees = parse_grantees()
    write_db(grantees)
    
