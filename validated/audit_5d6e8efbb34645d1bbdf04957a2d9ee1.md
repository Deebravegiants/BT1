### Title
Unbounded, attacker-amplified O(workflows × topics) loop in webapi trigger message handling causes gateway/node DoS - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger`, invoked from `HandleGatewayMessage` for every inbound `MethodWebAPITrigger` gateway message, iterates over **all** registered webapi-trigger workflows nested inside a loop over **all** topics supplied in the untrusted request payload, before any per-sender authorization or rate limiting is applied. Both dimensions of this loop are attacker-influenced (number of registered triggers grows over time and the `Topics` array is fully controlled by the caller of the request), making this the same unbounded-loop DoS pattern described in the reference finding, but with an added attacker-controlled multiplier.

### Finding Description
`HandleGatewayMessage` dispatches every `MethodWebAPITrigger` message to `processTrigger`: [1](#0-0) 

`processTrigger` snapshots all currently registered workflow triggers and then runs a nested loop over `triggers × topics`: [2](#0-1) 

Key observations:
- `topics := payload.Topics` is taken directly from the incoming, attacker-supplied JSON payload with no length/size cap enforced anywhere in this handler (no `MaxTopics`/`MaxAllowedTopics` guard exists in the codebase).
- `triggers` is `slices.Collect(maps.Values(h.registeredWorkflows))` — every workflow that has ever called `RegisterTrigger` for the `web-api-trigger@1.0.0` capability, which grows as more workflows onboard the trigger over time.
- For every `(trigger, topic)` pair the code performs a map lookup (`trigger.allowedTopics[topic]`) and, only on a match, checks `trigger.allowedSenders[sender.String()]` and the per-workflow rate limiter. Critically, the `matchedWorkflows++` counting and the double-loop iteration cost itself occurs **before** any of the sender-allowlist or rate-limit checks can short-circuit, so the CPU cost of the loop scales with `len(triggers) * len(topics)` regardless of whether the caller is authorized for any of the matched workflows.
- Registration (`RegisterTrigger`) has no upper bound on the number of registered triggers, and no validation caps `len(reqConfig.AllowedTopics)`: [3](#0-2) 

This mirrors the reported bug class (`BatchRequests.sendWithdrawalRequests`'s unbounded `for` over `contracts`), but here the loop is reachable from an inbound, internet-facing gateway message path (`HandleGatewayMessage`) processed synchronously per request, and one of the two loop dimensions (`topics`) is entirely attacker-controlled within a single request, letting an attacker amplify the cost of a single message without needing to grow the workflow registry at all.

### Impact Explanation
As the number of workflows subscribed to the `web-api-trigger` capability grows (a normal, permissionless outcome of onboarding workflows), and/or as an attacker submits a request with a very large `Topics` array, the per-message CPU cost of `processTrigger` grows multiplicatively. Because this runs synchronously inside `HandleGatewayMessage` for every inbound webapi-trigger message, a burst of such requests (each with a large `Topics` array) can consume significant CPU on the node/gateway processing path, degrading or denying processing of legitimate trigger events for all workflows registered against that node — a availability/DoS impact on the gateway-connected node's workflow trigger handling.

### Likelihood Explanation
Likelihood is moderate-to-high: reaching `processTrigger` only requires sending a `MethodWebAPITrigger` message through the gateway with an arbitrarily large `Topics` list; there is no validation limiting the size of `Topics`, and no early rejection based on sender identity before the loop executes. The severity scales further as the trigger capability's registered-workflow count naturally grows in production. This does not require any privileged access, malicious peer, or malicious node — a single unprivileged remote sender crafting the JSON payload is sufficient to trigger the amplification.

### Recommendation
- Enforce a strict maximum on `len(payload.Topics)` (and reject/](truncate) oversized payloads) before entering the matching loop in `processTrigger`.
- Restructure lookups to avoid nested `O(triggers × topics)` iteration, e.g. maintain a topic→triggers index (`map[topic][]*webapiTrigger`) updated on `RegisterTrigger`/`UnregisterTrigger`, so a request with `n` topics only iterates over the (bounded) set of triggers subscribed to those specific topics.
- Move sender-allowlist authorization ahead of/independent from the expensive matching loop where feasible, or apply a lightweight per-sender rate limit at the `HandleGatewayMessage` entry point before invoking `processTrigger`, so unauthorized/unrelated senders cannot pay-to-trigger the full iteration cost.
- Cap the total number of triggers considered per invocation or add a global registration limit for `web-api-trigger` capability instances.

### Proof of Concept
1. Register `N` workflows for the `web-api-trigger@1.0.0` capability, each with distinct `AllowedTopics`, via legitimate `RegisterTrigger` calls, as shown in [3](#0-2) .
2. As any external caller (no special node privilege required), send a gateway message with `Method = MethodWebAPITrigger` and a `TriggerRequestPayload.Topics` array containing a very large number of distinct (mostly non-matching) topic strings.
3. `HandleGatewayMessage` → `processTrigger` executes the nested loop shown in [2](#0-1)  over `N` triggers × the attacker-chosen topic count, consuming CPU proportional to that product for every such message received, with no caps in place to bound it.

### Citations

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
