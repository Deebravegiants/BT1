# [?] eth/downloader: fix timeout resurrection panic (#26652)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-02-09
Source: https://github.com/ethereum/go-ethereum/commit/3086c256c932dc6da26822a5ec130c2fba7e222e
Type: security-commit

## Details
eth/downloader: fix timeout resurrection panic (#26652)

* common/prque, eth/downloader: fix timeout resurrection panic

* common/prque: revert -1 hack for les, temporaryly!

## Patch
### eth/downloader/fetchers_concurrent.go
```diff
@@ -280,13 +280,14 @@ func (d *Downloader) concurrentFetch(queue typedQueue, beaconMode bool) error {
 			// overloading it further.
 			delete(pending, req.Peer)
 			stales[req.Peer] = req
-			delete(ordering, req)
 
-			timeouts.Pop()
+			timeouts.Pop() // Popping an item will reorder indices in `ordering`, delete after, otherwise will resurrect!
 			if timeouts.Size() > 0 {
 				_, exp := timeouts.Peek()
 				timeout.Reset(time.Until(time.Unix(0, -exp)))
 			}
+			delete(ordering, req)
+
 			// New timeout potentially set if there are more requests pending,
 			// reschedule the failed one to a free peer
 			fails := queue.unreserve(req.Peer)
```
