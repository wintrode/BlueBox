import json
from datetime import datetime
import time
import argparse
import sys

# merge the results downloaded by location.py to
# remove duplicates 

def main() :
    parser = argparse.ArgumentParser()
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
    
    with open(args.inputfile, 'r') as infile :
        for row in infile :
            data = json.loads(row.strip())
            #print(json.dumps(data, indent=2))
            if "locations" not in data :
                continue
            timestamp = data["SCRAPE_REQ_TS"]
            (date, time) = timestamp.split()
            
            for ldata in data["locations"] :
                if "locationID" not in ldata : continue
                lid = ldata["locationID"]
                zip = ldata["zip5"]
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
            #
        #

    for zip in locations :
        for date in locations[zip] :
            for lid in locations[zip][date] :
                ldata = locations[zip][date][lid]
                outfd.write("%s,%s,%s,%s\n" % (date, zip, lid, json.dumps(ldata)))
    outfd.close()
                                        
if __name__=="__main__" :
    main()
