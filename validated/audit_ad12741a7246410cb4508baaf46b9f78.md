## Finding

### Title
Unbounded `web_api_trigger` registrations combined with unbounded caller-supplied `Topics` cause O(N×M) DoS in the WebAPI Trigger gateway handler - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
`triggerConnectorHandler.RegisterTrigger` accepts an unlimited number of trigger registrations into `h.registeredWorkflows` with no cap on the total count, and `processTrigger`, invoked once per incoming gateway message from an external HTTP/gateway caller, iterates over *every* registered trigger and *every* caller-supplied topic on every single request. This is the same unbounded-iteration-over-a-privileged-but-uncapped-list DoS pattern as the reported `StakingModule` plugin issue: as the number of registered triggers (or the size of a single request's `Topics` array) grows, per-request cost grows unboundedly and can starve/serialize processing for all tenants sharing the gateway/DON.

### Finding Description
`RegisterTrigger` performs no bound check on the size of `h.registeredWorkflows`: [1](#0-0) 

Any workflow owner deploying workflows that use the `web_api_trigger` capability can call `RegisterTrigger` repeatedly (one call per deployed workflow/trigger) to grow this map without limit; there is no maximum-triggers check analogous to a `PLUGIN_EDITOR` cap.

Every inbound gateway message routed to method `MethodWebAPITrigger` is handled by `HandleGatewayMessage`, which calls `processTrigger`: [2](#0-1) 

`processTrigger` snapshots the entire trigger set and iterates it in a nested loop against `payload.Topics`, which is decoded directly from the unauthenticated (pre-authorization) message payload with no length limit imposed before the loop runs: [3](#0-2) 

Unlike the analogous remote-trigger fan-in path (`core/capabilities/remote/trigger_subscriber.go`), which explicitly truncates batched IDs via `maxBatchedWorkflowIDs` before iterating: [4](#0-3) 
`processTrigger` has no equivalent guard on `len(topics)` or `len(triggers)`. Per-request cost is `O(len(registeredWorkflows) * len(payload.Topics))`, both of which are attacker/tenant-influenceable: the trigger count grows with the number of deployed workflows across all owners, and `Topics` is fully controlled by whoever sends the message to the gateway.

Because `h.mu` is only held to snapshot the map (not during the iteration), the lock itself isn't held for the whole loop, but the single-threaded cost of the loop still directly delays the response (and, because gateway connector handlers are invoked serially per connection per the codebase's own concurrency notes, e.g. `TestHandler_ServesRequestsConcurrently` in `core/capabilities/confidentialrelay/handler_test.go`), a slow `processTrigger` call for one workflow owner can degrade or block processing of gateway messages intended for other tenants.

### Impact Explanation
A single unprivileged caller able to reach the `web_api_trigger` gateway endpoint can send a message with a very large `Topics` array; combined with organic growth of `registeredWorkflows` from any number of deployed workflows, this multiplies CPU/latency cost per request without bound. This can degrade or deny gateway responsiveness for all workflows sharing that trigger handler/DON, not just the caller's own workflow — matching the Medium-severity “DoS via unbounded plugin/array iteration” class in the reference report.

### Likelihood Explanation
Reaching `RegisterTrigger` requires deploying workflows (a normal CRE tenant action, not a privileged node-operator action), and reaching `processTrigger` requires only sending a gateway message with method `MethodWebAPITrigger`, which is the intended external-facing entry point for this trigger type — no special privilege is required to submit an oversized `Topics` payload.

### Recommendation
- Cap the number of concurrently registered triggers in `triggerConnectorHandler.RegisterTrigger` (return an error once a configurable maximum is reached), similar to bounding other unbounded collections in the gateway path (e.g. `RequestCache.maxCacheSize` in `core/services/gateway/handlers/common/requestcache.go`).
- Validate/limit `len(payload.Topics)` in `processTrigger` before the double loop, mirroring the `maxBatchedWorkflowIDs` truncation pattern used in `core/capabilities/remote/trigger_subscriber.go`.
- Consider indexing triggers by topic (e.g., `map[topic][]*webapiTrigger`) instead of a full linear scan, to avoid O(N×M) cost altogether.

### Proof of Concept
1. Deploy (or simulate registering) a large number of workflows using the `web_api_trigger` capability, each calling `RegisterTrigger` — `h.registeredWorkflows` grows without bound since no cap exists.
2. Send a single JSON-RPC gateway message with method `web_api_trigger` and a `TriggerRequestPayload.Topics` array containing a large number of entries (e.g., tens of thousands of strings).
3. Observe `processTrigger`'s nested loop over `len(registeredWorkflows) * len(topics)` causing significant CPU time/latency for this single request, delaying or blocking subsequent gateway messages routed through the same handler for unrelated workflow owners.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L85-107)
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

**File:** core/capabilities/remote/trigger_subscriber.go (L316-319)
```go
		if len(meta.WorkflowIds) > maxBatchedWorkflowIDs {
			s.lggr.Errorw("received message with too many workflow IDs - truncating", "nWorkflows", len(meta.WorkflowIds), "sender", sender)
			meta.WorkflowIds = meta.WorkflowIds[:maxBatchedWorkflowIDs]
		}
```
