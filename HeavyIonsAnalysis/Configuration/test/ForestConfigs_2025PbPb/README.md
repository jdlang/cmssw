# CMSHI Run 3 Foresting: 2025 PbPb
*Last updated: 2 December 2025*

* **Overview of Config Files**
* **1) Setup CMSSW**
  * 1.1) Install CMSSW
  * 1.2) Add CMS Heavy Ion foresting tools
* **2) Processing Forests**
  * 2.1) Check CMSSWConfig Era and Global Tag
  * 2.2A) Edit CRAB Config (PromptReco)
  * 2.2B) Edit CRAB Config (ExpressReco)
  * 2.3) Initialize VOMS proxy
  * 2.4) Test your CMSSW config
  * 2.5) Submit CRAB jobs
  * 2.6) Tracking CRAB jobs
* **3) Quick Reference**
  * CMSSW
  * CRAB
  * VOMS Certificate Setup



--------------------------------------------------------------------------------

## 1) Setup

### 1.1) Install CMSSW
```bash
cmsrel CMSSW_15_1_0_patch4
cd CMSSW_15_1_0_patch4/src
cmsenv
```



### 1.2) Add CMS Heavy Ion foresting tools
```bash
git cms-merge-topic CmsHI:forest_CMSSW_15_1_X
scram build -j4
```

> [!TIP] 
> You can add CMSHI as a remote git reference in case of updates:
> ```bash
> git remote add cmshi git@github.com:CmsHI/cmssw.git
> ```

> [!IMPORTANT]
> To use Dfinder, clone the repo below into `<CMSSW>/src/` and recompile:
> ```bash
> git clone -b Dfinder_14XX_miniAOD git@github.com:boundino/Bfinder.git --depth 1
> sed -i "s|forest_miniAOD_run3_UPC_23rereco_DATA|forest_miniAOD_run3_UPC_23rereco_DATA_wDfinder|" Bfinder/test/DnBfinder_to_Forest.sh
> source Bfinder/test/DnBfinder_to_Forest.shx
> scram build -j4
> ```



--------------------------------------------------------------------------------

## 2) Processing Forests

### 2.1) Check CMSSWConfig Era and Global Tag
Confirm that your CMSSWConfig Era and Global Tag match the reco settings. These
are the lines shown below (for example):
```python
import FWCore.ParameterSet.Config as cms
from Configuration.Eras.Era_Run3_pp_on_PbPb_2025_cff import Run3_pp_on_PbPb_2025
process = cms.Process('HiForest', Run3_pp_on_PbPb_2025)

HIFOREST_VERSION = "151X"
GLOBAL_TAG = "151X_dataRun3_Prompt_v1"
```

> [!TIP]
> If you are foresting from PromptReco and have a CMS DAS path, click the
> "Configs" link below the dataset entry on DAS
> ([example](https://cmsweb.cern.ch/das/request?instance=prod/global&input=config+dataset%3D%2FHIForward0%2FHIRun2025A-PromptReco-v1%2FMINIAOD)),
> and then click "show" to see the era and global tag used for reco.

### 2.2A) Edit CRAB Config (PromptReco)
Make a copy of the `forest_CRABConfig` file with an appropriate name:
```bash
cp forest_CRABConfig_Run3_2025PbPb_PromptReco_TEMPLATE.py forest_CRABConfig_Run3_2025PbPb_PromptReco_<your_label>.py
```

Modify the input and output paths in the config (example shown below):
```Python
# INPUT/OUTPUT SETTINGS

pd = 'HIPhysicsRawPrime0'
jobTag = '2025PbPb_' + pd
cmsswConfig = 'forest_CMSSWConfig_Run3_2025PbPb_PromptReco.py'

inputDAS = '/' + pd + '/HIRun2025A-PromptReco-v1/MINIAOD'
inputDatabase = 'global'

output = '/store/group/phys_heavyions/' + username + '/Run3_2025PbPb_PromptRecoForest/'
outputServer = 'T2_CH_CERN'
```
Explanation of variables:
- `pd` is the PD tag of the dataset (as you would see on DAS).
- `jobTag` is a personal label for differentiating samples.
- `cmsswConfig` is the CMSSW config file these CRAB jobs should use.
- `inputDAS` is the miniAOD path on [CMS DAS](https://cmsweb.cern.ch/das/).
- `inputDatabase` is the DAS "dbs instance" that contains the files
  (typically `'global'` or `'phys03'`).
- `output` is the path on the output server. Forested files are saved here.
- `outputServer` is the CMS T2 server where data will be stored.

> [!TIP] 
> To process UPC data (PDs labelled with `HIForward`), use
> `forest_CMSSWConfig_Run3_151X_2025PbPb_DATA_UPC.py`



### 2.2B) Edit CRAB Config (ExpressReco)
Make a copy of the `forest_CRABConfig` file with an appropriate name:
```bash
cp forest_CRABConfig_Run3_PbPb_ExpressReco_TEMPLATE.py forest_CRABConfig_Run3_PbPb_ExpressReco_<your_label>.py
```

Assuming you are processing a list of files (i.e. there is **no** DAS path),
use `forest_CRABConfig_Run3_PbPb_ExpressReco_TEMPLATE.py` as your template. 
Save your file path(s) to a `.txt` file using a command like:
```bash
ls /path/to/files/*.root > filelist_<your_label>.txt

# NOTE! If the miniaod files are on /eos, you MUST remove "/eos/cms" from
# the start of the paths:
sed -i "s|/eos/cms||" filelist_<your_label>.txt
```

Modify the input and output paths in the config (example shown below):
```Python
# INPUT/OUTPUT SETTINGS

pd = 'HIPhysicsRawPrime0'
run = '399600'
jobTag = '2025PbPb_' + pd + '_' + run
cmsswConfig = 'forest_CMSSWConfig_Run3_151X_2025PbPb_PromptReco.py'

inputFilelist = 'filelist_<your_label>.txt'

output = '/store/group/phys_heavyions/' + username + '/Run3_2025PbPb_ExpressRecoForest/'
outputServer = 'T2_CH_CERN'
```
Explanation of variables:
- `pd` is the PD tag of the dataset (as you would see on DAS).
- `jobTag` is a personal label for differentiating samples.
- `cmsswConfig` is the CMSSW config file these CRAB jobs should use.
- `inputFilelist` list of local file paths on `/eos`.
- `output` is the path on the output server. Forested files are saved here.
- `outputServer` is the CMS T2 server where data will be stored.



### 2.3) Initialize VOMS proxy
```bash
voms-proxy-init -rfc -voms cms
```
> [!TIP] 
> Add an alias for this to `~/.bash_profile` to make VOMS easier:
> ```bash
> alias proxy='voms-proxy-init -rfc -voms cms; cp/tmp/x509up_u'$(id -u)' ~/'
> ```
> This will let you initialize VOMS just by running the command: `proxy`



### 2.4) Test your CMSSW config
```bash
cmsRun forest_CMSSWConfig_Run3_<your_label>.py
```

If this fails to produce a file (such as `HIForest.root`) or encounters
errors, you will need to debug your config or adjust settings before 
submitting jobs to CRAB.



### 2.5) Submit CRAB jobs
```bash
crab submit -c forest_CRABConfig_Run3_<your_label>.py
```

> [!TIP] 
> If you have issues with submissions not working, try copying your 
> CMSSW and CRAB configs to `<CMSSW>/src/` and submitting jobs from
> the `src` directory.



### 2.6) Tracking CRAB jobs
You can view the status of a job with:
```bash
crab status -d CrabWorkArea/crab_<your job tag>/
```

> [!TIP]
> Always check job status ~2-3 minutes after submitting to make sure the job
> has been accepted! If you see the status `SUBMITREFUSED` you will need to fix
> the config(s) and delete the job folder from `CrabWorkArea/` before
> submitting it again.

When you (inevitably) have failed jobs, you can resubmit them with:
```bash
crab resubmit -d CrabWorkArea/crab_<your job tag>/
```

Optionally you can also change the requested memory or runtime for jobs when
you resubmit:
```bash
crab resubmit --maxmemory 2500 --maxruntime 300 -d CrabWorkArea/crab_<your job tag>/
```

> [!WARNING]
> Requesting more than the maximum allowed memory or runtime will result in
> your job being refused and **you will be unable to __resubmit__ any failed jobs
> for that CRAB submission!** 
> * `maxmemory` **must not exceed 3000 (MB)** for the initial submission,
>   and must not exceed 5000 (MB) for resubmissions!
> * `maxruntime` **must not exceed 900** (minutes)!

If you need to stop a job before it finishes, use:
```bash
crab kill -d CrabWorkArea/crab_<your job tag>/
```



--------------------------------------------------------------------------------

# 3) Quick Reference

## CMSSW
```bash
# Run CMSSWConfig LOCALLY:
cmsRun forest_CMSSWConfig_XXXX.py
```



## CRAB
```bash
# Submit job:
crab submit -c <CRAB_config_file.py>

# Check job status:
crab status -d <path/to/crab_status_directory/>

# Kill a job (WARNING: this is irreversible!):
crab kill -d <path/to/crab_status_directory/>

# Resubmit failed jobs:
crab resubmit -d <path/to/crab_status_directory/>
# Resubmit with max memory and max runtime
crab resubmit --maxmemory 3000 --maxruntime 450 -d <path/to/crab_status_directory/>
```



## VOMS Certificate Setup

### Obtaining Certificates

https://ca.cern.ch/ca/user/Request.aspx?template=ee2user

Use the “New Grid User Certificate” tab to get a new CERN grid. You should set a password for this, and will need to remember it.

### Linux/Unix Installation

https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookStartingGrid#BasicGrid

To **setup the certificate** in your remote workspace, you should:
1. Export the certificate from your browser to a file in p12 format. You can 
give any name to your p12 file (in the example below the name is `mycert.p12`).

2. Place the p12 certificate file in the `.globus` directory of your home area. 
If the `.globus` directory doesn't exist, create it.
```bash
cd ~
mkdir .globus
cd ~/.globus
mv /path/to/mycert.p12 .
```

3. Execute the following shell commands:
```bash
rm -f usercert.pem
rm -f userkey.pem
openssl pkcs12 -in mycert.p12 -clcerts -nokeys -out usercert.pem
openssl pkcs12 -in mycert.p12 -nocerts -out userkey.pem
chmod 400 userkey.pem
chmod 400 usercert.pem
```
> [!WARNING]
> **If you are new to VOMS, you will need to sign the Acceptable Usage Policy 
> (AUP)** before you are able to access files, tools, and servers secured by
> certificate access. Just follow instructions here to sign the CMS AUP:
> https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideLcgAccess#AUP

