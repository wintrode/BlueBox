#!/bin/bash

if [[ -z $BB_OUT_TYPE ]] ; then
    BB_OUT_TYPE=json
fi

if [[ -z $BB_DIR ]] ; then
    BB_DIR=/opt/BlueBox
fi

state=$1
ziplist=$2
field=$3

if [[ -z $field ]]; then
    field=ZIPCODE1
fi

# store data by state by month
DATE=`date +'%Y%m%d'`
MONTH=`date +'%Y-%m'`
outfile=$BB_DIR/USPS_DATA/$state/$MONTH/$DATE.$BB_OUT_TYPE
outdir=`dirname $outfile`
mkdir -p $outdir

bindir=`dirname "$(readlink -f "$0")"`

python3 $bindir/location.py -Z $field -o $BB_OUT_TYPE $ziplist $outfile
