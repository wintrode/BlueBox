import requests
import json
import csv
from datetime import datetime
import time
import argparse

PO_API='https://tools.usps.com/UspsToolsRestServices/rest/POLocator/findLocations'

def request_location(zip, maxdist=100) :
    req = {
        "lbro": "",
        "maxDistance": str(maxdist),
        "requestRefineHours": "",
        "requestRefineTypes": "",
        "requestServices": "",
        "requestType": "collectionbox",
        "requestZipCode": str(zip), 
        "requestZipPlusFour": "",
    }

    headers = {'user-agent': 'my-app/0.0.1', 'Content-Type': 'application/json;charset=utf-8'}
    r = requests.post(PO_API,
                      headers=headers, data = json.dumps(req))

    if r.status_code == requests.codes.ok :
        resp = json.loads(r.text)
        return resp
    else :
        sys.stderr.write("Error code returned: %d\n" % (r.status_code))
        return None

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-M", "--max-distance", type=int, default=100,
                        help="Max distance radius for PO API lookup")
    parser.add_argument("-Z", "--zipcode-field", type=str, default=None,
                        help="If set, interpret input file as a csv and extract this field")
    parser.add_argument("inputfile", type=str,
                        help="File with zipcodes ")
    parser.add_argument("outfile", type=str,
                        help="File to write or - for stdout")
    
    args = parser.parse_args()

    if args.outfile != "-" :
        outfd = open(args.outfile, 'w')
    else :
        outfd = sys.stdout

    with open(args.inputfile, 'r') as infile :
        if args.zipcode_field :
            reader = csv.DictReader(infile)
        else :
            reader = infile

        for row in reader :
            if args.zipcode_field :
                zipcode = row[args.zipcode_field]
            else :
                zipcode = row.strip()

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            print("Requesting mailboxes in ", zipcode, timestamp)
            data = request_location(zipcode, maxdist=args.max_distance)
            if data is not None :
                data["SCRAPE_REQ_TS"]=timestamp
                data["SCRAPE_REQ_ZIP"]=zipcode
                outfd.write(json.dumps(data) + "\n")
            time.sleep(1)
            
if __name__=="__main__" :
    main()
    

