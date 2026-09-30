# [?] fix: correct mutex usage in consensus logic to prevent potential deadlock (#4946)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2025-09-23
Source: https://github.com/harmony-one/harmony/commit/85254d61257a3c3a200bd1e83be6f60126dc3b7f
Type: security-commit

## Details
fix: correct mutex usage in consensus logic to prevent potential deadlock (#4946)

## Patch
### consensus/consensus_v2.go
```diff
@@ -318,7 +318,7 @@ func (consensus *Consensus) BlockCommitSigs(blockNum uint64) ([]byte, error) {
 	defer consensus.mutex.Unlock()
 	if err != nil ||
 		len(lastCommits) < bls.BLSSignatureSizeInBytes {
-		msgs := consensus.FBFTLog().GetMessagesByTypeSeq(
+		msgs := consensus.fBFTLog.GetMessagesByTypeSeq(
 			msg_pb.MessageType_COMMITTED, blockNum,
 		)
 		if len(msgs) != 1 {
```
