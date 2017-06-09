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

# parses the existing xml file into meaningful grantee data
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

