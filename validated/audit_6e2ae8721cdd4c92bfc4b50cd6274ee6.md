Audit Report

## Title
Sequential, unbounded per-node fan-out in the Vault gateway handler lets one blocked node stall responses to legitimate secret requests - ([File: core/services/gateway/handlers/vault/handler.go])

## Summary
`fanOutToVaultNodes` iterates over all DON members and calls `h.don.SendToNode(ctx, node.Address, &ar.req)` synchronously in a loop, using only the caller's request-scoped `ctx` with no independent per-node timeout. [1](#0-0)  This differs from the confidentialrelay and HTTP-trigger fan-out implementations, which bound each node send with its own timeout and/or dispatch concurrently. [2](#0-1) 

## Finding Description
`SendToNode` forwards to `nodeState.conn.Write(ctx, ...)`, which is implemented by `wsConnectionWrapper.Write` in `core/services/gateway/network/wsconnection.go`. [3](#0-2)  That `Write` implementation first attempts to push the message onto an unbuffered `writeCh`, which is drained by a single `writePump` goroutine per connection that calls the blocking `conn.WriteMessage` synchronously. [4](#0-3)  If a node's underlying TCP write blocks (half-open connection, congested socket, unresponsive peer), the `writePump` for that node stalls, `writeCh` fills, and any subsequent `Write` call for that same node blocks on the first `select` until either `ctx.Done()` or `shutdownCh` fires. Since `fanOutToVaultNodes` passes the same long-lived request `ctx` to every node with no per-node `context.WithTimeout`, the loop over `h.donConfig.Members` blocks at the stuck node and never proceeds to send to the remaining, healthy nodes until the overall request context is cancelled. [5](#0-4) 

This is the same bug class already identified and fixed in `nodeKeepalive`, where a per-node `context.WithTimeout` was added specifically to prevent one stuck node from blocking pings to all others. [6](#0-5)  The confidentialrelay handler and the HTTP trigger handler have both been hardened against exactly this failure mode by bounding each node send independently and/or sending concurrently. [2](#0-1) [7](#0-6)  The Vault handler was not updated to match this pattern.

No existing auth/role check mitigates this: the fan-out is reached by any legitimate, unprivileged user request to the Vault gateway handler (e.g., `handlePublicKeyGet` calls `fanOutToVaultNodes` directly), so the vulnerable code path is reachable without any elevated privileges. [8](#0-7) 

## Impact Explanation
An unprivileged client's Vault secrets request (e.g., public key get, create/get secret) reaches `fanOutToVaultNodes`. If any single DON node has a stalled/blocked websocket write (a plausible, non-malicious condition such as half-open TCP or a slow consumer — the same condition the codebase's own keepalive fix explicitly targets), the entire fan-out stalls on that node and no other node in the DON receives the forwarded request until the caller's context expires. This causes a request-level denial of service for legitimate Vault operations routed through that gateway/DON — an in-scope availability impact affecting the delivery of legitimate secret requests, without requiring any malicious actor.

## Likelihood Explanation
Moderate. No attacker action is required — an ordinary transient connectivity fault on one DON node is sufficient, and the mechanism is deterministic once a node's write blocks. The codebase's own analogous, already-fixed bug (`nodeKeepalive`/`TestKeepAliveLoop_StuckNodeBlocksAll`) demonstrates this exact failure mode is realistic in this connection-handling stack, and the Vault fan-out loop was not given the equivalent fix.

## Recommendation
Bound each `SendToNode` call in `fanOutToVaultNodes` with an independent `context.WithTimeout` (mirroring the fix in `nodeKeepalive` and the pattern in `confidentialrelay.fanOutToNodes` / `http_trigger_handler`'s per-node timeout), and/or fan out to nodes concurrently (e.g., via `errgroup` or goroutines + `sync.WaitGroup`) so a single blocked node cannot delay delivery to the rest of the DON.

## Proof of Concept
1. Configure a Vault DON with N members, using the existing `wsConnectionWrapper`/`donConnectionManager` stack.
2. Simulate one node's connection stalling on write, analogous to the existing `mockPingConn.Write`-blocking pattern used in `TestKeepAliveLoop_StuckNodeBlocksAll` — e.g., have the underlying `conn.WriteMessage` for one member's connection block indefinitely on an unblock channel.
3. Submit a legitimate Vault request (e.g., public key get) from an unprivileged client that reaches `handlePublicKeyGet` → `fanOutToVaultNodes` in `core/services/gateway/handlers/vault/handler.go:736-752`.
4. Observe that `SendToNode` for the remaining N-1 healthy members is never invoked until the request's `ctx` is cancelled, because the loop is sequential and each `SendToNode` call shares the unbounded request context rather than an independent per-node timeout — unlike the fixed `nodeKeepalive` loop in `core/services/gateway/connectionmanager.go:427-441`.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L692-707)
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		l.Debugw("returning cached public key response")
		return h.sendSuccessResponse(ctx, l, ar, &jsonrpc.Response[json.RawMessage]{
			Version: jsonrpc.JsonRpcVersion,
			ID:      ar.req.ID,
			Method:  ar.req.Method,
			Result:  (*json.RawMessage)(&publicKeyResponseBytes),
		})
	}

	l.Debugw("cache stale: forwarding request to nodes", "now", h.clock.Now())
	return h.fanOutToVaultNodes(ctx, l, ar)
```

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

**File:** core/services/gateway/network/wsconnection.go (L123-195)
```go
func (c *wsConnectionWrapper) Write(ctx context.Context, msgType int, data []byte) error {
	errCh := make(chan error, 1)
	// push to write channel
	select {
	case c.writeCh <- writeItem{msgType, data, errCh}:
		break
	case <-c.shutdownCh:
		return ErrWrapperShutdown
	case <-ctx.Done():
		return ctx.Err()
	}
	// wait for write result
	select {
	case err := <-errCh:
		return err
	case <-c.shutdownCh:
		return ErrWrapperShutdown
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (c *wsConnectionWrapper) ReadChannel() <-chan ReadItem {
	return c.readCh
}

func (c *wsConnectionWrapper) IsConnected() bool {
	return c.conn.Load() != nil
}

func (c *wsConnectionWrapper) Close() error {
	return c.StopOnce("WSConnectionWrapper", func() error {
		close(c.shutdownCh)
		c.Reset(nil)
		c.wg.Wait()
		return nil
	})
}

func (c *wsConnectionWrapper) writePump() {
	defer c.wg.Done()
	for {
		select {
		case wsMsg := <-c.writeCh:
			// synchronization is a tradeoff for the ability to use a single write channel
			conn := c.conn.Load()
			if conn == nil {
				wsMsg.ErrCh <- ErrNoActiveConnection
				close(wsMsg.ErrCh)
				break
			}
			err := conn.WriteMessage(wsMsg.MsgType, wsMsg.Data)
			if err != nil {
				c.lggr.Errorw("failed to write message", "msgType", wsMsg.MsgType, "dataLen", len(wsMsg.Data), "error", err)
				// A write failure (e.g. i/o timeout on a half-open TCP session) does not
				// produce a read error, so readPump would stay blocked and reconnectLoop
				// would never get the closeCh signal it needs to redial. Close the conn
				// here to unblock readPump and trigger the existing reconnect path.
				// If CAS fails, Reset already swapped the pointer and will close the old
				// conn itself — don't close it twice.
				if c.conn.CompareAndSwap(conn, nil) {
					if closeErr := conn.Close(); closeErr != nil {
						c.lggr.Errorw("error closing connection after write failure", "error", closeErr)
					}
				}
			}
			wsMsg.ErrCh <- err
			close(wsMsg.ErrCh)
		case <-c.shutdownCh:
			return
		}
	}
}
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
