# 2025 PbPb
# CMSSW_15_1_0_patch3+
# HIPhysicsRawPrime

from CRABClient.UserUtilities import config
from CRABClient.UserUtilities import getUsername
username = getUsername()

###############################################################################
# INPUT/OUTPUT SETTINGS

pd = 'HIPhysicsRawPrime0'
jobTag = '2025PbPb_' + pd
cmsswConfig = 'forest_CMSSWConfig_Run3_2025PbPb_PromptReco.py'

inputDAS = '/' + pd + '/PbPbRun2025-PromptReco-v1/MINIAOD'
inputDatabase = 'global'

output = '/store/group/phys_heavyions/' + username + '/Run3_2025PbPb_PromptRecoForests/'
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

config.Data.inputDataset = inputDAS
config.Data.inputDBS = inputDatabase
config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions25HI/DCSOnly_JSONS/dailyDCSOnlyJSON/Collisions25HI_5p36TeV_Latest.json'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 10000
config.Data.totalUnits = -1

config.Data.outLFNDirBase = output
config.Data.publication = False
config.Data.allowNonValidInputDataset = True

config.Site.storageSite = outputServer
