#!/usr/bin/env python

import shutil
import glob
import csv
import xmltodict
import os
import re
import yaml
import json
import sys

def find_latest_metadata_dir(output_dir):
    dir_pattern = re.compile(u'^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}_[A-Z]{3}$')
    metadata_dirs = []
    for dir in os.listdir(output_dir):
        if not os.path.isdir(output_dir + '/' + dir):
            continue
        if dir_pattern.search(dir):
            metadata_dirs.append(output_dir + '/' + dir)

    return sorted(metadata_dirs)[-1]

def read_annotations(annotations, type, file_path):
    if type == 'pcawg_final_list':
        annotations[type] = {
            'donor': set(),
            'specimen': set(),
            'sample': set()
        }
        with open(file_path, 'r') as r:
            reader = csv.DictReader(r, delimiter='\t')
            for row in reader:
                annotations[type]['donor'].add(row.get('donor_unique_id'))
                annotations[type]['specimen'].add(row.get('dcc_project_code')+'::'+row.get('submitter_specimen_id'))
                annotations[type]['sample'].add(row.get('dcc_project_code')+'::'+row.get('submitter_sample_id'))
    elif type == 'aliquot_blacklist':
        annotations[type] = set()
        with open(file_path, 'r') as r:
            for line in r:
                if line.startswith('#'): continue
                if len(line.rstrip()) == 0: continue
                annotations[type].add(line.rstrip())
    elif type == 'exclude_gnos_id':
        annotations[type] = set()
        files = glob.glob(file_path)
        for f in files:
            with open(f, 'r') as r:
                for line in r:
                    if line.startswith('#'): continue
                    if len(line.rstrip()) == 0: continue
                    annotations[type].add(line.rstrip())
    else:
        annotations[type] = set()
        files = [file_path+'/'+type+'.live.not_index.gnos_id.txt']
        for file_name in files:
            with open(file_name, 'r') as f:
                for line in f:
                    if line.startswith('#'): continue
                    if len(line.rstrip()) == 0: continue
                    gnos_id= line.rstrip()
                    annotations[type].add(gnos_id)
    return annotations

def get_analysis_attrib(gnos_analysis):
    analysis_attrib = {}
    if (not gnos_analysis['analysis_xml']['ANALYSIS_SET'].get('ANALYSIS')
          or not gnos_analysis['analysis_xml']['ANALYSIS_SET']['ANALYSIS'].get('ANALYSIS_ATTRIBUTES')
          or not gnos_analysis['analysis_xml']['ANALYSIS_SET']['ANALYSIS']['ANALYSIS_ATTRIBUTES'].get('ANALYSIS_ATTRIBUTE')
       ):
        return None

    analysis_attrib_fragment = gnos_analysis['analysis_xml']['ANALYSIS_SET']['ANALYSIS']['ANALYSIS_ATTRIBUTES']['ANALYSIS_ATTRIBUTE']
    if (type(analysis_attrib_fragment) != list): analysis_attrib_fragment = [analysis_attrib_fragment]

    for a in analysis_attrib_fragment:
        if not analysis_attrib.get(a['TAG']):
            analysis_attrib[a['TAG']] = a['VALUE']

    return analysis_attrib

def get_xml_files( metadata_dir, conf, repo, annotations):
    xml_files = []
    for r in conf.get('gnos_repos'):
        if repo and not r.get('repo_code') == repo:
            continue
        gnos_ao_list_file = metadata_dir + '/analysis_objects.' + r.get('repo_code') + '.tsv'
        if not os.path.isfile(gnos_ao_list_file):
            logger.warning('gnos analsysi object list file does not exist: {}'.format(gnos_ao_list_file))
            continue
        with open(gnos_ao_list_file, 'r') as l:
            for ao in l:
                ao_uuid, ao_state = str.split(ao, '\t')[0:2]
                if not ao_state == 'live': continue  # skip ao that is not live
                if not ao_uuid in annotations.get(r.get('repo_code')): continue
                xml_files.append(r.get('repo_code') + '/' + ao.replace('\t', '__').replace('\n','') + '.xml')

    return xml_files

def get_gnos_analysis(f):
    with open (f, 'r') as x: xml_str = x.read()
    gnos_analysis = xmltodict.parse(xml_str).get('ResultSet').get('Result')
    # add_effective_xml_md5sum(gnos_analysis, xml_str)
    return gnos_analysis


def process_one(gnos_analysis):

    analysis_attrib = get_analysis_attrib(gnos_analysis)

    info = {}
    for i in ['analysis_id', 'aliquot_id', 'study', 'refassem_short_name', 'library_strategy']:
        info[i] = gnos_analysis.get(i, '')

    for i in ['workflow_name', 'workflow_version', 'workflow_output_bam_contents', 'dcc_project_code', 'submitter_donor_id', 'submitter_specimen_id', 'submitter_sample_id', 'dcc_specimen_type', 'variant_workflow_name', 'variant_workflow_version']:
        if analysis_attrib:
            info[i] = analysis_attrib.get(i, '')
        else:
            info[i] = ''

    if gnos_analysis['analysis_xml']['ANALYSIS_SET']['ANALYSIS']['DESCRIPTION'].startswith('Specimen-level BAM from the reference alignment') and gnos_analysis.get('library_strategy') == 'WGS' :
        info['workflow_output_bam_contents'] = 'aligned'
    if gnos_analysis['analysis_xml']['ANALYSIS_SET']['ANALYSIS']['DESCRIPTION'].startswith('The BAM file includes unmapped reads extracted from specimen-level BAM with the reference alignment') and gnos_analysis.get('library_strategy') == 'WGS' :
        info['workflow_output_bam_contents'] = 'unaligned'

    files = []
    if isinstance(gnos_analysis.get('files').get('file'), dict):
        file_list = [gnos_analysis.get('files').get('file')]  
    elif isinstance(gnos_analysis.get('files').get('file'), list):
        file_list = gnos_analysis.get('files').get('file') 

    file_ext = set([])
    file_md5sum = ''
    for f in file_list:
        files.append({'file_name': f.get('filename'), 'file_size': f.get('filesize'), 'file_md5sum': f.get('checksum').get('#text')})

        ext = f.get('filename').split('.')[-1]
        if ext == "gz" or ext == "bam":
            file_md5sum = f.get('checksum').get('#text')

        file_ext.add(ext)

    filenames = [ f.get('file_name') for f in files ]

    info['file_md5sum'] = file_md5sum
    info['file_name'] = ','.join(filenames)
    info['file_count'] = str(len(files))
    info['file_ext'] = ','.join(sorted(file_ext))

    return info


def main():
    with open('settings.yml') as f:
        conf = yaml.safe_load(f)

        index_work_dir = conf.get('index_work_dir')
        metadata_dir = conf.get('metadata_dir')
        latest_metadata_dir = find_latest_metadata_dir(os.path.join(index_work_dir, metadata_dir))

        annotations = {}
        annotations = read_annotations(annotations, 'pcawg_final_list', index_work_dir+'/../pcawg-operations/lists/pc_annotation-pcawg_final_list.tsv')
        annotations = read_annotations(annotations, 'aliquot_blacklist', index_work_dir+'/../pcawg-operations/lists/blacklist/pc_annotation-aliquot_blacklist.tsv')
        annotations = read_annotations(annotations, 'exclude_gnos_id', index_work_dir+'/dup_*_to_be_removed_gnos_id.tsv')

        for r in conf.get('gnos_repos'):
            conf[r.get('base_url')] = r.get('repo_code')
            file_path = '/'.join(['repos', r.get('repo_code')])
            annotations = read_annotations(annotations, r.get('repo_code'), file_path)
            path = '/'.join(['repos', r.get('repo_code'), r.get('repo_code')+'.live.not_index'])
            if os.path.exists(path): shutil.rmtree(path)
            os.makedirs(path)
#            print annotations.keys()
            for f in get_xml_files( latest_metadata_dir, conf, r.get('repo_code'), annotations):
                f = os.path.join(index_work_dir, metadata_dir, '__all_metadata_xml', f)
                gnos_analysis = get_gnos_analysis(f)
                if gnos_analysis:
                    info = process_one(gnos_analysis)
                    info['pcawg_donor'] = 'true' if str(info.get('dcc_project_code', ''))+'::'+str(info.get('submitter_donor_id', '')) in annotations.get('pcawg_final_list').get('donor') else 'false'
                    info['not_blacklist_aliquot'] = 'true' if not info['aliquot_id'] in annotations.get('aliquot_blacklist') else 'false'
                    info['not_exclude'] = 'true' if not info['analysis_id'] in annotations.get('exclude_gnos_id') else 'false'
                    
                    # determine the datatype
    #                if info['pcawg_donor'] == 'false' or info['not_blacklist_aliquot'] == 'false' or info['not_exclude'] == 'false':
    #                    info['data_type'] = 'excluded'

                    if info['variant_workflow_name']:
                        name = info['variant_workflow_name'].lower()
                        if name.startswith('sanger') or name.startswith('dkfz') or name.startswith('embl') or name.startswith('broad_muse'):
                            info['data_type'] = 'variant_call'
                        elif info['variant_workflow_name'] == 'OxoGWorkflow-OxoGFiltering':
                            info['data_type'] = 'oxog'
                        elif info['variant_workflow_name'] == 'OxoGWorkflow-variantbam':
                            info['data_type'] = 'wgs_minibam'
                        elif info['variant_workflow_name'] in ['consensus_snv_mnv', 'consensus_indel']:
                            info['data_type'] = 'consensus_call'
                        else:
                            info['data_type'] = 'wgs_unknown_variant_caller'

                    elif info['library_strategy'] == 'WGS':
                        if  info['refassem_short_name'] == 'unaligned':
                            info['data_type'] = 'wgs_unaligned_bam'
                        elif info['workflow_output_bam_contents'] == 'unaligned':
                            info['data_type'] = 'wgs_unmapped_bam'
                        elif info['workflow_output_bam_contents'] == 'aligned':
                            info['data_type'] = 'wgs_aligned_bam'
                        else:
                            info['data_type'] = 'wgs_unknown_workflow_name'

                    elif info['library_strategy'] == 'RNA-Seq':
                        if info['refassem_short_name'] == 'unaligned':
                           info['data_type'] = 'rna_seq_unaligned'
                        elif 'TOPHAT' in info['workflow_name'] or 'STAR' in info['workflow_name']:
                           info['data_type'] = 'rna_seq_aligned'
                        else:
                           info['data_type'] = 'rna_seq_unknown_workflow'
                    else:
                        info['data_type'] = 'others' 


                    field_names = sorted(info.keys())
                    output_file = '/'.join([path, r.get('repo_code')+'.live.not_index.'+info['data_type']+'.txt'])
                    if not os.path.exists(output_file):
                        header_printed = False
                    with open(output_file, 'a') as o:  
                        if not header_printed:
                            o.write('\t'.join(field_names)+'\n')
                            header_printed = True

                        fields = []
                        for f in field_names:
                            fields.append(info.get(f) if info.get(f) else '')
                        o.write('\t'.join(fields)+'\n') 


if __name__ == "__main__":
    sys.exit(main())               

