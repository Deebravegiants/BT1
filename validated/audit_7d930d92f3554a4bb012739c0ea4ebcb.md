## Analysis

`BasicSpell.addStrategy()`'s flaw is that it lets the same underlying resource (vault) be registered multiple times under different strategy IDs, so per-instance limits (`maxPositionSize`) can be bypassed because each instance tracks its own limit while the underlying resource's balance is shared/summed.

The closest reachable analog in this codebase is in the Web API trigger registration path exposed through the gateway, in `triggerConnectorHandler.RegisterTrigger` in `core/capabilities/webapi/trigger/trigger.go`.

### Title
Duplicate Web API trigger registrations for the same workflow bypass per-sender rate limiting and cause duplicated trigger execution - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`RegisterTrigger` only rejects a registration if the exact same `req.TriggerID` already exists [1](#0-0) . It never checks whether another `webapiTrigger` already exists for the same `req.Metadata.WorkflowID` (or the same `allowedTopics`/`allowedSenders` combination). Each successful registration allocates its own independent `ratelimit.RateLimiter` instance [2](#0-1) , keyed only within that single trigger object. `processTrigger`, which handles inbound gateway messages from external HTTP senders, iterates over *all* registered triggers and independently checks each one's rate limiter and allowed senders/topics before forwarding the event to that trigger's channel [3](#0-2) .

### Finding Description
This mirrors the `BasicSpell.addStrategy()` bug class exactly: a resource-scoped invariant (per-workflow, per-sender rate limit) is enforced only at the granularity of a distinct identifier (`TriggerID`/`strategyId`) instead of the actual underlying resource (workflow/vault). Since nothing prevents two (or many) `TriggerRegistrationRequest`s from being submitted for the same `WorkflowID` with different `TriggerID`s but identical `AllowedSenders`/`AllowedTopics`, an attacker (or a buggy/duplicated registration flow) can create N independent `webapiTrigger` instances for the same workflow, each with its own fresh `PerSenderRPS`/`PerSenderBurst` allowance [4](#0-3) .

When an external HTTP sender's message reaches the gateway and is routed to `HandleGatewayMessage` → `processTrigger` [5](#0-4) , the loop checks *every* registered trigger matching the topic, independently validating `allowedSenders` and calling `trigger.rateLimiter.Allow(body.Sender)` per trigger instance [6](#0-5) . Because each duplicate trigger has its own rate limiter, the effective per-sender rate limit for that workflow becomes N times the configured limit. Worse, each fully-matched trigger independently emits a `TriggerResponse` to its own channel, meaning a single inbound HTTP request can cause the same underlying workflow to be started multiple times (once per duplicate registration) rather than once, since `fullyMatchedWorkflows` can exceed 1 for what should be a single logical trigger.

### Impact Explanation
- Rate limiting intended to protect a workflow trigger from an external, unprivileged HTTP sender can be inflated arbitrarily by registering additional duplicate trigger instances for the same workflow, defeating the configured `PerSenderRPS`/`PerSenderBurst`/`GlobalRPS` protections.
- A single external request can cause multiple workflow executions to start (amplification), consuming compute/gas resources disproportionately and potentially causing duplicate side effects for one logical trigger event.
- This is reachable purely through the standard, unprivileged workflow-registration and gateway-trigger-invocation flow — no node/peer compromise required.

### Likelihood Explanation
Registration of `webapiTrigger`s originates from workflow specs / capability registration calls that are not restricted to be singular per workflow; the only uniqueness check is on the caller-supplied `TriggerID` string [7](#0-6) , which is trivially different across calls. Any code path (legitimate retry logic, a compromised/careless workflow owner, or a malicious workflow spec) that calls `RegisterTrigger` more than once for the same `WorkflowID`/topics combination triggers this.

### Recommendation
Enforce uniqueness of trigger registration at the `WorkflowID` (and/or `AllowedTopics`/`AllowedSenders`) level, not solely on the caller-supplied `TriggerID`. Before inserting into `registeredWorkflows`, check whether an existing entry already maps to the same `req.Metadata.WorkflowID` and reject (or replace) the registration rather than silently allowing an additional independent instance, analogous to how `BasicSpell.addStrategy()` should validate against the vault address instead of an opaque strategy ID.

### Proof of Concept
1. A workflow owner (or an unprivileged caller of the capability registration path) calls `RegisterTrigger` twice for the same `WorkflowID` and `AllowedTopics`/`AllowedSenders`, using two different `TriggerID`s, e.g. `triggerA` and `triggerB`.
2. Both succeed because the only duplicate check is on `TriggerID` [7](#0-6) , creating two `webapiTrigger` entries each with a fresh rate limiter configured for, say, 1 RPS/1 burst per sender.
3. An external sender listed in `AllowedSenders` sends 2 requests in quick succession via the gateway to `HandleGatewayMessage`.
4. In `processTrigger`, both requests pass because each request is checked against both trigger instances' independent rate limiters — the sender effectively gets 2 RPS instead of the intended 1 RPS, and the workflow is started twice for what should logically be a single trigger. [6](#0-5)

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

**File:** core/capabilities/webapi/trigger/trigger.go (L227-232)
```go
	h.mu.Lock()
	defer h.mu.Unlock()
	_, errBool := h.registeredWorkflows[req.TriggerID]
	if errBool {
		return nil, fmt.Errorf("triggerId %s already registered", req.TriggerID)
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L234-245)
```go
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L259-266)
```go
	h.registeredWorkflows[req.TriggerID] = &webapiTrigger{
		workflowID:     req.Metadata.WorkflowID,
		allowedTopics:  allowedTopicsMap,
		allowedSenders: allowedSendersMap,
		ch:             ch,
		config:         *reqConfig,
		rateLimiter:    rateLimiter,
	}
```
