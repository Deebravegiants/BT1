### Title
Missing allowlist/rate-limiting on legacy gateway user messages allows any unauthenticated caller to trigger DON-wide webapi_trigger capability execution - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The internet-facing Gateway HTTP server accepts JSON-RPC requests and routes legacy ("DonID"-bearing) messages to `handler.HandleLegacyUserMessage`. That function contains an explicit `// TODO: apply allowlist and rate-limiting here` and performs no allowlist, authentication-strength, or per-caller rate-limiting check before broadcasting the request to every member node of the target DON. This mirrors the reported bug class: a state-mutating/DON-triggering entry point is reachable "callable from anyone" without an access-control gate.

### Finding Description
The HTTP server accepts raw requests with only an optional bearer token passed through as `auth`, with no requirement that it be present or valid for legacy DON-ID requests: [1](#0-0) 

`gateway.ProcessRequest` decodes the request and, for legacy requests (`msg.Body.DonID != ""`), only calls `msg.Validate()` (structural/signature-format validation) before dispatching straight to the handler's `HandleLegacyUserMessage`: [2](#0-1) 

Inside the capabilities handler, `HandleLegacyUserMessage` performs payload decoding, a staleness check, and a method check, but the allowlist/rate-limiting gate is explicitly marked as not implemented: [3](#0-2) 

After these checks, the handler unconditionally fans the message out to every node in the DON: [4](#0-3) 

Unlike the newer `v2` HTTP trigger path, which enforces JWT authentication, authorized-key checks, and per-workflow-owner rate limiting before dispatch, this legacy path has no equivalent gate — the comment in the code acknowledges the gap is intentional/known but unresolved.

### Impact Explanation
Any client able to reach the gateway's public HTTP endpoint (no valid API key, JWT, or DON-membership check is enforced for this path) can submit a well-formed, appropriately-timestamped `web_api_trigger` message and have it broadcast to every node of an arbitrary configured DON. This can be used to: flood DON nodes with trigger messages (no per-caller rate limit), consume `savedCallbacks` capacity (partially bounded by `MaxSavedCallbacks`/pruning), and invoke workflow trigger processing on nodes without any check that the caller is an authorized/allowlisted requester. This is analogous to the reported "callable from anyone" issue — the mutating/dispatch operation lacks the restriction that the code's own comment admits is missing.

### Likelihood Explanation
High likelihood of exploitability if this legacy code path is exposed on any production gateway configuration: the only preconditions are a syntactically valid signed `api.Message` with a `DonID` set to a value that maps to a configured handler in `g.handlers`, and a valid message signature per `msg.Validate()` (which does not need to correspond to any allowlisted identity — it only needs to be well-formed and structurally consistent, since the gap the TODO refers to is precisely the allowlist step). No secret, JWT, or session token is required for this path, unlike the parallel v2 HTTP trigger flow.

### Recommendation
Implement the allowlist/rate-limiting check called out by the TODO in `HandleLegacyUserMessage` before fanning out to DON members: verify the caller/sender is present in a DON- or workflow-scoped allowlist (mirroring the `v2` `httpTriggerHandler`'s JWT + authorized-key + per-owner rate-limit pattern), and reject/rate-limit unauthenticated or unauthorized legacy requests. Until fixed, consider disabling or gating the legacy DON-ID request path in production configurations.

### Proof of Concept
1. Deploy a Gateway with a configured DON (`donConfig.Members` non-empty) using the `capabilities` handler for legacy requests.
2. From an unauthenticated client, POST to the gateway's configured HTTP path a JSON-RPC request whose decoded `api.Message` has: `Body.DonID` = the target DON ID, `Body.Method` = `web_api_trigger`, a `Body.Payload` containing a `webapicap.TriggerRequestPayload` with `Timestamp` set to `now()`, and a structurally valid `Signature` per `msg.Validate()`.
3. Observe in `gateway.ProcessRequest` (`core/services/gateway/gateway.go:253-272`) that only `msg.Validate()` runs before `HandleLegacyUserMessage` is invoked.
4. Observe in `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go:359-420`) that no allowlist check occurs (per the `TODO` comment) and the message is sent to every DON member via `don.SendToNode`.
5. Confirm the request reaches and is processed by DON nodes, despite the caller never having been checked against any allowlist or authenticated beyond message-format validation.

Note: I was unable to fully inspect `api.Message.Validate()`/`Sign()` implementation details (in `core/services/gateway/api/message.go`) within the available iterations to conclusively determine whether `Validate()` cryptographically ties the signature to a DON-known public key. If `Validate()` does enforce that the signer is a member of the target DON's own signer set, the severity of this specific finding would be reduced to a rate-limiting/DoS gap rather than a full authorization bypass; this should be verified directly in that file before finalizing severity.

### Citations

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
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
