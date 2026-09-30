# [?] testing: fix random data race in TestAppAccountDataStorage (#3315)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-12-15
Source: https://github.com/algorand/go-algorand/commit/de7fe4538af68a18d1a4963be1ea6b932649f579
Type: security-commit

## Details
testing: fix random data race in TestAppAccountDataStorage (#3315)

fix random data race in unit test

## Patch
### ledger/applications_test.go
```diff
@@ -39,7 +39,18 @@ func commitRound(offset uint64, dbRound basics.Round, l *Ledger) {
 	l.trackers.mu.Unlock()
 
 	l.trackers.scheduleCommit(l.Latest(), l.Latest()-(dbRound+basics.Round(offset)))
-	l.trackers.waitAccountsWriting()
+	// wait for the operation to complete. Once it does complete, the tr.lastFlushTime is going to be updated, so we can
+	// use that as an indicator.
+	for {
+		l.trackers.mu.Lock()
+		isDone := (!l.trackers.lastFlushTime.IsZero()) && (len(l.trackers.deferredCommits) == 0)
+		l.trackers.mu.Unlock()
+		if isDone {
+			break
+		}
+		time.Sleep(time.Millisecond)
+
+	}
 }
 
 // test ensures that
```
