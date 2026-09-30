# [?] Fix panic on concurrent map rw (#12714)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2024-11-14
Source: https://github.com/erigontech/erigon/commit/59c424f7dcc80d9403667b265c3710e69beb887c
Type: security-commit

## Details
Fix panic on concurrent map rw (#12714)

## Patch
### cl/phase1/network/services/sync_contribution_service.go
```diff
@@ -50,7 +50,7 @@ type syncContributionService struct {
 	syncedDataManager              *synced_data.SyncedDataManager
 	beaconCfg                      *clparams.BeaconChainConfig
 	syncContributionPool           sync_contribution_pool.SyncContributionPool
-	seenSyncCommitteeContributions map[seenSyncCommitteeContribution]struct{}
+	seenSyncCommitteeContributions sync.Map //  map[seenSyncCommitteeContribution]struct{}
 	emitters                       *beaconevents.EventEmitter
 	ethClock                       eth_clock.EthereumClock
 	batchSignatureVerifier         *BatchSignatureVerifier
@@ -73,7 +73,7 @@ func NewSyncContributionService(
 		syncedDataManager:              syncedDataManager,
 		beaconCfg:                      beaconCfg,
 		syncContributionPool:           syncContributionPool,
-		seenSyncCommitteeContributions: make(map[seenSyncCommitteeContribution]struct{}),
+		seenSyncCommitteeContributions: sync.Map{},
 		ethClock:                       ethClock,
 		emitters:                       emitters,
 		batchSignatureVerifier:         batchSignatureVerifier,
@@ -237,7 +237,7 @@ func (s *syncContributionService) wasContributionSeen(contribution *cltypes.Cont
 		subCommitteeIndex: contribution.Contribution.SubcommitteeIndex,
 	}
 
-	_, ok := s.seenSyncCommitteeContributions[key]
+	_, ok := s.seenSyncCommitteeContributions.Load(key)
 	return ok
 }
 
@@ -248,7 +248,7 @@ func (s *syncContributionService) markContributionAsSeen(contribution *cltypes.C
 		slot:              contribution.Contribution.Slot,
 		subCommitteeIndex: contribution.Contribution.SubcommitteeIndex,
 	}
-	s.seenSyncCommitteeContributions[key] = struct{}{}
+	s.seenSyncCommitteeContributions.Store(key, struct{}{})
 }
 
 // verifySyncContributionProof verifies the sync contribution proof.
```
