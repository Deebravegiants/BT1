# [?] Use mutexes for byte counts to fix i386/arm panic.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2014-02-13
Source: https://github.com/btcsuite/btcd/commit/e5a1c6e5aca9eee937e774e45140802eda7035ef
Type: security-commit

## Details
Use mutexes for byte counts to fix i386/arm panic.

This commit changes the server byte counters over to use a mutex instead
of the atomic package.  The atomic.AddUint64 function requires the struct
fields to be 64-bit aligned on 32-bit platforms.  The byte counts are
fields in the server struct and are not 64-bit aligned.  While it would be
possible to arrange the fields to be aligned through various means, it
would make the code too fragile for my tastes.  I prefer code that doesn't
depend on platform specific alignment.

Fixes #96.

## Patch
### peer.go
```diff
@@ -956,7 +956,7 @@ func (p *peer) handlePongMsg(msg *btcwire.MsgPong) {
 func (p *peer) readMessage() (btcwire.Message, []byte, error) {
 	n, msg, buf, err := btcwire.ReadMessageN(p.conn, p.protocolVersion, p.btcnet)
 	p.bytesReceived += uint64(n)
-	atomic.AddUint64(&p.server.bytesReceived, uint64(n))
+	p.server.AddBytesReceived(uint64(n))
 	if err != nil {
 		return nil, nil, err
 	}
@@ -1025,7 +1025,7 @@ func (p *peer) writeMessage(msg btcwire.Message) {
 	// Write the message to the peer.
 	n, err := btcwire.WriteMessageN(p.conn, msg, p.protocolVersion, p.btcnet)
 	p.bytesSent += uint64(n)
-	atomic.AddUint64(&p.server.bytesSent, uint64(n))
+	p.server.AddBytesSent(uint64(n))
 	if err != nil {
 		p.Disconnect()
 		p.logError("Can't send message: %v", err)
```

### server.go
```diff
@@ -51,11 +51,12 @@ type server struct {
 	nonce         uint64
 	listeners     []net.Listener
 	btcnet        btcwire.BitcoinNet
-	started       int32  // atomic
-	shutdown      int32  // atomic
-	shutdownSched int32  // atomic
-	bytesReceived uint64 // Total bytes received from all peers since start.
-	bytesSent     uint64 // Total bytes sent by all peers since start.
+	started       int32      // atomic
+	shutdown      int32      // atomic
+	shutdownSched int32      // atomic
+	bytesMutex    sync.Mutex // For the following two fields.
+	bytesReceived uint64     // Total bytes received from all peers since start.
+	bytesSent     uint64     // Total bytes sent by all peers since start.
 	addrManager   *AddrManager
 	rpcServer     *rpcServer
 	blockManager  *blockManager
@@ -696,12 +697,31 @@ func (s *server) RemoveAddr(addr string) error {
 	return <-replyChan
 }
 
+// AddBytesSent adds the passed number of bytes to the total bytes sent counter
+// for the server.  It is safe for concurrent access.
+func (s *server) AddBytesSent(bytesSent uint64) {
+	s.bytesMutex.Lock()
+	defer s.bytesMutex.Unlock()
+
+	s.bytesSent += bytesSent
+}
+
+// AddBytesReceived adds the passed number of bytes to the total bytes received
+// counter for the server.  It is safe for concurrent access.
+func (s *server) AddBytesReceived(bytesReceived uint64) {
+	s.bytesMutex.Lock()
+	defer s.bytesMutex.Unlock()
+
+	s.bytesReceived += bytesReceived
+}
+
 // NetTotals returns the sum of all bytes received and sent across the network
-// for all peers.
+// for all peers.  It is safe for concurrent access.
 func (s *server) NetTotals() (uint64, uint64) {
-	totalBytesReceived := atomic.LoadUint64(&s.bytesReceived)
-	totalBytesSent := atomic.LoadUint64(&s.bytesSent)
-	return totalBytesReceived, totalBytesSent
+	s.bytesMutex.Lock()
+	defer s.bytesMutex.Unlock()
+
+	return s.bytesReceived, s.bytesSent
 }
 
 // Start begins accepting connections from peers.
```
