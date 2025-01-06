### HiForest Configuration
# Input: miniAOD
# Type: data

import FWCore.ParameterSet.Config as cms
from Configuration.Eras.Era_Run3_pp_on_PbPb_2024_cff import Run3_pp_on_PbPb_2024
process = cms.Process('HiForest',Run3_pp_on_PbPb_2024)

###############################################################################

# HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 141X, data")

# import subprocess, os
# version = subprocess.check_output(
#     ['git', '-C', os.path.expandvars('$CMSSW_BASE/src'), 'describe', '--tags'])
# if version == '':
#     version = 'no git info'
# process.HiForestInfo.HiForestVersion = cms.string(version)

###############################################################################

# input files
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        # '/store/hidata/HIRun2024A/HIPhysicsRawPrime2/MINIAOD/PromptReco-v1/000/387/908/00000/93a76f4f-4e90-4357-9a7f-3c64a1be8e29.root'
        '/store/group/phys_heavyions/wangj/RECO2024/miniaod_PhysicsHIPhysicsRawPrime0_388056_ZB.root'
    ), 
)

# number of events to process, set to -1 to process all events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(20)
    )

###############################################################################

# load Global Tag, geometry, etc.
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')


from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '141X_dataRun3_Prompt_v3', '')
process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

## --> only use this starting from 388000
process.es_prefer = cms.ESPrefer('HcalTextCalibrations','es_ascii')
process.es_ascii = cms.ESSource('HcalTextCalibrations',
   input = cms.VPSet(
      cms.PSet(
         object = cms.string('Gains'),
         file   = cms.FileInPath('HeavyIonsAnalysis/Configuration/data/ZDCConditions_1400V/DumpGainsForUpload_AllChannels.txt')
      ),
      cms.PSet(
        object = cms.string('TPChannelParameters'),
        file   = cms.FileInPath('HeavyIonsAnalysis/Configuration/data/ZDCConditions_1400V/DumpTPChannelParameters_Run387473.txt')
      ),
   )
)
## <--
###############################################################################

# Define centrality binning
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("hiCentrality")
process.centralityBin.centralityVariable = cms.string("HFtowers")

###############################################################################

# root output
process.TFileService = cms.Service("TFileService",
    fileName = cms.string("HiForestMiniAOD.root"))

# # edm output for debugging purposes
# process.output = cms.OutputModule(
#     "PoolOutputModule",
#     fileName = cms.untracked.string('HiForestEDM.root'),
#     outputCommands = cms.untracked.vstring(
#         'keep *',
#         )
#     )

# process.output_path = cms.EndPath(process.output)

###############################################################################

# event analysis
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_data_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltobject_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.l1object_cfi')

#process.hiEvtAnalyzer.doCentrality = cms.bool(False)
#process.hiEvtAnalyzer.doHFfilters = cms.bool(False)

# FIXME: Do we have an updated trigger list?
#from HeavyIonsAnalysis.EventAnalysis.hltobject_cfi import trigger_list_data_2023_skimmed
#process.hltobject.triggerNames = trigger_list_data_2023_skimmed

process.load('HeavyIonsAnalysis.EventAnalysis.particleFlowAnalyser_cfi')
################################
# electrons, photons, muons
process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
process.ggHiNtuplizer.doMuons = cms.bool(False)
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
################################
# jet reco sequence
process.load('HeavyIonsAnalysis.JetAnalysis.akCs4PFJetSequence_pponPbPb_data_cff')
process.load('HeavyIonsAnalysis.JetAnalysis.akPu4CaloJetSequence_pponPbPb_data_cff')
process.akPu4CaloJetAnalyzer.doHiJetID = True
################################
# tracks
process.load("HeavyIonsAnalysis.TrackAnalysis.TrackAnalyzers_cff")
# muons (FTW)
process.load("HeavyIonsAnalysis.MuonAnalysis.unpackedMuons_cfi")
process.load("HeavyIonsAnalysis.MuonAnalysis.muonAnalyzer_cfi")
###############################################################################

#########################
# ZDC RecHit Producer && Analyzer
#########################
# to prevent crash related to HcalSeverityLevelComputerRcd record
process.load("RecoLocalCalo.HcalRecAlgos.hcalRecAlgoESProd_cfi")
process.load('HeavyIonsAnalysis.ZDCAnalysis.ZDCAnalyzersPbPb_cff')

###############################################################################
# main forest sequence
process.forest = cms.Path(
    process.HiForestInfo +
    process.centralityBin +
    process.hiEvtAnalyzer +
    process.hltanalysis +
    #process.hltobject +
    process.l1object +
    process.trackSequencePbPb +
    process.particleFlowAnalyser +
    process.ggHiNtuplizer +
    process.zdcSequencePbPb +
    process.unpackedMuons +
    process.muonAnalyzer +
    process.akPu4CaloJetAnalyzer
    )

#customisation

# Select the types of jets filled
jetPtMin = 15
jetAbsEtaMax = 2.5

# Choose which additional information is added to jet trees
doHIJetID = True             # Fill jet ID and composition information branches
doWTARecluster = True        # Add jet phi and eta for WTA axis
doBtagging  =  False         # Note that setting to True increases computing time a lot

# 0 means use original mini-AOD jets, otherwise use R value, e.g., 3,4,8
jetLabel = "0"

# add candidate tagging, copy/paste to add other jet radii
from HeavyIonsAnalysis.JetAnalysis.setupJets_PbPb_cff import candidateBtaggingMiniAOD
candidateBtaggingMiniAOD(process, isMC = False, jetPtMin = jetPtMin, jetCorrLevels = ['L2Relative', 'L2L3Residual'], doBtagging = doBtagging, labelR = jetLabel)

# setup jet analyzer
setattr(process,"akCs"+jetLabel+"PFJetAnalyzer",process.akCs4PFJetAnalyzer.clone())
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").jetTag = 'selectedUpdatedPatJetsDeepFlavour'
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").jetName = 'akCs'+jetLabel+'PF'
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").doHiJetID = doHIJetID
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").doWTARecluster = doWTARecluster
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").jetPtMin = jetPtMin
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").jetAbsEtaMax = cms.untracked.double(jetAbsEtaMax)
getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").rParam = int(jetLabel)*0.1
if doBtagging:
    getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").useNewBtaggers = True
    getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").pfJetProbabilityBJetTag = cms.untracked.string("pfJetProbabilityBJetTagsDeepFlavour") 
    getattr(process,"akCs"+jetLabel+"PFJetAnalyzer").pfUnifiedParticleTransformerAK4JetTags = cms.untracked.string("pfUnifiedParticleTransformerAK4JetTagsDeepFlavour")
process.forest += getattr(process,"akCs"+jetLabel+"PFJetAnalyzer")


# Options for reclustering jets with different parameters. 
# TODO:  Integrate with deepNtupleSettings script above -Matt
addR3FlowJets = False
addR4FlowJets = False
addUnsubtractedR4Jets = False



if addR3FlowJets or addR4FlowJets or addUnsubtractedR4Jets :
    process.load("HeavyIonsAnalysis.JetAnalysis.extraJets_cff")
    from HeavyIonsAnalysis.JetAnalysis.clusterJetsFromMiniAOD_cff import setupHeavyIonJets

    if addR3FlowJets :
        process.jetsR3flow = cms.Sequence()
        setupHeavyIonJets('akCs3PFFlow', process.jetsR3flow, process, isMC = 0, radius = 0.30, JECTag = 'AK3PF', doFlow = True)
        process.akCs3PFFlowpatJetCorrFactors.levels = ['L2Relative', 'L2L3Residual']
        process.akFlowPuCs3PFJetAnalyzer = process.akCs4PFJetAnalyzer.clone(jetTag = "akCs3PFFlowpatJets", jetName = 'akCs3PFFlow', doHiJetID = doHIJetID, doWTARecluster = doWTARecluster)
        process.forest += process.extraFlowJets * process.jetsR3flow * process.akFlowPuCs3PFJetAnalyzer


    if addR4FlowJets :
        process.jetsR4flow = cms.Sequence()
        setupHeavyIonJets('akCs4PFFlow', process.jetsR4flow, process, isMC = 0, radius = 0.40, JECTag = 'AK4PF', doFlow = True)
        process.akCs4PFFlowpatJetCorrFactors.levels = ['L2Relative', 'L2L3Residual']
        process.akFlowPuCs4PFJetAnalyzer.jetTag = 'akCs4PFFlowpatJets'
        process.akFlowPuCs4PFJetAnalyzer.jetName = 'akCs4PFFlow'
        process.akFlowPuCs4PFJetAnalyzer.doHiJetID = doHIJetID
        process.akFlowPuCs4PFJetAnalyzer.doWTARecluster = doWTARecluster
        process.forest += process.extraFlowJets * process.jetsR4flow * process.akFlowPuCs4PFJetAnalyzer

    if addUnsubtractedR4Jets:
        process.load('HeavyIonsAnalysis.JetAnalysis.ak4PFJetSequence_ppref_data_cff')
        from HeavyIonsAnalysis.JetAnalysis.clusterJetsFromMiniAOD_cff import setupPprefJets
        process.unsubtractedJetR4 = cms.Sequence()
        setupPprefJets('ak04PF', process.unsubtractedJetR4, process, isMC = 0, radius = 0.40, JECTag = 'AK4PF')
        process.ak04PFpatJetCorrFactors.levels = ['L2Relative', 'L2L3Residual']
        process.ak4PFJetAnalyzer.jetTag = "ak04PFpatJets"
        process.ak4PFJetAnalyzer.jetName = "ak04PF"
        process.forest += process.unsubtractedJetR4 * process.ak4PFJetAnalyzer



#########################
# Event Selection -> add the needed filters here
#########################

process.load('HeavyIonsAnalysis.EventAnalysis.collisionEventSelection_cff')
process.pclusterCompatibilityFilter = cms.Path(process.clusterCompatibilityFilter)
process.pprimaryVertexFilter = cms.Path(process.primaryVertexFilter)
process.load('HeavyIonsAnalysis.EventAnalysis.hffilterPF_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hffilter_cfi')
process.pphfCoincFilter4Th2 = cms.Path(process.phfCoincFilter4Th2)
process.pphfCoincFilter1Th3 = cms.Path(process.phfCoincFilter1Th3)
process.pphfCoincFilter2Th3 = cms.Path(process.phfCoincFilter2Th3)
process.pphfCoincFilter3Th3 = cms.Path(process.phfCoincFilter3Th3)
process.pphfCoincFilter4Th3 = cms.Path(process.phfCoincFilter4Th3)
process.pphfCoincFilter5Th3 = cms.Path(process.phfCoincFilter5Th3)
process.pphfCoincFilter1Th4 = cms.Path(process.phfCoincFilter1Th4)
process.pphfCoincFilter2Th4 = cms.Path(process.phfCoincFilter2Th4)
process.pphfCoincFilter3Th4 = cms.Path(process.phfCoincFilter3Th4)
process.pphfCoincFilter4Th4 = cms.Path(process.phfCoincFilter4Th4)
process.pphfCoincFilter5Th4 = cms.Path(process.phfCoincFilter5Th4)
process.pphfCoincFilter1Th5 = cms.Path(process.phfCoincFilter1Th5)
process.pphfCoincFilter2Th5 = cms.Path(process.phfCoincFilter2Th5)
process.pphfCoincFilter3Th5 = cms.Path(process.phfCoincFilter3Th5)
process.pphfCoincFilter4Th5 = cms.Path(process.phfCoincFilter4Th5)
process.pphfCoincFilter5Th5 = cms.Path(process.phfCoincFilter5Th5)
process.pAna = cms.EndPath(process.skimanalysis)

#from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
#process.hltfilter = hltHighLevel.clone(
#    HLTPaths = [
#        #"HLT_HIZeroBias_v4",                                                     
#        "HLT_HIMinimumBias_v2",
#    ]
#)
#process.filterSequence = cms.Sequence(
#    process.hltfilter
#)
#
#process.superFilterPath = cms.Path(process.filterSequence)
#process.skimanalysis.superFilters = cms.vstring("superFilterPath")
#
#for path in process.paths:
#    getattr(process, path)._seq = process.filterSequence * getattr(process,path)._seq

