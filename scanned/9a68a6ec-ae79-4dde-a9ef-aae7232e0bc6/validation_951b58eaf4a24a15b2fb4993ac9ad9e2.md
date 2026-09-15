### Title
Unbounded `topics` array in `WebAPITrigger` payload allows a single sender to force O(registeredWorkflows × topics) work per gateway message - (File: `core/capabilities/webapi/trigger/trigger.go`)

### Summary
The gateway-facing `triggerConnectorHandler.processTrigger` iterates over **all** registered workflow triggers and, for each trigger, over the full `topics` array supplied in the incoming, attacker-controlled `TriggerRequestPayload`. Neither the trigger-registration schema (`allowedSenders`/`allowedTopics`) nor the request payload schema (`topics`) enforces any maximum array length, so a single externally-reachable message can force the node to perform an unbounded number of iterations before any authorization check gates the work.

### Finding Description
`triggerConnectorHandler.HandleGatewayMessage` unmarshals an inbound gateway message into `webapicap.TriggerRequestPayload` and, for the `MethodWebAPITrigger` method, calls `processTrigger`: [1](#0-0) 

`processTrigger` performs a nested loop over every currently registered `webapiTrigger` and every string in `payload.Topics`: [2](#0-1) 

Critically, the per-topic work (`trigger.allowedTopics[topic]` lookup, and on match a further `trigger.allowedSenders[sender.String()]` check) happens for *every* topic against *every* registered trigger, before the sender is confirmed to be authorized for that specific trigger. The `topics` field of `TriggerRequestPayload` has no length bound in its JSON schema: [3](#0-2) 

Likewise, `allowedSenders`/`allowedTopics` on the `TriggerConfig` used at `RegisterTrigger` time are unbounded arrays with no size cap: [4](#0-3) 

The registration path itself only requires at least one entry, not a maximum: [5](#0-4) 

The inbound message is only structurally validated (`ValidatedMessageFromReq`/`msg.Validate()`), which does not impose a size limit on the `topics` array carried in the message body: [6](#0-5) 

This handler sits in the gateway's message-envelope/handler pipeline that receives messages from external (non-DON-operator) callers via `HandleGatewayMessage`, which is exactly the internet-facing gateway surface in scope.

### Impact Explanation
An external caller (not necessarily one that is whitelisted for any given workflow) can submit a single `WebAPITrigger` message with a very large `topics` array. Because `processTrigger` walks `registeredWorkflows × topics` before any per-trigger authorization succeeds, and this loop executes while holding no rate limiting until after a topic match is found, one malicious/oversized message can consume disproportionate CPU on the node handling gateway traffic, delaying or starving processing of legitimate trigger messages from other, properly-whitelisted senders — i.e., it can make it practically impossible for legitimate callers' triggers to be delivered/processed in a timely manner. This mirrors the reported bug class (unbounded array iteration on an unprivileged-facing entry point causing denial of the intended operation for legitimate users), scoped here to the gateway trigger-handling path rather than smart-contract gas.

### Likelihood Explanation
Likelihood is moderate: the request only needs to pass `ValidatedMessageFromReq`/`msg.Validate()` structural checks (a well-formed signed envelope with a valid `Sender`), not per-trigger authorization, before the expensive nested loop executes. Any party capable of sending a signed webapi-trigger message to the gateway can attempt this; the more registered triggers/topics existing at a given time, the larger the amplification.

### Recommendation
1. Enforce explicit maximum sizes for `TriggerRequestPayload.Topics` and for `TriggerConfig.AllowedSenders`/`AllowedTopics` in the JSON schema and/or in `ValidateConfig`/`RegisterTrigger`/payload validation, rejecting oversized arrays before processing.
2. Reorder `processTrigger` to check `trigger.allowedSenders[sender.String()]` once per trigger before iterating `topics` for that trigger, so unauthorized senders cannot force full topic-array iteration against triggers they cannot match.
3. Apply the existing per-sender rate limiter (or a lightweight pre-check) before the nested topic loop rather than after a topic/sender match, to bound CPU cost of the initial message-processing phase itself.

### Proof of Concept
1. Register N workflows via `RegisterTrigger` each with distinct `allowedTopics`/`allowedSenders` sets (attacker can be one of many external workflow developers able to register triggers without size limits, per `RegisterTrigger` at [5](#0-4) ).
2. Craft a `WebAPITrigger` gateway message whose `TriggerRequestPayload.Topics` contains a very large number of distinct topic strings (no size limit is enforced by the schema at [7](#0-6) ).
3. Send the message through `HandleGatewayMessage`; `processTrigger`'s nested loop at [8](#0-7)  executes `N × len(Topics)` map lookups for this single message, consuming CPU proportional to attacker-chosen input size before any authorization for the sender against most triggers is confirmed, delaying processing of concurrently arriving legitimate trigger messages.

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

**File:** core/capabilities/webapi/trigger/trigger.go (L212-250)
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
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L5-33)
```json
        "TriggerConfig": {
            "description": "See https://gateway-us-1.chain.link/web-api-trigger",
            "type": "object",
            "properties": {
                "allowedSenders": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "allowedTopics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "rateLimiter": {
                    "$ref": "#/$defs/RateLimiterConfig"
                },
                "requiredParams": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["allowedSenders", "allowedTopics", "rateLimiter", "requiredParams"],
            "additionalProperties": false
        },
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L53-84)
```json
        "TriggerRequestPayload": {
            "type": "object",
            "properties": {
                "trigger_id": {
                    "type": "string",
                    "description": "ID of the trigger corresponding to the capability ID."
                },
                "trigger_event_id": {
                    "type": "string",
                    "description": "Uniquely identifies generated event (scoped to trigger_id and sender)."
                },
                "timestamp": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Timestamp of the event (unix time), needs to be within certain freshness to be processed."
                },
                "topics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description" : "An array of a single topic (string) to be started by this event."
                    }
                },
                "params": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Key-value pairs for the workflow engine, untranslated."
                }
            },
            "required": ["trigger_id", "trigger_event_id", "timestamp", "topics", "params"],
            "additionalProperties": false
        }
```

**File:** core/services/gateway/handlers/common/message_util.go (L34-58)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
}
```
