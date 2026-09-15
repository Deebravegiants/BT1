Confirmed: `TriggerRequestPayload.Topics` is a fully attacker-controlled `[]string` (`core/capabilities/webapi/webapicap/event_trigger_generated.go:110`), only required to be non-empty, and `TriggerEventId` is a single string that does not vary per topic. This confirms the analog bug.

### Title
Web-API trigger fires the same workflow multiple times per request when multiple attacker-supplied topics match one workflow's allowlist - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
`processTrigger` in `core/capabilities/webapi/trigger/trigger.go` iterates every registered `trigger` and, for each, every attacker-supplied `topic` in the request's `payload.Topics`. Whenever a topic is in `trigger.allowedTopics`, it unconditionally sends a `TriggerResponse` on `trigger.ch`, once per matching topic — not once per matching workflow, mirroring the underlying bug class of calling the incentive/side-effect logic multiple times for what should be a single logical unit (there, the same address; here, the same trigger/workflow and the same `TriggerEventID`).

### Finding Description
`processTrigger` loops `for _, trigger := range triggers { for _, topic := range topics { if trigger.allowedTopics[topic] { ... trigger.ch <- tr ... } } }` [1](#0-0) . The code comment claims "Sending n topics that match a workflow with n allowedTopics, can only be triggered once," relying on the `break` at line 152 [2](#0-1) . However, that `break` is inside a Go `select` statement, so it only exits the `select`, not the enclosing `for _, topic := range topics` loop — the classic Go break-scoping gotcha. Consequently, if a single request's `payload.Topics` contains more than one topic that is present in the same workflow's `allowedTopics` set, the loop body executes once per matching topic, sending multiple `TriggerResponse` events into `trigger.ch` for that one workflow from one gateway request.

Critically, the `TriggerEventID` used for both the emitted event and the sent `TriggerResponse` is computed as `body.Sender + payload.TriggerEventId` [3](#0-2) , which does not depend on `topic` at all. So the duplicate sends are not distinct logical events — they carry the identical `TriggerEventID`/execution identity but are delivered as N separate `capabilities.TriggerResponse` on the trigger channel, causing the workflow engine to start N executions from what the requester intended (and what `TriggerEventId` uniquely identifies) as one event.

`payload.Topics` is fully attacker-controlled: it is a JSON array of strings with no uniqueness or cardinality restriction beyond "not empty" [4](#0-3) , and `TriggerRequestPayload.Topics []string` is decoded directly from the gateway request body signed by an ordinary allowed sender [5](#0-4) . An `allowedSenders`-authorized but otherwise unprivileged caller of the Web API trigger gateway endpoint (`HandleGatewayMessage` → `processTrigger`) can set `Topics` to multiple entries that are all registered in one workflow's `allowedTopics`, e.g. `["daily_price_update", "ad_hoc_price_update"]` when both are allowed for the same trigger, in a single HTTP/gateway call.

### Impact Explanation
This lets an already-authorized-but-untrusted external sender trigger repeated/duplicate workflow executions from a single logical trigger event by crafting a request with multiple matching topics, multiplying `fullyMatchedWorkflows` and the number of `TriggerResponse` sent to the same workflow's channel [6](#0-5) . Because workflows can perform actions with side effects (on-chain writes, external calls, spend), this is an unauthorized/duplicate job-run condition triggered by a single external request rather than the intended once-per-event semantics implied by `TriggerEventId`.

### Likelihood Explanation
Any sender already listed in a workflow's `allowedSenders` — a routine unprivileged caller of the Web API trigger endpoint, not an operator or node — can trigger this simply by including several topics from the same workflow's `allowedTopics` list in one request; no race condition, timing, or special privilege is required, only knowledge of a workflow's configured allowed topics.

### Recommendation
Break out of both loops (e.g., via a labeled `break` or a per-trigger flag) once a match/send has occurred for a given `trigger`, so at most one `TriggerResponse` is emitted per workflow per request regardless of how many of its topics matched, matching the intended "only once" semantics the existing comment already describes.

### Proof of Concept
1. Register one workflow trigger with `allowedTopics = ["daily_price_update", "ad_hoc_price_update"]` and `allowedSenders` containing the caller's address (as in `RegisterTrigger`) [7](#0-6) .
2. As that allowed sender, send one gateway `web_api_trigger` message whose `TriggerRequestPayload` has `Topics: ["daily_price_update", "ad_hoc_price_update"]` and a single `TriggerEventId` [5](#0-4) .
3. `processTrigger` matches both topics against the same `trigger.allowedTopics`; because the inner `select`'s `break` does not exit the topic loop, it sends two `TriggerResponse` messages (both with the same `TriggerEventID`) into `trigger.ch` [8](#0-7) , causing the workflow to be started twice from a single request.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L105-154)
```go
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

**File:** core/capabilities/webapi/webapicap/event_trigger_generated.go (L101-117)
```go
type TriggerRequestPayload struct {
	// Key-value pairs for the workflow engine, untranslated.
	Params TriggerRequestPayloadParams `json:"params" yaml:"params" mapstructure:"params"`

	// Timestamp of the event (unix time), needs to be within certain freshness to be
	// processed.
	Timestamp int64 `json:"timestamp" yaml:"timestamp" mapstructure:"timestamp"`

	// Topics corresponds to the JSON schema field "topics".
	Topics []string `json:"topics" yaml:"topics" mapstructure:"topics"`

	// Uniquely identifies generated event (scoped to trigger_id and sender).
	TriggerEventId string `json:"trigger_event_id" yaml:"trigger_event_id" mapstructure:"trigger_event_id"`

	// ID of the trigger corresponding to the capability ID.
	TriggerId string `json:"trigger_id" yaml:"trigger_id" mapstructure:"trigger_id"`
}
```
