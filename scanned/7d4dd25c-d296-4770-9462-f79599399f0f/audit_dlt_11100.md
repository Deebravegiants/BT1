# [?] fix(tx-submitter): prevent restart panic caused by sealed batch indices holes

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2026-06-11
Source: https://github.com/morph-l2/morph/commit/8d95e4b7e82e6af0ccbecf506dcc4be06896ec9b
Type: security-commit

## Details
fix(tx-submitter): prevent restart panic caused by sealed batch indices holes

Finalize cleanup deleted only a single batch index, so when the finalize
target jumped past batches finalized by other submitters, the persisted
sealed batch indices snapshot was left with holes. On restart,
LoadAllSealedBatchesAndHeader assumed contiguous indices and dereferenced
a nil parent batch (SIGSEGV at batch_storage.go:146), crash-looping the
service.

- load path: sort indices, verify contiguity and nil-check the parent
  batch, returning an error so the existing self-heal path rebuilds from
  the rollup contract instead of panicking
- finalize cleanup: replace single-index Delete with range-based
  DeleteUntil so surviving indices always form a contiguous window (also
  reclaims previously leaked header keys)
- storage: add atomic WriteBatch to SealedBatchKV and persist batch
  data + header + indices in one write; indices update errors are no
  longer swallowed

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### common/batch/batch_cache.go
```diff
@@ -752,13 +752,11 @@ func (bc *BatchCache) SealBatch(sequencerSets []byte, blockTimestamp uint64, rep
 	copy(batchHeaderCopy, batchHeader)
 	bc.sealedBatchHeaders[batchIndex] = &batchHeaderCopy
 
-	err = bc.batchStorage.StoreSealedBatch(batchIndex, sealedBatch)
+	// Persist batch data, header and indices in one atomic write so the stored
+	// snapshot can never be partially updated.
+	err = bc.batchStorage.StoreSealedBatchAndHeader(batchIndex, sealedBatch, &batchHeaderCopy)
 	if err != nil {
-		log.Error("failed to store sealed batch", "err", err)
-	}
-	err = bc.batchStorage.StoreSealedBatchHeader(batchIndex, &batchHeaderCopy)
-	if err != nil {
-		log.Error("failed to store sealed batch header", "err", err)
+		log.Error("failed to store sealed batch and header", "batch_index", batchIndex, "err", err)
 	}
 	// Update parent batch information for next batch
 	bc.parentBatchHeader = &batchHeaderCopy
@@ -1258,6 +1256,28 @@ func (bc *BatchCache) Delete(batchIndex uint64) error {
 	return nil
 }
 
+// DeleteUntil removes every sealed batch and header with index <= maxIndex from
+// both the in-memory maps and persistent storage. Finalize cleanup must use this
+// range-based form: the finalize target can jump (multiple submitters, several
+// batches finalized at once), so deleting a single index leaves stale lower
+// indices behind and punches holes into the persisted indices snapshot, which
+// breaks the contiguity assumption of the startup load path.
+func (bc *BatchCache) DeleteUntil(maxIndex uint64) error {
+	bc.mu.Lock()
+	defer bc.mu.Unlock()
+	for idx := range bc.sealedBatches {
+		if idx <= maxIndex {
+			delete(bc.sealedBatches, idx)
+		}
+	}
+	for idx := range bc.sealedBatchHeaders {
+		if idx <= maxIndex {
+			delete(bc.sealedBatchHeaders, idx)
+		}
+	}
+	return bc.batchStorage.DeleteSealedBatchesUpTo(maxIndex)
+}
+
 // logSealedBatch logs the details of the sealed batch for debugging purposes.
 func (bc *BatchCache) logSealedBatch(batchHeader BatchHeaderBytes, batchHash common.Hash, blockCount uint16, blobCount int) {
 	version, err := batchHeader.Version()
```

### common/batch/batch_storage.go
```diff
@@ -6,6 +6,7 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"sort"
 	"sync"
 
 	"github.com/morph-l2/go-ethereum/eth"
@@ -34,7 +35,9 @@ func NewBatchStorage(db SealedBatchKV) *BatchStorage {
 }
 
 // StoreSealedBatch stores a single sealed batch to LevelDB
-// Uses JSON encoding for serialization
+// Uses JSON encoding for serialization.
+// Batch data and the indices snapshot are written in one atomic batch so they
+// can never get out of sync; indices update failures are no longer swallowed.
 func (s *BatchStorage) StoreSealedBatch(batchIndex uint64, batch *eth.RPCRollupBatch) error {
 	s.mu.Lock()
 	defer s.mu.Unlock()
@@ -45,18 +48,45 @@ func (s *BatchStorage) StoreSealedBatch(batchIndex uint64, batch *eth.RPCRollupB
 		return fmt.Errorf("failed to marshal sealed batch %d: %w", batchIndex, err)
 	}
 
-	// Store batch data
-	key := encodeBatchKey(batchIndex)
-	if err := s.db.PutBytes(key, encoded); err != nil {
+	encodedIndices, err := s.indicesSnapshotWith(batchIndex)
+	if err != nil {
+		return fmt.Errorf("failed to update batch indices for batch %d: %w", batchIndex, err)
+	}
+
+	puts := []KVPair{
+		{Key: encodeBatchKey(batchIndex), Value: encoded},
+		{Key: []byte(SealedBatchIndicesKey), Value: encodedIndices},
+	}
+	if err := s.db.WriteBatch(puts, nil); err != nil {
 		return fmt.Errorf("failed to store sealed batch %d: %w", batchIndex, err)
 	}
+	return nil
+}
 
-	// Update indices list
-	if err = s.updateBatchIndices(batchIndex, true); err != nil {
-		log.Warn("Failed to update batch indices", "batch_index", batchIndex, "error", err)
-		// Don't fail the operation if indices update fails
+// StoreSealedBatchAndHeader stores the sealed batch, its header and the updated
+// indices snapshot in a single atomic write.
+func (s *BatchStorage) StoreSealedBatchAndHeader(batchIndex uint64, batch *eth.RPCRollupBatch, header *BatchHeaderBytes) error {
+	s.mu.Lock()
+	defer s.mu.Unlock()
+
+	encoded, err := json.Marshal(batch)
+	if err != nil {
+		return fmt.Errorf("failed to marshal sealed batch %d: %w", batchIndex, err)
+	}
+
+	encodedIndices, err := s.indicesSnapshotWith(batchIndex)
+	if err != nil {
+		return fmt.Errorf("failed to update batch indices for batch %d: %w", batchIndex, err)
 	}
 
+	puts := []KVPair{
+		{Key: encodeBatchKey(batchIndex), Value: encoded},
+		{Key: encodeBatchHeaderKey(batchIndex), Value: header.Bytes()},
+		{Key: []byte(SealedBatchIndicesKey), Value: encodedIndices},
+	}
+	if err := s.db.WriteBatch(puts, nil); err != nil {
+		return fmt.Errorf("failed to store sealed batch and header %d: %w", batchIndex, err)
+	}
 	return nil
 }
 
@@ -132,12 +162,26 @@ func (s *BatchStorage) LoadAllSealedBatchesAndHeader() (map[uint64]*eth.RPCRollu
 	for i, idx := range indices {
 		batch, err := s.LoadSealedBatch(idx)
 		if err != nil {
-			log.Warn("Failed to load sealed batch, skipping",
+			log.Warn("Failed to load sealed batch, aborting",
 				"batch_index", idx, "error", err)
 			return nil, nil, nil, fmt.Errorf("failed to load batch: %w", err)
 		}
 		if i > 0 {
-			parentBatch := batches[idx-1]
+			// indices is sorted ascending; a hole means some middle batch was
+			// deleted (e.g. by a finalize confirmed while other submitters
+			// advanced the finalize index). Return an error so the caller can
+			// self-heal instead of dereferencing a missing parent batch.
+			prevIdx := indices[i-1]
+			if idx != prevIdx+1 {
+				log.Error("Sealed batch indices are not contiguous",
+					"prev_index", prevIdx, "batch_index", idx)
+				return nil, nil, nil, fmt.Errorf("sealed batch indices not contiguous: %d -> %d", prevIdx, idx)
+			}
+			parentBatch := batches[prevIdx]
+			if parentBatch == nil {
+				log.Error("Parent batch missing", "parent_index", prevIdx, "batch_index", idx)
+				return nil, nil, nil, fmt.Errorf("parent batch %d missing for batch %d", prevIdx, idx)
+			}
 			parentBatchHash, err := BatchHeaderBytes(batch.ParentBatchHeader).Hash()
 			if err != nil {
 				log.Error("Failed to load parent batch header", "batch_index", idx, "error", err)
@@ -179,31 +223,36 @@ func (s *BatchStorage) LoadAllSealedBatchesAndHeader() (map[uint64]*eth.RPCRollu
 	return batches, headers, indices, nil
 }
 
-// DeleteSealedBatch removes a sealed batch from LevelDB
+// DeleteSealedBatch removes a sealed batch (data + header) from LevelDB.
+// Data, header and the indices snapshot are removed in one atomic write;
+// indices update failures are no longer swallowed.
 func (s *BatchStorage) DeleteSealedBatch(batchIndex uint64) error {
 	s.mu.Lock()
 	defer s.mu.Unlock()
 
-	key := encodeBatchKey(batchIndex)
-	if err := s.db.Delete(key); err != nil {
-		return fmt.Errorf("failed to delete sealed batch %d: %w", batchIndex, err)
+	encodedIndices, err := s.indicesSnapshotWithout(batchIndex)
+	if err != nil {
+		return fmt.Errorf("failed to update batch indices for batch %d: %w", batchIndex, err)
 	}
 
-	// Update indices list
-	if err := s.updateBatchIndices(batchIndex, false); err != nil {
-		log.Warn("Failed to update batch indices after deletion",
-			"batch_index", batchIndex, "error", err)
-		// Don't fail the operation if indices update fails
+	puts := []KVPair{{Key: []byte(SealedBatchIndicesKey), Value: encodedIndices}}
+	deletes := [][]byte{encodeBatchKey(batchIndex), encodeBatchHeaderKey(batchIndex)}
+	if err := s.db.WriteBatch(puts, deletes); err != nil {
+		return fmt.Errorf("failed to delete sealed batch %d: %w", batchIndex, err)
 	}
-
 	return nil
 }
 
-func (s *BatchStorage) DeleteAllSealedBatches() error {
-	s.mu.RLock()
-	// Load batch indices
+// DeleteSealedBatchesUpTo removes every sealed batch (data + header) with
+// index <= maxIndex in a single atomic write. Range-based cleanup keeps the
+// surviving indices a contiguous window: single-index deletes punch holes when
+// the finalize target jumps (multiple submitters, finalizing several batches at
+// once), and such holes crash the startup load path.
+func (s *BatchStorage) DeleteSealedBatchesUpTo(maxIndex uint64) error {
+	s.mu.Lock()
+	defer s.mu.Unlock()
+
 	indices, err := s.loadBatchIndices()
-	s.mu.RUnlock()
 	if err != nil {
 		if isKVNotFound(err) {
 			// No batches stored yet
@@ -212,21 +261,51 @@ func (s *BatchStorage) DeleteAllSealedBatches() error {
 		return fmt.Errorf("failed to load batch indices: %w", err)
 	}
 
+	kept := make([]uint64, 0, len(indices))
+	var deletes [][]byte
 	for _, idx := range indices {
-		err = s.DeleteSealedBatch(idx)
-		if err != nil {
-			log.Error("Failed to delete sealed batch",
-				"batch_index", idx, "error", err)
-			return err
+		if idx <= maxIndex {
+			deletes = append(deletes, encodeBatchKey(idx), encodeBatchHeaderKey(idx))
+		} else {
+			kept = append(kept, idx)
 		}
-		err = s.DeleteSealedBatchHeader(idx)
-		if err != nil {
-			log.Error("Failed to delete sealed batch header",
-				"batch_index", idx, "error", err)
-			return err
+	}
+	if len(deletes) == 0 {
+		return nil
+	}
+
+	encodedIndices, err := json.Marshal(kept)
+	if err != nil {
+		return fmt.Errorf("failed to marshal batch indices: %w", err)
+	}
+	puts := []KVPair{{Key: []byte(SealedBatchIndicesKey), Value: encodedIndices}}
+	if err := s.db.WriteBatch(puts, deletes); err != nil {
+		return fmt.Errorf("failed to delete sealed batches up to %d: %w", maxIndex, err)
+	}
+	return nil
+}
+
+func (s *BatchStorage) DeleteAllSealedBatches() error {
+	s.mu.Lock()
+	defer s.mu.Unlock()
+
+	indices, err := s.loadBatchIndices()
+	if err != nil {
+		if isKVNotFound(err) {
+			// No batches stored yet
+			return nil
 		}
+		return fmt.Errorf("failed to load batch indices: %w", err)
 	}
 
+	deletes := make([][]byte, 0, len(indices)*2+1)
+	for _, idx := range indices {
+		deletes = append(deletes, encodeBatchKey(idx), encodeBatchHeaderKey(idx))
+	}
+	deletes = append(deletes, []byte(SealedBatchIndicesKey))
+	if err := s.db.WriteBatch(nil, deletes); err != nil {
+		return fmt.Errorf("failed to delete all sealed batches: %w", err)
+	}
 	return nil
 }
 
@@ -238,45 +317,52 @@ func encodeBatchKey(batchIndex uint64) []byte {
 	return key
 }
 
-// updateBatchIndices updates the list of stored batch indices
-// add: true to add index, false to remove
-func (s *BatchStorage) updateBatchIndices(batchIndex uint64, add bool) error {
+// indicesSnapshotWith returns the marshaled indices snapshot with batchIndex added.
+func (s *BatchStorage) indicesSnapshotWith(batchIndex uint64) ([]byte, error) {
 	indices, err := s.loadBatchIndices()
 	if err != nil {
 		if isKVNotFound(err) {
 			indices = []uint64{}
 		} else {
-			return err
+			return nil, err
 		}
 	}
 
-	if add {
-		// Add index if not already present
-		found := false
-		for _, idx := range indices {
-			if idx == batchIndex {
-				found = true
-				break
-			}
-		}
-		if !found {
-			indices = append(indices, batchIndex)
+	found := false
+	for _, idx := range indices {
+		if idx == batchIndex {
+			found = true
+			break
 		}
-	} else {
-		// Remove index
-		newIndices := make([]uint64, 0, len(indices))
-		for _, idx := range indices {
-			if idx != batchIndex {
-				newIndices = append(newIndices, idx)
-			}
+	}
+	if !found {
+		indices = append(indices, batchIndex)
+		sort.Slice(indices, func(i, j int) bool { return indices[i] < indices[j] })
+	}
+	return json.Marshal(indices)
+}
+
+// indicesSnapshotWithout returns the marshaled indices snapshot with batchIndex removed.
+func (s *BatchStorage) indicesSnapshotWithout(batchIndex uint64) ([]byte, error) {
+	indices, err := s.loadBatchIndices()
+	if err != nil {
+		if isKVNotFound(err) {
+			indices = []uint64{}
+		} else {
+			return nil, err
 		}
-		indices = newIndices
 	}
 
-	return s.saveBatchIndices(indices)
+	newIndices := make([]uint64, 0, len(indices))
+	for _, idx := range indices {
+		if idx != batchIndex {
+			newIndices = append(newIndices, idx)
+		}
+	}
+	return json.Marshal(newIndices)
 }
 
-// loadBatchIndices loads the list of stored batch indices
+// loadBatchIndices loads the list of stored batch indices, sorted ascending.
 func (s *BatchStorage) loadBatchIndices() ([]uint64, error) {
 	encoded, err := s.db.GetBytes([]byte(SealedBatchIndicesKey))
 	if err != nil {
@@ -288,19 +374,11 @@ func (s *BatchStorage) loadBatchIndices() ([]uint64, error) {
 		return nil, fmt.Errorf("failed to unmarshal batch indices: %w", err)
 	}
 
+	// Keep ordering deterministic regardless of how the snapshot was produced.
+	sort.Slice(indices, func(i, j int) bool { return indices[i] < indices[j] })
 	return indices, nil
 }
 
-// saveBatchIndices saves the list of batch indices
-func (s *BatchStorage) saveBatchIndices(indices []uint64) error {
-	encoded, err := json.Marshal(indices)
-	if err != nil {
-		return fmt.Errorf("failed to marshal batch indices: %w", err)
-	}
-
-	return s.db.PutBytes([]byte(SealedBatchIndicesKey), encoded)
-}
-
 // StoreSealedBatchHeader stores a single sealed batch header to LevelDB
 func (s *BatchStorage) StoreSealedBatchHeader(batchIndex uint64, header *BatchHeaderBytes) error {
 	s.mu.Lock()
```

### common/batch/batch_storage_test.go
```diff
@@ -0,0 +1,168 @@
+package batch
+
+// Regression tests for the restart panic caused by holes in the persisted
+// sealed batch indices (nil pointer dereference at the parent batch hash check
+// in LoadAllSealedBatchesAndHeader). See .vscode/doing/submitter-issue.md.
+
+import (
+	"encoding/json"
+	"errors"
+	"testing"
+
+	"github.com/morph-l2/go-ethereum/common/hexutil"
+	"github.com/morph-l2/go-ethereum/eth"
+	"github.com/stretchr/testify/require"
+)
+
+// makeTestHeader builds a unique, valid V1 batch header (257 bytes, version byte = 1).
+func makeTestHeader(idx uint64) BatchHeaderBytes {
+	h := make(BatchHeaderBytes, expectedLengthV1)
+	h[0] = BatchHeaderVersion1
+	h[1] = byte(idx)
+	h[2] = byte(idx >> 8)
+	return h
+}
+
+// storeTestChain stores a chain of sealed batches whose parent headers link
+// consecutively, mirroring what SealBatch persists.
+func storeTestChain(t *testing.T, s *BatchStorage, indices []uint64) {
+	t.Helper()
+	for _, idx := range indices {
+		header := makeTestHeader(idx)
+		hash, err := header.Hash()
+		require.NoError(t, err)
+
+		parentHeader := makeTestHeader(idx - 1)
+		b := &eth.RPCRollupBatch{
+			Hash:              hash,
+			ParentBatchHeader: hexutil.Bytes(parentHeader),
+		}
+		require.NoError(t, s.StoreSealedBatchAndHeader(idx, b, &header))
+	}
+}
+
+func TestLoadAllSealedBatchesAndHeaderContiguous(t *testing.T) {
+	s := NewBatchStorage(openTestKV(t))
+	storeTestChain(t, s, []uint64{100, 101, 102, 103})
+
+	batches, headers, indices, err := s.LoadAllSealedBatchesAndHeader()
+	require.NoError(t, err)
+	require.Len(t, batches, 4)
+	require.Len(t, headers, 4)
+	require.Equal(t, []uint64{100, 101, 102, 103}, indices)
+}
+
+// A hole in the indices (middle batch deleted, as finalize cleanup used to do
+// with single-index deletes) must surface as an error so the caller can
+// self-heal, instead of panicking on a nil parent batch.
+func TestLoadAllSealedBatchesAndHeaderHoleReturnsError(t *testing.T) {
+	s := NewBatchStorage(openTestKV(t))
+	storeTestChain(t, s, []uint64{100, 101, 102, 103})
+	require.NoError(t, s.DeleteSealedBatch(102))
+
+	require.NotPanics(t, func() {
+		_, _, _, err := s.LoadAllSealedBatchesAndHeader()
+		require.Error(t, err)
+		require.Contains(t, err.Error(), "not contiguous")
+	})
+}
+
+func TestDeleteSealedBatchesUpTo(t *testing.T) {
+	s := NewBatchStorage(openTestKV(t))
+	storeTestChain(t, s, []uint64{100, 101, 102, 103, 104, 105})
+
+	require.NoError(t, s.DeleteSealedBatchesUpTo(103))
+
+	indices, err := s.loadBatchIndices()
+	require.NoError(t, err)
+	require.Equal(t, []uint64{104, 105}, indices)
+
+	for idx := uint64(100); idx <= 103; idx++ {
+		_, err := s.LoadSealedBatch(idx)
+		require.Error(t, err, "batch %d should be deleted", idx)
+		_, err = s.LoadSealedBatchHeader(idx)
+		require.Error(t, err, "header %d should be deleted", idx)
+	}
+	for idx := uint64(104); idx <= 105; idx++ {
+		_, err := s.LoadSealedBatch(idx)
+		require.NoError(t, err, "batch %d should survive", idx)
+		_, err = s.LoadSealedBatchHeader(idx)
+		require.NoError(t, err, "header %d should survive", idx)
+	}
+
+	// The surviving window stays loadable.
+	batches, headers, _, err := s.LoadAllSealedBatchesAndHeader()
+	require.NoError(t, err)
+	require.Len(t, batches, 2)
+	require.Len(t, headers, 2)
+
+	// Deleting below the window is a no-op.
+	require.NoError(t, s.DeleteSealedBatchesUpTo(50))
+	indices, err = s.loadBatchIndices()
+	require.NoError(t, err)
+	require.Equal(t, []uint64{104, 105}, indices)
+}
+
+// Legacy snapshots may have been persisted unsorted; loading must normalize.
+func TestLoadBatchIndicesSortsLegacySnapshot(t *testing.T) {
+	kv := openTestKV(t)
+	s := NewBatchStorage(kv)
+
+	encoded, err := json.Marshal([]uint64{103, 100, 102, 101})
+	require.NoError(t, err)
+	require.NoError(t, kv.PutBytes([]byte(SealedBatchIndicesKey), encoded))
+
+	indices, err := s.loadBatchIndices()
+	require.NoError(t, err)
+	require.Equal(t, []uint64{100, 101, 102, 103}, indices)
+}
+
+func TestDeleteAllSealedBatches(t *testing.T) {
+	s := NewBatchStorage(openTestKV(t))
+	storeTestChain(t, s, []uint64{100, 101, 102})
+
+	require.NoError(t, s.DeleteAllSealedBatches())
+
+	_, err := s.loadBatchIndices()
+	require.True(t, isKVNotFound(err))
+	_, err = s.LoadSealedBatch(100)
+	require.Error(t, err)
+	_, err = s.LoadSealedBatchHeader(100)
+	require.Error(t, err)
+
+	// Idempotent on empty storage.
+	require.NoError(t, s.DeleteAllSealedBatches())
+}
+
+// failingIndicesKV simulates a KV whose indices key is unreadable; store/delete
+// must propagate the error instead of swallowing it.
+type failingIndicesKV struct {
+	SealedBatchKV
+}
+
+var errIndicesUnavailable = errors.New("indices unavailable")
+
+func (f *failingIndicesKV) GetBytes(key []byte) ([]byte, error) {
+	if string(key) == SealedBatchIndicesKey {
+		return nil, errIndicesUnavailable
+	}
+	return f.SealedBatchKV.GetBytes(key)
+}
+
+func TestStoreSealedBatchPropagatesIndicesError(t *testing.T) {
+	s := NewBatchStorage(&failingIndicesKV{SealedBatchKV: openTestKV(t)})
+
+	header := makeTestHeader(100)
+	hash, err := header.Hash()
+	require.NoError(t, err)
+	b := &eth.RPCRollupBatch{Hash: hash}
+
+	err = s.StoreSealedBatch(100, b)
+	require.ErrorIs(t, err, errIndicesUnavailable)
+
+	err = s.StoreSealedBatchAndHeader(100, b, &header)
+	require.ErrorIs(t, err, errIndicesUnavailable)
+
+	err = s.DeleteSealedBatch(100)
+	require.ErrorIs(t, err, errIndicesUnavailable)
+}
```

### common/batch/helpers_test.go
```diff
@@ -43,6 +43,17 @@ func (d *testLevelDB) Delete(key []byte) error {
 	return d.db.Delete(key, nil)
 }
 
+func (d *testLevelDB) WriteBatch(puts []KVPair, deletes [][]byte) error {
+	b := new(leveldb.Batch)
+	for _, kv := range puts {
+		b.Put(kv.Key, kv.Value)
+	}
+	for _, key := range deletes {
+		b.Delete(key)
+	}
+	return d.db.Write(b, nil)
+}
+
 func testLoop(ctx context.Context, d time.Duration, fn func()) {
 	ticker := time.NewTicker(d)
 	defer ticker.Stop()
```

### common/batch/interfaces.go
```diff
@@ -15,11 +15,21 @@ import (
 // ErrKeyNotFound is returned by SealedBatchKV implementations when a key is absent.
 var ErrKeyNotFound = errors.New("batch storage: key not found")
 
+// KVPair is a key/value entry applied as part of an atomic WriteBatch.
+type KVPair struct {
+	Key   []byte
+	Value []byte
+}
+
 // SealedBatchKV is a minimal key-value store used by BatchStorage.
 type SealedBatchKV interface {
 	GetBytes(key []byte) ([]byte, error)
 	PutBytes(key, val []byte) error
 	Delete(key []byte) error
+	// WriteBatch applies all puts and deletes as a single atomic write, so that
+	// batch data, batch header and the indices snapshot can never get out of sync
+	// with each other on crash or partial failure.
+	WriteBatch(puts []KVPair, deletes [][]byte) error
 }
 
 // L1HeaderClient is the L1 RPC surface required to recover batch headers from events.
```

### tx-submitter/db/db.go
```diff
@@ -5,6 +5,7 @@ import (
 	"strconv"
 	"sync"
 
+	"morph-l2/common/batch"
 	"morph-l2/tx-submitter/utils"
 
 	"github.com/morph-l2/go-ethereum/ethdb/leveldb"
@@ -90,6 +91,27 @@ func (d *Db) Delete(key []byte) error {
 	defer d.m.Unlock()
 	return d.db.Delete(key)
 }
+
+// WriteBatch applies all puts and deletes atomically in a single leveldb batch.
+func (d *Db) WriteBatch(puts []batch.KVPair, deletes [][]byte) error {
+	d.m.Lock()
+	defer d.m.Unlock()
+	b := d.db.NewBatch()
+	for _, kv := range puts {
+		if err := b.Put(kv.Key, kv.Value); err != nil {
+			return fmt.Errorf("failed to stage put in write batch: %w", err)
+		}
+	}
+	for _, key := range deletes {
+		if err := b.Delete(key); err != nil {
+			return fmt.Errorf("failed to stage delete in write batch: %w", err)
+		}
+	}
+	if err := b.Write(); err != nil {
+		return fmt.Errorf("failed to commit write batch: %w", err)
+	}
+	return nil
+}
 func (d *Db) Close() error {
 	return d.db.Close()
 }
```

### tx-submitter/services/rollup.go
```diff
@@ -809,8 +809,12 @@ func (r *Rollup) handleConfirmedTx(txRecord *types.TxRecord, tx *ethtypes.Transa
 			batchIndex := utils.ParseFBatchIndex(tx.Data())
 			if batchIndex > 0 {
 				if r.cfg.SealBatch {
-					if delErr := r.batchCache.Delete(batchIndex - 1); delErr != nil {
-						log.Error("failed to delete batch", "batch_index", batchIndex, "tx_hash", tx.Hash().String(), "error", delErr)
+					// Range-based cleanup: the finalize target can jump past batches
+					// finalized by other submitters, which this node never deletes.
+					// Deleting only batchIndex-1 would leave those behind and punch a
+					// hole into the persisted indices, crashing the next restart load.
+					if delErr := r.batchCache.DeleteUntil(batchIndex - 1); delErr != nil {
+						log.Error("failed to delete batches up to index", "batch_index", batchIndex-1, "tx_hash", tx.Hash().String(), "error", delErr)
 					}
 				} else {
 					r.batchCacheLegacy.Delete(batchIndex - 1)
```
