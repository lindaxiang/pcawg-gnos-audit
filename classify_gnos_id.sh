#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR

M=$1

rm -rf repos

for r in bsc dkfz ebi osdc-icgc osdc-tcga riken
do
 	mkdir -p repos/$r
 	less $M/analysis_objects.$r.tsv |grep live | awk '{print $1}' | sort -u > repos/$r/$r.live.gnos_id.txt
 	less $M/analysis_objects.$r.tsv |grep -v live | awk '{print $1}' |sort -u > repos/$r/$r.not_live.gnos_id.txt
done


for r in bsc dkfz ebi osdc-icgc osdc-tcga riken
do
  cp repos/$r/$r.live.gnos_id.txt repos/$r/$r.live.not_index.gnos_id.txt
  echo -n "" > repos/$r/$r.live.index.gnos_id.txt	
  for t in wgs_aligned_bam wgs_bam_with_unmappable_reads broad_tar_variant_calling broad_variant_calling dkfz_embl_variant_calling wgs_minibam muse_variant_calling oxog_variant_calling rna_seq_aligned sanger_variant_calling wgs_unaligned_bams consensus_call
  do	
	comm -1 -2 <(sort repos/$r/$r.live.gnos_id.txt | uniq) <(sort indexed_gnos_id/$t.gnos_id.txt | uniq) | sort -u > repos/$r/$r.live.$t.gnos_id.txt
	comm -1 -2 <(sort repos/$r/$r.live.$t.gnos_id.txt | uniq) <(sort gnos_id_on_portal.txt | uniq) | sort -u > repos/$r/$r.live.$t.portal.gnos_id.txt
	comm -2 -3 <(sort repos/$r/$r.live.$t.gnos_id.txt | uniq) <(sort gnos_id_on_portal.txt | uniq) | sort -u > repos/$r/$r.live.$t.not_portal.gnos_id.txt
	comm -2 -3 <(sort repos/$r/$r.live.not_index.gnos_id.txt | uniq) <(sort indexed_gnos_id/$t.gnos_id.txt | uniq) | sort -u > repos/$r/$r.live.not_index.gnos_id.bk.txt
	mv repos/$r/$r.live.not_index.gnos_id.bk.txt repos/$r/$r.live.not_index.gnos_id.txt
	less repos/$r/$r.live.$t.gnos_id.txt >> repos/$r/$r.live.index.gnos_id.txt
  done
done

