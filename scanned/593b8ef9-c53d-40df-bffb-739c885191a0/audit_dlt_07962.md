# [?] Fix panic with queue usage after Close (#1993)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2022-09-14
Source: https://github.com/ava-labs/avalanchego/commit/4cc1ed021e07a1dba8561e9283c071bcf07b1b5b
Type: security-commit

## Details
Fix panic with queue usage after Close (#1993)

## Patch
### network/peer/message_queue.go
```diff
@@ -157,7 +157,7 @@ func (q *throttledMessageQueue) PopNow() (message.OutboundMessage, bool) {
 	q.cond.L.Lock()
 	defer q.cond.L.Unlock()
 
-	if q.queue.Len() == 0 {
+	if q.closed || q.queue.Len() == 0 {
 		// There isn't a message
 		return nil, false
 	}
@@ -176,6 +176,10 @@ func (q *throttledMessageQueue) Close() {
 	q.cond.L.Lock()
 	defer q.cond.L.Unlock()
 
+	if q.closed {
+		return
+	}
+
 	q.closed = true
 
 	for q.queue.Len() > 0 {
```
