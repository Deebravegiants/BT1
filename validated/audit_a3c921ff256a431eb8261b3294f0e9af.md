### Title
Unbounded sequential fan-out to Vault DON nodes allows a single unresponsive node connection to stall/deny legitimate user vault requests - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
`fanOutToVaultNodes` in the Vault gateway handler sends a user's JSON-RPC request to every DON member sequentially via `h.don.SendToNode(ctx, node.Address, &ar.req)` in a plain `for` loop, with no per-node timeout and no concurrency bound on that call. [1](#0-0)  This mirrors the "gas griefing" pattern in the original report: an unbounded external interaction inside a loop, where one bad/slow participant consumes the available "resource" (there: gas; here: the caller's goroutine/time budget and the shared request context) and can prevent the loop from completing in time to serve the rest of the batch/queue — denying service to a legitimate request.

### Finding Description
The sibling `confidentialrelay` handler explicitly documents and fixes this exact class of bug: its `fanOutToNodes` uses `errgroup` to send to all DON members **concurrently** and bounds every send with a dedicated `sendCtx` derived from `context.WithTimeout(ctx, h.nodeSendTimeout)`, with an explicit comment stating why — "a node whose websocket accepts no writes blocks until its context is cancelled... an unbounded send would hold the request open." [2](#0-1)  The httpTriggerHandler for capabilities v2 similarly documents and enforces a per-node send timeout distinct from the overall request timeout specifically "so that a single slow or unresponsive node can't delay delivery to the rest of the DON." [3](#0-2) 

The Vault handler's `fanOutToVaultNodes`, in contrast, has neither of these protections:
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		...
	}
	...
}
``` [4](#0-3) 

`ctx` here is the caller/request-scoped context passed straight through, with no per-node `context.WithTimeout` and no goroutine fan-out (unlike the two handlers above). If `SendToNode` for one DON member blocks (e.g., a stalled websocket write, matching the `blockedDON`/`mockPingConn` scenarios explicitly tested for `confidentialrelay` and the gateway keepalive loop), the loop halts on that member and never reaches the remaining members, delaying delivery of the user's request to the rest of the DON until the overall request context expires (or indefinitely if the outer context has no deadline). This is functionally identical to the report's "one participant consumes the shared budget for everyone downstream in the loop" DoS class — except the resource exhausted is wall-clock/goroutine time rather than gas.

### Impact Explanation
Because the Vault handler serves unprivileged users' requests (secrets storage/retrieval operations reaching a quorum of DON members), a single DON member with a stuck connection (which could be triggered by network conditions or, in principle, targeted interference with that node's connection) can stall delivery of every subsequent vault request that is fanned out through this code path, since the loop is synchronous and blocking per node with no bound. This degrades availability of Vault requests DON-wide, not just for one caller, since `fanOutToVaultNodes` is invoked per active request and any given call can hang on the first slow member.

### Likelihood Explanation
Likelihood depends on whether a `SendToNode` call to a given member can actually block for a long/unbounded time on the underlying connection (websocket write). The codebase's own tests for the `confidentialrelay` and gateway keepalive-loop cases demonstrate this is a real, previously-encountered condition in this codebase (half-open TCP / stalled websocket writes), which is exactly why those two paths were hardened with per-node timeouts and concurrent fan-out. There is no equivalent regression test or timeout for the Vault path, so the same stall condition is plausible here too.

### Recommendation
Apply the same fix pattern already used elsewhere in the gateway: fan out to Vault DON members concurrently (e.g., via `errgroup`, as `confidentialrelay.fanOutToNodes` does) and bound each `SendToNode` call with its own `context.WithTimeout` distinct from (and smaller than) the overall request timeout, so one unresponsive node cannot block delivery to, or the response for, the rest of the DON. [2](#0-1) 

### Proof of Concept
1. Configure a Vault DON with N members where one member's connection (`don.SendToNode`) never returns (analogous to the `blockedDON`/`mockPingConn` test helpers used for `confidentialrelay` and the keepalive loop). [5](#0-4) [6](#0-5) 
2. Issue a legitimate user vault request that triggers `fanOutToVaultNodes`.
3. Observe that `fanOutToVaultNodes` blocks on the stuck member's `SendToNode` call, and never reaches the healthy remaining members, exactly as reproduced for the sibling handlers before their fixes (`TestConfidentialRelayHandler_BlockedNodeDoesNotStallFanOut`, `TestKeepAliveLoop_StuckNodeBlocksAll`). [7](#0-6) [8](#0-7) 

Note: I could not find an existing regression test specifically for `fanOutToVaultNodes` confirming the exact blocking behavior of `h.don` implementations in production (e.g., whether the real `SendToNode` websocket write always eventually times out at a lower layer). This should be verified in the actual DON connection manager implementation before treating this as fully confirmed exploitable, though the structural absence of a per-node timeout/concurrency bound, in contrast to the two hardened sibling handlers, is clearly established from the code itself.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L736-752)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}

	l.Debugw("successfully forwarded request to Vault nodes")
	return nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L686-710)
```go
func (h *handler) fanOutToNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var (
		group      errgroup.Group
		nodeErrors atomic.Uint32
	)

	// Each send is bounded independently. A node whose websocket accepts no writes blocks
	// until its context is cancelled, and because the caller only reads the response callback
	// after this function returns, an unbounded send would hold the request open until the
	// client gives up, discarding a bundle that already reached quorum.
	sendCtx, cancel := context.WithTimeout(ctx, h.nodeSendTimeout)
	defer cancel()

	for _, node := range h.donConfig.Members {
		group.Go(func() error {
			err := h.don.SendToNode(sendCtx, node.Address, &ar.req)
			if err != nil {
				nodeErrors.Add(1)
				l.Errorw("error sending request to node", "node", node.Address, "error", err)
			}
			return nil
		})
	}

	_ = group.Wait()
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L634-643)
```go
// sendWithRetries fans the request out to every shard the workflow is assigned
// to, running an independent per-shard retry loop in parallel. Each per-shard
// loop sends to that shard's members via the shard's own connection manager,
// retrying failed nodes until all succeed or the max trigger request duration
// is reached. Each send attempt is bounded by a per-node timeout, smaller than
// the overall request duration, so that a single slow or unresponsive node can't
// delay delivery to the rest of the DON.
// doneCh is closed when the callback has been responded to (first shard reaches
// quorum), allowing immediate termination of all shard loops.
func (h *httpTriggerHandler) sendWithRetries(ctx context.Context, legacyExecutionID, executionIDWithTriggerIndex string, req *jsonrpc.Request[json.RawMessage], workflowID string, doneCh <-chan struct{}) error {
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L60-79)
```go
}

// blockedDON models a node whose websocket accepts no writes: the send to blockedAddr blocks
// until its context is cancelled, while every other node returns immediately.
type blockedDON struct {
	blockedAddr string
	mu          sync.Mutex
	delivered   []string
}

func (d *blockedDON) SendToNode(ctx context.Context, addr string, _ *jsonrpc.Request[json.RawMessage]) error {
	if addr == d.blockedAddr {
		<-ctx.Done()
		return ctx.Err()
	}
	d.mu.Lock()
	d.delivered = append(d.delivered, addr)
	d.mu.Unlock()
	return nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L1178-1229)
```go
// A node that never drains its socket must not hold the request open. Before the per-send
// bound, group.Wait blocked until the caller's context expired, and because the gateway only
// reads the response callback after the handler returns, a bundle that had already reached
// quorum was discarded in favour of a client timeout.
func TestConfidentialRelayHandler_BlockedNodeDoesNotStallFanOut(t *testing.T) {
	t.Parallel()
	lggr := logger.Test(t)
	don := &blockedDON{blockedAddr: "0x0002"}
	donConfig := &config.DONConfig{
		DonID: "test_relay_don",
		F:     1,
		Members: []config.NodeConfig{
			{Name: "node0", Address: "0x0000"},
			{Name: "node1", Address: "0x0001"},
			{Name: "node2", Address: "0x0002"},
			{Name: "node3", Address: "0x0003"},
		},
	}

	methodConfig, err := json.Marshal(Config{RequestTimeoutSec: 30})
	require.NoError(t, err)
	limitsFactory := limits.Factory{Settings: cresettings.DefaultGetter, Logger: lggr}
	h, err := NewHandler(methodConfig, donConfig, don, lggr, clockwork.NewFakeClock(), limitsFactory)
	require.NoError(t, err)
	// Shortened so the test exercises the bound without waiting the production default.
	h.nodeSendTimeout = 50 * time.Millisecond

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-blocked-node",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	done := make(chan error, 1)
	start := time.Now()
	go func() {
		done <- h.HandleJSONRPCUserMessage(t.Context(), req, common.NewCallback())
	}()

	select {
	case fanOutErr := <-done:
		// Three of four nodes still received the request, so quorum remains possible and the
		// blocked node is reported as a node error rather than a request failure.
		require.NoError(t, fanOutErr)
	case <-time.After(5 * time.Second):
		t.Fatal("fan-out stalled on the blocked node instead of bounding the send")
	}

	assert.Less(t, time.Since(start), h.requestTimeout, "fan-out must return well inside the request timeout")
	assert.Equal(t, 3, don.deliveredCount(), "healthy nodes should all receive the request")
}
```

**File:** core/services/gateway/keepalive_loop_internal_test.go (L37-50)
```go
func (m *mockPingConn) Write(ctx context.Context, msgType int, _ []byte) error {
	if msgType == websocket.PingMessage {
		m.pingCount.Add(1)
	}
	if m.unblock != nil {
		select {
		case <-m.unblock:
			return nil
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	return nil
}
```

**File:** core/services/gateway/keepalive_loop_internal_test.go (L52-122)
```go
// TestKeepAliveLoop_StuckNodeDoesBlocksAll
// this reproduces a bug in which one stall node blocks pings to all nodes.
// This leads to a wrong representation of the communication between nodes and gateway, making it harder to diagnose an incident.
//
// Before the keepaliveLoop used to ping nodes sequentially with no per-node timeout. If one
// node's Write blocked (half-open TCP), the loop stalls and no other node
// receives pings.
func TestKeepAliveLoop_StuckNodeBlocksAll(t *testing.T) {
	if testing.Short() {
		t.Skip("too slow for testing.Short")
	}

	t.Parallel()

	lggr := logger.Test(t)
	gMetrics, err := monitoring.NewGatewayMetrics()
	require.NoError(t, err)

	unblock := make(chan struct{})
	t.Cleanup(func() { close(unblock) })

	stuckConn := &mockPingConn{unblock: unblock}
	healthyConns := make([]*mockPingConn, 3)
	mockNodes := make(map[string]*nodeState, 4)
	mockNodes["0xstuck"] = &nodeState{name: "stuck", conn: stuckConn}
	for i := range healthyConns {
		healthyConns[i] = &mockPingConn{}
		mockNodes["0xhealthy"+string(rune('0'+i))] = &nodeState{
			name: "healthy_" + string(rune('0'+i)),
			conn: healthyConns[i],
		}
	}

	donMgr := &donConnectionManager{
		donConfig:  &config.DONConfig{DonID: "test_don"},
		nodes:      mockNodes,
		handlers:   nil,
		closeWait:  sync.WaitGroup{},
		shutdownCh: make(services.StopChan),
		gMetrics:   gMetrics,
		lggr:       lggr,
	}

	// Start the keepalive loop directly with a 1-second interval.
	const heartbeatSec = 1
	donMgr.closeWait.Add(len(donMgr.nodes))
	for nodeAddress, nodeState := range donMgr.nodes {
		go donMgr.nodeKeepalive(nodeAddress, nodeState, heartbeatSec)
	}

	// Let at least 2 ticks fire. With the bug, the loop is stuck on the
	// first node and never reaches the healthy nodes. With the fix,
	// healthy nodes get pinged each tick.
	time.Sleep(3 * time.Second)

	// --- Check ping counts BEFORE stopping the loop ---
	//
	// BEFORE the fix (sequential, no per-node timeout):
	//   The loop calls Write on "0xstuck" first. It blocks on unblock.
	//   The loop never reaches the healthy nodes.
	//   → all healthyConns have pingCount == 0 → test FAILS.
	//
	// AFTER the fix (per-node timeout or concurrent sends):
	//   Each node is pinged independently. The stuck node blocks/times out
	//   but healthy nodes still receive pings.
	//   → all healthyConns have pingCount >= 1 → test PASSES.
	for i, hc := range healthyConns {
		pings := hc.pingCount.Load()
		t.Logf("healthy_%d: %d pings", i, pings)
		require.Positive(t, pings, "healthy node %d received 0 pings — keepaliveLoop is stuck on the blocked node", i)
	}
```
