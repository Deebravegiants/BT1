# [?] p2p: fix StopNotify vs notifyAll deadlock on stop (#6562)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2026-02-23
Source: https://github.com/algorand/go-algorand/commit/791c5ae0366f82677ff07f0d687d996b783f31ca
Type: security-commit

## Details
p2p: fix StopNotify vs notifyAll deadlock on stop (#6562)

## Patch
### network/p2p/streams.go
```diff
@@ -122,8 +122,14 @@ func (n *streamManager) dispatch(ctx context.Context, remotePeer peer.ID, stream
 
 // Connected is called when a connection is opened
 // for both incoming (listener -> addConn) and outgoing (dialer -> addConn) connections.
+// This is invoked from libp2p's Swarm.notifyAll which holds a read lock on the notifiees list.
+// We do some read/write operations in this handler for metadata exchange that creates a race condition
+// with StopNotify on network shutdown. To avoid, run the handler as a goroutine.
 func (n *streamManager) Connected(net network.Network, conn network.Conn) {
+	go n.handleConnected(conn)
+}
 
+func (n *streamManager) handleConnected(conn network.Conn) {
 	remotePeer := conn.RemotePeer()
 	localPeer := n.host.ID()
 
```

### network/p2p/streams_test.go
```diff
@@ -17,6 +17,7 @@
 package p2p
 
 import (
+	"bytes"
 	"context"
 	"strings"
 	"testing"
@@ -28,19 +29,45 @@ import (
 	"github.com/multiformats/go-multiaddr"
 	"github.com/stretchr/testify/require"
 
+	"github.com/algorand/go-deadlock"
+
 	"github.com/algorand/go-algorand/config"
 	"github.com/algorand/go-algorand/logging"
 	"github.com/algorand/go-algorand/network/p2p/peerstore"
 	"github.com/algorand/go-algorand/test/partitiontest"
 )
 
+// syncBuffer is a thread-safe bytes.Buffer for use as a log output target.
+type syncBuffer struct {
+	mu  deadlock.Mutex
+	buf bytes.Buffer
+}
+
+func (sb *syncBuffer) Write(p []byte) (int, error) {
+	sb.mu.Lock()
+	defer sb.mu.Unlock()
+	return sb.buf.Write(p)
+}
+
+func (sb *syncBuffer) String() string {
+	sb.mu.Lock()
+	defer sb.mu.Unlock()
+	return sb.buf.String()
+}
+
+func (sb *syncBuffer) Reset() {
+	sb.mu.Lock()
+	defer sb.mu.Unlock()
+	sb.buf.Reset()
+}
+
 // TestConnectedLogsNonDialedOutgoingConnection tests that the Connected function
 // exits early for non-dialed outgoing connections by checking the log output
 func TestStreamNonDialedOutgoingConnection(t *testing.T) {
 	partitiontest.PartitionTest(t)
 	t.Parallel()
 
-	logBuffer := &strings.Builder{}
+	logBuffer := &syncBuffer{}
 	logger := logging.NewLogger()
 	logger.SetOutput(logBuffer)
 	logger.SetLevel(logging.Debug)
@@ -110,9 +137,9 @@ func TestStreamNonDialedOutgoingConnection(t *testing.T) {
 	require.Len(t, conns, 1)
 	require.Equal(t, network.DirOutbound, conns[0].Stat().Direction)
 
-	// Check that the log contains the expected message for non-dialed outgoing connection
-	logOutput := logBuffer.String()
-	expectedMsg := "ignoring non-dialed outgoing peer ID"
-	require.Contains(t, logOutput, expectedMsg)
-	require.Contains(t, logOutput, listenerHost.ID().String())
+	const expectedMsg = "ignoring non-dialed outgoing peer ID"
+	require.Eventually(t, func() bool {
+		logOutput := logBuffer.String()
+		return strings.Contains(logOutput, expectedMsg) && strings.Contains(logOutput, listenerHost.ID().String())
+	}, 5*time.Second, 50*time.Millisecond)
 }
```
