# [?] go/runtime/txpool: Fix data race

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-10-31
Source: https://github.com/oasisprotocol/oasis-core/commit/c3356715939de8df5a2cd6c49797ef1046bd86c0
Type: security-commit

## Details
go/runtime/txpool: Fix data race

## Patch
### go/runtime/txpool/main_queue.go
```diff
@@ -62,6 +62,14 @@ func newMainQueue(capacity int) *mainQueue {
 	}
 }
 
+// Size returns the current number of transactions in the queue.
+func (q *mainQueue) Size() int {
+	q.mu.Lock()
+	defer q.mu.Unlock()
+
+	return q.scheduler.size()
+}
+
 // GetSchedulingSuggestion implements UsableTransactionSource.
 func (q *mainQueue) GetSchedulingSuggestion(limit int) []*TxQueueMeta {
 	q.mu.Lock()
```

### go/runtime/txpool/txpool.go
```diff
@@ -376,7 +376,7 @@ func (t *txPool) HandleTxsUsed(hashes []hash.Hash) {
 		q.HandleTxsUsed(hashes)
 	}
 
-	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.scheduler.size()))
+	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.Size()))
 	localQueueSize.With(t.getMetricLabels()).Set(float64(t.localQueue.size()))
 }
 
@@ -651,7 +651,7 @@ func (t *txPool) checkTxBatch(ctx context.Context) error {
 		t.checkTxNotifier.Broadcast(newTxs)
 	}
 
-	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.scheduler.size()))
+	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.Size()))
 	localQueueSize.With(t.getMetricLabels()).Set(float64(t.localQueue.size()))
 
 	return nil
@@ -868,7 +868,7 @@ func (t *txPool) recheck() {
 			results = append(results, notifyCh)
 		}
 	}
-	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.scheduler.size()))
+	mainQueueSize.With(t.getMetricLabels()).Set(float64(t.mainQueue.Size()))
 	localQueueSize.With(t.getMetricLabels()).Set(float64(t.localQueue.size()))
 
 	if len(pcts) == 0 {
```
