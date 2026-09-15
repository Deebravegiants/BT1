Audit Report

## Title
Missing Allowlist and Rate-Limiting Enforcement for User Requests in Gateway Capabilities Handler - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
The legacy `capabilities.handler.HandleLegacyUserMessage` function contains an explicit unresolved `// TODO: apply allowlist and rate-limiting here` comment, and the code path that follows performs no caller-based allowlist check or rate limiting before broadcasting the request to every DON member node. This is confirmed directly in the source and contrasts with sibling handlers (`vault`, `capabilities/v2`) that do implement authorization/rate-limiting before forwarding requests.

## Finding Description
`gateway.ProcessRequest` is the entry point invoked by the HTTP server (`core/services/gateway/network/httpserver.go`, `handleRequest`) for every incoming client request [1](#0-0) . For legacy requests (identified by a non-empty `DonID`), it validates the JSON-RPC envelope and dispatches directly to `h.HandleLegacyUserMessage(ctx, msg, callback)` without any allowlist or rate-limit check at the gateway layer [2](#0-1) .

Inside `capabilities.handler.HandleLegacyUserMessage`, after payload decoding and a staleness check, the code literally contains the TODO comment followed immediately by dispatch to every DON member with no allowlist/rate-limit gate in between: [3](#0-2) .

The only rate limiting present in this handler (`h.nodeRateLimiter`) is applied in the opposite direction — to outgoing messages initiated by DON nodes (`handleWebAPIOutgoingMessage`) — not to incoming user requests [4](#0-3) . The HTTP server layer (`network/httpserver.go`) only enforces a max-request-body-size limiter and CORS checks, no per-caller allowlist or rate limiter [5](#0-4) .

By contrast, the `vault` handler requires `requestProcessor.ProcessRequest` authorization before dispatching any method other than the public-key lookup, and the `capabilities/v2` HTTP trigger handler performs `authorizeRequest` plus `checkRateLimit` (including per-org/per-workflow settings-backed limits) before forwarding to nodes [6](#0-5) [7](#0-6) . These confirm the pattern exists elsewhere in the codebase but was never implemented for the legacy `web_api_trigger` path, exactly as the TODO states.

## Impact Explanation
Any unauthenticated client reaching the Gateway's HTTP endpoint can submit an unbounded number of `web_api_trigger` legacy messages, each broadcast to every configured DON member node with no per-caller allowlist or throttle [8](#0-7) . This is a genuine allowlist/rate-limit bypass on an internet-facing endpoint, enabling resource exhaustion of DON nodes and of the Gateway's `savedCallbacks` map, which is only bounded by expiry/size-based pruning rather than caller quotas [9](#0-8) .

## Likelihood Explanation
High. No credential, signature, or prior relationship with the DON is required — only a well-formed JSON-RPC envelope with `Method = "web_api_trigger"`, a valid `DonID`, and a non-stale `Timestamp`, all trivially satisfiable by any unprivileged caller per the validation logic shown at lines 359–383 of `handler.go` [10](#0-9) .

## Recommendation
Implement the allowlist and rate-limiting check referenced by the TODO in `HandleLegacyUserMessage`, following the established pattern in `vault.handler.requestProcessor.ProcessRequest` and `capabilities/v2.httpTriggerHandler.authorizeRequest`/`checkRateLimit`, before forwarding requests to DON member nodes.

## Proof of Concept
1. Send a legacy JSON-RPC POST to the Gateway's HTTP endpoint with `Method = "web_api_trigger"`, a valid `DonID`, and a fresh `Timestamp`, without any authorization token.
2. Observe `gateway.ProcessRequest` routes it straight to `capabilities.handler.HandleLegacyUserMessage`, which performs no allowlist or rate-limit check per the unresolved TODO, and forwards the message to every DON member via `don.SendToNode`.
3. Repeat at high volume from a single unauthenticated source; verify no per-caller allowlist or rate limiter blocks the requests, unlike the `vault` and `capabilities/v2` handler paths.

### Citations

**File:** core/services/gateway/network/httpserver.go (L195-235)
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
	duration := time.Since(startTime)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-338)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}

	if expired > 0 || evicted > 0 {
		h.lggr.Infow("Pruned savedCallbacks", "expired", expired, "evicted", evicted, "remaining", len(h.savedCallbacks))
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-383)
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

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
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
