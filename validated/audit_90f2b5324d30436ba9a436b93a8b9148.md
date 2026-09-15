This confirms the claim is accurate. `Message.Validate()` only recovers the signer via ECDSA signature recovery and requires an internally-consistent signature — it does not check the signer/sender against any whitelist. Any attacker with an arbitrary ECDSA keypair can self-sign a message and pass validation, meaning `msg.Validate()` provides no real authorization boundary before `HandleLegacyUserMessage` is invoked.

Audit Report

## Title
Legacy Web API Trigger messages bypass allowlist and rate-limiting, allowing free DON resource consumption - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`Handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` only performs payload-decode, non-zero-timestamp, and staleness checks before dispatching the trigger request to every DON member node via `don.SendToNode`. It explicitly skips allowlist and rate-limit enforcement (self-documented by `// TODO: apply allowlist and rate-limiting here` at line 384), unlike the sibling JSON-RPC trigger path in `core/capabilities/webapi/trigger/trigger.go`'s `processTrigger`, which enforces `allowedSenders` and `rateLimiter.Allow` before dispatch.

## Finding Description
`gateway.ProcessRequest` routes any legacy DON-ID-addressed request to the target handler after only generic envelope validation via `msg.Validate()` [1](#0-0) . `Message.Validate()` merely checks field-length/format constraints and recovers the signer address from the ECDSA signature via `ExtractSigner()` — it does not check the recovered sender against any allowlist, so any caller possessing an arbitrary keypair can self-sign a validly-shaped message and pass this check [2](#0-1) .

`HandleLegacyUserMessage` then only validates payload decoding, non-zero timestamp, and staleness, before immediately looping over `h.donConfig.Members` and calling `don.SendToNode` for every member — with the allowlist/rate-limit gate explicitly marked as unimplemented via the TODO comment on line 384 [3](#0-2) . This contrasts with `NewHandler`, which only wires a `nodeRateLimiter` for outbound node-originated messages (used in `handleWebAPIOutgoingMessage`), not a user-facing limiter for this inbound legacy path [4](#0-3) . The sibling `processTrigger` function in the JSON-RPC path does enforce `trigger.allowedSenders[sender.String()]` and `trigger.rateLimiter.Allow(body.Sender)` before dispatching an event [5](#0-4) . The project's own test suite acknowledges this gap with a TODO: "Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated" [6](#0-5) .

## Impact Explanation
Any unauthenticated caller who can reach the Gateway's public legacy HTTP endpoint can force every node in a targeted DON to process and act on attacker-controlled `web_api_trigger` messages, with no allowlist or rate-limit throttling gate at the Gateway/handler layer. This is a resource-consumption / DoS-class issue — nodes expend compute and network resources dispatching and (at the node/capability layer) evaluating these messages without the sender ever being checked against an allowlist or subjected to a per-sender/global rate limit at the gateway ingress point. Severity is bounded because final authorization (`allowedSenders`/`allowedTopics`) for actually triggering a workflow execution still occurs downstream in `processTrigger` at the capability layer, so unauthorized senders cannot actually start a workflow execution — but the Gateway itself provides no defense-in-depth and allows unthrottled fan-out to the full DON membership as free spam traffic.

## Likelihood Explanation
Likelihood is high for reachability: `HandleLegacyUserMessage` is a required part of the `handlers.Handler` interface and is directly invoked by `gateway.ProcessRequest` for any legacy DON-ID-addressed request [7](#0-6) . No privileged credential or role is required — only a self-generated ECDSA keypair to produce a signature that satisfies `Message.Validate()`. The gap is self-documented via the TODO comment and the corresponding test-file TODO, indicating it is a known, currently-unaddressed structural omission rather than a subtle edge case.

## Recommendation
Enforce sender allowlist and rate-limit checks (mirroring `trigger.allowedSenders`/`trigger.rateLimiter.Allow` from `core/capabilities/webapi/trigger/trigger.go`) in `HandleLegacyUserMessage` before invoking `don.SendToNode`, or add a dedicated user-facing rate limiter to the `handler` struct (distinct from `nodeRateLimiter`) keyed by `msg.Body.Sender`, and reject requests exceeding limits before fan-out. Alternatively, deprecate/remove the legacy path in favor of the already-guarded JSON-RPC (`HandleJSONRPCUserMessage`) flow.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration or credential needed).
2. Construct a `webapicap.TriggerRequestPayload` with arbitrary `Topics` and a fresh `Timestamp`, and sign it as a `web_api_trigger` legacy message addressed to a known `DonID` using `Message.Sign`.
3. POST this JSON-RPC request to the Gateway's public HTTP endpoint; `gateway.ProcessRequest` validates only the envelope via `msg.Validate()` (line `gateway.go:256`) and routes it to `handler.HandleLegacyUserMessage`.
4. Observe that `HandleLegacyUserMessage` passes decode/timestamp/staleness checks, skips the (unimplemented) allowlist/rate-limit step at line 384, and loops over `h.donConfig.Members` calling `don.SendToNode` for each member — confirmable via a Go unit test extending `handler_test.go`'s existing `TestHandlerReceiveHTTPMessageFromClient` suite by asserting `don.SendToNode` is invoked for every DON member even when the signer is not present in any `allowedSenders` configuration.
5. Repeat at high request volume from the same or different unregistered keys to demonstrate unthrottled fan-out to all DON nodes.

### Citations

**File:** core/services/gateway/gateway.go (L253-265)
```go
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

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L96-116)
```go
	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, err
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, err
	}

	return &handler{
		config:          cfg,
		don:             don,
		donConfig:       donConfig,
		lggr:            logger.Named(lggr, "WebAPIHandler."+donConfig.DonID),
		httpClient:      httpClient,
		nodeRateLimiter: nodeRateLimiter,
		savedCallbacks:  make(map[string]*savedCallback),
		stopCh:          make(services.StopChan),
		metrics:         metrics,
	}, nil
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```

**File:** core/services/gateway/handlers/handler.go (L31-47)
```go
type Handler interface {
	job.ServiceCtx

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback Callback) error

	// Handlers should not make any assumptions about goroutines calling HandleNodeMessage.
	// should be non-blocking
	// should validate the message inside the response
	HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error
```
