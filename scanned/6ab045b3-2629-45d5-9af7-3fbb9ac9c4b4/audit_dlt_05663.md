# [?] Fix panic in blob cache when scs array is empty or shorter than commitments (#15581)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-08-12
Source: https://github.com/OffchainLabs/prysm/commit/eace128ee9ef7b6b7d76b232045f47a173a71216
Type: security-commit

## Details
Fix panic in blob cache when scs array is empty or shorter than commitments (#15581)

* Fix panic in beacon-chain/das/blob_cache.go

* Regression test for empty/short scs array panic

* Changelog fragment

## Patch
### beacon-chain/das/blob_cache.go
```diff
@@ -99,20 +99,26 @@ func (e *blobCacheEntry) filter(root [32]byte, kc [][]byte, slot primitives.Slot
 		if e.diskSummary.HasIndex(i) {
 			continue
 		}
+		// Check if e.scs has this index before accessing
+		var sidecar *blocks.ROBlob
+		if i < uint64(len(e.scs)) {
+			sidecar = e.scs[i]
+		}
+
 		if kc[i] == nil {
-			if e.scs[i] != nil {
-				return nil, errors.Wrapf(errCommitmentMismatch, "root=%#x, index=%#x, commitment=%#x, no block commitment", root, i, e.scs[i].KzgCommitment)
+			if sidecar != nil {
+				return nil, errors.Wrapf(errCommitmentMismatch, "root=%#x, index=%#x, commitment=%#x, no block commitment", root, i, sidecar.KzgCommitment)
 			}
 			continue
 		}
 
-		if e.scs[i] == nil {
+		if sidecar == nil {
 			return nil, errors.Wrapf(errMissingSidecar, "root=%#x, index=%#x", root, i)
 		}
-		if !bytes.Equal(kc[i], e.scs[i].KzgCommitment) {
-			return nil, errors.Wrapf(errCommitmentMismatch, "root=%#x, index=%#x, commitment=%#x, block commitment=%#x", root, i, e.scs[i].KzgCommitment, kc[i])
+		if !bytes.Equal(kc[i], sidecar.KzgCommitment) {
+			return nil, errors.Wrapf(errCommitmentMismatch, "root=%#x, index=%#x, commitment=%#x, block commitment=%#x", root, i, sidecar.KzgCommitment, kc[i])
 		}
-		scs = append(scs, *e.scs[i])
+		scs = append(scs, *sidecar)
 	}
 
 	return scs, nil
```

### beacon-chain/das/blob_cache_test.go
```diff
@@ -155,6 +155,41 @@ func TestFilter(t *testing.T) {
 			},
 			err: errCommitmentMismatch,
 		},
+		{
+			name: "empty scs array with commitments",
+			setup: func(t *testing.T) (*blobCacheEntry, [][]byte, []blocks.ROBlob) {
+				// This reproduces the panic condition where entry.scs is empty or nil
+				// but we have commitments to check
+				entry := &blobCacheEntry{
+					scs: nil, // Empty/nil array that caused the panic
+				}
+				// Create a commitment that would trigger the check at index 0
+				commits := [][]byte{
+					bytesutil.PadTo([]byte("commitment1"), 48),
+				}
+				return entry, commits, nil
+			},
+			err: errMissingSidecar,
+		},
+		{
+			name: "scs array shorter than commitments",
+			setup: func(t *testing.T) (*blobCacheEntry, [][]byte, []blocks.ROBlob) {
+				// This reproduces the condition where entry.scs exists but is shorter
+				// than the number of commitments we're checking
+				entry := &blobCacheEntry{
+					scs: make([]*blocks.ROBlob, 2), // Only 2 slots
+				}
+				// Create 4 commitments, accessing index 2 and 3 would have panicked
+				commits := [][]byte{
+					nil,
+					nil,
+					bytesutil.PadTo([]byte("commitment3"), 48),
+					bytesutil.PadTo([]byte("commitment4"), 48),
+				}
+				return entry, commits, nil
+			},
+			err: errMissingSidecar,
+		},
 	}
 	for _, c := range cases {
 		t.Run(c.name, func(t *testing.T) {
```

### changelog/pvl-blob-cache-panic.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fixed a condition where the blob cache could panic when there were less than or no sidecars in the cache entry.
```
