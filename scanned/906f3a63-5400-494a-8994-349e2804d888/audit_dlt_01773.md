# [?] Add lock around catchpointsMu to avoid race condition (#3944)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-05-03
Source: https://github.com/algorand/go-algorand/commit/cd4015a00c47e3a583ee239ce2ca1145dd73f213
Type: security-commit

## Details
Add lock around catchpointsMu to avoid race condition (#3944)

While upgrading to golang 1.17.9 a couple of race conditions have been detected during E2E tests.
This fixes catchpoint label assignment.

## Patch
### ledger/catchpointtracker.go
```diff
@@ -413,20 +413,18 @@ func (ct *catchpointTracker) postCommit(ctx context.Context, dcc *deferredCommit
 		}
 	}
 
+	ct.catchpointsMu.Lock()
+	ct.roundDigest = ct.roundDigest[dcc.offset:]
 	if dcc.isCatchpointRound && dcc.catchpointLabel != "" {
 		ct.lastCatchpointLabel = dcc.catchpointLabel
 	}
+	ct.catchpointsMu.Unlock()
+
 	dcc.updatingBalancesDuration = time.Since(dcc.flushTime)
 
 	if dcc.updateStats {
 		dcc.stats.MemoryUpdatesDuration = time.Duration(time.Now().UnixNano())
 	}
-
-	ct.catchpointsMu.Lock()
-
-	ct.roundDigest = ct.roundDigest[dcc.offset:]
-
-	ct.catchpointsMu.Unlock()
 }
 
 func (ct *catchpointTracker) postCommitUnlocked(ctx context.Context, dcc *deferredCommitContext) {
```
