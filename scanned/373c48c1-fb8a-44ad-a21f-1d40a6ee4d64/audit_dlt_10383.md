# [?] tests: fix deadlock in TestWebsocketLargeCall (#17706)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-10-30
Source: https://github.com/erigontech/erigon/commit/b2ac9a4faf3bdc9ca5903ac3ce83a6cdd575b520
Type: security-commit

## Details
tests: fix deadlock in TestWebsocketLargeCall (#17706)

Fixes #16875

## Patch
### rpc/client.go
```diff
@@ -592,6 +592,9 @@ func (c *Client) dispatch(codec ServerCodec) {
 			conn.handler.logger.Trace("RPC connection read error", "err", err)
 			// A read error is fatal for the connection, and all pending requests must be cancelled, including any
 			// that might still be considered in-flight.
+			if lastOp != nil {
+				conn.handler.removeRequestOp(lastOp)
+			}
 			conn.close(err, nil)
 			reading = false
 
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
