import requests
import json
import csv
from datetime import datetime
import time
import argparse
import logging

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

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


def write_csv_header(outfd, headers) :
    hlist = sorted(list(headers))

    hstr = ",".join(hlist)
    outfd.write (hstr + "\n")

def write_csv_header(outfd, data, headers) :
    hlist = sorted(list(headers))

    hstr =""
    for (i, h) in enumerate(hlist) :
        if i > 0 :
            hstr += ","
        if h not in data:
            continue
        v = data[h]
        v.replace(",", "_")
        hstr += v
    outfd.write(hstr + "\n")
    

    
def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-M", "--max-distance", type=int, default=100,
                        help="Max distance radius for PO API lookup")
    parser.add_argument("-t", "--time-wait", type=int, default=1,
                        help="Time in seconds to wait between USPS REST requests")
    parser.add_argument("-Z", "--zipcode-field", type=str, default=None,
                        help="If set, interpret input file as a csv and extract this field")
    parser.add_argument("-s", "--state", type=str, default=None,
                        help="If set, filter results to this state")
    
    parser.add_argument("-o", "--output-type", type=str, default="json",
                        help="Data output type: [json, csv]")
    parser.add_argument("inputfile", type=str,
                        help="File with zipcodes ")
    parser.add_argument("outfile", type=str,
                        help="File to write or - for stdout")
    
    args = parser.parse_args()

    if args.outfile != "-" :
        outfd = open(args.outfile, 'w')
    else :
        outfd = sys.stdout

    stats={}
    locations={}
    headers={}
    
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
            log.info("Requesting mailboxes in %s, %s", zipcode, timestamp)
            data = request_location(zipcode, maxdist=args.max_distance)
            if data is not None :
                data["BB_QUERY_TS"]=timestamp
                data["BB_QUERY_ZIP"]=zipcode
                #outfd.write(json.dumps(data) + "\n")
            else :
                time.sleep(args.time_wait)
                continue

            time.sleep(args.time_wait)

            if "locations" not in data :
                continue
            
            (date, time_of_day) = timestamp.split()

            log.info("Merging duplicate hits by 'locationID'")
            for ldata in data["locations"] :
                if "locationID" not in ldata : continue
                lid = ldata["locationID"]
                zip = ldata["zip5"]

                if args.state is not None and ldata["state"] != args.state :
                    continue
                #if zip != zipcode : # query returned results outside zip
                #    continue
                
                del ldata["locationServiceHours"]
                del ldata["radius"]
                del ldata["distance"]
                if zip not in locations :
                    locations[zip]={}
                if date not in locations[zip] :
                    locations[zip][date]={}

                if lid not in locations[zip][date]:
                    locations[zip][date][lid]=ldata
                else :
                    if ldata["address1"] != locations[zip][date][lid]["address1"] :
                        print("Inconsistent addresses for ", lid, ldata["address1"],locations[zip][date][lid]["address1"])

                ldata["BB_QUERY_TS"]=timestamp
                ldata["BB_QUERY_ZIP"]=zipcode
                for h in ldata :
                    headers[h]=1
                    if h == "latitude" or h == "longitude" :
                        ldata[h]=float(ldata[h])
                #
                
            #
        
        # end for row
    # end with
    if args.output_type == "csv" :
        write_csv_header(outfd, headers)
        

    for zip in locations :
        for date in locations[zip] :
            for lid in locations[zip][date] :
                ldata = locations[zip][date][lid]
                if args.output_type == "json" :
                    outfd.write("%s\n" % (json.dumps(ldata)))
                elif args.output_type == "csv" :
                    write_csv(outfd, ldata, headers)
                #
            #
        #
    #
    outfd.close()

            
if __name__=="__main__" :
    main()
    

