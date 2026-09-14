Confirmed reachable path: any unprivileged HTTP client can call `httpServer.handleRequest` → `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage` for `MethodWebAPITrigger`, and this legacy path performs no sender allowlist check before broadcasting the trigger request to every DON node. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Missing allowlist enforcement on legacy WebAPI trigger requests lets any caller invoke privileged DON triggers - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` in the capabilities gateway handler processes `MethodWebAPITrigger` requests from any unauthenticated caller and forwards them to every member node of the DON, with an explicit unfinished TODO acknowledging the missing check: `// TODO: apply allowlist and rate-limiting here`. This mirrors the OpenClaw bug class: a message-handling path that is supposed to be gated by an allowlist/authorization check treats every inbound sender as authorized, letting any client trigger privileged DON-side execution.

### Finding Description
The gateway's public HTTP endpoint (`httpServer.handleRequest`) accepts raw requests from any network caller and passes them into `gateway.ProcessRequest`, which for legacy-style requests calls `h.HandleLegacyUserMessage(ctx, msg, callback)` [2](#0-1) . For the capabilities WebAPI handler, `HandleLegacyUserMessage` decodes the payload, validates only the message timestamp/age, and then — for `MethodWebAPITrigger` — sends the request to every node in `donConfig.Members` without any check that the sender is an authorized/allowlisted caller for that workflow/DON:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
    ...
}
req, err := common.ValidatedRequestFromMessage(msg)
...
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [4](#0-3) 

Unlike the newer JSON-RPC/HTTP-trigger v2 path, which authorizes each request via `workflowMetadataHandler.Authorize` against a per-workflow signer allowlist [5](#0-4)  and [6](#0-5) , the legacy `HandleLegacyUserMessage` path in `handler.go` contains no equivalent identity/allowlist check — it only validates message freshness (`MaxAllowedMessageAgeSec`) and method name before fanning the request out to all DON nodes.

### Impact Explanation
Any network client that can reach the gateway's public HTTP port can submit a legacy `web_api_trigger` request and have it broadcast to every node in the target DON, without being an allowlisted/authorized workflow signer. This is directly analogous to the "any DM sender treated as command-authorized" bug: the check exists conceptually (there is an explicit allowlist mechanism used elsewhere in the same codebase) but is not applied on this particular inbound path, letting an unprivileged caller reach privileged DON-triggering functionality.

### Likelihood Explanation
The gateway HTTP endpoint is explicitly internet/network-facing and accepts unauthenticated requests by design (`ProcessRequest` takes an optional bearer token but does not require or check a caller-identity allowlist for legacy requests). Reaching this code path requires only crafting a legacy-format JSON-RPC request with a DON ID and method `web_api_trigger`, which is straightforward for any client with network access to the gateway.

### Recommendation
Implement the allowlist/authorization check referenced by the TODO before forwarding `MethodWebAPITrigger` (and any other legacy) requests to DON nodes — e.g., reuse the same per-workflow authorized-key/signer verification used by the v2 HTTP trigger handler (`workflowMetadataHandler.Authorize`), or otherwise reject unauthenticated/unallowlisted senders prior to `don.SendToNode` fan-out.

### Proof of Concept
1. Stand up a gateway with the capabilities `handler.go` WebAPI handler configured for a DON.
2. As an arbitrary, non-allowlisted client, POST a legacy-format JSON-RPC request to the gateway's public HTTP port with `Body.Method = "web_api_trigger"`, a valid `DonID`, and a fresh timestamp/payload (no valid workflow signer credentials required).
3. Observe that `HandleLegacyUserMessage` forwards the request to all `donConfig.Members` nodes (per `core/services/gateway/handlers/capabilities/handler.go:416-419`) without ever checking the sender against a per-workflow or per-caller allowlist, unlike the v2 JWT/allowlist-gated trigger path.

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

**File:** core/services/gateway/gateway.go (L253-280)
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
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}

```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
```
