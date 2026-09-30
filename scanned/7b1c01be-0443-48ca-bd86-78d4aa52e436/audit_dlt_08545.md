# [?] network: align duplicateFilterCount to prevent panic on 32-bit platforms (#4702)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-10-28
Source: https://github.com/algorand/go-algorand/commit/40974eede5d31e5a2408ca9d7d924929a871c14f
Type: security-commit

## Details
network: align duplicateFilterCount to prevent panic on 32-bit platforms (#4702)

## Patch
### logging/telemetryspec/event.go
```diff
@@ -301,7 +301,7 @@ type PeerConnectionDetails struct {
 	// MessageDelay is the avarage relative message delay. Not being used for incoming connection.
 	MessageDelay int64 `json:",omitempty"`
 	// DuplicateFilterCount is the number of times this peer has sent us a message hash to filter that it had already sent before.
-	DuplicateFilterCount int64
+	DuplicateFilterCount uint64
 }
 
 // CatchpointGenerationEvent event
```

### network/wsPeer.go
```diff
@@ -180,6 +180,11 @@ type wsPeer struct {
 	// Nonce used to uniquely identify requests
 	requestNonce uint64
 
+	// duplicateFilterCount counts how many times the remote peer has sent us a message hash
+	// to filter that it had already sent before.
+	// this needs to be 64-bit aligned for use with atomic.AddUint64 on 32-bit platforms.
+	duplicateFilterCount uint64
+
 	wsPeerCore
 
 	// conn will be *websocket.Conn (except in testing)
@@ -203,9 +208,6 @@ type wsPeer struct {
 
 	incomingMsgFilter *messageFilter
 	outgoingMsgFilter *messageFilter
-	// duplicateFilterCount counts how many times the remote peer has sent us a message hash
-	// to filter that it had already sent before.
-	duplicateFilterCount int64
 
 	processed chan struct{}
 
@@ -614,7 +616,7 @@ func (wp *wsPeer) handleFilterMessage(msg IncomingMessage) {
 		// large message concurrently from several peers, and then sent the filter message to us after
 		// each large message finished transferring.
 		duplicateNetworkFilterReceivedTotal.Inc(nil)
-		atomic.AddInt64(&wp.duplicateFilterCount, 1)
+		atomic.AddUint64(&wp.duplicateFilterCount, 1)
 	}
 }
 
```

### network/wsPeer_test.go
```diff
@@ -103,6 +103,7 @@ func TestAtomicVariablesAlignment(t *testing.T) {
 	require.True(t, (unsafe.Offsetof(p.requestNonce)%8) == 0)
 	require.True(t, (unsafe.Offsetof(p.lastPacketTime)%8) == 0)
 	require.True(t, (unsafe.Offsetof(p.intermittentOutgoingMessageEnqueueTime)%8) == 0)
+	require.True(t, (unsafe.Offsetof(p.duplicateFilterCount)%8) == 0)
 }
 
 func TestTagCounterFiltering(t *testing.T) {
```
