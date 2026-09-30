# [?] cmd/thor/node: fix race condition (consensus.Process)

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2019-12-17
Source: https://github.com/vechain/thor/commit/94f57ab5f97999aa9916f8285cabd2f1a0ae3bde
Type: security-commit

## Details
cmd/thor/node: fix race condition (consensus.Process)

## Patch
### cmd/thor/node/node.go
```diff
@@ -36,9 +36,10 @@ import (
 var log = log15.New("pkg", "node")
 
 type Node struct {
-	goes   co.Goes
-	packer *packer.Packer
-	cons   *consensus.Consensus
+	goes     co.Goes
+	packer   *packer.Packer
+	cons     *consensus.Consensus
+	consLock sync.Mutex
 
 	master         *Master
 	chain          *chain.Chain
@@ -244,7 +245,12 @@ func (n *Node) txStashLoop(ctx context.Context) {
 func (n *Node) processBlock(blk *block.Block, stats *blockStats) (bool, error) {
 	startTime := mclock.Now()
 	now := uint64(time.Now().Unix())
+
+	// consensus object is not thread-safe
+	n.consLock.Lock()
 	stage, receipts, err := n.cons.Process(blk, now)
+	n.consLock.Unlock()
+
 	if err != nil {
 		switch {
 		case consensus.IsKnownBlock(err):
```
