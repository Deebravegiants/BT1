### Title
Unbounded nested loop over registered triggers × attacker-supplied topics in Web API trigger handler enables gateway-message DoS - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger` iterates every registered workflow trigger against every topic string supplied in an inbound gateway message, with no limit on the number of topics a caller can include and no bound on the number of registered triggers checked, mirroring the unbounded-loop DoS pattern described in the Forta `redeem` report (loop size controlled by attacker-influenced input, no cap, executed unconditionally on the hot path of message handling).

### Finding Description
`HandleGatewayMessage` unmarshals `body.Payload` into `webapicap.TriggerRequestPayload` and immediately calls `processTrigger` for `ghcapabilities.MethodWebAPITrigger` messages: [1](#0-0) 

Inside `processTrigger`, the handler snapshots all currently registered triggers and then runs a nested loop over `triggers × topics`: [2](#0-1) 

Two properties combine to make this loop unbounded relative to attacker input:
- `payload.Topics` (the inner loop bound) comes directly from the external, gateway-forwarded message body and is only checked for non-emptiness (`len(topics) == 0`), not for a maximum size: [3](#0-2) 
- The `allowedSenders`/`allowedTopics`/rate-limiter checks that would reject an unauthorized caller happen *inside* the nested loop, after the topic has already matched `trigger.allowedTopics[topic]`, and for every trigger/topic pair that does not match, the loop still executes the map lookups for all combinations. There is no early bound like the Vault capability's `MaxBatchSize` limiter, which caps batch-style requests at 10 items before any per-item work is done: [4](#0-3) [5](#0-4) 

By contrast, the trigger path has no analogous `RequestValidator`/`MaxBatchSize` check on `Topics`, so the cost of a single gateway message scales with `(number of registered triggers on the node) × (number of topics in the attacker's message)`.

### Impact Explanation
An external, unauthenticated-at-this-layer sender (any party able to reach the gateway's webapi-trigger endpoint and produce a syntactically valid signed message — they do not need to be an `allowedSender` for any specific workflow) can submit a single message containing a very large `Topics` array. This forces the node to execute an O(N×M) loop across all locally registered workflow triggers for every such message, monopolizing CPU on the node's gateway-message processing path and delaying or starving legitimate trigger delivery — a Denial of Service condition analogous to the unbounded `redeem` loop in the reported bug class.

### Likelihood Explanation
Likelihood is moderate: the message must pass `hc.ValidatedMessageFromReq` (structural/signature validation) but this does not appear to enforce a cap on the size or count of entries inside `payload.Topics`. As more workflows register web API triggers on a node (increasing N), the attack surface/impact grows without any corresponding rate limit protecting the pre-authorization portion of the loop.

### Recommendation
Add an explicit upper bound on `len(payload.Topics)` (and ideally document/enforce a cap independent of the number of registered triggers) in `processTrigger`, validated before entering the nested loop — following the same pattern already used for Vault batch requests (`MaxBatchSize` checked via `RequestValidator` prior to per-item work). Additionally, consider moving the `allowedSenders`/rate-limit check outside the inner topic loop so unauthorized senders are rejected in O(1) per trigger rather than after per-topic matching.

### Proof of Concept
1. Obtain (or forge, if signature validation of `body.Sender`/message envelope is not strict about sender authorization for this workflow) a validly-structured `HandleGatewayMessage` request with `body.Method = ghcapabilities.MethodWebAPITrigger`.
2. Set `payload.Topics` to a very large array (e.g., tens of thousands of short strings), which is not rejected by any size check in `processTrigger` (only `len(topics) == 0` is checked): [3](#0-2) 
3. Send this message repeatedly to a node with multiple registered workflow triggers; each message causes the node to iterate `registeredTriggers × len(Topics)` combinations under `h.mu`-derived snapshot, consuming CPU proportionally, degrading trigger dispatch for all workflows on that node.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-96)
```go
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L98-119)
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

**File:** core/capabilities/vault/vaulttypes/types.go (L37-38)
```go
	// MaxBatchSize is the maximum number of secrets that can be created/updated/deleted in a single request.
	MaxBatchSize = 10
```

**File:** core/capabilities/vault/validator.go (L55-60)
```go
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, len(encryptedSecrets)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("request batch size exceeds maximum of %d: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check request batch size limit: %w", err)
	}
```
