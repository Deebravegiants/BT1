# [?] Fix issue : Prevent makeslice panic from invalid Count values (#16227)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-01-16
Source: https://github.com/OffchainLabs/prysm/commit/a135a336c37d11883e9fc72e44f698339b18043b
Type: security-commit

## Details
Fix issue : Prevent makeslice panic from invalid Count values (#16227)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

Add defensive checks to prevent panic from large Count values that could
result from unsigned integer underflow:

1. In batch.blockRequest() and batch.blobRequest(): Return Count=0 when
end <= begin, preventing the underflow at the source.

2. In SendBeaconBlocksByRangeRequest(): Cap slice capacity to
MaxRequestBlock before allocation to prevent panic even if upstream code
produces invalid values.


**Which issues(s) does this PR fix?**

Fixes #16223

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
### beacon-chain/sync/backfill/batch.go
```diff
@@ -148,15 +148,15 @@ func (b batch) ensureParent(expected [32]byte) error {
 func (b batch) blockRequest() *eth.BeaconBlocksByRangeRequest {
 	return &eth.BeaconBlocksByRangeRequest{
 		StartSlot: b.begin,
-		Count:     uint64(b.end - b.begin),
+		Count:     uint64(b.end.FlooredSubSlot(b.begin)),
 		Step:      1,
 	}
 }
 
 func (b batch) blobRequest() *eth.BlobSidecarsByRangeRequest {
 	return &eth.BlobSidecarsByRangeRequest{
 		StartSlot: b.begin,
-		Count:     uint64(b.end - b.begin),
+		Count:     uint64(b.end.FlooredSubSlot(b.begin)),
 	}
 }
 
```

### beacon-chain/sync/backfill/batch_test.go
```diff
@@ -10,6 +10,93 @@ import (
 	"github.com/pkg/errors"
 )
 
+func TestBlockRequest(t *testing.T) {
+	cases := []struct {
+		name          string
+		begin         primitives.Slot
+		end           primitives.Slot
+		expectedCount uint64
+	}{
+		{
+			name:          "normal case",
+			begin:         100,
+			end:           200,
+			expectedCount: 100,
+		},
+		{
+			name:          "end equals begin",
+			begin:         100,
+			end:           100,
+			expectedCount: 0,
+		},
+		{
+			name:          "end less than begin (would underflow without check)",
+			begin:         200,
+			end:           100,
+			expectedCount: 0,
+		},
+		{
+			name:          "zero values",
+			begin:         0,
+			end:           0,
+			expectedCount: 0,
+		},
+		{
+			name:          "single slot",
+			begin:         0,
+			end:           1,
+			expectedCount: 1,
+		},
+	}
+
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			b := batch{begin: tc.begin, end: tc.end}
+			req := b.blockRequest()
+			require.Equal(t, tc.expectedCount, req.Count)
+			require.Equal(t, tc.begin, req.StartSlot)
+			require.Equal(t, uint64(1), req.Step)
+		})
+	}
+}
+
+func TestBlobRequest(t *testing.T) {
+	cases := []struct {
+		name          string
+		begin         primitives.Slot
+		end           primitives.Slot
+		expectedCount uint64
+	}{
+		{
+			name:          "normal case",
+			begin:         100,
+			end:           200,
+			expectedCount: 100,
+		},
+		{
+			name:          "end equals begin",
+			begin:         100,
+			end:           100,
+			expectedCount: 0,
+		},
+		{
+			name:          "end less than begin (would underflow without check)",
+			begin:         200,
+			end:           100,
+			expectedCount: 0,
+		},
+	}
+
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			b := batch{begin: tc.begin, end: tc.end}
+			req := b.blobRequest()
+			require.Equal(t, tc.expectedCount, req.Count)
+			require.Equal(t, tc.begin, req.StartSlot)
+		})
+	}
+}
+
 func TestSortBatchDesc(t *testing.T) {
 	orderIn := []primitives.Slot{100, 10000, 1}
 	orderOut := []primitives.Slot{10000, 100, 1}
```

### beacon-chain/sync/rpc_send_request.go
```diff
@@ -77,8 +77,13 @@ func SendBeaconBlocksByRangeRequest(
 	}
 	defer closeStream(stream, log)
 
+	// Cap the slice capacity to MaxRequestBlock to prevent panic from invalid Count values.
+	// This guards against upstream bugs that may produce astronomically large Count values
+	// (e.g., due to unsigned integer underflow).
+	sliceCap := min(req.Count, params.MaxRequestBlock(slots.ToEpoch(tor.CurrentSlot())))
+
 	// Augment block processing function, if non-nil block processor is provided.
-	blocks := make([]interfaces.ReadOnlySignedBeaconBlock, 0, req.Count)
+	blocks := make([]interfaces.ReadOnlySignedBeaconBlock, 0, sliceCap)
 	process := func(blk interfaces.ReadOnlySignedBeaconBlock) error {
 		blocks = append(blocks, blk)
 		if blockProcessor != nil {
```

### changelog/pvl-fix-16223.md
```diff
@@ -0,0 +1,3 @@
+### Changed
+
+- Added some defensive checks to prevent overflows in block batch requests.
```
