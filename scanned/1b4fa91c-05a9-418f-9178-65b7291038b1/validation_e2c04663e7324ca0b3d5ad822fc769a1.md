## Title
Unbounded loop over all registered workflow triggers on every Gateway-forwarded WebAPI trigger message causes DoS - (File: `core/capabilities/webapi/trigger/trigger.go`)

### Summary
The NFTX report describes a `distribute()` function that loops over an unbounded, ever-growing `feeReceivers` list on every fee-distribution call, letting the receiver count control the gas/time cost of a routine operation and eventually blocking user-facing token operations. The Chainlink analog is `triggerConnectorHandler.processTrigger` in `core/capabilities/webapi/trigger/trigger.go`, which iterates over the entire in-memory `registeredWorkflows` map (and, nested, every topic in the incoming payload) on **every single inbound Gateway message**, with no cap on how many workflows can be registered.

### Finding Description
`triggerConnectorHandler` keeps all currently registered WebAPI triggers in `h.registeredWorkflows map[string]*webapiTrigger`, populated by `RegisterTrigger` with no upper bound check on the number of entries: [1](#0-0) 

Every message coming in from the Gateway connector is dispatched to `HandleGatewayMessage`, which for the `MethodWebAPITrigger` method calls `processTrigger`: [2](#0-1) 

`processTrigger` snapshots and then iterates over **all** registered triggers, and for each trigger iterates over **all** topics in the attacker-supplied payload, doing string map lookups, rate-limit checks, execution-ID generation, and event emission for every match: [3](#0-2) 

This is structurally identical to the NFTX `distribute()` pattern: a list that can only grow (`feeReceivers` / `registeredWorkflows`), traversed in full on every externally triggered operation, with per-entry work (`_sendForReceiver` / event emission + channel send) that is not bounded by any pagination, batch limit, or entry cap. The Gateway message path (`core/services/gateway/gateway.go:ProcessRequest` → connector `readLoop` → `HandleGatewayMessage`) is the internet-facing ingress point reachable by any client able to reach the Gateway, matching the unprivileged-actor / gateway-handler scope. [4](#0-3) 

### Impact Explanation
As the number of workflows registered for the WebAPI trigger capability grows on a node (which is expected to increase over time as more workflows subscribe, analogous to NFTX's "NFTX team adds a feature... number of receivers grows dramatically" scenario), the cost of `processTrigger` grows linearly (or with topic count, super-linearly) with no bound. Because this executes synchronously inside the Gateway message handling path for *every* incoming trigger message, a large registered-workflow set turns ordinary trigger traffic into a CPU/latency amplifier, and a flood of trigger messages (each cheap to send) can be used to repeatedly force full-list traversals, degrading or blocking Gateway message processing for all workflows/tenants sharing that node — a denial-of-service condition consistent with the reported bug class.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment where the number of registered WebAPI-trigger workflows is large, since there is no limit enforced in `RegisterTrigger` and no batching/pagination in `processTrigger`. Any client capable of sending a `MethodWebAPITrigger` message through the Gateway (the intended, internet-facing entry point for this capability) can trigger the full-list traversal repeatedly at will, without needing to be an authorized sender for any of the registered workflows (the sender/topic checks happen *inside* the loop, after the cost of iterating has already been paid).

### Recommendation
- Short term: cap the number of concurrently registered triggers per node/DON and add per-request bounds (e.g., limit `topics` length) to `processTrigger`; consider indexing triggers by topic (`map[topic][]*webapiTrigger`) instead of a full scan, to make lookup cost proportional to matches rather than total registrations.
- Long term: redesign trigger dispatch to avoid O(n·m) full scans on the hot path — e.g., build a topic→trigger index maintained incrementally in `RegisterTrigger`/`UnregisterTrigger`, and rate-limit/queue Gateway-sourced trigger messages independent of per-workflow rate limiters so a large registration set cannot be leveraged to degrade the shared Gateway message-handling path.

### Proof of Concept
1. Register many WebAPI trigger workflows via `RegisterTrigger` (no cap enforced) so `h.registeredWorkflows` grows large.
2. From the Gateway ingress, send `MethodWebAPITrigger` messages (`core/services/gateway/gateway.go:ProcessRequest` → connector `readLoop` → `triggerConnectorHandler.HandleGatewayMessage`) with a payload containing an arbitrary, non-matching `Topics` list.
3. Each such message forces `processTrigger` to iterate the entire `registeredWorkflows` snapshot × topics before returning `"no Matching Workflow Topics"`, consuming CPU proportional to the registration count regardless of the caller's authorization for any specific workflow.
4. Repeating step 2 at volume amplifies cost linearly with the registered-workflow count, degrading Gateway message processing for all workflows on the node.

### Citations

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

**File:** core/capabilities/webapi/trigger/trigger.go (L167-201)
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

**File:** core/services/gateway/connector/connector.go (L268-296)
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
```
