I found a concrete analog: an unbounded, attacker-controlled `topics` array processed in a nested loop within the WebAPI Trigger gateway message handler.

### Title
Unbounded attacker-controlled `topics` array causes O(triggers × topics) CPU amplification in WebAPI Trigger gateway handler - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
The `web-api-trigger@1.0.0` capability accepts an externally-supplied HTTP trigger request (relayed by the Gateway) whose payload contains a `topics` array with no maximum length enforced by validation, schema, or the gateway transport layer. `processTrigger` iterates this array in a nested loop against every registered trigger, so a single unprivileged HTTP caller can force disproportionate CPU work on the node.

### Finding Description
`triggerConnectorHandler.processTrigger` unmarshal's the `TriggerRequestPayload` from the message body received via `HandleGatewayMessage`, which is itself invoked whenever the Gateway relays an external, unauthenticated-until-later-checked HTTP request to a node's WebAPI Trigger capability [1](#0-0) . The only validation performed on `topics` is a non-empty check; there is no upper bound on its length: [2](#0-1) .

The function then executes a nested loop `for _, trigger := range triggers { for _, topic := range topics { ... } }`, comparing every topic against every registered trigger's `allowedTopics` map, and for matches also checks `allowedSenders` and rate limiter state: [3](#0-2) .

The JSON schema for `TriggerRequestPayload` also does not constrain array size or item count for `topics`: [4](#0-3) , and the generated Go struct performs no additional bound: [5](#0-4) .

Because sender/allowlist and rate-limit checks only run *after* a topic is matched against a trigger's `allowedTopics` (i.e., inside the innermost `if`), an unauthenticated caller can still cause the outer `O(len(triggers) * len(topics))` iteration to execute in full even if none of the supplied topics are legitimate, since the comparison itself (map lookup per topic per trigger) is unavoidable before any authorization gate is reached.

### Impact Explanation
This is a classic unbounded-loop resource-exhaustion pattern analogous to the referenced report: work performed scales with a caller-controlled input size (`topics`) multiplied by node state (number of registered triggers/workflows), with no cap on either the request size (topics count) at the JSON-RPC/message layer specific to this handler, or on iteration cost. A single crafted HTTP-relayed request with a very large `topics` array can consume disproportionate CPU on the node's gateway connector goroutine relative to the small request size, potentially degrading trigger processing for legitimate senders (a DoS on trigger dispatch), especially as more workflows register triggers on the same node.

### Likelihood Explanation
Reaching this path requires only sending an HTTP request that the Gateway relays as a `MethodWebAPITrigger` message — this is the intended entry point for arbitrary external/unprivileged clients invoking web-API-triggered workflows, and does not require prior authentication beyond what the Gateway/handler generically enforces before dispatch (sender/topic authorization happens inside the loop, not before it). The overall message size is bounded by the gateway's generic `MaxRequestBytes`/`MaxRequestBytesLimiter` config [6](#0-5) , which limits worst-case topic count somewhat, but no per-field limit exists on the number of `topics` entries or on total registered triggers being multiplied against them, so likelihood of a meaningful CPU-amplification effect is moderate to high depending on configured `MaxRequestBytes` and the number of registered workflows.

### Recommendation
Add an explicit maximum length check on `payload.Topics` (and ideally on `allowedTopics`/`allowedSenders` set sizes) in `processTrigger`, similar to the existing empty-check, rejecting oversized requests early with a clear error before the nested loop executes. Consider restructuring the loop to deduplicate topics (e.g., via a set) before iterating, and to move sender/rate-limit checks earlier where possible to fail fast, reducing the effective iteration cost from `O(len(triggers) * len(topics))` to a bounded amount independent of attacker input size.

### Proof of Concept
1. Register one or more WebAPI Trigger workflows with `allowedTopics` (as in `TestTriggerExecute`) [7](#0-6) .
2. As an unprivileged external client, send an HTTP request to the Gateway's WebAPI Trigger endpoint with a `TriggerRequestPayload` whose `topics` array contains a very large number of distinct strings (bounded only by `MaxRequestBytes`), none of which need to match `allowedTopics`.
3. The Gateway relays this as a `MethodWebAPITrigger` JSON-RPC request to `HandleGatewayMessage` → `processTrigger` [8](#0-7) .
4. `processTrigger`'s nested loop performs `len(triggers) * len(topics)` map lookups per request; repeating this request (optionally against multiple concurrently registered triggers) amplifies CPU cost with each single, small HTTP call, since there is no size cap beyond overall byte-size limits.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-96)
```go
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-119)
```go
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

**File:** core/services/gateway/network/httpserver.go (L40-52)
```go
type HTTPServerConfig struct {
	Host                   string
	Port                   uint16
	TLSEnabled             bool
	TLSCertPath            string
	TLSKeyPath             string
	Path                   string
	ContentTypeHeader      string
	ReadTimeoutMillis      uint32
	WriteTimeoutMillis     uint32
	RequestTimeoutMillis   uint32
	MaxRequestBytes        int64
	MaxRequestBytesLimiter limits.BoundLimiter[config.Size] // supersedes MaxRequestBytes, if set
```

**File:** core/capabilities/webapi/trigger/trigger_test.go (L159-177)
```go
func TestTriggerExecute(t *testing.T) {
	if testing.Short() {
		t.Skip("too slow for testing.Short")
	}

	th := setup(t)
	ctx := t.Context()
	ctx, cancelContext := context.WithDeadline(ctx, time.Now().Add(10*time.Second))
	Config, _ := workflowTriggerConfig(th, []string{address1}, []string{"daily_price_update", "ad_hoc_price_update"})
	triggerReq := capabilities.TriggerRegistrationRequest{
		TriggerID: triggerID1,
		Metadata: capabilities.RequestMetadata{
			WorkflowID:    workflowID1,
			WorkflowOwner: owner1,
		},
		Config: Config,
	}
	channel, err := th.trigger.RegisterTrigger(ctx, triggerReq)
	require.NoError(t, err)
```
