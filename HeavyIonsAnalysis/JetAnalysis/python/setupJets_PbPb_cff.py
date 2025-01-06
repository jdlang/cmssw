import FWCore.ParameterSet.Config as cms

def candidateBtaggingMiniAOD(process, isMC = True, jetPtMin = 15, jetCorrLevels = ['L2Relative', 'L3Absolute'], doBtagging = False, labelR = "0"):
    # DeepNtuple settings
    jetR = 0.1*int(labelR)
    if labelR == "0": jetR = 0.4

    #jetCorrectionsAK4 = ('AK4PF' if labelR == "0" else 'AK'+labelR+'PF', jetCorrLevels, 'None')
    jetCorrectionsAK4 = ('AK4PF', jetCorrLevels, 'None')  # temporary while we wait for updated JECs


    if doBtagging:
        bTagInfos = [
            'pfDeepCSVTagInfos',
            'pfDeepFlavourTagInfos',
            'pfImpactParameterTagInfos',
            'pfInclusiveSecondaryVertexFinderTagInfos',
            'pfParticleTransformerAK4TagInfos',
            'pfUnifiedParticleTransformerAK4TagInfos'
        ]

        bTagDiscriminators = [
            'pfUnifiedParticleTransformerAK4JetTags:probb',
            'pfUnifiedParticleTransformerAK4JetTags:probbb',
            'pfUnifiedParticleTransformerAK4JetTags:probc',
            'pfUnifiedParticleTransformerAK4JetTags:probg',
            'pfUnifiedParticleTransformerAK4JetTags:problepb',
            'pfUnifiedParticleTransformerAK4JetTags:probu',
            'pfUnifiedParticleTransformerAK4JetTags:probd',
            'pfUnifiedParticleTransformerAK4JetTags:probs',
            'pfUnifiedParticleTransformerAK4JetTags:probtaup1h0p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaup1h1p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaup1h2p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaup3h0p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaup3h1p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaum1h0p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaum1h1p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaum1h2p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaum3h0p',
            'pfUnifiedParticleTransformerAK4JetTags:probtaum3h1p',
            'pfUnifiedParticleTransformerAK4JetTags:probele',
            'pfUnifiedParticleTransformerAK4JetTags:probmu',
            'pfUnifiedParticleTransformerAK4JetTags:ptcorr',
            'pfUnifiedParticleTransformerAK4JetTags:ptnu',
        ]
    else: 
        bTagInfos = ['None']
        bTagDiscriminators = ['None']

    # Create gen-level information
    if isMC:
        from RecoHI.HiJetAlgos.hiSignalParticleProducer_cfi import hiSignalParticleProducer as hiSignalGenParticles
        process.hiSignalGenParticles = hiSignalGenParticles.clone(
            src = "prunedGenParticles"
        )
        from PhysicsTools.PatAlgos.producersHeavyIons.heavyIonJets_cff import allPartons
        process.allPartons = allPartons.clone(
            src = 'hiSignalGenParticles'
        )
        from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets
        setattr(process,"ak"+labelR+"GenJetsWithNu",
                ak4GenJets.clone(
                    src = 'packedGenParticlesSignal',
                    rParam = jetR
                )
        )
        process.packedGenParticlesForJetsNoNu = cms.EDFilter("CandPtrSelector",
            src = cms.InputTag("packedGenParticlesSignal"),
            cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16")
        )
        setattr(process,"ak"+labelR+"GenJetsRecluster",
                ak4GenJets.clone(
                    src = 'packedGenParticlesForJetsNoNu'
                )
        )
        process.genTask = cms.Task(process.hiSignalGenParticles, process.allPartons, getattr(process,"ak"+labelR+"GenJetsWithNu"), process.packedGenParticlesForJetsNoNu, getattr(process,"ak"+labelR+"GenJetsRecluster"))

    # Remake secondary vertices
    from RecoVertex.AdaptiveVertexFinder.inclusiveVertexing_cff import inclusiveCandidateVertexFinder, candidateVertexMerger, candidateVertexArbitrator, inclusiveCandidateSecondaryVertices
    process.inclusiveCandidateVertexFinder = inclusiveCandidateVertexFinder.clone(
        tracks = "packedPFCandidates",
        primaryVertices = "offlineSlimmedPrimaryVertices",
        minHits = 0,
        minPt = 0.8
    )
    process.candidateVertexMerger = candidateVertexMerger.clone()
    process.candidateVertexArbitrator = candidateVertexArbitrator.clone(
        tracks = "packedPFCandidates",
        primaryVertices = "offlineSlimmedPrimaryVertices"
    )
    process.inclusiveCandidateSecondaryVertices = inclusiveCandidateSecondaryVertices.clone()
    process.svTask = cms.Task(process.inclusiveCandidateVertexFinder, process.candidateVertexMerger, process.candidateVertexArbitrator, process.inclusiveCandidateSecondaryVertices)
    svSource = cms.InputTag("inclusiveCandidateSecondaryVertices")

    # Create unsubtracted reco jets

    from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff import ak4PFJets
    setattr(process, "ak"+labelR+"PFUnsubJets", 
            ak4PFJets.clone(
                src = 'packedPFCandidates',
                jetPtMin = 5.,  # set lower than subtracted version
                rParam = jetR
            )
    )
    

    if isMC:
        from PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi import selectedHadronsAndPartons
        from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos
        process.selectedHadronsAndPartons = selectedHadronsAndPartons.clone(particles = "prunedGenParticles")
        setattr(process,"ak"+labelR+"PFUnsubJetFlavourInfos",
                ak4JetFlavourInfos.clone(
                    jets = "ak"+labelR+"PFUnsubJets",
                    partons = "selectedHadronsAndPartons:algorithmicPartons",
                    hadronFlavourHasPriority = True,
                    rParam = jetR
                )
        )
        process.genTask.add(process.selectedHadronsAndPartons)
        process.genTask.add(getattr(process,"ak"+labelR+"PFUnsubJetFlavourInfos"))

    matchedGenJets = ""
    if isMC:
        if labelR == "0": matchedGenJets = "slimmedGenJets"
        else: matchedGenJets  = "ak"+labelR+"GenJetsWithNu"



    from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
    addJetCollection(
        process,
        postfix            = "UnsubJets",
        labelName          = str("AK"+labelR+"PF"),
        jetSource          = cms.InputTag("ak"+labelR+"PFUnsubJets"),
        algo               = "ak", #name of algo must be in this format
        rParam             = jetR,
        pvSource           = cms.InputTag("offlineSlimmedPrimaryVertices"),
        pfCandidates       = cms.InputTag("packedPFCandidates"),
        svSource           = svSource,
        muSource           = cms.InputTag("slimmedMuons"),
        elSource           = cms.InputTag("slimmedElectrons"),
        getJetMCFlavour    = isMC,
        genJetCollection   = cms.InputTag(matchedGenJets),
        genParticles       = cms.InputTag("hiSignalGenParticles" if isMC else ""),
        #jetCorrections     = ('AK4PF' if labelR=='0' else 'AK'+labelR+'PF',) + jetCorrectionsAK4[1:],
        jetCorrections     = ('AK4PF',) + jetCorrectionsAK4[1:],  #tempoorary while we wait for updated JECs
    )

    getattr(process,"patJetsAK"+labelR+"PFUnsubJets").useLegacyJetMCFlavour = False

    process.patAlgosToolsTask.add(getattr(process,"ak"+labelR+"PFUnsubJets"))

    # Create HIN subtracted reco jets
    from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
    addJetCollection(
        process,
        postfix            = "",
        labelName          = "AKCs"+labelR+"PF",
        jetSource          = cms.InputTag("akCs"+labelR+"PFJets"),
        algo               = "ak", #name of algo must be in this format
        rParam             = jetR,
        pvSource           = cms.InputTag("offlineSlimmedPrimaryVertices"),
        pfCandidates       = cms.InputTag("packedPFCandidates"),
        svSource           = svSource,
        muSource           = cms.InputTag("slimmedMuons"),
        elSource           = cms.InputTag("slimmedElectrons"),
        getJetMCFlavour    = isMC,
        genJetCollection   = cms.InputTag(matchedGenJets),
        genParticles       = cms.InputTag("hiSignalGenParticles" if isMC else ""),
        jetCorrections     = jetCorrectionsAK4,
    )
    getattr(process,"patJetsAKCs"+labelR+"PF").embedPFCandidates = True

    if not isMC:
        for label in ["patJetsAK"+labelR+"PFUnsubJets", "patJetsAKCs"+labelR+"PF"]:
            getattr(process, label).addGenJetMatch = False
            getattr(process, label).addGenPartonMatch = False
            getattr(process, label).embedGenJetMatch = False
            getattr(process, label).embedGenPartonMatch = False
            getattr(process, label).genJetMatch = ""
            getattr(process, label).genPartonMatch = ""

    # left here for reference in case we want to move reclustering here
    from PhysicsTools.PatAlgos.producersHeavyIons.heavyIonJets_cff import PackedPFTowers, hiPuRho
    process.PackedPFTowers = PackedPFTowers.clone()
    process.hiPuRho = hiPuRho.clone(
        src = 'PackedPFTowers'
    )
    from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff import akCs4PFJets
    setattr(process,"akCs"+labelR+"PFJets",
            akCs4PFJets.clone(
                src = 'packedPFCandidates',
                jetPtMin = jetPtMin,
                rParam = jetR
            )
    )
    for mod in ["PackedPFTowers", "hiPuRho", "akCs"+labelR+"PFJets"]:
        process.patAlgosToolsTask.add(getattr(process, mod))

    # Create b-tagging sequence ----------------
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    updateJetCollection(
        process,
        labelName = "DeepFlavour",
        jetSource = cms.InputTag("slimmedJets" if labelR == "0" else "patJetsAKCs"+labelR+"PF"), 
        jetCorrections = jetCorrectionsAK4,
        pfCandidates = cms.InputTag('packedPFCandidates'),
        pvSource = cms.InputTag("offlineSlimmedPrimaryVertices"),
        svSource = svSource,
        muSource = cms.InputTag('slimmedMuons'),
        elSource = cms.InputTag('slimmedElectrons'),
        btagInfos = bTagInfos,
        btagDiscriminators = bTagDiscriminators,
        explicitJTA = False
    )

    process.unsubUpdatedPatJetsDeepFlavour = cms.EDProducer("JetMatcherDR",
                                                            source = cms.InputTag("updatedPatJetsDeepFlavour"),
                                                            matched = cms.InputTag("patJetsAK"+labelR+"PFUnsubJets")
    )
    process.patAlgosToolsTask.add(process.unsubUpdatedPatJetsDeepFlavour)

    if doBtagging:

        process.pfUnifiedParticleTransformerAK4JetTagsDeepFlavour.model_path = 'RecoBTag/Combined/data/UParTAK4/HIN/V00/UParTAK4_PbPb_2023.onnx'
        process.pfUnifiedParticleTransformerAK4TagInfosDeepFlavour.sort_cand_by_pt = True

        if hasattr(process,'updatedPatJetsTransientCorrectedDeepFlavour'):
            process.updatedPatJetsTransientCorrectedDeepFlavour.addTagInfos = True
            process.updatedPatJetsTransientCorrectedDeepFlavour.addBTagInfo = True
        else:
            raise ValueError('I could not find updatedPatJetsTransientCorrectedDeepFlavour to embed the tagInfos, please check the cfg')

            # Remove PUPPI
        process.patAlgosToolsTask.remove(process.packedpuppi)
        process.patAlgosToolsTask.remove(process.packedpuppiNoLep)
        process.pfInclusiveSecondaryVertexFinderTagInfosDeepFlavour.weights = ""
        for taginfo in ["pfDeepFlavourTagInfosDeepFlavour", "pfParticleTransformerAK4TagInfosDeepFlavour", "pfUnifiedParticleTransformerAK4TagInfosDeepFlavour"]:
            getattr(process, taginfo).fallback_puppi_weight = True
            getattr(process, taginfo).fallback_vertex_association = True
            getattr(process, taginfo).unsubjet_map = "unsubUpdatedPatJetsDeepFlavour"
            getattr(process, taginfo).puppi_value_map = ""

    # Match with unsubtracted jets
    process.unsubJetMap = process.unsubUpdatedPatJetsDeepFlavour.clone(
        source = "selectedUpdatedPatJetsDeepFlavour"
    )
    process.patAlgosToolsTask.add(process.unsubJetMap)

    # Add extra b tagging algos
    from RecoBTag.ImpactParameter.pfJetProbabilityBJetTags_cfi import pfJetProbabilityBJetTags
    process.pfJetProbabilityBJetTagsDeepFlavour = pfJetProbabilityBJetTags.clone(tagInfos = ["pfImpactParameterTagInfosDeepFlavour"])
    if doBtagging:
        process.patAlgosToolsTask.add(process.pfJetProbabilityBJetTagsDeepFlavour)

    # Associate to forest sequence
    if isMC:
        process.forest.associate(process.genTask)
    if doBtagging: 
        process.forest.associate(process.svTask)
    process.forest.associate(process.patAlgosToolsTask)
