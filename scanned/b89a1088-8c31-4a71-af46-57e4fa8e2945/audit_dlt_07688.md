# [?] Fix panic (#13270)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2024-12-30
Source: https://github.com/erigontech/erigon/commit/a11af15f2dd0b6f5c66901bbda97889af6b84f6b
Type: security-commit

## Details
Fix panic (#13270)

fix #13269

## Patch
### erigon-lib/state/aggregator.go
```diff
@@ -1056,7 +1056,7 @@ func (ac *AggregatorRoTx) PruneSmallBatchesDb(ctx context.Context, timeout time.
 				ac.a.logger.Info("[snapshots] pruning state",
 					"until commit", time.Until(started.Add(timeout)).String(),
 					"pruneLimit", pruneLimit,
-					"aggregatedStep", ac.StepsInFiles(),
+					"aggregatedStep", ac.StepsInFiles(kv.StateDomains...),
 					"stepsRangeInDB", ac.a.StepsRangeInDBAsStr(tx),
 					"pruned", fullStat.String(),
 				)
@@ -1150,7 +1150,7 @@ func (ac *AggregatorRoTx) PruneSmallBatches(ctx context.Context, timeout time.Du
 			ac.a.logger.Info("[snapshots] pruning state",
 				"until commit", time.Until(started.Add(timeout)).String(),
 				"pruneLimit", pruneLimit,
-				"aggregatedStep", ac.StepsInFiles(),
+				"aggregatedStep", ac.StepsInFiles(kv.StateDomains...),
 				"stepsRangeInDB", ac.a.StepsRangeInDBAsStr(tx),
 				"pruned", fullStat.String(),
 			)
```
