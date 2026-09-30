# [?] eth/downloader: fix race condition in tests (#22140)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-01-09
Source: https://github.com/celo-org/celo-blockchain/commit/89030ec0b442a08fb82d4452f3132ab1602b8182
Type: security-commit

## Details
eth/downloader: fix race condition in tests (#22140)

* downloader: fix race condition in tests

* eth/downloader: fix race condition in tests

* Revert "downloader: fix race condition in tests"

This reverts commit 108033ebc6985de83791d375b6e6647a77d28d5a.

## Patch
### eth/downloader/downloader_test.go
```diff
@@ -584,14 +584,15 @@ func testThrottling(t *testing.T, protocol uint, mode SyncMode) {
 			time.Sleep(25 * time.Millisecond)
 
 			tester.lock.Lock()
+			tester.downloader.queue.lock.Lock()
+			tester.downloader.queue.resultCache.lock.Lock()
 			{
-				tester.downloader.queue.resultCache.lock.Lock()
 				cached = tester.downloader.queue.resultCache.countCompleted()
-				tester.downloader.queue.resultCache.lock.Unlock()
 				frozen = int(atomic.LoadUint32(&blocked))
 				retrieved = len(tester.ownBlocks)
-
 			}
+			tester.downloader.queue.resultCache.lock.Unlock()
+			tester.downloader.queue.lock.Unlock()
 			tester.lock.Unlock()
 
 			if cached == blockCacheMaxItems ||
```
