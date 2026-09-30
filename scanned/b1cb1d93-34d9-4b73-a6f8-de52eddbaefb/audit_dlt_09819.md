# [?] [consensus] fix the rare consensus/sync race condition (#3539)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-02-11
Source: https://github.com/harmony-one/harmony/commit/6833b446fe2f37584610eabf7517f3325c667951
Type: security-commit

## Details
[consensus] fix the rare consensus/sync race condition (#3539)

## Patch
### consensus/consensus_v2.go
```diff
@@ -346,6 +346,9 @@ func (consensus *Consensus) Start(
 					consensus.consensusTimeout[timeoutConsensus].Start()
 					consensus.getLogger().Info().Str("Mode", mode.String()).Msg("Node is IN SYNC")
 					consensusSyncCounterVec.With(prometheus.Labels{"consensus": "in_sync"}).Inc()
+				} else if consensus.Mode() == Syncing {
+					mode := consensus.UpdateConsensusInformation()
+					consensus.SetMode(mode)
 				}
 				consensus.mutex.Unlock()
 
```
