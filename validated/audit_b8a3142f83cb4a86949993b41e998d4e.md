Confirmed: `readLoop` derives `ctx` from `c.shutdownCh.NewCtx()` [1](#0-0)  — this context only cancels on node shutdown, not per-message, so it never times out during normal operation. Every `HandleGatewayMessage` call for the trigger capability inherits this effectively unbounded context [2](#0-1) .

### Title
Unbounded blocking send in shared trigger dispatch loop lets one stalled workflow DoS delivery to all other workflows sharing a topic - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger` iterates sequentially over **all** registered workflow triggers (a shared, multi-tenant map) for every incoming gateway trigger message, and performs a blocking channel send to each matching trigger's consumer channel inside that shared loop. Any single workflow that stops draining its channel (maliciously or accidentally) can stall this loop indefinitely, because the `ctx` used to bound the blocking send is a connection/shutdown-scoped context that never expires during normal operation — not a per-request-bounded context.

### Finding Description
`RegisterTrigger` lets any workflow (an unprivileged caller relative to the node/gateway operator) register into the shared `h.registeredWorkflows` map with its own `allowedSenders`/`allowedTopics` and a bounded channel (`defaultSendChannelBufferSize = 1000`) [3](#0-2) .

For every incoming `MethodWebAPITrigger` message from any external sender, `processTrigger` snapshots all registered triggers and loops over them sequentially, and for each match it performs:

```go
trigger.chWriteMu.Lock()
...
select {
case <-ctx.Done():
    ...
case trigger.ch <- tr:
    ...
}
``` [4](#0-3) 

This send is only unblocked by the consumer draining `trigger.ch` or by `ctx.Done()`. The `ctx` passed all the way down originates in `gatewayConnector.readLoop`, which creates it once from `c.shutdownCh.NewCtx()` [1](#0-0)  and reuses it for every subsequent `HandleGatewayMessage` call for the lifetime of the connection [5](#0-4)  — it is not per-message and does not expire under normal operation.

Because `registeredWorkflows` is a single shared map iterated by one goroutine per incoming message (guarded only by `h.mu` while copying, then processed sequentially), once one workflow's channel buffer (1000 entries) fills up (e.g., that workflow never calls `RegisterTrigger`'s returned channel consumer, or is slow/compromised), any subsequent `trigger.ch <- tr` for that entry blocks the entire `for _, trigger := range triggers` loop. Since the `ctx` never cancels, the loop stalls indefinitely on the misbehaving/malicious entry, preventing delivery of trigger events to all other legitimately-matched workflows for that message and for the underlying node goroutine handling `readLoop`, which itself can affect subsequent gateway messages being read/dispatched.

This mirrors the report's bug class: a single, low-cost, permissionless registration into a shared allowlist/registry structure (`registeredWorkflows`, analogous to `erc20TokensToIncludeInFork`) that is iterated on behalf of many unrelated parties can be weaponized to deny service/delivery to all of them, because the shared iteration has no isolation or bounded-time guarantee per entry.

### Impact Explanation
A malicious or buggy workflow owner can register a trigger on a popular/shared topic and then simply never consume its `ch`. Once the 1000-entry buffer fills (trivially achievable by repeatedly sending valid trigger messages matching that topic), further trigger dispatch to that topic — and any subsequent trigger in the shared iteration — blocks indefinitely because the guarding context never expires. This denies delivery of trigger events to all other workflows subscribed to overlapping topics on that gateway/DON, a availability/DoS impact on the internet-facing trigger-handling path shared across all workflow owners connected through that node.

### Likelihood Explanation
Likelihood is moderate: it requires only the ability to register a workflow trigger (a normal, permissionless workflow-registration action) and to send enough matching trigger requests to exhaust the 1000-entry buffer without consuming it — no special privileges, contract governance, or majority vote is needed, unlike the original DAO scenario. This makes it easier to trigger than the referenced report's analog, though the effect is limited to the shared-topic subset of workflows processed while the stalled entry is being iterated.

### Recommendation
Do not perform blocking sends inside a loop that serves multiple unrelated tenants under a shared/long-lived context. Use a per-message-bounded context (with a short deadline) instead of the connection-lifetime `ctx`, and/or use a non-blocking send with a `default` branch that drops/logs and continues when a trigger's channel is full, so one stalled or malicious consumer cannot block delivery to all others sharing the iteration.

### Proof of Concept
1. Register workflow A with `AllowedTopics: ["shared_topic"]`, `AllowedSenders: [attacker]` via `RegisterTrigger`, and never read from the returned channel [6](#0-5) .
2. Register workflow B (victim) with `AllowedTopics: ["shared_topic"]`.
3. As `attacker`, send 1000+ `MethodWebAPITrigger` messages matching `"shared_topic"` through the gateway so workflow A's channel buffer fills.
4. Send one more matching message. `processTrigger`'s loop reaches workflow A's entry, blocks on `trigger.ch <- tr` because `ctx` (from `readLoop`) never cancels, and workflow B (iterated after A in map order on that call) never receives its trigger event for that message, and the `readLoop` goroutine for that gateway connection is stalled, delaying processing of subsequent incoming gateway messages as well [7](#0-6) [5](#0-4) .

### Citations

**File:** core/services/gateway/connector/connector.go (L270-271)
```go
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()
```

**File:** core/services/gateway/connector/connector.go (L273-296)
```go
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L98-156)
```go
	h.mu.Lock()
	triggers := slices.Collect(maps.Values(h.registeredWorkflows))
	h.mu.Unlock()

	// workflows that have matched topics
	matchedWorkflows := 0
	// workflows that have matched topic and passed all checks
	fullyMatchedWorkflows := 0
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
				TriggerEventID := body.Sender + payload.TriggerEventId

				// Emit trigger execution started event
				workflowExecutionID, genErr := events.GenerateExecutionID(trigger.workflowID, TriggerEventID)
				if genErr != nil {
					h.lggr.Errorw("failed to generate execution ID", "err", genErr)
					workflowExecutionID = ""
				}
				emitErr := events.EmitTriggerExecutionStarted(ctx, map[string]string{}, TriggerEventID, workflowExecutionID)
				if emitErr != nil {
					h.lggr.Errorw("failed to emit trigger execution started event", "err", emitErr)
				}

				tr := capabilities.TriggerResponse{
					Event: capabilities.TriggerEvent{
						TriggerType: TriggerType,
						ID:          TriggerEventID,
						Outputs:     wrappedPayload,
					},
				}
				trigger.chWriteMu.Lock()
				if trigger.ch == nil {
					trigger.chWriteMu.Unlock()
					return nil
				}
				select {
				case <-ctx.Done():
					trigger.chWriteMu.Unlock()
					return nil
				case trigger.ch <- tr:
					trigger.chWriteMu.Unlock()
					// Sending n topics that match a workflow with n allowedTopics, can only be triggered once.
					break
				}
			}
		}
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L212-269)
```go
func (h *triggerConnectorHandler) RegisterTrigger(ctx context.Context, req capabilities.TriggerRegistrationRequest) (<-chan capabilities.TriggerResponse, error) {
	cfg := req.Config
	if cfg == nil {
		return nil, errors.New("config is required to register a web api trigger")
	}

	reqConfig, err := h.ValidateConfig(cfg)
	if err != nil {
		return nil, err
	}

	if len(reqConfig.AllowedSenders) == 0 {
		return nil, errors.New("allowedSenders must have at least 1 entry")
	}

	h.mu.Lock()
	defer h.mu.Unlock()
	_, errBool := h.registeredWorkflows[req.TriggerID]
	if errBool {
		return nil, fmt.Errorf("triggerId %s already registered", req.TriggerID)
	}

	rateLimiterConfig := reqConfig.RateLimiter
	commonRateLimiter := ratelimit.RateLimiterConfig{
		GlobalRPS:      rateLimiterConfig.GlobalRPS,
		GlobalBurst:    int(rateLimiterConfig.GlobalBurst),
		PerSenderRPS:   rateLimiterConfig.PerSenderRPS,
		PerSenderBurst: int(rateLimiterConfig.PerSenderBurst),
	}

	rateLimiter, err := ratelimit.NewRateLimiter(commonRateLimiter)
	if err != nil {
		return nil, err
	}

	allowedSendersMap := map[string]bool{}
	for _, k := range reqConfig.AllowedSenders {
		allowedSendersMap[k] = true
	}

	allowedTopicsMap := map[string]bool{}
	for _, k := range reqConfig.AllowedTopics {
		allowedTopicsMap[k] = true
	}

	ch := make(chan capabilities.TriggerResponse, defaultSendChannelBufferSize)

	h.registeredWorkflows[req.TriggerID] = &webapiTrigger{
		workflowID:     req.Metadata.WorkflowID,
		allowedTopics:  allowedTopicsMap,
		allowedSenders: allowedSendersMap,
		ch:             ch,
		config:         *reqConfig,
		rateLimiter:    rateLimiter,
	}

	return ch, nil
}
```
