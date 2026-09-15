### Title
Unbounded loop over all registered web-api triggers, multiplied by attacker-controlled topic list, in `triggerConnectorHandler.processTrigger` allows gateway-message DoS - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger` handles every incoming `web_api_trigger` gateway message from an unauthenticated external caller (an "external initiator"-style webhook/gateway client) by iterating over **all** currently registered `web-api-trigger@1.0.0` workflow triggers, and for each trigger iterating over **all** attacker-supplied `payload.Topics`, performing an allowlist/rate-limit check inside the nested loop. Neither the number of registered triggers nor the size of the attacker-controlled `Topics` list is bounded, so the cost of a single incoming request scales with `O(registeredWorkflows × topics)`. This mirrors the dForce `calcAccountEquity` pattern: an unbounded, attacker-influenceable double loop reachable directly from an unprivileged request.

### Finding Description
`processTrigger` is invoked from `HandleGatewayMessage` for every message received on the gateway connector for method `MethodWebAPITrigger` [1](#0-0) . It snapshots the full set of currently registered triggers and loops over them, and for each registered trigger loops over every topic in the caller-supplied payload before doing any authorization check: [2](#0-1) 

Key points:
- `h.registeredWorkflows` grows without any documented cap — any workflow that registers a `web-api-trigger` capability adds an entry via `RegisterTrigger` [3](#0-2) . In a shared DON, many tenants' workflows can be registered concurrently, and this count is outside the control of the entity sending the trigger request.
- `payload.Topics` comes directly from the untrusted request body decoded in `HandleGatewayMessage` (`json.Unmarshal(body.Payload, &payload)`), with no length limit enforced before it is used as the inner loop bound [4](#0-3) .
- The sender allowlist check (`trigger.allowedSenders[sender.String()]`) and rate limiter check happen **inside** the nested loop, per topic per trigger, rather than being used to bound work up front — an unauthorized/unrelated caller still pays (and imposes) the full iteration cost for every topic against every registered trigger before being rejected.
- `HandleGatewayMessage` is invoked synchronously from the gateway connector's per-connection `readLoop`, which processes one JSON-RPC message at a time in a single goroutine per gateway connection [5](#0-4) . A slow `processTrigger` call therefore blocks processing of subsequent messages on that same gateway connection, not just the current caller's request.

This is a direct analog of the reported bug class: an unbounded loop over collateral/borrow positions in `Controller.calcAccountEquity`, reachable and inflatable by an unprivileged actor, causing costs to scale with attacker-controllable/shared state rather than being capped.

### Impact Explanation
An external, unauthenticated caller (any entity able to send a gateway message with method `web_api_trigger`, analogous to an external initiator hitting the internet-facing gateway) can:
1. Submit a large `Topics` array in a single trigger request.
2. Force the handler to iterate `len(registeredWorkflows) × len(Topics)` times on every such request, even for requests it is not authorized to trigger.

Because this runs synchronously in the connector's single-threaded per-gateway read loop, a sufficiently large request can starve or materially delay processing of trigger messages belonging to *other tenants' workflows* sharing the same gateway connection — a availability/DoS impact against unrelated users' triggers, not merely the attacker's own resource usage. This is consistent with the reported bug class's core harm (blocking legitimate operations for other users, e.g. liquidation in the original report; here, blocking other workflows' trigger delivery/execution).

### Likelihood Explanation
Likelihood is moderate: exploitation requires (a) a populated `registeredWorkflows` map with many active `web-api-trigger` registrations on the target DON/node (plausible in a busy multi-tenant deployment) and (b) the caller being able to submit an arbitrarily large `Topics` list in the request payload, which the code does not appear to bound before use. No special privilege is required to send a `web_api_trigger` gateway message — only a workflow's configured `AllowedSenders`/topics need not even match for the attacker to pay/impose the iteration cost, since the allowlist check happens only after topic match, deep inside the loop.

### Recommendation
- Enforce an explicit, configurable upper bound on `payload.Topics` length before entering the loop, rejecting oversized requests early.
- Index triggers by topic (e.g. `map[topic][]*webapiTrigger`) instead of doing an O(N×M) scan, so lookups are proportional to matching triggers rather than total registered triggers times submitted topics.
- Cap the number of `web-api-trigger` registrations a single node/DON will accept, or shard/rate-limit registration.
- Move authorization/rate-limit checks earlier, e.g. filter the sender against a precomputed sender→trigger index instead of checking `allowedSenders` on every topic iteration.
- Consider processing `HandleGatewayMessage` calls off the connector's synchronous read loop (e.g., dispatch to a bounded worker pool) so a single expensive message cannot delay delivery of subsequent, unrelated gateway messages.

### Proof of Concept
1. Register N workflows with `web-api-trigger@1.0.0` capabilities via `RegisterTrigger`, each with distinct `AllowedTopics`/`AllowedSenders` (N can be large in a busy shared DON).
2. As an unauthenticated external caller, send a `web_api_trigger` gateway message whose JSON payload contains a `Topics` array with M entries not present in most triggers' `allowedTopics` (so the check-and-skip path — the more expensive one relatively — is exercised) and a sender not present in `allowedSenders`.
3. Observe that `processTrigger` performs O(N×M) map lookups and rate limiter invocations synchronously inside the gateway connector's single message-processing goroutine before returning an error, delaying delivery of other queued/incoming gateway messages on that connection — comparable to how the dForce PoC pushed `calcAccountEquity` gas cost near the block limit by inflating loop counts.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L98-118)
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-200)
```go
func (h *triggerConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		h.lggr.Errorw("error validating message from request", "err", err, "request", req)
		return nil
	}
	body := &msg.Body
	sender := ethCommon.HexToAddress(body.Sender)
	var payload webapicap.TriggerRequestPayload
	err = json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw("error decoding payload", "err", err)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("error %s decoding payload", err.Error()).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
		return nil
	}

	switch body.Method {
	case ghcapabilities.MethodWebAPITrigger:
		resp := h.processTrigger(ctx, gatewayID, body, sender, payload)
		var response ghcapabilities.TriggerResponsePayload
		if resp == nil {
			response = ghcapabilities.TriggerResponsePayload{Status: "ACCEPTED"}
		} else {
			response = ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: resp.Error()}
			h.lggr.Errorw("Error processing trigger", "gatewayID", gatewayID, "body", body, "response", resp)
		}
		err = h.sendResponse(ctx, gatewayID, body, response)
		if err != nil {
			h.lggr.Errorw("Error sending response", "body", body, "response", response, "err", err)
		}
		return nil
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
