# [?] go/worker/compute/executor: Fix race condition

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-11-05
Source: https://github.com/oasisprotocol/oasis-core/commit/0309c44a690b6747bd9291129b3e6d50779b718c
Type: security-commit

## Details
go/worker/compute/executor: Fix race condition

## Patch
### go/worker/compute/executor/committee/node.go
```diff
@@ -1477,22 +1477,21 @@ func (n *Node) worker() {
 		}
 	}()
 
-	// (Re)Start the runtime worker every time a runtime block is finalized.
-	var (
-		wg sync.WaitGroup
-		bi *runtime.BlockInfo
-	)
+	// Restart the round worker every time a runtime block is finalized.
 	for {
+		var bi *runtime.BlockInfo
+
 		func() {
-			wg.Add(1)
+			var wg sync.WaitGroup
 			defer wg.Wait()
 
 			ctx, cancel := context.WithCancel(n.ctx)
 			defer cancel()
 
+			wg.Add(1)
 			go func() {
 				defer wg.Done()
-				n.roundWorker(ctx, bi)
+				n.roundWorker(ctx)
 			}()
 
 			select {
@@ -1501,6 +1500,9 @@ func (n *Node) worker() {
 			}
 		}()
 
+		// Round worker stopped, so it is safe to update the last block info.
+		n.blockInfo = bi
+
 		select {
 		case <-n.stopCh:
 			n.logger.Info("termination requested")
@@ -1510,12 +1512,11 @@ func (n *Node) worker() {
 	}
 }
 
-func (n *Node) roundWorker(ctx context.Context, bi *runtime.BlockInfo) {
-	if bi == nil {
+func (n *Node) roundWorker(ctx context.Context) {
+	if n.blockInfo == nil {
 		return
 	}
-	n.blockInfo = bi
-	round := bi.RuntimeBlock.Header.Round + 1
+	round := n.blockInfo.RuntimeBlock.Header.Round + 1
 
 	n.handleRoundStarted()
 	defer n.handleRoundEnded()
@@ -1531,10 +1532,10 @@ func (n *Node) roundWorker(ctx context.Context, bi *runtime.BlockInfo) {
 
 	// Need to be an executor committee member.
 	n.epoch = n.commonNode.Group.GetEpochSnapshot()
-	if epoch := n.epoch.GetEpochNumber(); epoch != bi.Epoch {
+	if epoch := n.epoch.GetEpochNumber(); epoch != n.blockInfo.Epoch {
 		n.logger.Debug("skipping round, behind common worker",
 			"epoch", epoch,
-			"block_epoch", bi.Epoch,
+			"block_epoch", n.blockInfo.Epoch,
 		)
 		return
 	}
@@ -1555,7 +1556,7 @@ func (n *Node) roundWorker(ctx context.Context, bi *runtime.BlockInfo) {
 
 	// Fetch state and round results upfront.
 	var err error
-	n.rtState, n.roundResults, err = n.getRtStateAndRoundResults(ctx, bi.ConsensusBlock.Height)
+	n.rtState, n.roundResults, err = n.getRtStateAndRoundResults(ctx, n.blockInfo.ConsensusBlock.Height)
 	if err != nil {
 		n.logger.Debug("skipping round, failed to fetch state and round results",
 			"err", err,
@@ -1565,7 +1566,7 @@ func (n *Node) roundWorker(ctx context.Context, bi *runtime.BlockInfo) {
 
 	// Prepare flush timer for the primary transaction scheduler.
 	flush := false
-	flushTimer := time.NewTimer(bi.ActiveDescriptor.TxnScheduler.BatchFlushTimeout)
+	flushTimer := time.NewTimer(n.blockInfo.ActiveDescriptor.TxnScheduler.BatchFlushTimeout)
 	defer flushTimer.Stop()
 
 	// Compute node's rank when scheduling transactions.
```
