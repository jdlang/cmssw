# 2025 PbPb
# CMSSW_15_1_0_patch3+
# HIPhysicsRawPrime

from CRABClient.UserUtilities import config
from CRABClient.UserUtilities import getUsername
username = getUsername()

###############################################################################
# INPUT/OUTPUT SETTINGS

pd = 'HIPhysicsRawPrime0'
run = '399306'
jobTag = '2025PbPb_' + pd + '_' + run
cmsswConfig = 'forest_CMSSWConfig_Run3_2025PbPb_PromptReco.py'

inputFilelist = 'filelist_' + pd + '_' + run + '.txt'

output = '/store/group/phys_heavyions/' + username + '/Run3_2025PbPb_ExpressRecoForests/'
outputServer = 'T2_CH_CERN'

###############################################################################

config = config()

config.General.requestName = jobTag
config.General.workArea = 'CrabWorkArea'
config.General.transferOutputs = True

config.JobType.psetName = cmsswConfig
config.JobType.pluginName = 'Analysis'
config.JobType.maxMemoryMB = 3000
config.JobType.pyCfgParams = ['noprint']
config.JobType.allowUndistributedCMSSW = True

config.Data.outputPrimaryDataset = jobTag
config.Data.userInputFiles = open(inputFilelist).readlines()
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = -1

config.Data.outLFNDirBase = output
config.Data.publication = False
config.Data.allowNonValidInputDataset = True

config.Site.storageSite = outputServer
