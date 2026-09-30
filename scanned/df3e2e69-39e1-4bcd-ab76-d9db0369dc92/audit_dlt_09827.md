# [?] fix uint64 overflow on committed msg out of sync check

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-08-01
Source: https://github.com/harmony-one/harmony/commit/c844b78d2dd6cacb579029d2db8a1a358a11fa2b
Type: security-commit

## Details
fix uint64 overflow on committed msg out of sync check

## Patch
### consensus/validator.go
```diff
@@ -294,7 +294,7 @@ func (consensus *Consensus) onCommitted(msg *msg_pb.Message) {
 	consensus.aggregatedCommitSig = aggSig
 	consensus.commitBitmap = mask
 
-	if recvMsg.BlockNum-consensus.blockNum > consensusBlockNumBuffer {
+	if recvMsg.BlockNum > consensus.blockNum && recvMsg.BlockNum-consensus.blockNum > consensusBlockNumBuffer {
 		consensus.getLogger().Info().Uint64("MsgBlockNum", recvMsg.BlockNum).Msg("[OnCommitted] OUT OF SYNC")
 		go func() {
 			select {
```
