### Title
Missing gateway-side allowlist/rate-limiting before forwarding legacy web_api_trigger messages to DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy web-api capabilities handler forwards any structurally-valid, timestamp-fresh `web_api_trigger` message to every node in the DON without applying any allowlist or rate-limiting check, despite an explicit `// TODO: apply allowlist and rate-limiting here` marker at the exact point such a check should occur.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` performs only structural checks — payload decoding, timestamp presence, staleness, and method name — before broadcasting the request to all DON members: [1](#0-0) 

The comment `// TODO: apply allowlist and rate-limiting here` sits directly before the method check and the loop that calls `don.SendToNode` for every member, confirming that gateway-level allowlisting/rate-limiting was intended but is not implemented at this layer. This mirrors the reported bug class: a function that accepts arbitrary externally supplied parameters (here, an unauthenticated/attacker-controlled `Message` with a signed sender that anyone can generate) and performs a sensitive action — network fan-out to every capability node in the DON — without access-control gating at the point of action.

Node-side mitigation exists (per-trigger `allowedSenders`/`allowedTopics`/rate limiter in `core/capabilities/webapi/trigger/trigger.go`, `processTrigger`), [2](#0-1)  but this is a downstream, per-workflow filter that runs only after every node has already received and processed the broadcast message from the gateway, not a gateway-side control preventing the broadcast itself. The absence of the intended allowlist at the gateway means any unauthenticated caller reaching the internet-facing gateway HTTP endpoint (`core/services/gateway/gateway.go` `ProcessRequest`) [3](#0-2)  can cause every node in a DON to receive and process crafted trigger payloads.

### Impact Explanation
Because the gateway forwards to `don.SendToNode` for every member without an allowlist/rate-limit gate, an unprivileged party can flood every node in a DON with crafted `web_api_trigger` messages (only requiring a self-generated valid ECDSA signature and a fresh timestamp — no relationship to any legitimate workflow owner is required at this layer). This is a resource-exhaustion / DoS vector across an entire DON's node fleet and increases attack surface for probing per-workflow trigger allowlists, since the request reaches every node's capability handler regardless of whether the sender is actually authorized for any registered workflow.

### Likelihood Explanation
High likelihood of reachability: the gateway's public HTTP endpoint is explicitly internet-facing and accepts requests routed to `HandleLegacyUserMessage`/`HandleJSONRPCUserMessage` based on DON ID/service name with no additional authentication beyond message signature validity, which any caller can produce. The missing check is explicitly flagged in code as a known gap (`TODO`), indicating it is not accidental dead code but a genuinely unimplemented control.

### Recommendation
Implement the intended gateway-side allowlist and rate-limiting check in `HandleLegacyUserMessage` before the request is dispatched to `don.SendToNode`, mirroring the per-sender/per-topic controls already implemented at the node level in `trigger.go`. At minimum, add a gateway-level rate limiter (the handler already carries a `nodeRateLimiter` field [4](#0-3)  but it is not invoked in `HandleLegacyUserMessage`) and restrict broadcast to senders present in a configured allowlist before message fan-out.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration or relationship to the DON required).
2. Craft a `web_api_trigger` legacy message with a fresh `timestamp` and any `topics`/`params`, sign it with the arbitrary key (as shown in `core/scripts/gateway/web_api_trigger/invoke_trigger.go`) [5](#0-4) .
3. POST the signed message to the gateway's public HTTP endpoint targeting any known DON ID.
4. Observe that `HandleLegacyUserMessage` accepts the message (only checks payload structure, timestamp freshness, and method name) and forwards it via `don.SendToNode` to every member of that DON — with no allowlist/rate-limit check at the gateway despite the `TODO` marking that intent.
5. Repeat rapidly to flood all DON nodes with attacker-controlled payloads, relying only on node-side per-workflow filtering (which does not prevent the broadcast itself) to eventually discard unmatched requests.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/webapi/trigger/trigger.go (L84-119)
```go
// processTrigger iterates over each topic, checking against senders and rateLimits, then starting event processing and responding
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
				fullyMatchedWorkflows++
```

**File:** core/services/gateway/gateway.go (L220-265)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}
```

**File:** core/scripts/gateway/web_api_trigger/invoke_trigger.go (L82-112)
```go
	payload := map[string]any{
		"trigger_id":       "web-api-trigger@1.0.0",
		"trigger_event_id": "action_1234567890",
		"timestamp":        int(time.Now().Unix()),
		"topics":           []string{"daily_price_update"},
		"params": map[string]string{
			"bid": "101",
			"ask": "102",
		},
	}

	payloadJSON, err := json.Marshal(payload)
	if err != nil {
		fmt.Println("error marshalling JSON payload", err)
		return
	}
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: *messageID,
			Method:    *methodName,
			DonID:     *donID,
			Payload:   payloadJSON,
		},
	}
	if err = msg.Sign(key); err != nil {
		fmt.Println("error signing message", err)
		return
	}

	codec := api.JSONRPCCodec{}
	rawMsg, err := codec.EncodeLegacyRequest(msg)
```
