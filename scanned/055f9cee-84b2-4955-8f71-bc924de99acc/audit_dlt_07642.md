# [?] eth/downloader: fix possible data race by inconsistent field protection (#20690)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-02-25
Source: https://github.com/ethereum/go-ethereum/commit/2a5ed1a1d3920a8a81aa5dfff21b148ee4f1107e
Type: security-commit

## Details
eth/downloader: fix possible data race by inconsistent field protection (#20690)

## Patch
### eth/downloader/queue.go
```diff
@@ -564,26 +564,29 @@ func (q *queue) reserveHeaders(p *peerConnection, count int, taskPool map[common
 
 // CancelHeaders aborts a fetch request, returning all pending skeleton indexes to the queue.
 func (q *queue) CancelHeaders(request *fetchRequest) {
+	q.lock.Lock()
+	defer q.lock.Unlock()
 	q.cancel(request, q.headerTaskQueue, q.headerPendPool)
 }
 
 // CancelBodies aborts a body fetch request, returning all pending headers to the
 // task queue.
 func (q *queue) CancelBodies(request *fetchRequest) {
+	q.lock.Lock()
+	defer q.lock.Unlock()
 	q.cancel(request, q.blockTaskQueue, q.blockPendPool)
 }
 
 // CancelReceipts aborts a body fetch request, returning all pending headers to
 // the task queue.
 func (q *queue) CancelReceipts(request *fetchRequest) {
+	q.lock.Lock()
+	defer q.lock.Unlock()
 	q.cancel(request, q.receiptTaskQueue, q.receiptPendPool)
 }
 
 // Cancel aborts a fetch request, returning all pending hashes to the task queue.
 func (q *queue) cancel(request *fetchRequest, taskQueue *prque.Prque, pendPool map[string]*fetchRequest) {
-	q.lock.Lock()
-	defer q.lock.Unlock()
-
 	if request.From > 0 {
 		taskQueue.Push(request.From, -int64(request.From))
 	}
```
