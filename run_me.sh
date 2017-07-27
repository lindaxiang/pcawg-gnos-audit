#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR

INDEX_WORK_DIR=$(grep 'index_work_dir:' settings.yml); INDEX_WORK_DIR=${INDEX_WORK_DIR//*index_work_dir: /};
METADATA_DIR=$(grep 'metadata_dir:' settings.yml); METADATA_DIR=${METADATA_DIR//*metadata_dir: /};

echo 
echo ----find the latest folder with metadata----
M=`find "$INDEX_WORK_DIR"/"$METADATA_DIR" -maxdepth 1 -type d -regex '.*/20[0-9][0-9]-[0-9][0-9].*[0-9][0-9]_[A-Z][A-Z][A-Z]' | sort | tail -1`
echo
echo $M

echo
echo ----get portal gnos_id and indexed gnos_id----
./get_index_gnos_id.sh $M

echo
echo ----classify the gnos_ids into different catagory----
./classify_gnos_id.sh $M

echo
echo ----parse the metadata xml for those which did not get indexed by pcawg metadata----
./get_not_index_gnos_info.py

echo
echo ----generate the overall report for each repo----
./report.sh

