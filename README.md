# BlueBox
Query the USPS PostOffice Locator to track Blue Collection Box locations

## Main Script
The ```scripts/location.py``` connects to the USPS Post Office Locatior REST API and queries for the location of blue collection boxes.  The input is a list of zipcodes, one per line, or a csv file with the zipcode field provided as a paramter.  Output can be either a json or csv file, one collection box info object per line.

```
usage: location.py [-h] [-M MAX_DISTANCE] [-t TIME_WAIT] [-Z ZIPCODE_FIELD]
                   [-o OUTPUT_TYPE]
                   inputfile outfile

positional arguments:
  inputfile             File with zipcodes
  outfile               File to write or - for stdout

optional arguments:
  -h, --help            show this help message and exit
  -M MAX_DISTANCE, --max-distance MAX_DISTANCE
                        Max distance radius for PO API lookup
  -t TIME_WAIT, --time-wait TIME_WAIT
                        Time in seconds to wait between USPS REST requests
  -Z ZIPCODE_FIELD, --zipcode-field ZIPCODE_FIELD
                        If set, interpret input file as a csv and extract this
                        field
  -o OUTPUT_TYPE, --output-type OUTPUT_TYPE
                        Data output type: [json, csv]
```

## Running Nightly
Given a list of zipcodes, the data can be refreshed nightly by adding the bash wrapper script ```scripts/location.py``` to your machine's crontab.

The following assumes you have checked out the repository to /opt/software/BlueBox, so adjust the paths appropriately.

For the Maryland zipcode list included in the resources directory run ```crontab -e ``` and add the following :

```
0 2 * * * /opt/software/BlueBox/scripts/location.sh MD /opt/software/BlueBox/resources/MD_zipcodes.csv ZIPCODE1
```