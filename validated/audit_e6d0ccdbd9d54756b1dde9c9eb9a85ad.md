### Title
Unhandled panic in Gateway connector's `readLoop` handler dispatch can permanently kill message processing for a node's Gateway connection - (File: core/services/gateway/connector/connector.go)

### Summary
The Chainlink node's `GatewayConnector` reads incoming JSON-RPC messages from a Gateway in a dedicated goroutine and dispatches them directly to a registered `core.GatewayConnectorHandler.HandleGatewayMessage` implementation with no `recover()` wrapper. This mirrors the reported Chainlink-VRF class of bug ("a callback path that must not revert/panic, or the service stops retrying/processing") — here, a single malformed or adversarial message routed to a handler that panics will crash the `readLoop` goroutine for that Gateway connection, silently halting all further message processing (including for other, unrelated legitimate users/workflows) until the node is restarted.

### Finding Description
`readLoop` unmarshals the raw message, looks up the handler by JSON-RPC method, and calls it without any panic recovery: [1](#0-0) 

If `handler.HandleGatewayMessage` panics — e.g., due to an unchecked type assertion, slice/array indexing, or nil dereference triggered by attacker-supplied (unprivileged, internet-facing) request content — the panic propagates up through this goroutine. Because there is no `recover()` in `readLoop` (confirmed absent in `core/services/gateway/connector/connector.go`), the goroutine terminates, and per the `closeWait.Done()` deferred call, the connector's wait group is decremented but processing of that Gateway connection's inbound message stream stops entirely. No new messages from that Gateway will ever be handled again for the life of the process, exactly analogous to the "VRF service will not retry after a revert" class of bug: a single bad input causes a permanent denial of service for that channel with no automatic recovery.

Several concrete downstream handlers process attacker-influenced fields with limited defensive coding (e.g., string splitting and indexing on `resp.ID`/`req.ID` in `core/services/gateway/handlers/capabilities/v2/http_handler.go`, JSON unmarshalling of payloads in `core/services/gateway/handlers/capabilities/handler.go` `HandleLegacyUserMessage`), increasing the practical likelihood that a crafted message from an unprivileged client reaching the Gateway (and forwarded to the node) could trigger a panic in one of these code paths.

### Impact Explanation
A single crafted or malformed message from an unprivileged actor (any client able to reach the Gateway's public-facing endpoint and get routed to a node) can crash the node-side goroutine responsible for consuming all further messages from that Gateway. This is a availability/denial-of-service impact affecting the node's entire Gateway-mediated capability service (vault secrets, workflow triggers, HTTP actions, etc.) — not just the request that caused the panic — because the shared `readLoop` goroutine is torn down. Unlike the VRF report where "the game no longer continues" for that specific request stream, here it is the node's entire Gateway message-processing pipeline for that connection that stops responding to all users, until manual intervention/restart.

### Likelihood Explanation
Likelihood depends on the existence of a reachable panic condition in one of the many registered `HandleGatewayMessage` implementations, several of which parse and index attacker-influenced strings/JSON without full bounds/type checking. Given the breadth of handlers wired into this single dispatch loop (vault, capabilities, webapi, confidential relay), and that the dispatch code itself provides no blast-radius containment (no per-message `recover()`), the likelihood that some handler input can be crafted to panic is non-trivial, and the consequence (permanent loop death) is severe and directly matches the reported bug class.

### Recommendation
Wrap the handler invocation in `readLoop` with a `recover()` so that a panic in any individual `HandleGatewayMessage` call is caught, logged, and converted into an error response (or dropped) instead of terminating the goroutine that services the entire Gateway connection. Additionally, audit downstream handlers (e.g., `core/services/gateway/handlers/capabilities/v2/http_handler.go`, `core/services/gateway/handlers/capabilities/handler.go`) for unchecked type assertions, slice indexing, and JSON decoding of attacker-controlled input, and add defensive length/type checks. Consider adding integration tests analogous to `TestDispatcher_ReceiverPanicDoesNotKillLoop` (which already validates panic-recovery behavior for the capabilities dispatcher) for the Gateway connector's `readLoop`.

### Proof of Concept
Not executable within this analysis (no runtime/filesystem access). Conceptually:
1. An unprivileged client sends a request through the internet-facing Gateway HTTP endpoint (`gateway.ProcessRequest`, `core/services/gateway/gateway.go`) that is routed to a node via `SendToNode`.
2. The node's `gatewayConnector.readLoop` receives this message and dispatches it to the registered handler matching `req.Method` (e.g., a capabilities/http/vault handler) without a `recover()` guard: [2](#0-1) 
3. If the message content is crafted such that the target handler's parsing logic panics (e.g., malformed ID/params causing an out-of-bounds index or bad type assertion in a handler like the one in `core/services/gateway/handlers/capabilities/v2/http_handler.go`), the panic is unrecovered and crashes the `readLoop` goroutine.
4. All subsequent legitimate messages from that Gateway connection are silently dropped/never processed again, since the consuming goroutine no longer exists — this is confirmed unverified at the exact panic trigger site since full contents of `http_handler.go`'s ID-splitting logic were not completely retrieved due to index truncation; a Devin session with full repository access would be needed to confirm a concrete panicking input for that specific handler.

### Citations

**File:** core/services/gateway/connector/connector.go (L268-298)
```go
func (c *gatewayConnector) readLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		select {
		case <-c.shutdownCh:
			return
		case item := <-gatewayState.conn.ReadChannel():
			var req jsonrpc.Request[json.RawMessage]
			err := json.Unmarshal(item.Data, &req)
			if err != nil {
				c.lggr.Errorw("parse error when reading from Gateway", "id", gatewayState.config.ID, "err", err)
				break
			}
			c.handlersMu.RLock()
			handler, exists := c.handlers[req.Method]
			c.handlersMu.RUnlock()
			if !exists {
				c.lggr.Errorw("no handler for method", "id", gatewayState.config.ID, "method", req.Method)
				break
			}
			// do not break on error. HandleGatewayMessage handles errors
			// by sending a response back to the Gateway.
			err = handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
		}
	}
```
