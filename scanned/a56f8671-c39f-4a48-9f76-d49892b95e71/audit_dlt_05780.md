# [?] fix(lp2p): reactor panic recovery (#5816)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-04-29
Source: https://github.com/cometbft/cometbft/commit/6bf6b8980d386325d1ddacd5c2064151c6cdf933
Type: security-commit

## Details
fix(lp2p): reactor panic recovery (#5816)

Closes STACK-2679

---

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

## Patch
### CHANGELOG.md
```diff
@@ -7,6 +7,8 @@
 ### BUG FIXES
 - `[mempool]` App mempool waits before broadcasting.
   ([\#5800](https://github.com/cometbft/cometbft/pull/5800))
+- `[p2p]` Add lp2p reactor panic recovery
+  ([\#5816](https://github.com/cometbft/cometbft/pull/5816))
 
 ### IMPROVEMENTS
 
```

### lp2p/reactor_set.go
```diff
@@ -250,6 +250,7 @@ func (rs *reactorSet) receiveQueued(reactorID int, e pendingEnvelope) {
 
 	now := time.Now()
 
+	defer rs.recoverReceive(reactor.name)
 	reactor.Receive(e.Envelope)
 
 	timeTaken := time.Since(now)
@@ -258,6 +259,13 @@ func (rs *reactorSet) receiveQueued(reactorID int, e pendingEnvelope) {
 	rs.switchRef.metrics.MessageReactorReceiveDuration.With(labels...).Observe(timeTaken.Seconds())
 }
 
+func (rs *reactorSet) recoverReceive(reactorName string) {
+	if p := recover(); p != nil {
+		err := fmt.Errorf("panic: %+v", p)
+		rs.switchRef.Logger.Error("Panic during receive", "reactor", reactorName, "err", err)
+	}
+}
+
 // newReactorPriorityQueue creates a consumer pool for reactor.Receive()
 // It allows to dynamically adjust consumption concurrency based on the load,
 // while maintaining the priority, order, and latency of messages.
```

### lp2p/reactor_set_test.go
```diff
@@ -173,18 +173,65 @@ func TestReactorSet(t *testing.T) {
 		assert.Len(t, reactorA.receivedEnvelopes(), 1)
 		assert.Len(t, reactorB.receivedEnvelopes(), 0)
 	})
+
+	t.Run("recover", func(t *testing.T) {
+		// ARRANGE
+		ts := newReactorSetTestSuite(t)
+		rs := newReactorSet(ts.sw)
+
+		reactorA := ts.newReactor([]*conn.ChannelDescriptor{{ID: 0xE1}})
+
+		require.NoError(t, rs.Add(reactorA, "A"))
+		require.NoError(t, rs.Start(func(protocol.ID) {}))
+		t.Cleanup(rs.Stop)
+
+		// Given a reactor panic during receive
+		reactorA.OnReceive(func(e p2p.Envelope) {
+			panic("oops")
+		})
+
+		// ACT: receive for known reactor A
+		// It should panic
+		envelopeA := p2p.Envelope{
+			ChannelID: 0xE1,
+			Message:   &tmp2p.PexRequest{},
+		}
+
+		rs.Receive("A", "PexRequest", envelopeA, 5)
+
+		// ASSERT
+		// No panic the in the background workers
+		checkCalled := func() bool {
+			return len(reactorA.receivedEnvelopes()) == 1
+		}
+
+		require.Eventually(t, checkCalled, 2*time.Second, 10*time.Millisecond)
+
+		checkLogContainsPanic := func() bool {
+			if len(reactorA.receivedEnvelopes()) != 1 {
+				return false
+			}
+
+			return ts.logBuffer.HasMatchingLine("Panic during receive", "reactor=A", `err="panic: oops"`)
+		}
+
+		require.Eventually(t, checkLogContainsPanic, 2*time.Second, 10*time.Millisecond)
+	})
 }
 
 type reactorSetTestSuite struct {
-	t  *testing.T
-	sw *Switch
+	t         *testing.T
+	sw        *Switch
+	logBuffer *syncBuffer
 }
 
 type reactorMock struct {
 	p2p.BaseReactor
 
 	mu sync.Mutex
 
+	onReceive func(e p2p.Envelope)
+
 	channels     []*conn.ChannelDescriptor
 	addPeers     []p2p.Peer
 	initPeers    []p2p.Peer
@@ -205,8 +252,9 @@ func newReactorSetTestSuite(t *testing.T, opts ...testOption) *reactorSetTestSui
 	require.NoError(t, err)
 
 	return &reactorSetTestSuite{
-		t:  t,
-		sw: sw,
+		t:         t,
+		sw:        sw,
+		logBuffer: logBuffer,
 	}
 }
 
@@ -251,10 +299,20 @@ func (r *reactorMock) RemovePeer(peer p2p.Peer, _ any) {
 }
 
 func (r *reactorMock) Receive(e p2p.Envelope) {
+	r.mu.Lock()
+	r.received = append(r.received, e)
+	r.mu.Unlock()
+
+	if r.onReceive != nil {
+		r.onReceive(e)
+	}
+}
+
+func (r *reactorMock) OnReceive(handler func(e p2p.Envelope)) {
 	r.mu.Lock()
 	defer r.mu.Unlock()
 
-	r.received = append(r.received, e)
+	r.onReceive = handler
 }
 
 func (r *reactorMock) receivedEnvelopes() []p2p.Envelope {
```

### node/node.go
```diff
@@ -545,11 +545,6 @@ func NewNodeWithContext(
 		transport = cometTransport
 		sw = switcher
 	} else {
-		p2pLogger.Info("Using go-libp2p transport!")
-		if state.LastBlockHeight != 0 {
-			p2pLogger.Warn("EXPERIMENTAL: go-libp2p transport is enabled. Only enable this setting if it can be activated simultaneously for all validators on the network and peer IDs have been predetermined and exchanged.")
-		}
-
 		reactors := []lp2p.SwitchReactor{
 			{Name: "MEMPOOL", Reactor: mempoolReactor},
 			{Name: "BLOCKSYNC", Reactor: bcReactor},
@@ -572,6 +567,11 @@ func NewNodeWithContext(
 		if err != nil {
 			return nil, fmt.Errorf("unable to create libp2p switch: %w", err)
 		}
+
+		p2pLogger.Info("Using libp2p transport", "host_id", host.ID().String())
+		if state.LastBlockHeight != 0 {
+			p2pLogger.Warn("EXPERIMENTAL: go-libp2p transport is enabled. Only enable this setting if it can be activated simultaneously for all validators on the network and peer IDs have been predetermined and exchanged.")
+		}
 	}
 
 	node := &Node{
```
