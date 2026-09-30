# [?] add comment about Signal unsoundness

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-03-30
Source: https://github.com/filecoin-project/lotus/commit/7b4e68249a2eec6c6fadf14992261682988f51b2
Type: security-commit

## Details
add comment about Signal unsoundness

## Patch
### chain/vm/execution.go
```diff
@@ -125,6 +125,8 @@ func (e *executionEnv) putToken(token *executionToken) {
 	e.available++
 	e.reserved += token.reserved
 
+	// Note: Signal is unsound, because a priority token could wake up a non-priority
+	// goroutnie and lead to deadlock. So Broadcast it must be.
 	e.cond.Broadcast()
 
 	metricsDown(metrics.VMExecutionRunning, token.lane)
```
