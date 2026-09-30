# [?] [crash] fix a segfault using wallet for transfer

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-07-26
Source: https://github.com/harmony-one/harmony/commit/6d070e4d39e29056dd25257d6f028b90a5c75bbb
Type: security-commit

## Details
[crash] fix a segfault using wallet for transfer

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### node/node.go
```diff
@@ -270,7 +270,7 @@ func (node *Node) getTransactionsForNewBlock(maxNumTxs int, coinbase common.Addr
 
 // MaybeKeepSendingPongMessage keeps sending pong message if the current node is a leader.
 func (node *Node) MaybeKeepSendingPongMessage() {
-	if node.Consensus.IsLeader() {
+	if node.Consensus != nil && node.Consensus.IsLeader() {
 		go node.SendPongMessage()
 	}
 }
```
