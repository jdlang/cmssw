### HiForest Configuration
# Collisions: pp
# Type: Data
# Input: miniAOD

###############################################################################
# VERSION CONFIG
###############################################################################

### Era
import FWCore.ParameterSet.Config as cms
from Configuration.Eras.Era_Run3_2024_ppRef_cff import Run3_2024_ppRef
process = cms.Process('HiForest', Run3_2024_ppRef)
process.options = cms.untracked.PSet()

### HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 141X, data")

### Global Tag (GT), geometry, sequences, etc.
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '141X_dataRun3_Prompt_v3', '')
process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

#####################################################################################
# Input source
#####################################################################################

### Input files (this is overwritten by CRAB config)
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        '/store/data/Run2024J/PPRefHardProbes4/MINIAOD/PromptReco-v1/000/387/570/00000/c855cc0a-2470-4978-acbb-e4618979cf0e.root'
    )
)
# Number of events to process, set to -1 to process all events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(20)
)

### Output file name (this is preserved by CRAB config)
process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("HiForestMiniAOD.root")
)

###############################################################################
# ANALYSIS CONFIG
###############################################################################

### Jets
process.load("HeavyIonsAnalysis.JetAnalysis.ak4PFJetSequence_ppref_data_cff")

### Event Analysis
# Use data version to avoid PbPb MC
process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_data_cfi')
process.hiEvtAnalyzer.Vertex = cms.InputTag("offlineSlimmedPrimaryVertices")
process.hiEvtAnalyzer.doCentrality = cms.bool(False)
process.hiEvtAnalyzer.doEvtPlane = cms.bool(False)
process.hiEvtAnalyzer.doEvtPlaneFlat = cms.bool(False)
process.hiEvtAnalyzer.doMC = cms.bool(False) # Turn off general MC info
process.hiEvtAnalyzer.doHiMC = cms.bool(False) # Turn off HI specific MC info
process.hiEvtAnalyzer.doHFfilters = cms.bool(False) # Disable HF filters for ppRef
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltobject_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.l1object_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')

### Particle flow
process.load('HeavyIonsAnalysis.EventAnalysis.particleFlowAnalyser_cfi')

### HLT list
from HeavyIonsAnalysis.EventAnalysis.hltobject_cfi import trigger_list_data_2024
process.hltobject.triggerNames = trigger_list_data_2024

### Tracks
process.load('HeavyIonsAnalysis.TrackAnalysis.TrackAnalyzers_cff')

### Electrons, photons, muons
process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
process.ggHiNtuplizer.doGenParticles = cms.bool(False)
process.ggHiNtuplizer.doMuons = cms.bool(False) # unpackedMuons collection not found from file
process.ggHiNtuplizer.useValMapIso = cms.bool(False) # True here causes seg fault
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

### ZDC RecHit Producer && Analyzer
# to prevent crash related to HcalSeverityLevelComputerRcd record
process.load("RecoLocalCalo.HcalRecAlgos.hcalRecAlgoESProd_cfi")
process.load('HeavyIonsAnalysis.ZDCAnalysis.ZDCAnalyzersPP_cff')

###############################################################################
# MAIN FOREST SEQUENCE
###############################################################################

process.forest = cms.Path(
    process.HiForestInfo +
    process.hltanalysis *
    process.hiEvtAnalyzer *
    process.hltobject +
    process.l1object +
    process.ggHiNtuplizer +
    process.zdcSequencePP +
    process.trackSequencePP +
    process.particleFlowAnalyser
)

###############################################################################
# EVENT SELECTION / FILTERING
###############################################################################

### Schedule definition
process.pAna = cms.EndPath(process.skimanalysis)

### Primary vertex filter
process.primaryVertexFilter = cms.EDFilter("VertexSelector",
    src = cms.InputTag("offlineSlimmedPrimaryVertices"),
    cut = cms.string("!isFake && abs(z) <= 25 && position.Rho <= 2"), #in miniADO trackSize()==0, however there is no influence.
    filter = cms.bool(True), # otherwise it won't filter the event
)
process.pprimaryVertexFilter = cms.Path(process.primaryVertexFilter)

###############################################################################
# CUSTOMISATION
###############################################################################

addR2Jets = False
addR3Jets = False
addR4Jets = False
addR8Jets = False

if addR2Jets or addR3Jets or addR4Jets or addR8Jets:
    process.load("HeavyIonsAnalysis.JetAnalysis.extraJets_cff")
    from HeavyIonsAnalysis.JetAnalysis.clusterJetsFromMiniAOD_cff import setupPprefJets

    if addR2Jets :
        process.jetsR2 = cms.Sequence()
        setupPprefJets('ak2PF', process.jetsR2, process, isMC = 0, radius = 0.20, JECTag = 'AK2PF')
        process.ak2PFpatJetCorrFactors.levels = ['L2Relative', 'L3Absolute']
        process.ak2PFpatJetCorrFactors.primaryVertices = "offlineSlimmedPrimaryVertices"
        process.load("HeavyIonsAnalysis.JetAnalysis.candidateBtaggingMiniAOD_cff")
        process.ak2PFJetAnalyzer = process.ak4PFJetAnalyzer.clone(jetTag = "ak2PFpatJets", jetName = 'ak2PF', genjetTag = "ak2GenJetsNoNu")
        process.forest += process.jetsR2 * process.ak2PFJetAnalyzer

    if addR3Jets :
        process.jetsR3 = cms.Sequence()
        setupPprefJets('ak3PF', process.jetsR3, process, isMC = 0, radius = 0.30, JECTag = 'AK3PF')
        process.ak3PFpatJetCorrFactors.levels = ['L2Relative', 'L3Absolute']
        process.ak3PFpatJetCorrFactors.primaryVertices = "offlineSlimmedPrimaryVertices"
        process.load("HeavyIonsAnalysis.JetAnalysis.candidateBtaggingMiniAOD_cff")
        process.ak3PFJetAnalyzer = process.ak4PFJetAnalyzer.clone(jetTag = "ak3PFpatJets", jetName = 'ak3PF', genjetTag = "ak3GenJetsNoNu")
        process.forest += process.jetsR3 * process.ak3PFJetAnalyzer

    if addR4Jets :
        # Recluster using an alias "0" in order not to get mixed up with the default AK4 collections
        process.jetsR4 = cms.Sequence()
        setupPprefJets('ak04PF', process.jetsR4, process, isMC = 0, radius = 0.40, JECTag = 'AK4PF')
        process.ak04PFpatJetCorrFactors.levels = ['L2Relative', 'L3Absolute']
        process.ak04PFpatJetCorrFactors.primaryVertices = "offlineSlimmedPrimaryVertices"
        process.load("HeavyIonsAnalysis.JetAnalysis.candidateBtaggingMiniAOD_cff")
        process.ak4PFJetAnalyzer.jetTag = 'ak04PFpatJets'
        process.ak4PFJetAnalyzer.jetName = 'ak04PF'
        process.ak4PFJetAnalyzer.doSubEvent = False # Need to disable this, since there is some issue with the gen jet constituents. More debugging needed is want to use constituents.
        process.forest += process.jetsR4 * process.ak4PFJetAnalyzer

    if addR8Jets :
        process.jetsR8 = cms.Sequence()
        setupPprefJets('ak8PF', process.jetsR8, process, isMC = 0, radius = 0.80, JECTag = 'AK8PF')
        process.ak8PFpatJetCorrFactors.levels = ['L2Relative', 'L3Absolute']
        process.ak8PFpatJetCorrFactors.primaryVertices = "offlineSlimmedPrimaryVertices"
        process.load("HeavyIonsAnalysis.JetAnalysis.candidateBtaggingMiniAOD_cff")
        process.ak8PFJetAnalyzer = process.ak4PFJetAnalyzer.clone(jetTag = "ak8PFpatJets", jetName = 'ak8PF', genjetTag = "ak8GenJetsNoNu")
        process.forest += process.jetsR8 * process.ak8PFJetAnalyzer

else:
    process.forest += process.ak4PFJetAnalyzer
