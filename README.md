# pcawg-gnos-audit
The tool is used to:
* Audit PCAWG files status in GNOS repos

## Getting Started
The tool needs to talk to the `gnos_metadata` hosted in `pcawg-central-index`. 

### Prerequisites
Before you can run the tool, you need to configure the tool. The configuration file locates `setting.yml`. You may need to change the following field to indicate the `index_work_dir` for `pcawg_central_index` on your local machine.
```
index_work_dir: /pancancer_dot_info/data/pancancer-sandbox/pcawg_metadata_parser
```
### Installing
Get the source script of the tool
```
git clone git@github.com:lindaxiang/ega_script.git
```

### Running the tool
```
./run_me.sh
```

### The location of the output reports
The reports `*.report.txt` for each GNOS repository locates under the folder `repos` and start with the name of repository
```
repos/
├── bsc
├── bsc.report.txt
├── dkfz
├── dkfz.report.txt
├── ebi
├── ebi.report.txt
├── osdc-icgc
├── osdc-icgc.report.txt
├── osdc-tcga
├── osdc-tcga.report.txt
├── riken
└── riken.report.txt
```
If you want to know more details about each repository, you can check the content inside each repo folder, for example:
```
repos/dkfz
├── dkfz.live.gnos_id.txt
├── dkfz.live.index.broad_tar_variant_calling.gnos_id.txt
├── dkfz.live.index.broad_tar_variant_calling.not_portal.gnos_id.txt
├── dkfz.live.index.broad_tar_variant_calling.portal.gnos_id.txt
├── dkfz.live.index.broad_variant_calling.gnos_id.txt
├── dkfz.live.index.broad_variant_calling.not_portal.gnos_id.txt
├── dkfz.live.index.broad_variant_calling.portal.gnos_id.txt
├── dkfz.live.index.consensus_call.gnos_id.txt
├── dkfz.live.index.consensus_call.not_portal.gnos_id.txt
├── dkfz.live.index.consensus_call.portal.gnos_id.txt
├── dkfz.live.index.dkfz_embl_variant_calling.gnos_id.txt
├── dkfz.live.index.dkfz_embl_variant_calling.not_portal.gnos_id.txt
├── dkfz.live.index.dkfz_embl_variant_calling.portal.gnos_id.txt
├── dkfz.live.index.gnos_id.txt
├── dkfz.live.index.muse_variant_calling.gnos_id.txt
├── dkfz.live.index.muse_variant_calling.not_portal.gnos_id.txt
├── dkfz.live.index.muse_variant_calling.portal.gnos_id.txt
├── dkfz.live.index.oxog_variant_calling.gnos_id.txt
......
```



