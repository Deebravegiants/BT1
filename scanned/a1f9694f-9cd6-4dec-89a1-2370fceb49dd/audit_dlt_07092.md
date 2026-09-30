# [?] Fix backfill nil panic in columnsNeeded when a batch needs no columns (#17496)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-09-15
Source: https://github.com/OffchainLabs/prysm/commit/4a8c3b9d2b2e9e93864bacb41aef6949c432ff60
Type: security-commit

## Details
Fix backfill nil panic in columnsNeeded when a batch needs no columns (#17496)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

- Backfill panicked with a nil pointer SIGSEGV in batch.columnsNeeded
when a batch had no column work (e.g. all blocks pre-Fulu or outside the
column retention window), because newColumnSync returns a non-nil
&columnSync{} whose embedded *columnBatch is nil, and the wrapper called
the promoted (*columnBatch).needed() instead of the nil-guarded
(*columnSync).columnsNeeded().
- This PR routes the call through the guarded method and adds a
regression test that reproduces the crash without the fix.

**Which issue(s) does this PR fix?**

Fixes #

**Other notes for review**

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

## Patch
### beacon-chain/sync/backfill/columns.go
```diff
@@ -147,7 +147,8 @@ func (b batch) columnsNeeded() peerdas.ColumnIndices {
 	if b.columns == nil {
 		return peerdas.ColumnIndices{}
 	}
-	return b.columns.needed()
+	// Use the guarded columnsNeeded: the embedded columnBatch may be nil.
+	return b.columns.columnsNeeded()
 }
 
 func (cs *columnSync) columnsNeeded() peerdas.ColumnIndices {
```

### beacon-chain/sync/backfill/columns_test.go
```diff
@@ -629,6 +629,13 @@ func TestColumnSync_ColumnsNeeded(t *testing.T) {
 	})
 }
 
+// TestBatch_ColumnsNeeded covers a non-nil columnSync with a nil embedded columnBatch (what
+// newColumnSync returns when no columns are needed), which panicked via the promoted needed().
+func TestBatch_ColumnsNeeded(t *testing.T) {
+	require.Equal(t, 0, batch{}.columnsNeeded().Count())
+	require.Equal(t, 0, batch{columns: &columnSync{}}.columnsNeeded().Count())
+}
+
 // TestValidatingColumnRequest_CountedValidation tests the countedValidation method
 func TestValidatingColumnRequest_CountedValidation(t *testing.T) {
 	mockPeer := peer.ID("test-peer")
```

### changelog/satushh_fix-backfill-columns-needed-panic.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fixed a nil-pointer panic in backfill's `batch.columnsNeeded` for batches with no column work (all blocks pre-Fulu or outside the column retention window): the wrapper called the promoted `(*columnBatch).needed` on the nil embedded `columnBatch` instead of the guarded `(*columnSync).columnsNeeded`.
```
