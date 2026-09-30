# [?] network: fix streamManager deadlock that causes goroutine leak on P2P hybrid relays (#6576)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2026-03-10
Source: https://github.com/algorand/go-algorand/commit/ba01f10e39e7dc0324dbbab43892854c0fcdfa5c
Type: security-commit

## Details
network: fix streamManager deadlock that causes goroutine leak on P2P hybrid relays (#6576)

## Patch
### network/p2p/streams.go
```diff
@@ -19,7 +19,6 @@ package p2p
 import (
 	"context"
 	"fmt"
-	"io"
 
 	"github.com/libp2p/go-libp2p/core/host"
 	"github.com/libp2p/go-libp2p/core/network"
@@ -41,6 +40,7 @@ type streamManager struct {
 	allowIncomingGossip bool
 
 	streams     map[peer.ID]network.Stream
+	inflight    map[peer.ID]int
 	streamsLock deadlock.Mutex
 }
 
@@ -55,19 +55,40 @@ func makeStreamManager(ctx context.Context, log logging.Logger, h host.Host, han
 		handlers:            handlers,
 		allowIncomingGossip: allowIncomingGossip,
 		streams:             make(map[peer.ID]network.Stream),
+		inflight:            make(map[peer.ID]int),
+	}
+}
+
+func (n *streamManager) beginPeerAttempt(remotePeer peer.ID) {
+	n.streamsLock.Lock()
+	n.inflight[remotePeer]++
+	n.streamsLock.Unlock()
+}
+
+func (n *streamManager) endPeerAttempt(remotePeer peer.ID) {
+	shouldUnprotect := false
+
+	n.streamsLock.Lock()
+	if count := n.inflight[remotePeer]; count <= 1 {
+		delete(n.inflight, remotePeer)
+	} else {
+		n.inflight[remotePeer] = count - 1
+	}
+	_, hasStream := n.streams[remotePeer]
+	_, hasInflight := n.inflight[remotePeer]
+	shouldUnprotect = !hasStream && !hasInflight
+	n.streamsLock.Unlock()
+
+	if shouldUnprotect {
+		n.host.ConnManager().Unprotect(remotePeer, cnmgrTag)
 	}
 }
 
 // streamHandler is called by libp2p when a new stream is accepted
 func (n *streamManager) streamHandler(stream network.Stream) {
-	dispatched := false
 	remotePeer := stream.Conn().RemotePeer()
-
-	defer func() {
-		if !dispatched {
-			n.host.ConnManager().Unprotect(remotePeer, cnmgrTag)
-		}
-	}()
+	n.beginPeerAttempt(remotePeer)
+	defer n.endPeerAttempt(remotePeer)
 
 	if stream.Conn().Stat().Direction == network.DirInbound && !n.allowIncomingGossip {
 		n.log.Debugf("rejecting stream from incoming connection from %s", remotePeer.String())
@@ -83,50 +104,37 @@ func (n *streamManager) streamHandler(stream network.Stream) {
 		}
 	}
 
-	n.streamsLock.Lock()
-	defer n.streamsLock.Unlock()
-
-	if oldStream, ok := n.streams[remotePeer]; ok {
-		// there's already a stream, for some reason, check if it's still open
-		buf := []byte{} // empty buffer for checking
-		_, err := oldStream.Read(buf)
-		if err != nil {
-			if err == io.EOF {
-				// old stream was closed by the peer
-				n.log.Infof("Old stream with %s was closed", remotePeer)
-			} else {
-				// an error occurred while checking the old stream
-				n.log.Infof("Failed to check old stream with %s: %v", remotePeer, err)
-			}
-			// old stream is dead, remove
-			delete(n.streams, remotePeer)
-
-			incoming := stream.Conn().Stat().Direction == network.DirInbound
-			if err1 := n.dispatch(n.ctx, remotePeer, stream, incoming); err1 != nil {
-				n.log.Errorln(err1.Error())
-				_ = stream.Reset()
-				return
-			}
-			n.streams[stream.Conn().RemotePeer()] = stream
-			dispatched = true
-			return
-		}
-		// otherwise, the old stream is still open, so we can close the new one
-		stream.Close()
-		dispatched = true
-		return
-	}
-	// no old stream
+	// Never do blocking I/O (like stream.Read) while holding streamsLock —
+	// that causes a deadlock with Disconnected which also needs the lock to
+	// close the old stream.
+	//
+	// Dispatch the new stream first (outside the lock), then swap the map
+	// entry only on success. This avoids dropping a healthy old stream when
+	// the replacement fails dispatch.
 	incoming := stream.Conn().Stat().Direction == network.DirInbound
 	if err := n.dispatch(n.ctx, remotePeer, stream, incoming); err != nil {
 		n.log.Errorln(err.Error())
 		_ = stream.Reset()
 		return
 	}
 
-	n.streams[stream.Conn().RemotePeer()] = stream
+	n.streamsLock.Lock()
+	// If the connection closed while we were dispatching, Disconnected has
+	// already fired (or will fire) and won't find this entry to clean up.
+	// Avoid adding a stale stream to the map.
+	if stream.Conn().IsClosed() {
+		n.streamsLock.Unlock()
+		_ = stream.Reset()
+		return
+	}
+	oldStream := n.streams[remotePeer]
+	n.streams[remotePeer] = stream
+	n.streamsLock.Unlock()
 
-	dispatched = true
+	if oldStream != nil {
+		n.log.Infof("Replacing old stream with %s", remotePeer)
+		oldStream.Close()
+	}
 }
 
 // dispatch the stream to the appropriate handler
@@ -176,21 +184,16 @@ func (n *streamManager) Connected(net network.Network, conn network.Conn) {
 }
 
 func (n *streamManager) handleConnected(conn network.Conn) {
-	dispatched := false
-	defer func() {
-		if !dispatched {
-			n.host.ConnManager().Unprotect(conn.RemotePeer(), cnmgrTag)
-		}
-	}()
 	remotePeer := conn.RemotePeer()
 	localPeer := n.host.ID()
+	n.beginPeerAttempt(remotePeer)
+	defer n.endPeerAttempt(remotePeer)
 
 	n.streamsLock.Lock()
 	_, ok := n.streams[remotePeer]
 	n.streamsLock.Unlock()
 	if ok {
 		n.log.Debugf("%s: already have a stream to/from %s", localPeer.String(), remotePeer.String())
-		dispatched = true
 		return // there's already an active stream with this peer for our protocol
 	}
 
@@ -217,16 +220,14 @@ func (n *streamManager) handleConnected(conn network.Conn) {
 	if _, exists := n.streams[remotePeer]; exists {
 		// another stream was added in the meantime, close this one and keep the existing one
 		_ = stream.Reset()
-		dispatched = true
 		return
 	}
 	// don't add disconnected / died conns, so Disconnect won't need to clean up
 	if stream.Conn().IsClosed() {
 		_ = stream.Reset()
-		return // dispatched is still false
+		return
 	}
 	n.streams[remotePeer] = stream
-	dispatched = true
 }
 
 // Disconnected is called when a connection is closed
```

### network/p2p/streams_stale_test.go
```diff
@@ -19,6 +19,7 @@ package p2p
 import (
 	"context"
 	"errors"
+	"io"
 	"testing"
 	"time"
 
@@ -48,10 +49,14 @@ const testProto = protocol.ID("/algorand-test/1.0.0")
 type mockConnMgr struct {
 	mu        deadlock.Mutex
 	protected map[peer.ID]map[string]bool
+	unprotect map[peer.ID]int
 }
 
 func newMockConnMgr() *mockConnMgr {
-	return &mockConnMgr{protected: make(map[peer.ID]map[string]bool)}
+	return &mockConnMgr{
+		protected: make(map[peer.ID]map[string]bool),
+		unprotect: make(map[peer.ID]int),
+	}
 }
 
 func (m *mockConnMgr) Protect(id peer.ID, tag string) {
@@ -66,6 +71,7 @@ func (m *mockConnMgr) Protect(id peer.ID, tag string) {
 func (m *mockConnMgr) Unprotect(id peer.ID, tag string) bool {
 	m.mu.Lock()
 	defer m.mu.Unlock()
+	m.unprotect[id]++
 	if m.protected[id] != nil {
 		delete(m.protected[id], tag)
 	}
@@ -78,6 +84,12 @@ func (m *mockConnMgr) IsProtected(id peer.ID, tag string) bool {
 	return m.protected[id] != nil && m.protected[id][tag]
 }
 
+func (m *mockConnMgr) UnprotectCalls(id peer.ID) int {
+	m.mu.Lock()
+	defer m.mu.Unlock()
+	return m.unprotect[id]
+}
+
 func (m *mockConnMgr) TagPeer(peer.ID, string, int)                {}
 func (m *mockConnMgr) UntagPeer(peer.ID, string)                   {}
 func (m *mockConnMgr) UpsertTag(peer.ID, string, func(int) int)    {}
@@ -212,10 +224,14 @@ func failingHandler(_ context.Context, _ peer.ID, _ network.Stream, _ bool) erro
 
 // newTestStreamManager creates a streamManager with a failing handler for testProto.
 func newTestStreamManager(localID peer.ID, allowIncoming bool) (*streamManager, *mockHost) {
+	return newTestStreamManagerWithHandler(localID, allowIncoming, failingHandler)
+}
+
+func newTestStreamManagerWithHandler(localID peer.ID, allowIncoming bool, handler StreamHandler) (*streamManager, *mockHost) {
 	cm := newMockConnMgr()
 	h := &mockHost{id: localID, cm: cm}
 	handlers := StreamHandlers{
-		{ProtoID: testProto, Handler: failingHandler},
+		{ProtoID: testProto, Handler: handler},
 	}
 	logger := logging.NewLogger()
 	logger.SetLevel(logging.Debug)
@@ -402,29 +418,368 @@ func TestStream_MapCleanupOnDispatchFailure(t *testing.T) {
 	})
 }
 
-// TestStream_HandlerCleanupReplacingDeadStream verifies that when streamHandler
-// replaces a dead stream and the new dispatch also fails, the map entry is cleaned up.
-func TestStream_HandlerCleanupReplacingDeadStream(t *testing.T) {
+// TestStream_HandlerKeepsOldStreamOnDispatchFailure verifies that when a new
+// stream arrives but dispatch fails, the existing stream is preserved.
+func TestStream_HandlerKeepsOldStreamOnDispatchFailure(t *testing.T) {
 	partitiontest.PartitionTest(t)
 	t.Parallel()
 
 	localID := peer.ID("ZZZZ-high-peer")
 	remoteID := peer.ID("AAAA-low-peer")
 	sm, h := newTestStreamManager(localID, true)
 
-	// Pre-populate n.streams with a dead (reset) stream
+	// Pre-populate n.streams with an existing stream
 	conn := newMockConn(localID, remoteID, network.DirInbound)
-	deadStream := newMockStream(conn, testProto, network.DirInbound)
-	deadStream.readErr = network.ErrReset // Read returns error => stream is dead
-	sm.streams[remoteID] = deadStream
+	oldStream := newMockStream(conn, testProto, network.DirInbound)
+	sm.streams[remoteID] = oldStream
 
 	// Protect so that Unprotect tracking works
 	h.cm.Protect(remoteID, cnmgrTag)
-
 	// New stream arrives from remote peer, dispatch will fail
 	newStream := newMockStream(conn, testProto, network.DirInbound)
 	sm.streamHandler(newStream)
 
-	assertStreamMapEmpty(t, sm, remoteID)
+	// Old stream is kept because new dispatch failed
+	sm.streamsLock.Lock()
+	current, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.True(t, exists, "old stream should still be in the map")
+	require.Equal(t, oldStream, current, "map should still reference the old stream")
+	require.False(t, oldStream.closeCalled, "old stream should not be closed")
 	require.True(t, newStream.wasReset(), "new stream should be reset on dispatch failure")
+	require.True(t, h.cm.IsProtected(remoteID, cnmgrTag), "peer should remain conn-manager protected after failed replacement")
+}
+
+// blockingMockStream wraps mockStream but makes Read block until the stream is
+// explicitly unblocked or closed, simulating a live yamux stream with no data.
+type blockingMockStream struct {
+	mockStream
+	readStarted chan struct{}
+	unblockRead chan struct{}
+}
+
+func newBlockingMockStream(conn *mockConn, proto protocol.ID, dir network.Direction) *blockingMockStream {
+	return &blockingMockStream{
+		mockStream:  mockStream{conn: conn, proto: proto, dir: dir},
+		readStarted: make(chan struct{}),
+		unblockRead: make(chan struct{}),
+	}
+}
+
+func (s *blockingMockStream) Read(p []byte) (int, error) {
+	select {
+	case <-s.readStarted:
+	default:
+		close(s.readStarted)
+	}
+	<-s.unblockRead
+	return 0, io.EOF
+}
+
+func (s *blockingMockStream) Close() error {
+	s.mu.Lock()
+	defer s.mu.Unlock()
+	s.closeCalled = true
+	// Unblock any pending Read.
+	select {
+	case <-s.unblockRead:
+	default:
+		close(s.unblockRead)
+	}
+	return nil
+}
+
+func (s *blockingMockStream) readWasStarted() bool {
+	select {
+	case <-s.readStarted:
+		return true
+	default:
+		return false
+	}
+}
+
+func closeSignal(ch chan struct{}) {
+	select {
+	case <-ch:
+	default:
+		close(ch)
+	}
+}
+
+// TestStream_HandlerDispatchesBeforeTouchingOldStream verifies that
+// streamHandler starts dispatch before interacting with any existing stream.
+// The pre-fix code called oldStream.Read while holding streamsLock, so this
+// test fails immediately if that regression returns.
+func TestStream_HandlerDispatchesBeforeTouchingOldStream(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	localID := peer.ID("ZZZZ-high-peer")
+	remoteID := peer.ID("AAAA-low-peer")
+	dispatchStarted := make(chan struct{})
+	dispatchRelease := make(chan struct{})
+	handler := func(_ context.Context, _ peer.ID, _ network.Stream, _ bool) error {
+		closeSignal(dispatchStarted)
+		<-dispatchRelease
+		return nil
+	}
+	sm, h := newTestStreamManagerWithHandler(localID, true, handler)
+	conn := newMockConn(localID, remoteID, network.DirInbound)
+
+	oldStream := newBlockingMockStream(conn, testProto, network.DirInbound)
+	sm.streams[remoteID] = oldStream
+	h.cm.Protect(remoteID, cnmgrTag)
+	t.Cleanup(func() {
+		closeSignal(dispatchRelease)
+		_ = oldStream.Close()
+	})
+
+	newStream := newMockStream(conn, testProto, network.DirInbound)
+	streamHandlerDone := make(chan struct{})
+	go func() {
+		sm.streamHandler(newStream)
+		close(streamHandlerDone)
+	}()
+
+	select {
+	case <-dispatchStarted:
+	case <-oldStream.readStarted:
+		t.Fatal("streamHandler tried to read the old stream before starting dispatch")
+	case <-time.After(2 * time.Second):
+		t.Fatal("streamHandler did not start dispatch")
+	}
+
+	closeSignal(dispatchRelease)
+
+	require.False(t, oldStream.readWasStarted(), "old stream should never be read")
+	select {
+	case <-streamHandlerDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("streamHandler did not complete after dispatch was released")
+	}
+	require.False(t, oldStream.readWasStarted(), "old stream should never be read")
+
+	sm.streamsLock.Lock()
+	current, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.True(t, exists, "replacement stream should be tracked")
+	require.Equal(t, newStream, current, "replacement stream should be installed in the map")
+	require.True(t, oldStream.closeCalled, "old stream should be closed after replacement")
+}
+
+// TestStream_DisconnectedCanRunWhileDispatchIsBlocked verifies that
+// Disconnected is not blocked by streamHandler while the new stream's dispatch
+// is in progress. The pre-fix implementation held streamsLock across a blocking
+// Read on the old stream, which prevented Disconnected from making progress.
+func TestStream_DisconnectedCanRunWhileDispatchIsBlocked(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	localID := peer.ID("ZZZZ-high-peer")
+	remoteID := peer.ID("AAAA-low-peer")
+	dispatchStarted := make(chan struct{})
+	dispatchRelease := make(chan struct{})
+	handler := func(_ context.Context, _ peer.ID, _ network.Stream, _ bool) error {
+		closeSignal(dispatchStarted)
+		<-dispatchRelease
+		return nil
+	}
+	sm, h := newTestStreamManagerWithHandler(localID, true, handler)
+	conn := newMockConn(localID, remoteID, network.DirInbound)
+
+	oldStream := newBlockingMockStream(conn, testProto, network.DirInbound)
+	sm.streams[remoteID] = oldStream
+	h.cm.Protect(remoteID, cnmgrTag)
+	t.Cleanup(func() {
+		closeSignal(dispatchRelease)
+		_ = oldStream.Close()
+	})
+
+	newStream := newMockStream(conn, testProto, network.DirInbound)
+	streamHandlerDone := make(chan struct{})
+	go func() {
+		sm.streamHandler(newStream)
+		close(streamHandlerDone)
+	}()
+
+	select {
+	case <-dispatchStarted:
+	case <-oldStream.readStarted:
+		t.Fatal("streamHandler tried to read the old stream before starting dispatch")
+	case <-time.After(2 * time.Second):
+		t.Fatal("streamHandler did not start dispatch")
+	}
+
+	disconnectedDone := make(chan struct{})
+	go func() {
+		sm.Disconnected(nil, conn)
+		close(disconnectedDone)
+	}()
+
+	select {
+	case <-disconnectedDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("Disconnected blocked while streamHandler was dispatching")
+	}
+
+	require.False(t, oldStream.readWasStarted(), "old stream should never be read")
+	sm.streamsLock.Lock()
+	_, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.False(t, exists, "Disconnected should remove the old stream while dispatch is blocked")
+
+	closeSignal(dispatchRelease)
+
+	select {
+	case <-streamHandlerDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("streamHandler did not complete after dispatch was released")
+	}
+
+	require.False(t, oldStream.readWasStarted(), "old stream should never be read")
+	sm.streamsLock.Lock()
+	current, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.True(t, exists, "replacement stream should be tracked after dispatch completes")
+	require.Equal(t, newStream, current, "replacement stream should be installed after disconnect cleanup")
+}
+
+func TestStream_ConcurrentFailureDoesNotUnprotectWhileAnotherAttemptInFlight(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	localID := peer.ID("ZZZZ-high-peer")
+	remoteID := peer.ID("AAAA-low-peer")
+	conn := newMockConn(localID, remoteID, network.DirInbound)
+
+	var successStream *mockStream
+	var failStream *mockStream
+	successStarted := make(chan struct{})
+	releaseSuccess := make(chan struct{})
+	handler := func(_ context.Context, _ peer.ID, s network.Stream, _ bool) error {
+		switch s {
+		case successStream:
+			closeSignal(successStarted)
+			<-releaseSuccess
+			return nil
+		case failStream:
+			return errDispatchFailed
+		default:
+			return nil
+		}
+	}
+	sm, h := newTestStreamManagerWithHandler(localID, true, handler)
+	h.cm.Protect(remoteID, cnmgrTag)
+	successStream = newMockStream(conn, testProto, network.DirInbound)
+	failStream = newMockStream(conn, testProto, network.DirInbound)
+
+	successDone := make(chan struct{})
+	go func() {
+		sm.streamHandler(successStream)
+		close(successDone)
+	}()
+
+	select {
+	case <-successStarted:
+	case <-time.After(2 * time.Second):
+		t.Fatal("success dispatch did not start")
+	}
+
+	failDone := make(chan struct{})
+	go func() {
+		sm.streamHandler(failStream)
+		close(failDone)
+	}()
+	select {
+	case <-failDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("failed dispatch did not complete")
+	}
+
+	require.True(t, h.cm.IsProtected(remoteID, cnmgrTag), "failed attempt must not unprotect while another attempt is in flight")
+	require.Equal(t, 0, h.cm.UnprotectCalls(remoteID), "no unprotect should happen before the in-flight attempt completes")
+
+	closeSignal(releaseSuccess)
+	select {
+	case <-successDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("success dispatch did not complete")
+	}
+
+	sm.streamsLock.Lock()
+	current, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.True(t, exists, "successful stream should be tracked")
+	require.Equal(t, successStream, current, "successful stream should be in the map")
+	require.True(t, h.cm.IsProtected(remoteID, cnmgrTag), "peer should remain protected after successful stream install")
+	require.Equal(t, 0, h.cm.UnprotectCalls(remoteID), "successful stream install should not unprotect")
+	require.True(t, failStream.wasReset(), "failed stream should be reset")
+}
+
+func TestStream_ConcurrentFailedAttemptsUnprotectOnce(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	localID := peer.ID("ZZZZ-high-peer")
+	remoteID := peer.ID("AAAA-low-peer")
+	conn := newMockConn(localID, remoteID, network.DirInbound)
+
+	var streamA *mockStream
+	var streamB *mockStream
+	started := make(chan struct{}, 2)
+	release := make(chan struct{})
+	handler := func(_ context.Context, _ peer.ID, s network.Stream, _ bool) error {
+		switch s {
+		case streamA, streamB:
+			started <- struct{}{}
+			<-release
+			return errDispatchFailed
+		default:
+			return errDispatchFailed
+		}
+	}
+	sm, h := newTestStreamManagerWithHandler(localID, true, handler)
+	h.cm.Protect(remoteID, cnmgrTag)
+	streamA = newMockStream(conn, testProto, network.DirInbound)
+	streamB = newMockStream(conn, testProto, network.DirInbound)
+
+	doneA := make(chan struct{})
+	go func() {
+		sm.streamHandler(streamA)
+		close(doneA)
+	}()
+	doneB := make(chan struct{})
+	go func() {
+		sm.streamHandler(streamB)
+		close(doneB)
+	}()
+
+	for i := 0; i < 2; i++ {
+		select {
+		case <-started:
+		case <-time.After(2 * time.Second):
+			t.Fatal("expected both dispatch attempts to start")
+		}
+	}
+	closeSignal(release)
+
+	select {
+	case <-doneA:
+	case <-time.After(2 * time.Second):
+		t.Fatal("first failed dispatch did not complete")
+	}
+	select {
+	case <-doneB:
+	case <-time.After(2 * time.Second):
+		t.Fatal("second failed dispatch did not complete")
+	}
+
+	sm.streamsLock.Lock()
+	_, exists := sm.streams[remoteID]
+	sm.streamsLock.Unlock()
+	require.False(t, exists, "no stream should remain after two failed attempts")
+	require.False(t, h.cm.IsProtected(remoteID, cnmgrTag), "peer should be unprotected after all attempts failed")
+	require.Equal(t, 1, h.cm.UnprotectCalls(remoteID), "peer should be unprotected exactly once")
+	require.True(t, streamA.wasReset(), "first failed stream should be reset")
+	require.True(t, streamB.wasReset(), "second failed stream should be reset")
 }
```

### network/p2pNetwork.go
```diff
@@ -1082,12 +1082,36 @@ func (n *P2PNetwork) peerRemoteClose(peer *wsPeer, reason disconnectReason) {
 }
 
 func (n *P2PNetwork) removePeer(peer *wsPeer, remotePeerID peer.ID, reason disconnectReason) {
-	n.service.UnprotectPeer(remotePeerID)
+	removed := false
+
 	n.wsPeersLock.Lock()
-	n.identityTracker.removeIdentity(peer)
-	delete(n.wsPeers, remotePeerID)
-	delete(n.wsPeersToIDs, peer)
+	n.identityTracker.removeIdentity(peer) // safe: removeIdentity only deletes if the stored identity matches this exact wsPeer
+	if cur, ok := n.wsPeers[remotePeerID]; ok && cur == peer {
+		delete(n.wsPeers, remotePeerID)
+		removed = true
+	}
+	_, knownPeer := n.wsPeersToIDs[peer]
+	delete(n.wsPeersToIDs, peer) // always delete reverse entry for this exact wsPeer
+
+	// Unprotect while still holding wsPeersLock so we can't race with a new
+	// wsPeer insertion for the same remotePeerID between map deletion and
+	// unprotect.
+	if removed {
+		n.service.UnprotectPeer(remotePeerID)
+	}
 	n.wsPeersLock.Unlock()
+
+	// Throttle slots are per-wsPeer, not per map entry: release for any
+	// known wsPeer on its first cleanup, even if it was already replaced.
+	if knownPeer && peer.throttledOutgoingConnection {
+		n.throttledOutgoingConnections.Add(int32(1))
+	}
+
+	if !removed {
+		// stale close from an old stream/wsPeer that was already replaced; skip
+		// unprotect, disconnect telemetry, and counter updates.
+		return
+	}
 	n.wsPeersChangeCounter.Add(1)
 
 	eventDetails := telemetryspec.PeerEventDetails{
@@ -1110,9 +1134,6 @@ func (n *P2PNetwork) removePeer(peer *wsPeer, remotePeerID peer.ID, reason disco
 			AVCount:          peer.avMessageCount.Load(),
 			PPCount:          peer.ppMessageCount.Load(),
 		})
-	if peer.throttledOutgoingConnection {
-		n.throttledOutgoingConnections.Add(int32(1))
-	}
 }
 
 func (n *P2PNetwork) peerSnapshot(dest []*wsPeer) ([]*wsPeer, int32) {
```

### network/p2pNetwork_test.go
```diff
@@ -326,9 +326,12 @@ func TestP2PSubmitWS(t *testing.T) {
 }
 
 type mockService struct {
-	id    peer.ID
-	addrs []ma.Multiaddr
-	peers map[peer.ID]peer.AddrInfo
+	id               peer.ID
+	addrs            []ma.Multiaddr
+	peers            map[peer.ID]peer.AddrInfo
+	unprotectStarted chan struct{}
+	unprotectRelease <-chan struct{}
+	unprotectCalls   atomic.Int32
 }
 
 func (s *mockService) Start() error {
@@ -364,6 +367,17 @@ func (s *mockService) ClosePeer(peer peer.ID) error {
 }
 
 func (s *mockService) UnprotectPeer(peer.ID) {
+	s.unprotectCalls.Add(1)
+	if s.unprotectStarted != nil {
+		select {
+		case <-s.unprotectStarted:
+		default:
+			close(s.unprotectStarted)
+		}
+	}
+	if s.unprotectRelease != nil {
+		<-s.unprotectRelease
+	}
 }
 
 func (s *mockService) Conns() []network.Conn {
@@ -398,6 +412,78 @@ func makeMockService(id peer.ID, addrs []ma.Multiaddr) *mockService {
 	}
 }
 
+func TestP2PRemovePeerHoldsLockAcrossUnprotect(t *testing.T) {
+	partitiontest.PartitionTest(t)
+
+	remotePeerID := peer.ID("12D3KooWRemotePeer")
+	oldPeer := &wsPeer{}
+	newPeer := &wsPeer{}
+	unprotectRelease := make(chan struct{})
+
+	mockSvc := &mockService{
+		id:               peer.ID("12D3KooWSelfPeer"),
+		unprotectStarted: make(chan struct{}),
+		unprotectRelease: unprotectRelease,
+	}
+	net := &P2PNetwork{
+		log:             logging.TestingLog(t),
+		service:         mockSvc,
+		wsPeers:         make(map[peer.ID]*wsPeer),
+		wsPeersToIDs:    make(map[*wsPeer]peer.ID),
+		identityTracker: noopIdentityTracker{},
+	}
+	net.wsPeers[remotePeerID] = oldPeer
+	net.wsPeersToIDs[oldPeer] = remotePeerID
+
+	removeDone := make(chan struct{})
+	go func() {
+		net.removePeer(oldPeer, remotePeerID, disconnectReasonNone)
+		close(removeDone)
+	}()
+
+	select {
+	case <-mockSvc.unprotectStarted:
+	case <-time.After(2 * time.Second):
+		t.Fatal("removePeer did not enter UnprotectPeer")
+	}
+
+	addDone := make(chan struct{})
+	go func() {
+		net.wsPeersLock.Lock()
+		net.wsPeers[remotePeerID] = newPeer
+		net.wsPeersToIDs[newPeer] = remotePeerID
+		net.wsPeersLock.Unlock()
+		close(addDone)
+	}()
+
+	select {
+	case <-addDone:
+		t.Fatal("wsPeersLock was released while UnprotectPeer was still running")
+	case <-time.After(100 * time.Millisecond):
+		// expected: add path stays blocked until UnprotectPeer returns
+	}
+
+	close(unprotectRelease)
+
+	select {
+	case <-removeDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("removePeer did not finish after UnprotectPeer was released")
+	}
+	select {
+	case <-addDone:
+	case <-time.After(2 * time.Second):
+		t.Fatal("add path did not complete after removePeer finished")
+	}
+
+	require.Equal(t, int32(1), mockSvc.unprotectCalls.Load(), "expected exactly one unprotect call")
+	net.wsPeersLock.RLock()
+	current, ok := net.wsPeers[remotePeerID]
+	net.wsPeersLock.RUnlock()
+	require.True(t, ok, "replacement peer should be present")
+	require.Equal(t, newPeer, current, "replacement peer should remain mapped")
+}
+
 func TestP2PNetworkAddress(t *testing.T) {
 	partitiontest.PartitionTest(t)
 
```
