### Title
Unbounded Nested Loop Over Attacker-Controlled `topics` Array in WebAPI Trigger Message Handling - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.processTrigger` iterates over every registered workflow trigger and, for each trigger, iterates over the full attacker-supplied `topics` slice from the incoming trigger payload. Neither the number of registered workflow triggers nor the length of the `topics` array is size-limited before this nested loop executes, producing an `O(triggers × topics)` unbounded loop driven directly by content in an externally-supplied, gateway-routed message.

### Finding Description
`processTrigger` is invoked from `HandleGatewayMessage` for every incoming trigger message that the Gateway forwards to a DON node: [1](#0-0) 

The `topics` value used in the loop bound comes straight from `payload.Topics`, which is decoded from the externally-supplied message body. Per the JSON schema backing `TriggerRequestPayload`, `topics` is declared only as `"type": "array", "items": {"type": "string"}` — there is no `maxItems`/length cap: [2](#0-1) 

The generated Go struct mirrors this with no size validation: [3](#0-2) 

The only checks performed before the nested loop are that `topics` is non-empty (`len(topics) == 0` returns an error) and that a workflow's config declares matching `allowedTopics`/`allowedSenders`/`rateLimiter`, none of which bound the size of the incoming array: [4](#0-3) 

For each call, the handler builds `triggers := slices.Collect(maps.Values(h.registeredWorkflows))` (proportional to the number of active workflow registrations on the node) and then executes a double loop `for _, trigger := range triggers { for _, topic := range topics { ... } }`, matching the reported bug class exactly: an attacker fully controls one dimension of the loop (`topics`) by simply padding the array in the request payload, while the other dimension (registered triggers) grows naturally with DON usage. This directly parallels the Sherlock finding's unbounded `_matchOrders` loop, where an unbounded, caller-supplied array size drives gas/CPU cost with no cap.

### Impact Explanation
A sender able to reach the gateway's trigger-message path (an external/unprivileged caller signing a webhook-trigger request, not an operator or trusted node) can submit a payload with an arbitrarily large `topics` array. Because `HandleGatewayMessage` is invoked from the single per-connection dispatch goroutine in the gateway connector's read loop (as documented by the regression-guard comment for head-of-line blocking in the confidential-relay handler), a single expensive `processTrigger` call can stall dispatch of subsequent messages on that connection, and CPU cost scales with `registeredWorkflows × len(topics)`, which can be made large by an attacker independent of any legitimate business need. This is a denial-of-service risk against the DON's gateway message-processing path, not a fund-movement or secret-disclosure bug.

### Likelihood Explanation
Likelihood is moderate: it requires only a validly signed message reaching `HandleGatewayMessage` with a large `topics` array; no privileged role, allowlist bypass, or additional exploit chain is needed beyond crafting the payload. However, actual severity depends on upstream message-size limits (e.g., gateway HTTP body size limits, JSON-RPC request size caps) that were not confirmed in this review to bound `topics` length tightly enough to make the attack impractical — this could not be fully verified in the given time and should be checked against the gateway's message/body size limits (e.g., `MessageRateLimiterCapacity`/`BytesRateLimiterCapacity` settings referenced elsewhere in the docs) before treating this as high severity.

### Recommendation
Add an explicit upper bound on `payload.Topics` length (and consider bounding on `len(triggers)` per iteration or restructuring the match to use a topic→trigger index instead of a full nested scan) in `processTrigger`/`RegisterTrigger`, analogous to the `MaxBatchSize` bound already used for vault secrets requests (see `vaulttypes.MaxBatchSize` and the corresponding batch-size limiter checks in `core/capabilities/vault/validator.go`). Reject requests exceeding the limit before entering the nested loop.

### Proof of Concept
Not independently executed; based on static analysis of `processTrigger`, sending a `TriggerRequestPayload` with `topics` containing many entries (e.g., tens of thousands of distinct strings) to a DON node hosting numerous registered `web-api-trigger@1.0.0` workflows would force `HandleGatewayMessage`/`processTrigger` to execute `len(registeredWorkflows) × len(topics)` iterations per request, with no size check rejecting the request beforehand. Full exploitability depends on gateway-level message size limits, which were not verified within the scope of this review.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L85-118)
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

**File:** core/capabilities/webapi/trigger/trigger.go (L212-255)
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
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L69-75)
```json
                "topics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description" : "An array of a single topic (string) to be started by this event."
                    }
                },
```

**File:** core/capabilities/webapi/webapicap/event_trigger_generated.go (L60-72)
```go
type TriggerConfig struct {
	// AllowedSenders corresponds to the JSON schema field "allowedSenders".
	AllowedSenders []string `json:"allowedSenders" yaml:"allowedSenders" mapstructure:"allowedSenders"`

	// AllowedTopics corresponds to the JSON schema field "allowedTopics".
	AllowedTopics []string `json:"allowedTopics" yaml:"allowedTopics" mapstructure:"allowedTopics"`

	// RateLimiter corresponds to the JSON schema field "rateLimiter".
	RateLimiter RateLimiterConfig `json:"rateLimiter" yaml:"rateLimiter" mapstructure:"rateLimiter"`

	// RequiredParams corresponds to the JSON schema field "requiredParams".
	RequiredParams []string `json:"requiredParams" yaml:"requiredParams" mapstructure:"requiredParams"`
}
```
