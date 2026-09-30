# [?] tests: fix a rare data race in staling tracker tests (#5737)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-09-13
Source: https://github.com/algorand/go-algorand/commit/f96542704ad22c470d6c43fe73dc98abf9391599
Type: security-commit

## Details
tests: fix a rare data race in staling tracker tests (#5737)

## Patch
### ledger/acctonline_test.go
```diff
@@ -1605,8 +1605,6 @@ func TestAcctOnlineTopBetweenCommitAndPostCommit(t *testing.T) {
 		postCommitUnlockedReleaseLock: make(chan struct{}),
 		postCommitEntryLock:           make(chan struct{}),
 		postCommitReleaseLock:         make(chan struct{}),
-		alwaysLock:                    false,
-		shouldLockPostCommit:          false,
 	}
 
 	conf := config.GetDefaultLocal()
@@ -1632,7 +1630,7 @@ func TestAcctOnlineTopBetweenCommitAndPostCommit(t *testing.T) {
 		newBlockWithUpdates(genesisAccts, updates, totals, t, ml, i, oa)
 	}
 
-	stallingTracker.shouldLockPostCommit = true
+	stallingTracker.shouldLockPostCommit.Store(true)
 
 	updateAccountsRoutine := func() {
 		var updates ledgercore.AccountDeltas
@@ -1698,8 +1696,6 @@ func TestAcctOnlineTopDBBehindMemRound(t *testing.T) {
 		postCommitUnlockedReleaseLock: make(chan struct{}),
 		postCommitEntryLock:           make(chan struct{}),
 		postCommitReleaseLock:         make(chan struct{}),
-		alwaysLock:                    false,
-		shouldLockPostCommit:          false,
 	}
 
 	conf := config.GetDefaultLocal()
@@ -1725,7 +1721,7 @@ func TestAcctOnlineTopDBBehindMemRound(t *testing.T) {
 		newBlockWithUpdates(genesisAccts, updates, totals, t, ml, i, oa)
 	}
 
-	stallingTracker.shouldLockPostCommit = true
+	stallingTracker.shouldLockPostCommit.Store(true)
 
 	updateAccountsRoutine := func() {
 		var updates ledgercore.AccountDeltas
```

### ledger/acctupdates_test.go
```diff
@@ -2192,8 +2192,8 @@ func testAcctUpdatesLookupRetry(t *testing.T, assertFn func(au *accountUpdates,
 		postCommitUnlockedReleaseLock: make(chan struct{}),
 		postCommitEntryLock:           make(chan struct{}),
 		postCommitReleaseLock:         make(chan struct{}),
-		alwaysLock:                    true,
 	}
+	stallingTracker.alwaysLock.Store(true)
 	ml.trackers.trackers = append([]ledgerTracker{stallingTracker}, ml.trackers.trackers...)
 
 	// kick off another round
```

### ledger/catchpointtracker_test.go
```diff
@@ -778,9 +778,9 @@ type blockingTracker struct {
 	postCommitEntryLock           chan struct{}
 	postCommitReleaseLock         chan struct{}
 	committedUpToRound            int64
-	alwaysLock                    bool
-	shouldLockPostCommit          bool
-	shouldLockPostCommitUnlocked  bool
+	alwaysLock                    atomic.Bool
+	shouldLockPostCommit          atomic.Bool
+	shouldLockPostCommitUnlocked  atomic.Bool
 }
 
 // loadFromDisk is not implemented in the blockingTracker.
@@ -815,15 +815,15 @@ func (bt *blockingTracker) commitRound(context.Context, trackerdb.TransactionSco
 
 // postCommit implements entry/exit blockers, designed for testing.
 func (bt *blockingTracker) postCommit(ctx context.Context, dcc *deferredCommitContext) {
-	if bt.alwaysLock || dcc.catchpointFirstStage || bt.shouldLockPostCommit {
+	if bt.alwaysLock.Load() || dcc.catchpointFirstStage || bt.shouldLockPostCommit.Load() {
 		bt.postCommitEntryLock <- struct{}{}
 		<-bt.postCommitReleaseLock
 	}
 }
 
 // postCommitUnlocked implements entry/exit blockers, designed for testing.
 func (bt *blockingTracker) postCommitUnlocked(ctx context.Context, dcc *deferredCommitContext) {
-	if bt.alwaysLock || dcc.catchpointFirstStage || bt.shouldLockPostCommitUnlocked {
+	if bt.alwaysLock.Load() || dcc.catchpointFirstStage || bt.shouldLockPostCommitUnlocked.Load() {
 		bt.postCommitUnlockedEntryLock <- struct{}{}
 		<-bt.postCommitUnlockedReleaseLock
 	}
@@ -1004,8 +1004,8 @@ func TestCatchpointTrackerWaitNotBlocking(t *testing.T) {
 	writeStallingTracker := &blockingTracker{
 		postCommitUnlockedEntryLock:   make(chan struct{}),
 		postCommitUnlockedReleaseLock: make(chan struct{}),
-		shouldLockPostCommitUnlocked:  true,
 	}
+	writeStallingTracker.shouldLockPostCommitUnlocked.Store(true)
 	ledger.trackerMu.Lock()
 	ledger.trackers.mu.Lock()
 	ledger.trackers.trackers = append(ledger.trackers.trackers, writeStallingTracker)
@@ -1032,7 +1032,7 @@ func TestCatchpointTrackerWaitNotBlocking(t *testing.T) {
 		// consume to unblock
 		<-writeStallingTracker.postCommitUnlockedEntryLock
 		// disable further blocking
-		writeStallingTracker.shouldLockPostCommitUnlocked = false
+		writeStallingTracker.shouldLockPostCommitUnlocked.Store(false)
 
 		// wait the writeStallingTracker.postCommitUnlockedReleaseLock passes
 		wg.Wait()
```
