# [?] go/runtime/client: Fix possible panic on shutdown

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-09-14
Source: https://github.com/oasisprotocol/oasis-core/commit/1d217affc69a0516fe1a5341e2f3eeb6fed8eb6c
Type: security-commit

## Details
go/runtime/client: Fix possible panic on shutdown

## Patch
### .changelog/3271.bugfix.md
```diff
@@ -0,0 +1 @@
+go/runtime/client: Fix possible panic on shutdown
```

### go/runtime/client/client.go
```diff
@@ -84,37 +84,49 @@ func (c *runtimeClient) SubmitTx(ctx context.Context, request *api.SubmitTxReque
 	}
 	c.Unlock()
 
+	// Send a request for watching a new runtime transaction.
 	respCh := make(chan *watchResult)
-	var requestID hash.Hash
-	requestID.FromBytes(request.Data)
-	watcher.newCh <- &watchRequest{
-		id:     &requestID,
+	req := &watchRequest{
 		ctx:    ctx,
 		respCh: respCh,
 	}
+	req.id.FromBytes(request.Data)
+	select {
+	case <-ctx.Done():
+		// The context we're working in was canceled, abort.
+		return nil, ctx.Err()
+	case <-c.common.ctx.Done():
+		// Client is shutting down.
+		return nil, fmt.Errorf("client: shutting down")
+	case watcher.newCh <- req:
+	}
 
+	// Wait for response, handling retries if/when needed.
 	for {
 		var resp *watchResult
 		var ok bool
 
 		select {
 		case <-ctx.Done():
 			// The context we're working in was canceled, abort.
-			return nil, context.Canceled
-
+			return nil, ctx.Err()
+		case <-c.common.ctx.Done():
+			// Client is shutting down.
+			return nil, fmt.Errorf("client: shutting down")
 		case resp, ok = <-respCh:
-			// The main event is getting a response from the watcher, handled below.
+			if !ok {
+				return nil, fmt.Errorf("client: block watch channel closed unexpectedly (unknown error)")
+			}
+
+			// The main event is getting a response from the watcher, handled below. If there is
+			// no result yet, this means that we need to retry publish.
 			if resp.result == nil {
 				break
 			}
 
 			return resp.result, nil
 		}
 
-		if !ok {
-			return nil, fmt.Errorf("client: block watch channel closed unexpectedly (unknown error)")
-		}
-
 		c.common.p2p.Publish(context.Background(), request.RuntimeID, &p2p.Message{
 			Tx: &executor.Tx{
 				Data: request.Data,
```

### go/runtime/client/watcher.go
```diff
@@ -19,7 +19,7 @@ const (
 )
 
 type watchRequest struct {
-	id     *hash.Hash
+	id     hash.Hash
 	ctx    context.Context
 	respCh chan *watchResult
 	height int64
@@ -96,7 +96,6 @@ func (w *blockWatcher) checkBlock(blk *block.Block) {
 
 func (w *blockWatcher) watch() {
 	defer func() {
-		close(w.newCh)
 		for _, watch := range w.watched {
 			close(watch.respCh)
 		}
@@ -204,13 +203,13 @@ func (w *blockWatcher) watch() {
 			}
 
 		case newWatch := <-w.newCh:
-			w.watched[*newWatch.id] = newWatch
+			w.watched[newWatch.id] = newWatch
 
 			res := &watchResult{
 				groupVersion: latestGroupVersion,
 			}
 			if newWatch.send(res, latestHeight) != nil {
-				delete(w.watched, *newWatch.id)
+				delete(w.watched, newWatch.id)
 			}
 
 		case <-w.stopCh:
```
