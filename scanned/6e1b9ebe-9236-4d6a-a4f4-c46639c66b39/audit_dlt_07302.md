# [?] Fix a data race in app tests (#3269)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-12-02
Source: https://github.com/algorand/go-algorand/commit/6657c2b8cf6289d25bc789d6d147e47b068eb40c
Type: security-commit

## Details
Fix a data race in app tests (#3269)

## Summary

A test helper function `commitRound` accessed `l.trackers.lastFlushTime` without taking a lock. Fixed.

## Test Plan

```
go test ./ledger -run TestAppEmpty -race -count=50
ok      github.com/algorand/go-algorand/ledger  4.078s
```

## Patch
### ledger/applications_test.go
```diff
@@ -34,7 +34,10 @@ import (
 )
 
 func commitRound(offset uint64, dbRound basics.Round, l *Ledger) {
+	l.trackers.mu.Lock()
 	l.trackers.lastFlushTime = time.Time{}
+	l.trackers.mu.Unlock()
+
 	l.trackers.scheduleCommit(l.Latest(), l.Latest()-(dbRound+basics.Round(offset)))
 	l.trackers.waitAccountsWriting()
 }
```
