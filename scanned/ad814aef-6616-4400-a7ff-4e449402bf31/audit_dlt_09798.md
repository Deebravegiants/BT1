# [?] Fix possible panic when the leader is unknown. (#4684)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2024-06-05
Source: https://github.com/harmony-one/harmony/commit/434abca415e0142bed8e886e92517c9a988b567f
Type: security-commit

## Details
Fix possible panic when the leader is unknown. (#4684)

## Patch
### consensus/consensus_service.go
```diff
@@ -484,6 +484,9 @@ func (consensus *Consensus) IsLeader() bool {
 // isLeader check if the node is a leader or not by comparing the public key of
 // the node with the leader public key. This function assume it runs under lock.
 func (consensus *Consensus) isLeader() bool {
+	if consensus.LeaderPubKey == nil {
+		return false
+	}
 	obj := consensus.LeaderPubKey.Object
 	for _, key := range consensus.priKey {
 		if key.Pub.Object.IsEqual(obj) {
```
