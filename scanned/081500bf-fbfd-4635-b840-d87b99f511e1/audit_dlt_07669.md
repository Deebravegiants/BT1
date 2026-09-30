# [?] tests: fix deadlock in TestBatchLimit_WebSocket_Exceeded on macOS (#16829)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-08-27
Source: https://github.com/erigontech/erigon/commit/6378098a8bae0d02e3677b64151d9faec30767ae
Type: security-commit

## Details
tests: fix deadlock in TestBatchLimit_WebSocket_Exceeded on macOS (#16829)

Fixes #16382
Replaces #16431

## Patch
### rpc/batch_limit_ws_test.go
```diff
@@ -10,7 +10,6 @@ import (
 )
 
 func TestBatchLimit_WebSocket_Exceeded(t *testing.T) {
-	t.Skip("TODO: https://github.com/erigontech/erigon/issues/16382")
 	t.Parallel()
 	logger := log.New()
 
```

### rpc/client.go
```diff
@@ -576,7 +576,9 @@ func (c *Client) dispatch(codec ServerCodec) {
 					conn.handler.logger.Warn("[rpc] batch limit exceeded", "limit", c.batchLimit, "requested", len(op.msgs))
 					// Send error response
 					errMsg := errorMessage(batchErr)
-					_ = conn.codec.WriteJSON(context.Background(), errMsg)
+					if err := conn.codec.WriteJSON(context.Background(), errMsg); err != nil {
+						conn.handler.logger.Debug("Failed to send batch limit error", "err", err)
+					}
 					// Then close the connection
 					conn.close(batchErr, lastOp)
 					continue
@@ -588,7 +590,9 @@ func (c *Client) dispatch(codec ServerCodec) {
 
 		case err := <-c.readErr:
 			conn.handler.logger.Trace("RPC connection read error", "err", err)
-			conn.close(err, lastOp)
+			// A read error is fatal for the connection, and all pending requests must be cancelled, including any
+			// that might still be considered in-flight.
+			conn.close(err, nil)
 			reading = false
 
 		// Reconnect:
```
