# [?] tests: fix deadlock in TestWebsocketLargeCall - 2nd try (#17762)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-04
Source: https://github.com/erigontech/erigon/commit/3e12ced54707974b30f95cc986f5cbffa18cdbed
Type: security-commit

## Details
tests: fix deadlock in TestWebsocketLargeCall - 2nd try (#17762)

Fixes #16875

## Patch
### rpc/client.go
```diff
@@ -593,6 +593,7 @@ func (c *Client) dispatch(codec ServerCodec) {
 			// A read error is fatal for the connection, and all pending requests must be cancelled, including any
 			// that might still be considered in-flight.
 			conn.close(err, nil)
+			lastOp = nil
 			reading = false
 
 		// Reconnect:
@@ -610,9 +611,10 @@ func (c *Client) dispatch(codec ServerCodec) {
 			go c.read(newcodec)
 			reading = true
 			conn = c.newClientConn(newcodec)
-			// Re-register the in-flight request on the new handler
-			// because that's where it will be sent.
-			conn.handler.addRequestOp(lastOp)
+			// Re-register the in-flight request on the new handler because that's where it will be sent.
+			if lastOp != nil {
+				conn.handler.addRequestOp(lastOp)
+			}
 
 		// Send path:
 		case op := <-reqInitLock:
@@ -622,7 +624,7 @@ func (c *Client) dispatch(codec ServerCodec) {
 			conn.handler.addRequestOp(op)
 
 		case err := <-c.reqSent:
-			if err != nil {
+			if lastOp != nil && err != nil {
 				// Remove response handlers for the last send. When the read loop
 				// goes down, it will signal all other current operations.
 				conn.handler.removeRequestOp(lastOp)
```

### rpc/websocket_test.go
```diff
@@ -85,10 +85,6 @@ func TestWebsocketOriginCheck(t *testing.T) {
 
 // This test checks whether calls exceeding the request size limit are rejected.
 func TestWebsocketLargeCall(t *testing.T) {
-	//if runtime.GOOS == "darwin" {
-	t.Skip("issue #16875")
-	//}
-
 	if testing.Short() {
 		t.Skip()
 	}
```
