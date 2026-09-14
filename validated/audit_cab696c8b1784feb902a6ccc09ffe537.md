Confirmed: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the internet-facing entry point reachable from an unprivileged HTTP client via the gateway's `ProcessRequest` legacy path, and it broadcasts every incoming `web_api_trigger`/`web_api_target` message to all DON node members without any sender allowlist or rate-limit enforcement, despite an explicit `// TODO: apply allowlist and rate-limiting here` comment marking the intended (but never implemented) check. This is directly analogous to the HardVault report: documentation/comments promise a security control (allowlist enforcement) that is never actually wired up in the code path, so unprivileged callers get more capability than intended.

### Title
Legacy gateway user-message handler never enforces the documented allowlist/rate-limit, letting any unprivileged caller broadcast trigger requests to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `handler.HandleLegacyUserMessage` function, which processes incoming HTTP requests from external, unauthenticated callers via the Gateway's legacy `ProcessRequest` path, contains a comment stating `// TODO: apply allowlist and rate-limiting here` but never implements this check before forwarding the request to every member of the DON.

### Finding Description
`gateway.ProcessRequest` in `core/services/gateway/gateway.go` accepts raw HTTP bodies from external, unauthenticated clients and, for legacy requests (`msg.Body.DonID != ""`), calls `h.HandleLegacyUserMessage(ctx, msg, callback)` [1](#0-0) . Inside `HandleLegacyUserMessage`, the code validates payload decoding, timestamp freshness, and method name, but the intended allowlist/rate-limit check is only a comment that was never implemented: `// TODO: apply allowlist and rate-limiting here` [2](#0-1) . After these checks the request is saved as a callback and broadcast unconditionally to every DON member: `for _, member := range h.donConfig.Members { err = errors.Join(err, don.SendToNode(ctx, member.Address, req)) }` [3](#0-2) .

This contrasts with the sibling, better-implemented `webapiTrigger`/`triggerConnectorHandler` path in `core/capabilities/webapi/trigger/trigger.go`, which enforces a real `allowedSenders` map and per-sender rate limiter before dispatching a trigger event: it rejects unauthorized senders with `err = fmt.Errorf("unauthorized Sender %s, messageID %s", ...)` and checks `trigger.rateLimiter.Allow(body.Sender)` [4](#0-3) . The `handler.go` legacy path has no equivalent sender check at all — it is documented/intended (per the TODO and per the analogous trigger handler design) but simply missing, so requests reach the DON with no gate.

### Impact Explanation
Any unprivileged client that can reach the Gateway's HTTP endpoint can send arbitrary `web_api_trigger` payloads that get broadcast to every node in the configured DON, with no allowlist restricting which senders may trigger which DON/workflow, and no rate limiting to bound abuse. This is analogous to the HardVault report where a documented protection (yield generation via Compound deposit) was silently never implemented — here the documented protection (allowlist/rate-limiting) is silently never implemented, exposing the DON nodes to unauthenticated request flooding/spam via this legacy ingestion path.

### Likelihood Explanation
High: this is the default legacy code path executed whenever a `DonID`-bearing message hits the gateway's `ProcessRequest` (i.e., whenever any legacy-configured DON handler serves external HTTP requests), requiring no special privileges — just an HTTP POST to the gateway's public-facing endpoint.

### Recommendation
Implement the missing allowlist and rate-limiting checks in `HandleLegacyUserMessage` before saving the callback and broadcasting to DON members, mirroring the `allowedSenders`/`rateLimiter` enforcement already present in `triggerConnectorHandler.processTrigger` [4](#0-3) , or explicitly document/gate this legacy handler as deprecated/internal-only if it is not meant to serve untrusted external traffic.

### Proof of Concept
1. Configure a Gateway with a legacy service-based/DON-ID handler using `capabilities.NewHandler` (`core/services/gateway/handlers/capabilities/handler.go`).
2. Send an HTTP POST directly to the Gateway's `ProcessRequest` endpoint with a well-formed legacy `api.Message` whose `Body.DonID` is set, `Body.Method` is `web_api_trigger`, and `Body.Payload` contains a valid, fresh `webapicap.TriggerRequestPayload` with an arbitrary sender/topic — no credentials, allowlist membership, or prior authorization are required.
3. Observe that `HandleLegacyUserMessage` passes payload/timestamp/method checks and calls `don.SendToNode` for every DON member [3](#0-2) , delivering the request to all nodes despite no allowlist or rate-limit having been applied, confirming the documented (TODO) control is absent.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-419)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-118)
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
```
