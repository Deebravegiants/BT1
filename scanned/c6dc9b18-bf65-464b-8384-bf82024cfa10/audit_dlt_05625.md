# [?] db/state: fix FilesAmount data race with background file integration (#22264)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-06
Source: https://github.com/erigontech/erigon/commit/bb96f7be9e5ceda83878411d4ffa145df2b25a64
Type: security-commit

## Details
db/state: fix FilesAmount data race with background file integration (#22264)

## What

`Aggregator.FilesAmount()` read each domain's / inverted index's
`dirtyFiles.Len()` without taking `dirtyFilesLock`. In `tidwall/btree`,
`Len()` does not take the tree's internal mutex (it's a plain read of
`tr.count`) even when the tree is created with internal locking, so
callers must synchronize externally. This races concurrent
`dirtyFiles.Set` from background file integration
(`integrateDirtyFiles`), which mutates the tree.

The race tripped the race-tests job on `main`
([run](https://github.com/erigontech/erigon/actions/runs/28785362605/job/85350623665)):
`TestEngineApiUnwindAcrossDomainStepBoundaries` failed with `race
detected during execution of test`. Its `waitForDomainFilesSettled`
helper (added in #21973) polls `FilesAmount()` while the background
builder is integrating files — that helper is the function's only
caller, so the race became reachable when #21973 merged. The same
`test-all-erigon-race.yml` runs in the merge-queue CI Gate, so this can
flake any PR until fixed.

## Fix

Take `a.dirtyFilesLock` in `FilesAmount()`, matching every other
`dirtyFiles` reader in `aggregator.go`. The write side
(`IntegrateDirtyFiles`) already holds this lock.

## Test

TDD: the new `TestFilesAmountConcurrent` (modeled on the neighboring
`TestReferencesInCommitmentBranchesConcurrent`) deterministically
reproduces the race under `-race` — it fails on `main` with the exact
stacks from the CI failure (`FilesAmount` → `btree.Len` racing
`btree.Set`) and passes with the fix.

Related: #15342 (audit of unsynchronized `dirtyFiles` access —
`FilesAmount` wasn't in its list).

## Patch
### db/state/aggregator.go
```diff
@@ -1710,6 +1710,8 @@ func (a *Aggregator) CollateAndPrune(ctx context.Context, db kv.TemporalRwDB, pr
 	return nil
 }
 func (a *Aggregator) FilesAmount() (res []int) {
+	a.dirtyFilesLock.Lock()
+	defer a.dirtyFilesLock.Unlock()
 	for _, d := range a.d {
 		res = append(res, d.dirtyFiles.Len())
 	}
```

### db/state/aggregator_test.go
```diff
@@ -175,6 +175,37 @@ func TestReferencesInCommitmentBranchesConcurrent(t *testing.T) {
 	wg.Wait()
 }
 
+// TestFilesAmountConcurrent exercises FilesAmount against concurrent dirtyFiles
+// mutation as done by background file integration; meaningful under -race.
+func TestFilesAmountConcurrent(t *testing.T) {
+	t.Parallel()
+	_, agg := testDbAndAggregatorv3(t, 1)
+
+	d := agg.d[kv.AccountsDomain]
+	const iters = 2000
+	var wg sync.WaitGroup
+	wg.Add(2)
+	go func() {
+		defer wg.Done()
+		for i := 0; i < iters; i++ {
+			item := &FilesItem{startTxNum: uint64(i), endTxNum: uint64(i + 1)}
+			agg.dirtyFilesLock.Lock()
+			d.dirtyFiles.Set(item)
+			agg.dirtyFilesLock.Unlock()
+			agg.dirtyFilesLock.Lock()
+			d.dirtyFiles.Delete(item)
+			agg.dirtyFilesLock.Unlock()
+		}
+	}()
+	go func() {
+		defer wg.Done()
+		for i := 0; i < iters; i++ {
+			_ = agg.FilesAmount()
+		}
+	}()
+	wg.Wait()
+}
+
 // generate test data for table tests, containing n; n < 20 keys of length 20 bytes and values of length <= 16 bytes
 func generateInputData(tb testing.TB, keySize, valueSize, keyCount int) ([][]byte, [][]byte) {
 	tb.Helper()
```
