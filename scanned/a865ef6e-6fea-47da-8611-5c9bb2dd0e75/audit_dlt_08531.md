# [?] tests: fix data race in catchpoint tests (#6593)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2026-03-25
Source: https://github.com/algorand/go-algorand/commit/094ea6b25e84f0b8b66af847a54d4892b261aa5c
Type: security-commit

## Details
tests: fix data race in catchpoint tests (#6593)

## Patch
### ledger/catchpointfilewriter_test.go
```diff
@@ -860,8 +860,10 @@ func testCatchpointFlushRound(l *Ledger) (basics.Round, basics.Round) {
 	l.trackers.mu.Unlock()
 
 	r, _ := l.LatestCommitted()
+	l.trackerMu.Lock()
 	l.trackers.committedUpTo(r)
 	l.trackers.waitAccountsWriting()
+	l.trackerMu.Unlock()
 	return r, l.LatestTrackerCommitted()
 }
 
```
