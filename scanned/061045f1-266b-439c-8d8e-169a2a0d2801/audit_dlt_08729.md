# [?] op-supervisor: remove redundant RLock/RUnlock and fix deadlock (#16642)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-07-10
Source: https://github.com/ethereum-optimism/optimism/commit/a8163353753d200f966ded7ef84412cf5b785ff7
Type: security-commit

## Details
op-supervisor: remove redundant RLock/RUnlock and fix deadlock (#16642)

* op-supervisor: remove redundant RLock/RUnlock and fix deadlock

* op-supervisor: unexport HasInitializedStatuses

## Patch
### op-supervisor/supervisor/backend/status/status.go
```diff
@@ -82,10 +82,8 @@ func (su *StatusTracker) OnEvent(ctx context.Context, ev event.Event) bool {
 	return true
 }
 
-func (su *StatusTracker) HasInitializedStatuses() bool {
-	su.mu.RLock()
-	defer su.mu.RUnlock()
-
+// hasInitializedStatuses is not behind a lock, because it is used only internally
+func (su *StatusTracker) hasInitializedStatuses() bool {
 	for _, nodeStatus := range su.statuses {
 		if nodeStatus != nil && *nodeStatus != (NodeSyncStatus{}) {
 			return true
@@ -100,7 +98,7 @@ func (su *StatusTracker) SyncStatus() (eth.SupervisorSyncStatus, error) {
 
 	// after supervisor restarts, there is a timespan where all node's sync status is not fetched yet
 	// error immediately until at least single node sync status is available, which is not empty
-	if !su.HasInitializedStatuses() {
+	if !su.hasInitializedStatuses() {
 		return eth.SupervisorSyncStatus{}, ErrStatusTrackerNotReady
 	}
 
```
