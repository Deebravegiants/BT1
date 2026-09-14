### Title
Missing allowlist enforcement lets any unprivileged HTTP client trigger `web_api_trigger` broadcasts to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Capabilities gateway handler's `HandleLegacyUserMessage` accepts a `web_api_trigger` message from any client that reaches the gateway's public HTTP endpoint, and forwards it to every node in the DON without any allowlist check verifying the sender is an authorized workflow owner. The check is explicitly marked as not-yet-implemented in the code.

### Finding Description
The gateway's HTTP server dispatches every incoming request straight into `gateway.ProcessRequest`, which for legacy DON-addressed messages only validates message shape (`msg.Validate()`) before calling the target handler's `HandleLegacyUserMessage`. [1](#0-0) 

For the capabilities handler, `HandleLegacyUserMessage` decodes the payload, checks that the timestamp isn't stale, and then reaches a comment stating the missing control explicitly: [2](#0-1) 

Immediately after that `// TODO: apply allowlist and rate-limiting here` comment, the only remaining check is that the method equals `MethodWebAPITrigger`; there is no verification that the message sender/signature corresponds to an authorized/allowlisted workflow owner. If it passes, the request is broadcast to every member of the DON: [3](#0-2) 

The handler-level unit test file itself confirms this gap is still open and untested: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated`. [4](#0-3) 

This is structurally the same bug class as the Infrared report: a privileged/critical action (queuing validator cutting board weights that are supposed to reflect a trusted, verified onchain outcome) is executed based on unverified input, with no code-level guarantee tying the actual input to an authorized source. Here, the "critical action" is fanning a trigger message out to an entire DON of nodes, and the "verification gap" is the missing allowlist check on the message sender before that fan-out occurs — meaning any unprivileged actor capable of reaching the gateway's HTTP endpoint can cause every DON node to receive and process an arbitrary `web_api_trigger` message that has not been confirmed to originate from an authorized workflow/user.

### Impact Explanation
Because the gateway is internet-facing and the allowlist check is not yet implemented in this code path, an unprivileged actor can submit a legacy `web_api_trigger` request that is forwarded to every DON node as if it came from an authorized sender. Depending on how individual capability nodes act on these forwarded trigger messages downstream, this can lead to unauthorized workflow triggering/spam across an entire DON, resource exhaustion of `savedCallbacks`/DON capacity, or execution of workflow logic that was never vetted for that sender — a direct disconnect between what should be an "authorized outcome" (an allowlisted request) and what is actually being acted upon.

### Likelihood Explanation
High for reachability: the vulnerable path is on the standard, unauthenticated legacy request flow of the gateway's public HTTP server (`httpServer.handleRequest` → `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage`), requiring no special role, only a syntactically valid, timely, correctly-methoded message. [5](#0-4) 
The missing-check comment and the corresponding pending test TODO indicate the gap is a known, currently-unaddressed condition rather than a hypothetical/theoretical one.

### Recommendation
Implement the allowlist (and rate-limiting) check called out by the TODO before forwarding any `web_api_trigger` message to DON members in `HandleLegacyUserMessage`, verifying the message sender against an authoritative, verifiable list of permitted senders/workflow owners (mirroring the recommendation from the analog report to establish a trustless/verifiable connection between the claimed authorization and the action taken), and add corresponding tests that exercise both allowed and rejected senders.

### Proof of Concept
Not independently reproduced with a live environment; based on static code review only. An unprivileged client could reach this path by:
1. POSTing a JSON-RPC legacy request to the gateway's HTTP endpoint with `don_id` set to a valid DON and `method = "web_api_trigger"`, with a `TriggerRequestPayload` containing a non-zero, current `Timestamp`.
2. Because `msg.Validate()` only checks structural well-formedness (not sender authorization against an allowlist) and the capabilities handler's allowlist check is not implemented, the message passes through to `don.SendToNode` for every DON member.
Full exploit confirmation (e.g., what individual capability/workflow nodes do with an unauthorized trigger) would require tracing the DON-side node handling of `MethodWebAPITrigger`, which was not available within the scope of this review; this should be validated by a Devin session with full repository/runtime access.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-396)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/services/gateway/network/httpserver.go (L195-234)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

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
