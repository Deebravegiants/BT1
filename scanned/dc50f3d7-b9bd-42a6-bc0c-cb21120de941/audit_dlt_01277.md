# [?] fix 1-worker underflow; lower default batch size (#13734)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2024-03-14
Source: https://github.com/OffchainLabs/prysm/commit/9fcb9b86af651ed63d8ea5b8668491edd505c066
Type: security-commit

## Details
fix 1-worker underflow; lower default batch size (#13734)

* fix 1-worker underflow; lower default batch size

* adding test for single item in batcher

---------

Co-authored-by: Kasey Kirkham <kasey@users.noreply.github.com>

## Patch
### beacon-chain/sync/backfill/batcher.go
```diff
@@ -79,6 +79,10 @@ func (c *batchSequencer) update(b batch) {
 		// so we want to copy c to a, then on i=3, d to b, then on i=4 e to c.
 		c.seq[i-done] = c.seq[i]
 	}
+	if done == 1 && len(c.seq) == 1 {
+		c.seq[0] = c.batcher.beforeBatch(c.seq[0])
+		return
+	}
 	// Overwrite the moved batches with the next ones in the sequence.
 	// Continuing the example in the comment above, len(c.seq)==5, done=2, so i=3.
 	// We want to replace index 3 with the batch that should be processed after index 2,
```

### beacon-chain/sync/backfill/batcher_test.go
```diff
@@ -64,6 +64,35 @@ func TestBatcherBefore(t *testing.T) {
 	}
 }
 
+func TestBatchSingleItem(t *testing.T) {
+	var min, max, size primitives.Slot
+	// seqLen = 1 means just one worker
+	seqLen := 1
+	min = 0
+	max = 11235
+	size = 64
+	seq := newBatchSequencer(seqLen, min, max, size)
+	got, err := seq.sequence()
+	require.NoError(t, err)
+	require.Equal(t, 1, len(got))
+	b := got[0]
+
+	//  calling sequence again should give you the next (earlier) batch
+	seq.update(b.withState(batchImportComplete))
+	next, err := seq.sequence()
+	require.NoError(t, err)
+	require.Equal(t, 1, len(next))
+	require.Equal(t, b.end, next[0].end+size)
+
+	// should get the same batch again when update is called with an error
+	seq.update(next[0].withState(batchErrRetryable))
+	same, err := seq.sequence()
+	require.NoError(t, err)
+	require.Equal(t, 1, len(same))
+	require.Equal(t, next[0].begin, same[0].begin)
+	require.Equal(t, next[0].end, same[0].end)
+}
+
 func TestBatchSequencer(t *testing.T) {
 	var min, max, size primitives.Slot
 	seqLen := 8
```

### cmd/beacon-chain/sync/backfill/flags/flags.go
```diff
@@ -22,7 +22,7 @@ var (
 		Usage: "Number of blocks per backfill batch. " +
 			"A larger number will request more blocks at once from peers, but also consume more system memory to " +
 			"hold batches in memory during processing. This has a multiplicative effect with " + backfillWorkerCountName + ".",
-		Value: 64,
+		Value: 32,
 	}
 	// BackfillWorkerCount allows users to tune the number of concurrent backfill batches to download, to maximize
 	// network utilization at the cost of higher memory.
```
