### Title
Sequential, unbounded per-node fan-out in the Vault gateway handler lets one blocked node stall responses to legitimate secret requests - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
`fanOutToVaultNodes` sends a user's Vault (secrets) request to every DON member sequentially using `SendToNode`, without a per-node timeout, unlike the sibling fan-out implementations in the codebase (`confidentialrelay` handler and `http_trigger_handler`) which explicitly bound each node send with its own context timeout to avoid exactly this problem.

### Finding Description
`(h *handler) fanOutToVaultNodes` loops over `h.donConfig.Members` and calls `h.don.SendToNode(ctx, node.Address, &ar.req)` synchronously for each node, with no `context.WithTimeout` wrapping the individual send: [1](#0-0) 

`SendToNode` ultimately calls `nodeState.conn.Write(ctx, ...)` on the node's websocket connection: [2](#0-1) 

If any single node's underlying websocket write blocks (e.g., half-open TCP connection, slow/unresponsive node, full send buffer, or a node that never drains its socket), the loop stalls on that node and never proceeds to send the request to the remaining, healthy nodes — until the overall request context (`ctx`, the caller's request deadline) is cancelled. This is the same bug class as the reported liquidation issue: a single unresponsive/blocked participant in a loop over multiple independent targets prevents processing/delivery to every other participant, denying service that should otherwise succeed.

This is directly analogous to a bug that was already found and fixed elsewhere in this same codebase: the DON keepalive loop (`nodeKeepalive`) previously pinged nodes sequentially with no per-node timeout, and a stuck node would block pings to all other nodes — the fix added a per-node `context.WithTimeout` around each `Write` call: [3](#0-2) 

The confidentialrelay handler's fan-out and the HTTP trigger handler's fan-out have both been hardened against this exact class of bug by bounding each node send independently (and, in the confidentialrelay case, sending concurrently): [4](#0-3) [5](#0-4) 

`fanOutToVaultNodes` in the Vault handler was not updated to match this pattern, leaving it exposed to the same stall.

### Impact Explanation
An unprivileged workflow/client submitting a Vault secrets request (create/get/etc.) reaches `fanOutToVaultNodes` on the gateway. If any one DON node in the Vault DON has a stalled/blocked connection (which is plausible under normal network conditions — half-open TCP, congested socket, slow consumer — not requiring a malicious actor), the entire fan-out for that request stalls, and no other (healthy) node in the DON receives the request at all until the caller's context expires. This delays or fails legitimate secret operations for all users routed through that gateway/DON, i.e., a request-level denial of service triggered by an ordinary unprivileged-reachable request path, not a malicious actor.

### Likelihood Explanation
Moderate. It does not require an attacker; any transient connectivity issue with a single node (which the codebase's own keepalive-loop bug report/fix acknowledges as a realistic occurrence — "half-open TCP") is sufficient to trigger the stall. The bug is deterministic once a node's `Write` blocks, and the existing test-proven pattern for the keepalive loop analog (`TestKeepAliveLoop_StuckNodeBlocksAll`) demonstrates this exact failure mode occurs in this codebase's connection-handling code without per-send timeouts.

### Recommendation
Bound each `SendToNode` call in `fanOutToVaultNodes` with an independent `context.WithTimeout` (mirroring the fix already applied to `nodeKeepalive` and the pattern used in `confidentialrelay.fanOutToNodes` / `http_trigger_handler.sendToShard`), and/or send to nodes concurrently via goroutines/errgroup so that one blocked node cannot delay delivery to the rest of the DON.

### Proof of Concept
1. Configure a Vault DON with N members.
2. Cause one member's websocket connection to stop draining its socket (as simulated by `mockPingConn.Write` blocking on an unblock channel in the existing keepalive test).
3. Submit a legitimate Vault secrets request from an unprivileged client; observe that `fanOutToVaultNodes` never sends the request to the other N-1 healthy nodes until the request's context is cancelled, because the loop in `core/services/gateway/handlers/vault/handler.go:736-752` is sequential and unbounded per node, unlike the fixed `nodeKeepalive` loop in `core/services/gateway/connectionmanager.go:427-441`.

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

**File:** core/services/gateway/connectionmanager.go (L367-380)
```go
func (m *donConnectionManager) SendToNode(ctx context.Context, nodeAddress string, req *jsonrpc.Request[json.RawMessage]) error {
	if req == nil {
		return errors.New("nil request")
	}
	data, err := jsonrpc.EncodeRequest(req)
	if err != nil {
		return fmt.Errorf("error encoding request for node %s: %w", nodeAddress, err)
	}
	nodeState := m.nodes[nodeAddress]
	if nodeState == nil {
		return fmt.Errorf("node %s not found", nodeAddress)
	}
	return nodeState.conn.Write(ctx, websocket.BinaryMessage, data)
}
```

**File:** core/services/gateway/connectionmanager.go (L427-441)
```go
	for {
		select {
		case <-m.shutdownCh:
			return
		case <-ticker.C:
			// Per-node write with a timeout context
			pingCtx, pingCancel := context.WithTimeout(ctx, 5*time.Second)
			err := ns.conn.Write(pingCtx, websocket.PingMessage, []byte{})
			pingCancel()
			m.gMetrics.RecordKeepalivePingsSent(ctx, addr, ns.name, err == nil)
			if err != nil {
				m.lggr.Debugw("unable to send keepalive ping to node",
					"nodeAddress", addr, "name", ns.name, "err", err)
			}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L697-726)
```go
	for {
		var pending []string
		for _, member := range shard.members {
			if !successfulNodes[member.Address] {
				pending = append(pending, member.Address)
			}
		}

		// Buffered so every goroutine can send its result and exit without waiting on a reader.
		results := make(chan nodeSendResult, len(pending))
		var wg sync.WaitGroup
		for _, nodeAddress := range pending {
			wg.Add(1)
			go func(nodeAddress string) {
				defer wg.Done()

				nodeCtx, nodeCancel := context.WithTimeout(ctx, nodeTimeout)
				defer nodeCancel()

				h.metrics.IncrementTriggerCapabilityRequestCount(ctx, nodeAddress, gateway_common.MethodWorkflowExecute, h.lggr)
				sendStart := time.Now()
				err := shard.connMgr.SendToNode(nodeCtx, nodeAddress, req)
				h.metrics.RecordGatewayToNodeLatency(ctx, time.Since(sendStart).Milliseconds(), nodeAddress, gateway_common.MethodWorkflowExecute, h.lggr)
				if err != nil {
					h.metrics.IncrementTriggerCapabilityRequestFailures(ctx, nodeAddress, gateway_common.MethodWorkflowExecute, h.lggr)
				}
				results <- nodeSendResult{nodeAddress: nodeAddress, err: err}
			}(nodeAddress)
		}
		wg.Wait()
```
