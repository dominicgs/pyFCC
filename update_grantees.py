#!/usr/bin/env python3

from pyFCC.grantees import fetch_grantees_xml, parse_grantees#, write_db
from pyFCC.fccDB import create_grantee_table, populate_grantees
import argparse

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--remote", help="Download grantee data from FCC website", action="store_true")
    parser.add_argument("-l", "--local", help="Create grantee database from local file", action="store_true")
    args = parser.parse_args()
    if args.remote:
        print("Downloading grantee data...")
        fetch_grantees_xml()
    try:
        grantees = parse_grantees()
    except FileNotFoundError:
        print("No local xml file found.")
        print("Use '--help' for help")
        print("Downloading grantee data...")
        fetch_grantees_xml()
        grantees = parse_grantees()

    create_grantee_table()
    populate_grantees(grantees)
    
