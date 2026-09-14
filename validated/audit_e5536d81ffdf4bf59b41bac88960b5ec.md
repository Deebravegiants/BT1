### Title
Unbounded workflow/topic loop in `processTrigger` allows unprivileged gateway callers to exhaust CPU and block legitimate trigger dispatch - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
`triggerConnectorHandler.processTrigger` performs a nested O(registered workflows × payload.Topics) loop for every incoming gateway message, with no upper bound enforced on the number of topics an unprivileged sender can submit in a single `web_api_trigger` request. This mirrors the reported bug class ("Loop gas limit" / unbounded array iteration triggered by an unprivileged actor), except here the "gas" is CPU/goroutine time on the node rather than block gas.

### Finding Description
`HandleGatewayMessage` decodes the attacker-controlled JSON body directly into `webapicap.TriggerRequestPayload` and passes `payload.Topics` straight into `processTrigger` without any cap on array length: [1](#0-0) 

`processTrigger` then iterates over every registered workflow and, for each, over every submitted topic: [2](#0-1) 

There is no limit on `len(topics)` (only an empty-topics check at line 94), and no limit on `len(triggers)` besides however many workflows happen to be registered. A single unprivileged sender that reaches this handler through the gateway (i.e., any external party that can submit a `web_api_trigger` JSON-RPC/legacy message, since this trigger path allows arbitrary senders to hit `HandleGatewayMessage` before the per-workflow `allowedSenders` check occurs inside the loop) can submit a payload with an extremely large `Topics` array, forcing `processTrigger` to perform `len(triggers) * len(topics)` map lookups synchronously inside the gateway message-handling call.

Unlike the Solidity original where the concern is exceeding the block gas limit, here the effect is consuming CPU on the single-threaded per-message handling path and holding `h.mu` isn't held during the loop (it's copied via `slices.Collect` before the loop), but the loop itself still runs synchronously within `HandleGatewayMessage`, which is invoked per gateway message. A large topics array causes this call to take proportionally longer, and because it's invoked from the gateway's message-processing path, an attacker submitting many such requests (or one with an extremely large topics array) can degrade throughput for legitimate trigger processing on the node.

I was not able to find any explicit size limit on `payload.Topics` in `webapicap.TriggerRequestPayload`, nor a maximum on the number of `web_api_trigger` messages or a global message size cap enforced before this deserialization step in the code I could inspect.

### Impact Explanation
This is a Denial-of-Service class issue for the workflow trigger connector: an unprivileged sender who can reach `HandleGatewayMessage` (the gateway forwards any incoming `web_api_trigger` message to this handler regardless of allowlist status — allowlist check happens *inside* the loop, per matched topic, not before the loop begins) can cause disproportionate CPU consumption per node relative to the request size, potentially delaying or starving processing of legitimate trigger events for other workflows on the same DON/node. Impact is bounded by resource exhaustion/availability degradation, not by fund loss or authentication bypass.

### Likelihood Explanation
Likelihood is moderate: it requires an attacker to be able to route a `web_api_trigger` message to a node's gateway connector, which is a legitimate, reachable, unauthenticated (pre-allowlist-check) code path documented as accepting arbitrary sender addresses. Crafting a payload with a very large `Topics` array is straightforward since there is no explicit bound found in the reviewed code.

### Recommendation
Enforce a maximum length on `payload.Topics` (and reject requests exceeding it) before entering `processTrigger`'s loop, and/or move the `trigger.allowedSenders` check to run before iterating topics rather than inside the innermost loop, so unauthorized senders are rejected in O(1) per workflow instead of O(topics) per workflow.

### Proof of Concept
1. An unprivileged actor crafts a legacy or JSON-RPC gateway message with `Method: ghcapabilities.MethodWebAPITrigger` and a `TriggerRequestPayload` whose `Topics` field contains a very large number of unique strings (e.g., 100k+ entries), as accepted by `HandleGatewayMessage`: [1](#0-0) 
2. The message is routed to `processTrigger`, which loops over all registered workflows × all submitted topics before any sender-authorization short-circuit is applied at the workflow level: [3](#0-2) 
3. Repeated submission of such oversized payloads consumes CPU cycles proportional to `len(triggers) * len(topics)` per message, degrading gateway message processing throughput for the node.

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

**File:** core/capabilities/webapi/trigger/trigger.go (L167-188)
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
```
