# [?] Fix race condition in consensus.State code (#673)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2023-04-11
Source: https://github.com/cometbft/cometbft/commit/6a96eca67fb810aa823e9de4da41cc8028637a65
Type: security-commit

## Details
Fix race condition in consensus.State code (#673)

* Repro in e2e tests

* Change something in the code

* Fix race condition in `SwitchToConsensus`

* Revert "Repro in e2e tests"

This reverts commit 4f441f8ebac8f245d5a641c25ccdfa3b382ca063.

* RAII lock

## Patch
### consensus/reactor.go
```diff
@@ -107,14 +107,19 @@ func (conR *Reactor) OnStop() {
 func (conR *Reactor) SwitchToConsensus(state sm.State, skipWAL bool) {
 	conR.Logger.Info("SwitchToConsensus")
 
-	// We have no votes, so reconstruct LastCommit from SeenCommit.
-	if state.LastBlockHeight > 0 {
-		conR.conS.reconstructLastCommit(state)
-	}
+	func() {
+		// We need to lock, as we are not entering consensus state from State's `handleMsg` or `handleTimeout`
+		conR.conS.mtx.Lock()
+		defer conR.conS.mtx.Unlock()
+		// We have no votes, so reconstruct LastCommit from SeenCommit
+		if state.LastBlockHeight > 0 {
+			conR.conS.reconstructLastCommit(state)
+		}
 
-	// NOTE: The line below causes broadcastNewRoundStepRoutine() to broadcast a
-	// NewRoundStepMessage.
-	conR.conS.updateToState(state)
+		// NOTE: The line below causes broadcastNewRoundStepRoutine() to broadcast a
+		// NewRoundStepMessage.
+		conR.conS.updateToState(state)
+	}()
 
 	conR.mtx.Lock()
 	conR.waitSync = false
```
