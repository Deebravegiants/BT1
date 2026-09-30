# [?] fix nil pointer dereference in PrepareProposal

## Summary
Severity: Unknown
Chain: Rollkit
Component: evstack/ev-node
Published: 2023-11-19
Source: https://github.com/evstack/ev-node/commit/fb10c2dee7ea3d8e4484b5a0a7789990650fcd5a
Type: security-commit

## Details
fix nil pointer dereference in PrepareProposal

## Patch
### state/executor.go
```diff
@@ -130,9 +130,12 @@ func (e *BlockExecutor) CreateBlock(ctx context.Context, height uint64, lastComm
 	rpp, err := e.proxyApp.PrepareProposal(
 		ctx,
 		&abci.RequestPrepareProposal{
-			MaxTxBytes:         maxBytes,
-			Txs:                mempoolTxs.ToSliceOfBytes(),
-			LocalLastCommit:    abci.ExtendedCommitInfo{},
+			MaxTxBytes: maxBytes,
+			Txs:        mempoolTxs.ToSliceOfBytes(),
+			LocalLastCommit: abci.ExtendedCommitInfo{
+				Round: 0,
+				Votes: []abci.ExtendedVoteInfo{},
+			},
 			Misbehavior:        []abci.Misbehavior{},
 			Height:             int64(block.Height()),
 			Time:               block.Time(),
```
