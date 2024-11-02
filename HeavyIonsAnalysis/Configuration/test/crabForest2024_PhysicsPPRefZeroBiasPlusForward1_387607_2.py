from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import getUsername

config = Configuration()

inputList = 'fileList_PhysicsPPRefZeroBiasPlusForward1_387607_2.txt'
jobTag = "rapidValidation_PhysicsPPRefZeroBiasPlusForward1_387607_2"
username = getUsername()

config.section_("General")
config.General.requestName = jobTag
config.General.workArea = 'WorkArea/' + config.General.requestName
config.General.transferOutputs = True
config.General.transferLogs = False

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'forest_miniAOD_run3_ppref_DATA.py'
config.JobType.maxMemoryMB = 2500
config.JobType.maxJobRuntimeMin = 420
#config.JobType.inputFiles = ['CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_374289.db']
config.JobType.allowUndistributedCMSSW = True

config.section_("Data")
config.Data.userInputFiles = open(inputList).readlines()
config.Data.totalUnits = len(config.Data.userInputFiles)
#config.Data.inputDataset = '/Alternatively/DefineDataset/InsteadOf/InputFileList'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 2
config.Data.outLFNDirBase = '/store/group/phys_heavyions/' + username + '/run3RapidValidation/' + config.General.requestName
config.Data.publication = False

config.section_("Site")
config.Site.whitelist = ['T2_CH_CERN', 'T2_US_MIT']
config.Site.storageSite = 'T2_CH_CERN'
