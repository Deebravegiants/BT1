# [?] eth/downloader: fix mutex regression causing panics on fail (#3591)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-01-20
Source: https://github.com/scroll-tech/go-ethereum/commit/ebc3d232f4b6c197d5dc5da2e1868d56b2096f1a
Type: security-commit

## Details
eth/downloader: fix mutex regression causing panics on fail (#3591)

## Patch
### eth/downloader/queue.go
```diff
@@ -1129,12 +1129,13 @@ func (q *queue) deliverNodeData(results []trie.SyncResult, callback func(int, bo
 		if err != nil {
 			q.stateSchedLock.Unlock()
 			callback(i, progressed, err)
+			return
 		}
 		if err = batch.Write(); err != nil {
 			q.stateSchedLock.Unlock()
 			callback(i, progressed, err)
+			return // TODO(karalabe): If a DB write fails (disk full), we ought to cancel the sync
 		}
-
 		// Item processing succeeded, release the lock (temporarily)
 		progressed = progressed || prog
 		q.stateSchedLock.Unlock()
```
