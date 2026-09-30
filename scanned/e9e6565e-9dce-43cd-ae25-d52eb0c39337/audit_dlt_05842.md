# [?] fix(index): avoid deadlock on close (#12950)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2025-03-14
Source: https://github.com/filecoin-project/lotus/commit/c1e5f5ddf664cdfd5c5ad63ea1156f3ceefc7257
Type: security-commit

## Details
fix(index): avoid deadlock on close (#12950)

We can't hold the write lock while waiting on close because isClosed was
taking the read lock (and called while closing).

Instead, I just got rid of the locks entirely. Now, we just check the
context. Really, I'm not sure why we even have such an "is closed"
check. I _think_ what we actually want is to lock to prevent closing
until we've finished all atomic operations, but that's a larger change
and I don't have enough understanding of this code to easily make that
change.

## Patch
### chain/index/indexer.go
```diff
@@ -82,9 +82,6 @@ type SqliteIndexer struct {
 
 	started bool
 
-	closeLk sync.RWMutex
-	closed  bool
-
 	// ensures writes are serialized so backfilling does not race with index updates
 	writerLk sync.Mutex
 }
@@ -157,19 +154,10 @@ func (si *SqliteIndexer) buildExecutedMessagesLoader(rf RecomputeTipSetStateFunc
 }
 
 func (si *SqliteIndexer) Close() error {
-	si.closeLk.Lock()
-	defer si.closeLk.Unlock()
-	if si.closed {
-		return nil
-	}
-	si.closed = true
-
-	if si.db == nil {
-		return nil
-	}
 	si.cancel()
 	si.wg.Wait()
 
+	// Close is idempotent, it doesn't hurt to call it multiple times.
 	if err := si.db.Close(); err != nil {
 		return xerrors.Errorf("failed to close db: %w", err)
 	}
@@ -409,9 +397,7 @@ func (si *SqliteIndexer) Revert(ctx context.Context, from, to *types.TipSet) err
 }
 
 func (si *SqliteIndexer) isClosed() bool {
-	si.closeLk.RLock()
-	defer si.closeLk.RUnlock()
-	return si.closed
+	return si.ctx.Err() != nil
 }
 
 func (si *SqliteIndexer) setExecutedMessagesLoaderFunc(f emsLoaderFunc) {
```
