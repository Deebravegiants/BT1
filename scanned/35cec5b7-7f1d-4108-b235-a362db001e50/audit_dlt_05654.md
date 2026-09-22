# [?] Fix makeslice panic in blob versioned-hash filtering for duplicate commitments (#17199)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-17
Source: https://github.com/OffchainLabs/prysm/commit/5744c60727b5b509f6ed65dd4a136ba0a98863e3
Type: security-commit

## Details
Fix makeslice panic in blob versioned-hash filtering for duplicate commitments (#17199)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

`GET /eth/v1/beacon/blobs/{block_id}?versioned_hashes=<vh>` panics with
`runtime error: makeslice: cap out of range` when a requested versioned
hash
matches a KZG commitment that appears more than once in the target block
(legal per consensus rules — e.g. mainnet slot 8626186 carries the same
commitment three times). net/http recovers the panic per-request, so the
node
survives, but every such request aborts with a connection reset and a
panic
stack in the logs. Remotely triggerable on any node whose block DB
contains a
duplicate-commitment block: hash matching runs before any blob-storage
access, so blob pruning does not prevent it.

Root cause, in `resolveBlobsContext`
(`beacon-chain/rpc/lookup/blocker.go`):
requested hashes are deduplicated into a set, but `indices` receives one
entry per *matching commitment*. The missing-hash detection then
compares
raw counts:

    if len(indices) != len(cfg.VersionedHashes) {
missingHashes := make([]string, 0,
len(cfg.VersionedHashes)-len(indices)) // negative cap → panic

One requested hash matching N≥2 duplicate commitments makes the capacity
negative. The same count heuristic causes two more defects:

- A client repeating a hash in the query gets a spurious 404 with an
empty
`missing:` list, even though the hash is in the block (the handler does
not
  deduplicate query values).
- Duplicate matches can make the counts line up and mask a genuinely
missing
hash: requesting `[vh(A), vh(B)]` against a block with commitments `[A,
A]`
  returns 200 with both copies of A and no B.

The fix accounts for found/missing hashes on unique hash sets: the
request
fails iff some unique requested hash matched no commitment.
Duplicate-matching
commitments still contribute one index per occurrence, since sidecars
are
position-indexed objects, and the existing block-order filter semantics
are
preserved. Error message wording is unchanged; its counts now refer to
unique
hashes.

**Which issue(s) does this PR fix?**

None filed (small bug fix per the contribution guidelines).

**Other notes for review**

- Introduced by #15610 (`7e32bbc199`); reproduced against v7.1.7.
- The deprecated `/eth/v1/beacon/blob_sidecars/{block_id}` endpoint is
not
  affected (it only parses `indices`), but the internal
  `BlobSidecars`/`resolveBlobsContext` lookup path accepts
  `WithVersionedHashes` and is fixed for all callers.

**Testing plan**

New regression test `TestResolveBlobsContext_DuplicateCommitments`
exercises
the conversion directly (no storage needed — the panic precedes storage
access). Against the unfixed code, the first subtest reproduces the
exact
`makeslice: cap out of range` panic, and the spurious-404 /
masked-missing-hash
subtests fail. `go test ./beacon-chain/rpc/lookup/
./beacon-chain/rpc/eth/blob/`
passes.

Live repro (any node serving a block with duplicated commitments):
`curl
"$NODE/eth/v1/beacon/blobs/8626186?versioned_hashes=0x01c7011435804298c2e816d32e51791eacf8921494a317d54f029a4d4b9823a7"`

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>
Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

### beacon-chain/rpc/lookup/blocker.go
```diff
@@ -300,15 +300,17 @@ func (p *BeaconDbBlocker) resolveBlobsContext(ctx context.Context, id string, op
 	// Convert versioned hashes to indices if provided
 	indices := cfg.Indices
 	if len(cfg.VersionedHashes) > 0 {
-		// Build a map of requested versioned hashes for fast lookup and tracking
-		requestedHashes := make(map[string]bool)
+		// Build a map of requested versioned hashes for fast lookup and tracking.
+		// Accounting is on unique hashes: a block may carry the same commitment
+		// at multiple indices, and a request may repeat a hash.
+		requestedHashes := make(map[string]bool, len(cfg.VersionedHashes))
 		for _, versionedHash := range cfg.VersionedHashes {
 			requestedHashes[string(versionedHash)] = true
 		}
 
 		// Create indices array and track which hashes we found
-		indices = make([]int, 0, len(cfg.VersionedHashes))
-		foundHashes := make(map[string]bool)
+		indices = make([]int, 0, len(commitments))
+		foundHashes := make(map[string]bool, len(requestedHashes))
 
 		for i, commitment := range commitments {
 			versionedHash := primitives.ConvertKzgCommitmentToVersionedHash(commitment)
@@ -320,18 +322,21 @@ func (p *BeaconDbBlocker) resolveBlobsContext(ctx context.Context, id string, op
 		}
 
 		// Check if all requested hashes were found
-		if len(indices) != len(cfg.VersionedHashes) {
-			// Collect missing hashes
-			missingHashes := make([]string, 0, len(cfg.VersionedHashes)-len(indices))
+		if len(foundHashes) != len(requestedHashes) {
+			// Collect missing hashes in request order, reporting each hash once
+			missingHashes := make([]string, 0, len(requestedHashes)-len(foundHashes))
+			reported := make(map[string]bool, len(requestedHashes))
 			for _, requestedHash := range cfg.VersionedHashes {
-				if !foundHashes[string(requestedHash)] {
+				hashStr := string(requestedHash)
+				if !foundHashes[hashStr] && !reported[hashStr] {
 					missingHashes = append(missingHashes, hexutil.Encode(requestedHash))
+					reported[hashStr] = true
 				}
 			}
 
 			// Create detailed error message
-			errMsg := fmt.Sprintf("versioned hash(es) not found in block (requested %d hashes, found %d, missing: %v)",
-				len(cfg.VersionedHashes), len(indices), missingHashes)
+			errMsg := fmt.Sprintf("versioned hash(es) not found in block (requested %d unique hashes, found %d, missing: %v)",
+				len(requestedHashes), len(foundHashes), missingHashes)
 
 			return nil, &core.RpcError{Err: errors.New(errMsg), Reason: core.NotFound}
 		}
```

### beacon-chain/rpc/lookup/blocker_test.go
```diff
@@ -5,6 +5,7 @@ import (
 	"math"
 	"net/http"
 	"reflect"
+	"strings"
 	"testing"
 	"time"
 
@@ -877,7 +878,7 @@ func TestBlobs_CommitmentOrdering(t *testing.T) {
 		require.NotNil(t, rpcErr)
 		require.Equal(t, core.ErrorReason(core.NotFound), rpcErr.Reason)
 		require.StringContains(t, "versioned hash(es) not found in block", rpcErr.Err.Error())
-		require.StringContains(t, "requested 1 hashes, found 0", rpcErr.Err.Error())
+		require.StringContains(t, "requested 1 unique hashes, found 0", rpcErr.Err.Error())
 		require.StringContains(t, "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", rpcErr.Err.Error())
 	})
 
@@ -897,13 +898,78 @@ func TestBlobs_CommitmentOrdering(t *testing.T) {
 		require.NotNil(t, rpcErr)
 		require.Equal(t, core.ErrorReason(core.NotFound), rpcErr.Reason)
 		require.StringContains(t, "versioned hash(es) not found in block", rpcErr.Err.Error())
-		require.StringContains(t, "requested 3 hashes, found 1", rpcErr.Err.Error())
+		require.StringContains(t, "requested 3 unique hashes, found 1", rpcErr.Err.Error())
 		// Check that both missing hashes are reported
 		require.StringContains(t, "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", rpcErr.Err.Error())
 		require.StringContains(t, "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", rpcErr.Err.Error())
 	})
 }
 
+// TestResolveBlobsContext_DuplicateCommitments covers versioned-hash filtering
+// against a block that carries the same KZG commitment at multiple indices
+// (legal per consensus rules), as well as repeated hashes in the request.
+// Hash-to-index conversion happens before any blob storage access, so these
+// tests exercise resolveBlobsContext directly with only a block DB.
+func TestResolveBlobsContext_DuplicateCommitments(t *testing.T) {
+	params.SetupTestConfigCleanup(t)
+	cfg := params.BeaconConfig().Copy()
+	cfg.DenebForkEpoch = 1
+	cfg.FuluForkEpoch = primitives.Epoch(math.MaxUint64)
+	params.OverrideBeaconConfig(cfg)
+
+	db := testDB.SetupDB(t)
+	ctx := t.Context()
+
+	// Deneb block with the same commitment at indices 0 and 1.
+	commitment := bytesutil.PadTo([]byte("duplicate-commitment"), 48)
+	blk := util.NewBeaconBlockDeneb()
+	blk.Block.Slot = util.SlotAtEpoch(t, cfg.DenebForkEpoch)
+	blk.Block.Body.BlobKzgCommitments = [][]byte{commitment, commitment}
+	util.SaveBlock(t, ctx, db, blk)
+	root, err := blk.Block.HashTreeRoot()
+	require.NoError(t, err)
+	blockID := hexutil.Encode(root[:])
+
+	blocker := &BeaconDbBlocker{BeaconDB: db}
+
+	dupHash := primitives.ConvertKzgCommitmentToVersionedHash(commitment)
+	missingHash := make([]byte, 32)
+	for i := range missingHash {
+		missingHash[i] = 0xFF
+	}
+
+	t.Run("hash matching duplicate commitments resolves all indices", func(t *testing.T) {
+		bctx, rpcErr := blocker.resolveBlobsContext(ctx, blockID, options.WithVersionedHashes([][]byte{dupHash[:]}))
+		require.IsNil(t, rpcErr)
+		require.DeepEqual(t, []int{0, 1}, bctx.indices)
+	})
+
+	t.Run("repeated request hashes resolve without error", func(t *testing.T) {
+		requestedHashes := [][]byte{dupHash[:], dupHash[:], dupHash[:]}
+		bctx, rpcErr := blocker.resolveBlobsContext(ctx, blockID, options.WithVersionedHashes(requestedHashes))
+		require.IsNil(t, rpcErr)
+		require.DeepEqual(t, []int{0, 1}, bctx.indices)
+	})
+
+	t.Run("duplicate matches do not mask a missing hash", func(t *testing.T) {
+		requestedHashes := [][]byte{dupHash[:], missingHash}
+		_, rpcErr := blocker.resolveBlobsContext(ctx, blockID, options.WithVersionedHashes(requestedHashes))
+		require.NotNil(t, rpcErr)
+		require.Equal(t, core.ErrorReason(core.NotFound), rpcErr.Reason)
+		require.StringContains(t, "requested 2 unique hashes, found 1", rpcErr.Err.Error())
+		require.StringContains(t, hexutil.Encode(missingHash), rpcErr.Err.Error())
+	})
+
+	t.Run("repeated missing hash is reported once", func(t *testing.T) {
+		requestedHashes := [][]byte{missingHash, missingHash}
+		_, rpcErr := blocker.resolveBlobsContext(ctx, blockID, options.WithVersionedHashes(requestedHashes))
+		require.NotNil(t, rpcErr)
+		require.Equal(t, core.ErrorReason(core.NotFound), rpcErr.Reason)
+		require.StringContains(t, "requested 1 unique hashes, found 0", rpcErr.Err.Error())
+		require.Equal(t, 1, strings.Count(rpcErr.Err.Error(), hexutil.Encode(missingHash)))
+	})
+}
+
 func TestGetDataColumns(t *testing.T) {
 	const (
 		blobCount     = 4
```

### changelog/Tristan-Wilson_fix-versioned-hash-duplicate-commitments.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix a panic in `GET /eth/v1/beacon/blobs/{block_id}` when a `versioned_hashes` filter matches a commitment that appears more than once in the block.
```
