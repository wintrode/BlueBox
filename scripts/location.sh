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

if [[ ! -z $field ]]; then
    field="-Z ZIPCODE1"
else
    field=""
fi

# store data by state by month
DATE=`date +'%Y%m%d'`
MONTH=`date +'%Y-%m'`
outfile=$BB_DIR/USPS_DATA/$state/$MONTH/$DATE.$BB_OUT_TYPE
outdir=`dirname $outfile`
mkdir -p $outdir

logdir=$BB_DIR/logs/$state/$MONTH
mkdir -p $logdir

bindir=`dirname "$(readlink -f "$0")"`

python3 $bindir/location.py $field -s $state -o $BB_OUT_TYPE $ziplist $outfile &> $logdir/$DATE.log

echo "Completed query for $DATE" >> $logdir/$DATE.log

# to run daily at 2am, add the following to your /etc/crontab
# 0 2 * * * /opt/software/BlueBox/scripts/location.sh MD /opt/software/BlueBox/resources/MD_zipcodes.csv ZIPCODE1
