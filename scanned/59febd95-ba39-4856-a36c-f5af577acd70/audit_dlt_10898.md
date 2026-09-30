# [?] fix(node): crash when add future block

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-05-04
Source: https://github.com/vechain/thor/commit/f0307419f98a226664ed78e951af482b0ede3620
Type: security-commit

## Details
fix(node): crash when add future block

## Patch
### cmd/thor/node/node.go
```diff
@@ -212,7 +212,7 @@ func (n *Node) consensusLoop(ctx context.Context) {
 			if isTrunk, err := n.processBlock(newBlock.Block, &stats); err != nil {
 				if consensus.IsFutureBlock(err) ||
 					(consensus.IsParentMissing(err) && futureBlocks.Contains(newBlock.Header().ParentID())) {
-					futureBlocks.Set(newBlock.Header().ID(), newBlock)
+					futureBlocks.Set(newBlock.Header().ID(), newBlock.Block)
 				}
 			} else if isTrunk {
 				log.Info("imported blocks", stats.LogContext(newBlock.Block.Header())...)
```
