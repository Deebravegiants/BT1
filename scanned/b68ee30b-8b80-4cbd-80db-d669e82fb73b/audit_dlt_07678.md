# [?] Fix race condition when closing flusher (#14258)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-21
Source: https://github.com/erigontech/erigon/commit/cc802524c4b9162234dc5f8f68d8d1e8e74e1cc7
Type: security-commit

## Details
Fix race condition when closing flusher (#14258)

Co-authored-by: antonis19 <antonis19@users.noreply.github.com>

## Patch
### erigon-lib/kv/mdbx/kv_mdbx.go
```diff
@@ -87,7 +87,7 @@ func (flusher *PeriodicFlusher) Close() {
 	if flusher.ticker != nil {
 		flusher.ticker.Stop() // Stop the ticker
 	}
-	flusher.quitFlushingChan <- struct{}{} // signal quit
+	close(flusher.quitFlushingChan) //  close channel to signal quit
 }
 
 func (flusher *PeriodicFlusher) FlushInBackground(ctx context.Context) {
@@ -97,13 +97,14 @@ func (flusher *PeriodicFlusher) FlushInBackground(ctx context.Context) {
 			if err := flusher.env.Sync(true, false); err != nil {
 				flusher.opts.log.Error("Error during periodic mdbx sync", "err", err, "dbName", flusher.opts.label)
 			}
-		case <-flusher.quitFlushingChan:
-			return
+		case _, ok := <-flusher.quitFlushingChan:
+			if !ok {
+				return
+			}
 		case <-ctx.Done():
 			// here the flusher is not closed explicitly from outside,
 			// so we must close it from within
 			flusher.ticker.Stop()
-			flusher.closed.CompareAndSwap(false, true)
 			return
 		}
 	}
```
