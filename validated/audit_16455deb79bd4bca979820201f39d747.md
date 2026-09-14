### Title
Unbounded `Topics` array in `web_api_trigger` gateway messages causes O(W×T) CPU blow-up in `processTrigger` - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
The `processTrigger` function in `core/capabilities/webapi/trigger/trigger.go` iterates every registered `web-api-trigger@1.0.0` workflow against every entry in the attacker-supplied `payload.Topics` slice with no bound on either dimension, mirroring the reported "nested loop with no ceiling on the inner dimension" bug class from the CosmWasm `claim` finding (there `P*F*E`; here `W*T`). This computation runs synchronously inside `HandleGatewayMessage`, which is the entry point for messages relayed from the internet-facing Gateway.

### Finding Description
`processTrigger` is called from `HandleGatewayMessage` [1](#0-0)  whenever a `MethodWebAPITrigger` message arrives from the Gateway. Inside it, the handler snapshots all currently registered trigger workflows and then runs a nested loop over `triggers × topics`: [2](#0-1) 

`topics := payload.Topics` comes directly from the unauthenticated/unprivileged sender's JSON payload (`webapicap.TriggerRequestPayload`), and there is no length cap enforced anywhere on `Topics` before this loop runs — `len(topics) == 0` is the only check [3](#0-2) . The per-sender/allowed-sender and rate-limiter checks (`trigger.allowedSenders`, `trigger.rateLimiter.Allow`) are only evaluated **after** a topic match is found inside the inner loop [4](#0-3) , so they do not bound the total number of loop iterations (`W×T`) that must execute before any rejection can occur for topics that don't match any workflow's allow-list, and even for topics that do match, the limiter is only consulted once a workflow+topic pair matches — it does not prevent the initial O(W×T) scan cost.

`W` (number of registered workflows on the node) can grow with legitimate node usage, and `T` (topics in a single message) is entirely attacker-controlled with no upper bound, matching the report's core observation that one input-controlled loop dimension (there, epoch count `E`; here, `Topics` length `T`) can be driven arbitrarily large by delaying/batching input, while the other dimension is state accumulated over time (`W`, analogous to `F`/farms count growing over the life of the node).

### Impact Explanation
An unauthenticated external actor able to reach the Gateway can submit a single `web_api_trigger` message with a very large `Topics` array. Because there is no size limit on this field prior to the nested loop, and the loop is O(registered-workflows × topics-in-request), this can consume significant CPU synchronously within `HandleGatewayMessage` on the node. Depending on how many workflows are registered for `web-api-trigger` and how large an attacker makes `Topics`, this can materially degrade or stall message processing for the trigger connector on that node, which is a resource-exhaustion / node-availability impact reachable by an unprivileged actor — the same class of impact (unbounded loop reachable from user input causing resource exhaustion of the processing path) as the referenced report, adapted from "block gas limit" to "node CPU/goroutine time on the Gateway-connector message path."

### Likelihood Explanation
Likelihood is moderate: the attack requires only a validly-signed `web_api_trigger` message (any sender key works to reach the loop; being an "allowed sender" is only needed to actually trigger a workflow, not to enter the loop), and requires no special privilege beyond being able to send a signed message through the Gateway to a node running this connector. The severity scales with the number of `web-api-trigger` workflows registered on that node and the size of `Topics` the attacker chooses to send, both of which are outside the defender's per-message control absent an explicit cap.

### Recommendation
- Enforce a maximum length on `payload.Topics` (and reject/short-circuit messages with excessive topic counts) before entering the nested loop in `processTrigger`.
- Restructure the matching to avoid O(W×T): e.g., build a topic→workflow(s) index (map lookup) once per topic instead of a double loop over all workflows for all topics, so the complexity is O(T) average-case lookups against a hash index rather than O(W×T).
- Apply sender-allow-list and rate-limit checks earlier (e.g., a cheap pre-check) so unmatched/unauthorized requests are rejected before scanning all registered workflows.

### Proof of Concept
1. Register N `web-api-trigger@1.0.0` workflows on a node's capability registry (this is normal legitimate node operation, e.g., N in the thousands over the node's lifetime, as seen at [5](#0-4) ).
2. As an external, unprivileged client, send a single Gateway `web_api_trigger` message whose `Payload.Topics` contains a very large array (e.g., tens of thousands of arbitrary strings), signed with any private key (sender need not be in any workflow's `allowedSenders`).
3. `HandleGatewayMessage` → `processTrigger` executes the nested loop over all N workflows × all topics [6](#0-5) , consuming CPU proportional to N×T with no early exit, before returning a `"no Matching Workflow Topics"` or `"unauthorized Sender"` error — the cost is paid regardless of whether the request is legitimate.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-96)
```go
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

**File:** core/capabilities/webapi/trigger/trigger.go (L186-200)
```go
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
