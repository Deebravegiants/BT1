### Title
Unbounded topics field in Web API trigger requests causes O(triggers × topics) DoS in `processTrigger` - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
`triggerConnectorHandler.processTrigger` in `core/capabilities/webapi/trigger/trigger.go` iterates over every registered workflow trigger and, for each one, iterates over every entry in the caller-supplied `payload.Topics` array with no upper bound on either dimension. Because `Topics` is fully attacker-controlled request data, this mirrors the Sherlock finding: an unprivileged caller can inflate the size of an array that a hot-path loop scans in full, degrading or denying service to the trigger-processing pipeline.

### Finding Description
`processTrigger` is invoked from `HandleGatewayMessage` for every incoming gateway message with `body.Method == ghcapabilities.MethodWebAPITrigger`: [1](#0-0) 

Inside `processTrigger`, the handler snapshots all currently registered triggers and then runs a nested loop: for every trigger, for every topic in the request payload, it checks map membership: [2](#0-1) 

`topics := payload.Topics` comes directly from the unmarshaled request body with no size validation: [3](#0-2) 

Because the outer loop scales with the number of registered workflow triggers (which can also grow, e.g. via workflow registration) and the inner loop scales with `len(payload.Topics)` — a value entirely controlled by the message sender — a single caller can submit a payload with a very large `Topics` array (e.g., tens of thousands of entries) to multiply the cost of every incoming trigger message by that factor. This is directly analogous to the Sherlock report's unbounded loop over `activeProtectionIndexes`: work performed by a shared, security-relevant code path scales with attacker-supplied data rather than being bounded.

### Impact Explanation
`processTrigger` runs under `h.mu` only briefly (to snapshot triggers) but the actual double loop executes unlocked and synchronously inside `HandleGatewayMessage`. Gateway message handling is typically processed on a limited number of worker goroutines per node/gateway connection; a computationally expensive request can starve the processing of subsequent legitimate trigger messages for all workflows sharing this capability handler, degrading availability of the Web API trigger capability for other workflow owners on the same node — an availability/DoS impact reachable purely from unprivileged request content.

### Likelihood Explanation
Likelihood is moderate: the caller must be an entity permitted to send `web_api_trigger` messages through the gateway (i.e., pass whatever gateway-level authentication exists for that method), but there is no additional check limiting the size of the `Topics` array or the cost of `processTrigger` before the nested loop executes. No rate limiting or bound is applied prior to entering the loop — the per-sender/per-workflow rate limiter is only checked per matched topic *inside* the loop, after the (potentially large) topic list has already been scanned once per registered trigger.

### Recommendation
- Enforce a maximum size on `payload.Topics` (e.g., reject requests with more than N topics) before entering the matching loop.
- Consider indexing triggers by topic (e.g., a `map[topic][]*webapiTrigger]`) instead of doing an O(triggers × topics) scan, so lookup cost is proportional to the number of matches, not the full cross-product.
- Apply a global/per-sender request-cost or rate limit ahead of the loop, not just on the matched-topic branch.

### Proof of Concept
Conceptual (no execution environment available to verify runtime behavior — this is derived purely from static code reading of `core/capabilities/webapi/trigger/trigger.go`):
1. An attacker with a valid sender registered on the gateway (or any sender if `allowedSenders` checks happen only per-topic-match, as shown in the code) sends a `web_api_trigger` gateway message whose JSON payload's `topics` field contains a very large array (e.g., 100,000 unique strings).
2. `HandleGatewayMessage` unmarshals the payload and calls `processTrigger`.
3. `processTrigger` snapshots all registered triggers (`triggers := slices.Collect(...)`) and executes the nested `for _, trigger := range triggers { for _, topic := range topics { ... } }` loop, performing `len(triggers) * len(topics)` map lookups synchronously.
4. With enough registered triggers and a sufficiently large `topics` array, this single message consumes significant CPU time on the node, delaying processing of subsequent trigger messages from other workflows/senders.

Note: I could not verify from static analysis alone whether an upstream gateway-level size limit on message payloads (e.g., total JSON body size caps) indirectly bounds `Topics` length, which would reduce but not necessarily eliminate the severity of this issue. Confirming the presence/absence of such a limit would require further investigation of the gateway message-size validation path (e.g., `hc.ValidatedMessageFromReq`).

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L85-96)
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
