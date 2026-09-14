### Title
Missing sender allowlist/rate-limit check on the legacy `web_api_trigger` gateway path allows any unprivileged HTTP client to fan out workflow-trigger requests to a full DON - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the entry point the public-facing gateway HTTP server invokes (via `gateway.ProcessRequest` → `HandleLegacyUserMessage`) for legacy `web_api_trigger` requests submitted by any external, unauthenticated caller reachable over the gateway's user-facing HTTP port. Unlike its sibling paths (`vault` handler, `httpTriggerHandler`, `webapiTrigger` connector), this handler contains an explicit `// TODO: apply allowlist and rate-limiting here` and never checks whether the requesting sender/workflow is allowed to trigger the target DON before broadcasting the request to every node in `donConfig.Members`.

### Finding Description
The gateway's public HTTP server (`core/services/gateway/network/httpserver.go:195-244`) accepts raw, unauthenticated JSON-RPC messages from the internet and passes them straight to `gateway.ProcessRequest` [1](#0-0) . For legacy messages (`msg.Body.DonID != ""`), `ProcessRequest` only validates the envelope (`msg.Validate()`) and dispatches to the resolved handler's `HandleLegacyUserMessage` — with no allowlist, subscription, or authorization check at the gateway layer itself [2](#0-1) .

Inside the capabilities handler, `HandleLegacyUserMessage` performs only structural checks: payload decoding, a non-zero timestamp check, and a staleness check based on `MaxAllowedMessageAgeSec`. Immediately after those checks, the code contains the unmistakable acknowledgement of the missing control:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [3](#0-2) 

Once the method check passes, the request is converted via `common.ValidatedRequestFromMessage` and unconditionally broadcast to **every** node in the DON:

```go
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [4](#0-3) 

This is structurally identical to the `FCFSMint()` defect: the docstring/comment states an authorization gate ("whitelisted wallet"/"allowlist") is required, but the code path that is actually reachable by an untrusted caller lacks it. Compare this to the two other capability trigger paths that were hardened with real checks:
- The v2 `httpTriggerHandler.HandleUserTriggerRequest` explicitly calls `h.authorizeRequest` (`workflowMetadataHandler.Authorize`) and `h.checkRateLimit` before dispatch [5](#0-4) .
- The node-side `webapiTrigger` connector checks `trigger.allowedSenders[sender.String()]` and a per-workflow `rateLimiter` before delivering the trigger event [6](#0-5) .

The legacy gateway-side `HandleLegacyUserMessage` path has neither of these controls, even though the TODO comment says they belong there and the surrounding code (`nodeRateLimiter`) shows the pattern is normally applied — it's simply applied to node→gateway (outgoing HTTP) traffic in `handleWebAPIOutgoingMessage`, not to the incoming user→gateway trigger path.

### Impact Explanation
Any unauthenticated internet client that can reach the gateway's user HTTP port can submit an arbitrarily-crafted `web_api_trigger` legacy message specifying any `DonID` known to the gateway config. Because there is no sender allowlist or per-sender/workflow rate limit at this layer, the request is broadcast to every member node of that DON. This allows:
- Triggering workflow executions on nodes without proof the caller is an authorized sender for that workflow (impersonation/unauthorized job run — a direct analog of "unauthorized user minting" in the reference finding).
- Unbounded fan-out amplification: one HTTP request causes `N` node-directed sends with no gateway-side throttling of the requesting party, enabling a DoS/spam vector against the DON's node compute.

### Likelihood Explanation
High. The path is reachable by any party who can send an HTTP POST to the gateway's public port with no prior authentication — the same trust boundary described in the external report ("anyone, not only whitelisted users"). The only gates present (`payload.Timestamp != 0`, staleness window, method must equal `MethodWebAPITrigger`) are trivially satisfiable by an attacker crafting the request body themselves.

### Recommendation
Add the sender/workflow allowlist check and a rate limiter to `HandleLegacyUserMessage` before request forwarding, mirroring the pattern already implemented in `httpTriggerHandler.authorizeRequest`/`checkRateLimit` and `webapiTrigger.processTrigger` (`allowedSenders`/`rateLimiter`). Concretely: resolve the request's claimed sender/workflow, verify it against a maintained allowlist (e.g. via the DON config or workflow registry), and reject/`429` requests that fail rate limiting — removing the `// TODO` and closing the gap prior to `don.SendToNode` fan-out.

### Proof of Concept
1. Stand up (or point at) a gateway instance with a configured DON (`donConfig.Members` populated) using the legacy capabilities handler.
2. As an unauthenticated client, send a raw JSON-RPC POST to the gateway's public HTTP endpoint (`core/services/gateway/network/httpserver.go`) with:
   - `msg.Body.DonID` = the target DON ID,
   - `msg.Body.Method` = `"web_api_trigger"`,
   - a `TriggerRequestPayload` with a non-zero, fresh `Timestamp`,
   - any signature value accepted by `common.ValidatedRequestFromMessage` (structural validation only, no sender-allowlist check).
3. Observe that `gateway.ProcessRequest` routes to `handler.HandleLegacyUserMessage`, which passes all checks (decode, timestamp, staleness, method) and calls `don.SendToNode` for every member of `donConfig.Members` — without ever verifying the caller is an allowlisted sender for that workflow/DON, confirming the bypass.

Note: I was not able to fully trace whether the referenced `common.ValidatedRequestFromMessage` performs any signature-based sender check that might partially mitigate this (its implementation was not returned by search), so confirm during triage whether signature validation alone restores an equivalent allowlist guarantee, or whether — as the TODO comment and code structure strongly suggest — no such guarantee exists at this layer.

### Citations

**File:** core/services/gateway/network/httpserver.go (L211-234)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/gateway.go (L253-276)
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
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-396)
```go
	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-420)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
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
