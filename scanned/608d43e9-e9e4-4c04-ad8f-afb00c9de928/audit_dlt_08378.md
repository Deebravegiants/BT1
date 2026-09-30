# [?] fix(store): a data race in the root multi-store pruning test. (#26782)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-09-11
Source: https://github.com/cosmos/cosmos-sdk/commit/421967a3ceae941f505ec01a696596a43da40e90
Type: security-commit

## Details
fix(store): a data race in the root multi-store pruning test. (#26782)

## Patch
### CHANGELOG.md
```diff
@@ -49,8 +49,10 @@ Ref: https://keepachangelog.com/en/1.0.0/
 ### Improvements
 
 * (types) [#26729](https://github.com/cosmos/cosmos-sdk/pull/26729) Memoize `GetConfig`'s "hostname|binary|pid" registry-key fallback, which derived the executable path, hostname, and PID on every call.
+* (store) [#26782](https://github.com/cosmos/cosmos-sdk/pull/26782) Fix a data race in the root multi-store pruning test.
 * (blockstm) [#26779](https://github.com/cosmos/cosmos-sdk/pull/26779) perf(blockstm): memoize merge iterator source.
 
+
 ### Bug Fixes
 
 * (blockstm) [#26772](https://github.com/cosmos/cosmos-sdk/pull/26772) Panic with a descriptive error when accessing an unregistered store instead of silently using store index zero.
```

### store/rootmulti/store_test.go
```diff
@@ -760,9 +760,10 @@ func TestMultiStore_PruningWithIntervalUpdates(t *testing.T) {
 					height := ms.Commit().Version
 					if height != 0 && snapshotInterval != 0 && uint64(height)%snapshotInterval == 0 {
 						ms.pruningManager.AnnounceSnapshotHeight(height)
+						delay := time.Duration(rnd.Int31n(int32(time.Millisecond)))
 						wg.Add(1)
 						go func() { // random completion order
-							time.Sleep(time.Duration(rnd.Int31n(int32(time.Millisecond))))
+							time.Sleep(delay)
 							ms.pruningManager.HandleSnapshotHeight(height)
 							wg.Done()
 						}()
```
