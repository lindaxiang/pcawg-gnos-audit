#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR

NOTE=old_versions\/virtually_suppressed_gnos_entries\/blacklisted_aliquots\/non-pcawg_donors

for r in bsc dkfz ebi osdc-icgc osdc-tcga riken
do
        if [ "$r" = "ebi" ]; then
	        echo -n "Study=PCAWG2.0 are not covered in this auditing" > repos/$r.report.txt
                printf "\n" >> repos/$r.report.txt
        else
	        echo -n "" > repos/$r.report.txt
	fi
        for t in not_live live
	do
		if [ -f repos/$r/$r.$t.gnos_id.txt ]; then
		  num=`less repos/$r/$r.$t.gnos_id.txt|wc -l`
		  printf "%s\t%10s\n" $t $num >> repos/$r.report.txt
		fi

		if [ -f repos/$r/$r.$t.not_index.gnos_id.txt ]; then
		num=`less repos/$r/$r.$t.not_index.gnos_id.txt|wc -l`
		printf "\t\t%s\t%10s\n" excluded_from_pcawg_metadata $num >> repos/$r.report.txt
		fi
		# not_indexed files
		for d in wgs_aligned_bam wgs_unmapped_bam wgs_unaligned_bam variant_call oxog wgs_minibam consensus_call rna_seq_aligned rna_seq_unaligned wgs_unknown_workflow_name wgs_unknown_variant_caller rna_seq_unknown_workflow others
		do
                  NOTE=old_versions\/virtually_suppressed_gnos_entries\/blacklisted_aliquots\/non-pcawg_donors
                  if [ "$d" = "others" ]; then
                      NOTE=Germline_calls\/invalid_library_strategy\/invalid_dcc_project_code\/invalid_study 
                  fi
                  if [[ "$d" == *"unknown"* ]]; then
                      NOTE=""
                  fi
		  if [ -f repos/$r/$r.$t.not_index.$d.txt ]; then
			num=`less repos/$r/$r.$t.not_index.$d.txt|grep -v data_type|wc -l`
			printf "\t\t\t\t%s\t%10s\t\t%s\n" $d $num $NOTE >> repos/$r.report.txt
		  fi
		done
		
		if [ -f repos/$r/$r.$t.index.gnos_id.txt ]; then
		num=`less repos/$r/$r.$t.index.gnos_id.txt|wc -l`
		printf "\t\t%s\t%10s\n" indexed_by_pcawg_metadata $num >> repos/$r.report.txt
		fi

		# indexed files
		for d in wgs_aligned_bam wgs_bam_with_unmappable_reads wgs_unaligned_bams sanger_variant_calling broad_tar_variant_calling broad_variant_calling dkfz_embl_variant_calling muse_variant_calling oxog_variant_calling wgs_minibam consensus_call rna_seq_aligned 
		do
		  if [ -f repos/$r/$r.$t.index.$d.gnos_id.txt ]; then
			num=`less repos/$r/$r.$t.index.$d.gnos_id.txt|wc -l`
			printf "\t\t\t\t%s\t%10s\n" $d $num >> repos/$r.report.txt
		  fi
		  for p in not_portal portal
		    do
		      if [ -f repos/$r/$r.$t.index.$d.$p.gnos_id.txt ]; then
			    num=`less repos/$r/$r.$t.index.$d.$p.gnos_id.txt|wc -l`
			    printf "\t\t\t\t\t\t%s\t%10s\n" $p $num >> repos/$r.report.txt
		      fi	
		    done
		done	
	done
done
