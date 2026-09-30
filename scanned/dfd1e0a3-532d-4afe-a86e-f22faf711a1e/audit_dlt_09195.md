# [?] Merge pull request #965 from libp2p/fix/panic

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2020-06-05
Source: https://github.com/libp2p/go-libp2p/commit/ed4bd39dda32f3891ab20fbb6f2faba9fc939a88
Type: security-commit

## Details
Merge pull request #965 from libp2p/fix/panic

Fix peer handler race

## Patch
### p2p/protocol/identify/id.go
```diff
@@ -181,14 +181,22 @@ func (ids *IDService) loop() {
 		return
 	}
 
+	phClosedCh := make(chan peer.ID)
+
 	defer func() {
 		sub.Close()
-		for pid := range phs {
-			phs[pid].close()
+		// The context will cancel the workers. Now, wait for them to
+		// exit.
+		for range phs {
+			<-phClosedCh
 		}
 	}()
 
-	phClosedCh := make(chan peer.ID)
+	// Use a fresh context for the handlers. Otherwise, they'll get canceled
+	// before we're ready to shutdown and they'll have "stopped" without us
+	// _calling_ stop.
+	handlerCtx, cancel := context.WithCancel(context.Background())
+	defer cancel()
 
 	for {
 		select {
@@ -197,7 +205,7 @@ func (ids *IDService) loop() {
 			ph, ok := phs[rp]
 			if !ok && ids.Host.Network().Connectedness(rp) == network.Connected {
 				ph = newPeerHandler(rp, ids)
-				ph.start()
+				ph.start(handlerCtx, func() { phClosedCh <- rp })
 				phs[rp] = ph
 			}
 			addReq.resp <- ph
@@ -212,16 +220,8 @@ func (ids *IDService) loop() {
 					// move on, move on, there's nothing to see here.
 					continue
 				}
-				ids.refCount.Add(1)
-				go func(req rmPeerHandlerReq, ph *peerHandler) {
-					defer ids.refCount.Done()
-					ph.close()
-					select {
-					case <-ids.ctx.Done():
-						return
-					case phClosedCh <- req.p:
-					}
-				}(rmReq, ph)
+				// This is idempotent if already stopped.
+				ph.stop()
 			}
 
 		case rp := <-phClosedCh:
@@ -234,7 +234,7 @@ func (ids *IDService) loop() {
 			// The fact that we got the handler on this channel means that it's context and handler
 			// have completed because we write the handler to this chanel only after it closed.
 			if ids.Host.Network().Connectedness(rp) == network.Connected {
-				ph.start()
+				ph.start(handlerCtx, func() { phClosedCh <- rp })
 			} else {
 				delete(phs, rp)
 			}
```

### p2p/protocol/identify/peer_loop.go
```diff
@@ -28,11 +28,11 @@ type identifySnapshot struct {
 }
 
 type peerHandler struct {
-	ids *IDService
+	ids     *IDService
+	started bool
 
 	ctx    context.Context
 	cancel context.CancelFunc
-	wg     sync.WaitGroup
 
 	pid peer.ID
 
@@ -57,49 +57,62 @@ func newPeerHandler(pid peer.ID, ids *IDService) *peerHandler {
 	return ph
 }
 
-func (ph *peerHandler) start() {
-	ctx, cancel := context.WithCancel(context.Background())
-	ph.ctx = ctx
+// start starts a handler. This may only be called on a stopped handler, and must
+// not be called concurrently with start/stop.
+//
+// This may _not_ be called on a _canceled_ handler. I.e., a handler where the
+// passed in context expired.
+func (ph *peerHandler) start(ctx context.Context, onExit func()) {
+	if ph.cancel != nil {
+		// If this happens, we have a bug. It means we tried to start
+		// before we stopped.
+		panic("peer handler already running")
+	}
+
+	ctx, cancel := context.WithCancel(ctx)
 	ph.cancel = cancel
 
-	ph.wg.Add(1)
-	go ph.loop()
+	go ph.loop(ctx, onExit)
 }
 
-func (ph *peerHandler) close() error {
-	ph.cancel()
-	ph.wg.Wait()
+// stop stops a handler. This may not be called concurrently with any
+// other calls to stop/start.
+func (ph *peerHandler) stop() error {
+	if ph.cancel != nil {
+		ph.cancel()
+		ph.cancel = nil
+	}
 	return nil
 }
 
 // per peer loop for pushing updates
-func (ph *peerHandler) loop() {
-	defer ph.wg.Done()
+func (ph *peerHandler) loop(ctx context.Context, onExit func()) {
+	defer onExit()
 
 	for {
 		select {
 		// our listen addresses have changed, send an IDPush.
 		case <-ph.pushCh:
-			if err := ph.sendPush(); err != nil {
+			if err := ph.sendPush(ctx); err != nil {
 				log.Warnw("failed to send Identify Push", "peer", ph.pid, "error", err)
 			}
 
 		case <-ph.deltaCh:
-			if err := ph.sendDelta(); err != nil {
+			if err := ph.sendDelta(ctx); err != nil {
 				log.Warnw("failed to send Identify Delta", "peer", ph.pid, "error", err)
 			}
 
-		case <-ph.ctx.Done():
+		case <-ctx.Done():
 			return
 		}
 	}
 }
 
-func (ph *peerHandler) sendDelta() error {
+func (ph *peerHandler) sendDelta(ctx context.Context) error {
 	// send a push if the peer does not support the Delta protocol.
-	if !ph.peerSupportsProtos([]string{IDDelta}) {
+	if !ph.peerSupportsProtos(ctx, []string{IDDelta}) {
 		log.Debugw("will send push as peer does not support delta", "peer", ph.pid)
-		if err := ph.sendPush(); err != nil {
+		if err := ph.sendPush(ctx); err != nil {
 			return fmt.Errorf("failed to send push on delta message: %w", err)
 		}
 		return nil
@@ -111,7 +124,7 @@ func (ph *peerHandler) sendDelta() error {
 		return nil
 	}
 
-	ds, err := ph.openStream([]string{IDDelta})
+	ds, err := ph.openStream(ctx, []string{IDDelta})
 	if err != nil {
 		return fmt.Errorf("failed to open delta stream: %w", err)
 	}
@@ -128,8 +141,8 @@ func (ph *peerHandler) sendDelta() error {
 	return nil
 }
 
-func (ph *peerHandler) sendPush() error {
-	dp, err := ph.openStream([]string{IDPush})
+func (ph *peerHandler) sendPush(ctx context.Context) error {
+	dp, err := ph.openStream(ctx, []string{IDPush})
 	if err == errProtocolNotSupported {
 		log.Debugw("not sending push as peer does not support protocol", "peer", ph.pid)
 		return nil
@@ -150,25 +163,25 @@ func (ph *peerHandler) sendPush() error {
 	return nil
 }
 
-func (ph *peerHandler) openStream(protos []string) (network.Stream, error) {
+func (ph *peerHandler) openStream(ctx context.Context, protos []string) (network.Stream, error) {
 	// wait for the other peer to send us an Identify response on "all" connections we have with it
 	// so we can look at it's supported protocols and avoid a multistream-select roundtrip to negotiate the protocol
 	// if we know for a fact that it dosen't support the protocol.
 	conns := ph.ids.Host.Network().ConnsToPeer(ph.pid)
 	for _, c := range conns {
 		select {
 		case <-ph.ids.IdentifyWait(c):
-		case <-ph.ctx.Done():
-			return nil, ph.ctx.Err()
+		case <-ctx.Done():
+			return nil, ctx.Err()
 		}
 	}
 
-	if !ph.peerSupportsProtos(protos) {
+	if !ph.peerSupportsProtos(ctx, protos) {
 		return nil, errProtocolNotSupported
 	}
 
 	// negotiate a stream without opening a new connection as we "should" already have a connection.
-	ctx, cancel := context.WithTimeout(ph.ctx, 30*time.Second)
+	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
 	defer cancel()
 	ctx = network.WithNoDial(ctx, "should already have connection")
 
@@ -183,12 +196,12 @@ func (ph *peerHandler) openStream(protos []string) (network.Stream, error) {
 }
 
 // returns true if the peer supports atleast one of the given protocols
-func (ph *peerHandler) peerSupportsProtos(protos []string) bool {
+func (ph *peerHandler) peerSupportsProtos(ctx context.Context, protos []string) bool {
 	conns := ph.ids.Host.Network().ConnsToPeer(ph.pid)
 	for _, c := range conns {
 		select {
 		case <-ph.ids.IdentifyWait(c):
-		case <-ph.ctx.Done():
+		case <-ctx.Done():
 			return false
 		}
 	}
```

### p2p/protocol/identify/peer_loop_test.go
```diff
@@ -3,6 +3,7 @@ package identify
 import (
 	"context"
 	"testing"
+	"time"
 
 	"github.com/libp2p/go-libp2p-core/network"
 	"github.com/libp2p/go-libp2p-core/peer"
@@ -21,8 +22,8 @@ func TestMakeApplyDelta(t *testing.T) {
 	defer h1.Close()
 	ids1 := NewIDService(h1)
 	ph := newPeerHandler(h1.ID(), ids1)
-	ph.start()
-	defer ph.close()
+	ph.start(ctx, func() {})
+	defer ph.stop()
 
 	m1 := ph.nextDelta()
 	require.NotNil(t, m1)
@@ -66,9 +67,24 @@ func TestHandlerClose(t *testing.T) {
 	defer h1.Close()
 	ids1 := NewIDService(h1)
 	ph := newPeerHandler(h1.ID(), ids1)
-	ph.start()
-
-	require.NoError(t, ph.close())
+	closedCh := make(chan struct{}, 2)
+	ph.start(ctx, func() {
+		closedCh <- struct{}{}
+	})
+
+	require.NoError(t, ph.stop())
+	select {
+	case <-closedCh:
+	case <-time.After(time.Second):
+		t.Fatal("expected the handler to close")
+	}
+
+	require.NoError(t, ph.stop())
+	select {
+	case <-closedCh:
+		t.Fatal("expected only one close event")
+	case <-time.After(10 * time.Millisecond):
+	}
 }
 
 func TestPeerSupportsProto(t *testing.T) {
@@ -82,10 +98,10 @@ func TestPeerSupportsProto(t *testing.T) {
 	rp := peer.ID("test")
 	ph := newPeerHandler(rp, ids1)
 	require.NoError(t, h1.Peerstore().AddProtocols(rp, "test"))
-	require.True(t, ph.peerSupportsProtos([]string{"test"}))
-	require.False(t, ph.peerSupportsProtos([]string{"random"}))
+	require.True(t, ph.peerSupportsProtos(ctx, []string{"test"}))
+	require.False(t, ph.peerSupportsProtos(ctx, []string{"random"}))
 
 	// remove support for protocol and check
 	require.NoError(t, h1.Peerstore().RemoveProtocols(rp, "test"))
-	require.False(t, ph.peerSupportsProtos([]string{"test"}))
+	require.False(t, ph.peerSupportsProtos(ctx, []string{"test"}))
 }
```
