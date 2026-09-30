# [?] Fix nil panic.

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-02-22
Source: https://github.com/harmony-one/harmony/commit/e6287c16350890549b61a1982f72fa424eb5f904
Type: security-commit

## Details
Fix nil panic.

## Patch
### consensus/view_change.go
```diff
@@ -202,7 +202,7 @@ func (consensus *Consensus) getNextLeaderKey(viewID uint64) *bls.PublicKeyWrappe
 	// FIXME: rotate leader on harmony nodes only before fully externalization
 	var wasFound bool
 	var next *bls.PublicKeyWrapper
-	if consensus.Blockchain().Config().IsLeaderRotation(epoch) {
+	if blockchain != nil && blockchain.Config().IsLeaderRotation(epoch) {
 		if consensus.ShardID == shard.BeaconChainShardID {
 			wasFound, next = consensus.Decider.NthNextHmy(
 				shard.Schedule.InstanceForEpoch(epoch),
```
