#!/usr/bin/env python3

from pyFCC.grantees import fetch_grantees_xml, parse_grantees, write_db
import argparse

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
    
