### Title
Unbounded nested loop over attacker-controlled `Topics` array in web-api trigger gateway handler enables CPU-exhaustion DoS - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger` in `core/capabilities/webapi/trigger/trigger.go` iterates over every registered workflow trigger nested inside a loop over `payload.Topics`, an attacker-supplied array taken directly from the incoming gateway message, with no upper bound check on its length.

### Finding Description
`HandleGatewayMessage` unmarshals the message body into `webapicap.TriggerRequestPayload` and passes it to `processTrigger`: [1](#0-0) 

Inside `processTrigger`, the only validation performed on `topics := payload.Topics` is a check that it is non-empty; there is no upper bound (`MaxTopics` or similar) enforced anywhere in this handler or in `webapicap.TriggerRequestPayload`: [2](#0-1) 

The handler then runs a nested loop over all currently registered triggers (`triggers`) crossed with all attacker-supplied `topics`: [3](#0-2) 

This is O(len(triggers) × len(topics)). `len(triggers)` grows with the number of workflows registered on the node (out of the attacker's control but can be large on a busy DON member), and `len(topics)` is fully controlled by whoever sends the `web_api_trigger` gateway message — no size or count limit is enforced before the loop executes. Per-sender authorization (`trigger.allowedSenders[sender.String()]`) and rate limiting (`trigger.rateLimiter.Allow`) are only checked *inside* the loop, after a topic has already matched `trigger.allowedTopics`, so they do not bound the total iteration cost, only whether an event is ultimately dispatched.

### Impact Explanation
A sender able to reach this gateway handler (the sender identity is self-asserted via a signature over the message body and is not otherwise access-controlled at this handler) can submit a `web_api_trigger` message with a very large `Topics` array. This forces the node to perform a large number of map lookups (`trigger.allowedTopics[topic]`) across every registered trigger for every topic, consuming CPU on the node's gateway-message-handling goroutine. Because this handler runs synchronously as part of gateway message dispatch, sustained or repeated submission of oversized `Topics` payloads can degrade or block processing of other gateway messages on that node, i.e. a denial-of-service condition — directly analogous to the reported unbounded-loop DoS pattern (attacker-controlled input driving loop iteration count with no cap, causing resource exhaustion in a request-handling path).

### Likelihood Explanation
Medium. The `Topics` field size is bounded only indirectly by whatever overall gateway message size limit exists at the transport layer (not verified in the available index), but even a modest overall message-size cap still allows tens of thousands of short topic strings, and this multiplies against however many workflows are registered on the node at the time. No explicit `MaxBatchSize`-style limiter (as exists for the analogous vault batch endpoints, e.g. `vaulttypes.MaxBatchSize` in `core/capabilities/vault/vaulttypes/types.go`) is applied to `Topics` here, which is inconsistent with the rest of the codebase's pattern of bounding attacker-controlled batch sizes.

### Recommendation
Enforce an explicit upper bound on `len(payload.Topics)` (and reject with an error before entering the nested loop) in `processTrigger`, mirroring the `MaxRequestBatchSizeLimiter` pattern already used for vault requests (`core/capabilities/vault/validator.go`). Consider also restructuring the check to look up topics via `trigger.allowedTopics` membership from the smaller side (i.e., iterate over the request's topics against a fixed-size allowed set, or vice versa, whichever is smaller) to cap worst-case cost independent of the number of registered triggers.

### Proof of Concept
1. Register several workflows as `web-api-trigger` triggers (`RegisterTrigger`), each with a moderate `allowedTopics` set.
2. As an external message sender (self-signed identity, not necessarily one of the `allowedSenders` for any workflow), craft a `web_api_trigger` gateway message whose JSON payload contains `Topics` with a very large number of distinct strings (e.g., 50,000+ entries), staying under any transport-level message size cap by using short topic strings.
3. Submit this message repeatedly to the node's gateway connector.
4. Observe that `processTrigger` executes `len(triggers) × len(topics)` map lookups per message, consuming CPU on the goroutine handling `HandleGatewayMessage`, delaying processing of legitimate trigger messages and other gateway traffic on the node.

Note: I could not fully verify the presence/absence of an overall gateway message size cap that transport layer enforces (`ValidatedMessageFromReq` / `message_util.go`) within the indexed content, so the exact practical ceiling on `len(topics)` achievable in a single message is not fully confirmed from the available code; this is stated as an area of uncertainty.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-96)
```go
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}
```

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
