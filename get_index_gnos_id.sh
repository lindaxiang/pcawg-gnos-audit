#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR

M=$1

MAX_NUM3=705

## get the latest gnos_ids visible on dcc portal
#touch gnos_id_on_portal.txt
#echo "get all the PCAWG data file gnos_ids which are visible on DCC portal"
#for i in $(eval echo "{0..$MAX_NUM3}")
#do 
#     curl -XGET "https://dcc.icgc.org/api/v1/repository/files?filters=%7B%22file%22:%7B%22study%22:%7B%22is%22:%5B%22PCAWG%22%5D%7D%7D%7D&size=100&from=$(($i * 100 + 1))" | jq -r '.hits[].fileCopies[] | .repoDataBundleId'| sort -u | grep -v null | grep -v EGAZ  >> gnos_id_on_portal.txt
#done
#
#less gnos_id_on_portal.txt |sort -u > gnos_id_on_portal.sort.txt
#mv gnos_id_on_portal.sort.txt gnos_id_on_portal.txt

rm -rf indexed_gnos_id
mkdir indexed_gnos_id

# parse the donor.*.jsonl to get the gnos_ids which are indexed
# wgs 
for f in minibam bam_with_unmappable_reads aligned_bam
do
    zless $M/donor_p_*.jsonl.gz |jq --arg i $f  -r '.normal_alignment_status[$i].gnos_id' | sort -u |grep -v null > indexed_gnos_id/wgs_$f.gnos_id.txt
    zless $M/donor_p_*.jsonl.gz |jq --arg i $f  -r '.tumor_alignment_status[][$i].gnos_id' | sort -u |grep -v null >> indexed_gnos_id/wgs_$f.gnos_id.txt
done
zless $M/donor_p_*.jsonl.gz |jq -r '.normal_alignment_status.unaligned_bams[]?.gnos_id' | sort -u |grep -v null > indexed_gnos_id/wgs_unaligned_bams.gnos_id.txt
zless $M/donor_p_*.jsonl.gz |jq -r '.tumor_alignment_status[].unaligned_bams[]?.gnos_id' | sort -u|grep -v null >> indexed_gnos_id/wgs_unaligned_bams.gnos_id.txt    

# rna-seq
zless $M/donor_p_*.jsonl.gz |jq -r '.rna_seq.alignment | (.tumor[]? | .tophat.aligned_bam.gnos_id), (.tumor[]? | .star.aligned_bam.gnos_id), (.normal.tophat.aligned_bam.gnos_id), (.normal.star.aligned_bam.gnos_id) ' | sort -u|grep -v null > indexed_gnos_id/rna_seq_aligned.gnos_id.txt 

# variant call
for f in sanger_variant_calling dkfz_embl_variant_calling broad_variant_calling muse_variant_calling broad_tar_variant_calling oxog_variant_calling
do 
    zless $M/donor_p_*.jsonl.gz |jq --arg i $f -r '.variant_calling_results[$i].gnos_id'| sort -u| grep -v null > indexed_gnos_id/$f.gnos_id.txt
done

# concensus call
zless $M/donor_p_*.jsonl.gz |jq -r '.consensus_somatic_variant_calls | (.snv_mnv[]?.gnos_id), (.indel[]?.gnos_id)' | sort -u|grep -v null > indexed_gnos_id/consensus_call.gnos_id.txt




