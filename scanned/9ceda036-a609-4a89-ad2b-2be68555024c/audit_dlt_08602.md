# [?] fix(itests): prevent wdPostLoop deadline skip race condition (#13464)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2026-01-06
Source: https://github.com/filecoin-project/lotus/commit/0ba6009d91206bef79c2c2934edf0cc99274e521
Type: security-commit

## Details
fix(itests): prevent wdPostLoop deadline skip race condition (#13464)

## Patch
### itests/kit/node_unmanaged.go
```diff
@@ -966,7 +966,15 @@ func (tm *TestUnmanagedMiner) wdPostLoop() {
 		}
 
 		for tm.ctx.Err() == nil {
-			postSectors, err := tm.sectorsToPost()
+			// Get deadline info at the start of this iteration to avoid race conditions
+			// where the chain advances between checking sectors and waiting for next deadline.
+			di, err := tm.FullNode.StateMinerProvingDeadline(tm.ctx, tm.ActorAddr, types.EmptyTSK)
+			if err != nil {
+				recordPostOrError(windowPost{Error: fmt.Errorf("failed to get proving deadline: %w", err)})
+				return
+			}
+
+			postSectors, err := tm.sectorsToPostWithDeadline(di)
 			if err != nil {
 				recordPostOrError(windowPost{Error: err})
 				return
@@ -981,28 +989,25 @@ func (tm *TestUnmanagedMiner) wdPostLoop() {
 				recordPostOrError(windowPost{Posted: postSectors})
 			}
 
-			// skip to next challenge window
-			if err := tm.waitForNextPostDeadline(); err != nil {
+			// skip to next challenge window, using the deadline info from the start of this iteration
+			if err := tm.waitForNextPostDeadlineFrom(di); err != nil {
 				recordPostOrError(windowPost{Error: err})
 				return
 			}
 		}
 	}()
 }
 
-// waitForNextPostDeadline waits until we are within the next challenge window for this miner
-func (tm *TestUnmanagedMiner) waitForNextPostDeadline() error {
+// waitForNextPostDeadlineFrom waits until the deadline described in di closes and the next one opens.
+func (tm *TestUnmanagedMiner) waitForNextPostDeadlineFrom(di *dline.Info) error {
 	ctx, cancel := context.WithCancel(tm.ctx)
 	defer cancel()
 
-	di, err := tm.FullNode.StateMinerProvingDeadline(ctx, tm.ActorAddr, types.EmptyTSK)
-	if err != nil {
-		return fmt.Errorf("waitForNextPostDeadline: failed to get proving deadline: %w", err)
-	}
-	currentDeadlineIdx := CurrentDeadlineIndex(di)
-	nextDeadlineEpoch := di.PeriodStart + di.WPoStChallengeWindow*abi.ChainEpoch(currentDeadlineIdx+1)
+	// Wait for the current deadline to close. di.Close is the epoch when
+	// the current deadline ends, which is also when the next deadline opens.
+	nextDeadlineEpoch := di.Close
 
-	tm.log("Window PoST waiting until next challenge window, currentDeadlineIdx: %d, nextDeadlineEpoch: %d", currentDeadlineIdx, nextDeadlineEpoch)
+	tm.log("Window PoST waiting until next challenge window, currentDeadlineIdx: %d, nextDeadlineEpoch: %d", di.Index, nextDeadlineEpoch)
 
 	heads, err := tm.FullNode.ChainNotify(ctx)
 	if err != nil {
@@ -1020,16 +1025,12 @@ func (tm *TestUnmanagedMiner) waitForNextPostDeadline() error {
 		}
 	}
 
-	return fmt.Errorf("waitForNextPostDeadline: failed to wait for nextDeadlineEpoch %d", nextDeadlineEpoch)
+	return fmt.Errorf("waitForNextPostDeadlineFrom: failed to wait for nextDeadlineEpoch %d", nextDeadlineEpoch)
 }
 
-// sectorsToPost returns the sectors that are due to be posted in the current challenge window
-func (tm *TestUnmanagedMiner) sectorsToPost() ([]abi.SectorNumber, error) {
-	di, err := tm.FullNode.StateMinerProvingDeadline(tm.ctx, tm.ActorAddr, types.EmptyTSK)
-	if err != nil {
-		return nil, fmt.Errorf("failed to get proving deadline: %w", err)
-	}
-
+// sectorsToPostWithDeadline returns the sectors that are due to be posted for the deadline
+// described in di.
+func (tm *TestUnmanagedMiner) sectorsToPostWithDeadline(di *dline.Info) ([]abi.SectorNumber, error) {
 	currentDeadlineIdx := CurrentDeadlineIndex(di)
 
 	var allSectors []abi.SectorNumber
```
