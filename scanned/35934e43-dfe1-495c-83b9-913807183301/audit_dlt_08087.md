# [?] Fix data race.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2015-06-15
Source: https://github.com/btcsuite/btcd/commit/77baeb8d7959628bf113a9cde2e052a5be785227
Type: security-commit

## Details
Fix data race.

This synchronizes access to the (*Client).disconnect channel, which
may change during reconnects.

Fixes #54.

## Patch
### infrastructure.go
```diff
@@ -394,6 +394,16 @@ out:
 	log.Tracef("RPC client input handler done for %s", c.config.Host)
 }
 
+// disconnectChan returns a copy of the current disconnect channel.  The channel
+// is read protected by the client mutex, and is safe to call while the channel
+// is being reassigned during a reconnect.
+func (c *Client) disconnectChan() <-chan struct{} {
+	c.mtx.Lock()
+	ch := c.disconnect
+	c.mtx.Unlock()
+	return ch
+}
+
 // wsOutHandler handles all outgoing messages for the websocket connection.  It
 // uses a buffered channel to serialize output messages while allowing the
 // sender to continue running asynchronously.  It must be run as a goroutine.
@@ -410,7 +420,7 @@ out:
 				break out
 			}
 
-		case <-c.disconnect:
+		case <-c.disconnectChan():
 			break out
 		}
 	}
@@ -436,7 +446,7 @@ func (c *Client) sendMessage(marshalledJSON []byte) {
 	// Don't send the message if disconnected.
 	select {
 	case c.sendChan <- marshalledJSON:
-	case <-c.disconnect:
+	case <-c.disconnectChan():
 		return
 	}
 }
@@ -618,9 +628,9 @@ out:
 			// has happened.
 			c.wsConn = wsConn
 			c.retryCount = 0
-			c.disconnect = make(chan struct{})
 
 			c.mtx.Lock()
+			c.disconnect = make(chan struct{})
 			c.disconnected = false
 			c.mtx.Unlock()
 
```
