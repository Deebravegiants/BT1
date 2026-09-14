### Title
Unbounded `registeredWorkflows` map combined with unvalidated `payload.Topics` in `triggerConnectorHandler.processTrigger` allows gateway-message DDOS - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
`triggerConnectorHandler.RegisterTrigger` places no cap on the number of triggers (`TriggerID`s) that can be registered in the shared `registeredWorkflows` map, and `processTrigger`—invoked once per incoming gateway `web_api_trigger` message—iterates the full cross product of `registeredWorkflows × payload.Topics` while holding no protective bound on either dimension. This mirrors the reported Carapace `ProtectionPool` pattern where an attacker-influenced, unbounded collection is looped through in a critical, shared code path, degrading service for all other users.

### Finding Description
`RegisterTrigger` only rejects a request if the exact `TriggerID` already exists; there is no limit on the total number of entries the map can hold: [1](#0-0) 

Every incoming gateway message for the `web_api_trigger` method is dispatched to `processTrigger`, which snapshots **all** registered triggers under a shared mutex and then runs a nested loop over every trigger and every topic in the caller-supplied payload: [2](#0-1) 

`payload.Topics` comes directly from the untrusted request body (`webapicap.TriggerRequestPayload`) with no upper bound enforced before this loop runs: [3](#0-2) 

The mutex is held only while copying the map reference, but the resulting `triggers` slice can still be arbitrarily large, and the per-message cost is `O(len(registeredWorkflows) * len(topics))`. Because any workflow owner able to reach `RegisterTrigger` (via the workflow/capabilities registration path) can register many `TriggerID`s with distinct configurations, and any caller can submit a message with an inflated `Topics` array, the per-message processing cost for this single-threaded/mutex-guarded handler can be pushed arbitrarily high — directly analogous to the reported `ProtectionPool.accruePremiumAndExpireProtections` issue where an unprivileged actor inflates an array that a critical function must loop through in full.

### Impact Explanation
Because `HandleGatewayMessage`/`processTrigger` is the single entry point through which *all* `web_api_trigger` gateway messages for *every* registered workflow are processed, an attacker who can register many low-cost triggers (or send messages with large `Topics` arrays) increases the processing cost of every subsequent trigger message on the node — including those belonging to unrelated, legitimate workflows. This can starve legitimate trigger delivery (denial of service against other users' workflow executions), which is the same "protocol halted for a shared critical loop" impact described in the source report.

### Likelihood Explanation
Likelihood is moderate: reaching `RegisterTrigger` requires being a workflow owner able to register a `web-api-trigger@1.0.0` capability (some barrier exists via workflow/DON registration, unlike the fully open on-chain buy call in the original report), but no additional cost or limit prevents registering an arbitrarily large number of triggers or inflating `Topics` in a request once registered. I could not verify within the available index whether an outer size limit is enforced on `payload.Topics` or on the total count of `registeredWorkflows` elsewhere in the gateway ingress path (e.g., message-size limits at the JSON-RPC/gateway layer), so likelihood should be validated against those layers before treating this as fully unmitigated.

### Recommendation
- Enforce a maximum number of triggers a single workflow/owner may register in `RegisterTrigger` (return an error once a configurable cap is exceeded).
- Enforce a maximum length on `payload.Topics` in `processTrigger` before entering the loop, rejecting oversized requests early.
- Consider indexing triggers by topic (`map[topic][]*webapiTrigger`) instead of iterating the full trigger set per topic, to make the lookup cost independent of the total number of registered triggers.

### Proof of Concept
1. As a workflow owner capable of registering the `web-api-trigger@1.0.0` capability, repeatedly call `RegisterTrigger` with unique `TriggerID`s (e.g., thousands of registrations), each with minimal `AllowedTopics`/`AllowedSenders` — nothing in `RegisterTrigger` (lines 212-269) prevents this.
2. Send a `web_api_trigger` gateway message with a large `Topics` array in the payload.
3. `processTrigger` (lines 85-165) will iterate `len(registeredWorkflows) * len(topics)` times while holding the trigger snapshot, materially increasing latency/CPU cost for processing this and subsequent gateway messages routed to this handler, degrading service for all workflows sharing this node's `GatewayHandler`/`triggerConnectorHandler` instance.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L85-97)
```go
func (h *triggerConnectorHandler) processTrigger(ctx context.Context, gatewayID string, body *api.MessageBody, sender ethCommon.Address, payload webapicap.TriggerRequestPayload) error {
	// Pass on the payload with the expectation that it's in an acceptable format for the executor
	wrappedPayload, err := values.WrapMap(payload)
	if err != nil {
		return fmt.Errorf("error wrapping payload %w", err)
	}
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
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

**File:** core/capabilities/webapi/trigger/trigger.go (L227-266)
```go
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
```
