# [?] Fix panic on StopTracking

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-28
Source: https://github.com/celo-org/celo-blockchain/commit/35b3d7e438fe1ea9383b131babd21a26608c29a0
Type: security-commit

## Details
Fix panic on StopTracking

## Patch
### test/tracker.go
```diff
@@ -197,6 +197,9 @@ func (tr *Tracker) StopTracking() error {
 	tr.sub.Unsubscribe()
 	close(tr.stopCh)
 	tr.wg.Wait()
+	// Set this to nil to mark the tracker as stopped. This must be done after
+	// waiting for wg, to avoid a data race in trackTransactions.
+	tr.sub = nil
 	tr.wg = sync.WaitGroup{}
 	return nil
 }
```
