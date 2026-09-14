## Finding

### Title
Unvalidated Web API trigger requests are forwarded to DON nodes without allowlist/authorization checks - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's `capabilities` handler forwards any signed `web_api_trigger` request straight to all DON node members without verifying that the sender is an authorized/allowlisted workflow owner, mirroring the reported flash-loan-callback bug class where a privileged action is executed without validating the true initiator of the request.

### Finding Description
The public gateway HTTP endpoint accepts JSON-RPC requests from any external caller and routes them via `gateway.ProcessRequest` [1](#0-0)  to the resolved handler's `HandleLegacyUserMessage`. For legacy requests, the only check performed before dispatch is `msg.Validate()`, which is a self-consistency check that the request signature matches the claimed sender — it does not check whether that sender/workflow is registered or permitted to trigger anything.

In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` decodes the payload, checks the payload isn't stale, and then — right where an authorization/allowlist check should occur — has an explicit `// TODO: apply allowlist and rate-limiting here` comment, followed immediately by forwarding the request to every member of the DON: [2](#0-1) 

This is functionally the same root cause as the reported issue: a function that performs a consequential, trust-sensitive action (here: forwarding a trigger request that causes DON nodes to execute a workflow trigger) without validating that the caller/initiator is a permitted party. Just as `executeOperation` in the audited contract executes flash-loan repayment logic for *any* caller claiming to be the AAVE pool, `HandleLegacyUserMessage` executes DON-forwarding logic for *any* caller who can produce a validly-signed (but self-generated, since anyone can generate an ECDSA keypair) message.

By contrast, the sibling `vault` gateway handler in the same codebase *does* enforce an authorization step (`AuthorizeRequest`) that checks a workflow-registry-backed allowlist before any request is processed [3](#0-2)  and [4](#0-3) , confirming that allowlist-based authorization is the intended security control for gateway-routed requests, and that its absence in the capabilities/webapicap handler is a gap rather than by design (as marked by the TODO).

### Impact Explanation
Any unprivileged party who can reach the gateway's public HTTP endpoint can submit a `web_api_trigger` message that gets fanned out to every node in the configured DON, without being an allowlisted/registered workflow owner. This allows an attacker to: (1) consume DON node compute/resources by generating unauthorized trigger fan-out traffic to all DON members, and (2) potentially cause unauthorized workflow/job execution on nodes if the downstream node-side handler also lacks equivalent allowlist enforcement for this legacy code path, since the gateway is the first (and here, only) checkpoint before the message reaches capability nodes.

### Likelihood Explanation
The gateway HTTP server accepts arbitrary requests from the internet-facing endpoint [5](#0-4) , and the only precondition to reach the vulnerable forwarding code is producing a validly self-signed message with a non-zero, non-stale timestamp and the correct method name — both trivially satisfiable by any caller, since signature validity only proves internal consistency of sender/signature, not caller authorization.

### Recommendation
Add an allowlist/authorization check (equivalent to the `Authorizer.AuthorizeRequest` pattern already used by the vault handler) in `HandleLegacyUserMessage` before forwarding the request to DON nodes, replacing the `// TODO: apply allowlist and rate-limiting here` comment with an actual enforcement call, and reject/return an error response for unauthorized senders.

### Proof of Concept
1. An attacker crafts a JSON-RPC legacy request body with `Method: "web_api_trigger"`, a valid `Timestamp`, and signs it with a freshly generated (unregistered) ECDSA key, producing a self-consistent `Sender`/`Signature` pair that passes `msg.Validate()`.
2. The attacker POSTs this to the gateway's public HTTP endpoint (`s.handleRequest` → `gateway.ProcessRequest`).
3. `gateway.ProcessRequest` resolves the handler by `DonID` and calls `HandleLegacyUserMessage`.
4. Inside `HandleLegacyUserMessage`, the payload decodes successfully, the timestamp check passes, and execution reaches the `// TODO: apply allowlist and rate-limiting here` line with no rejection, then loops over `h.donConfig.Members` calling `don.SendToNode` for each — sending the unauthorized trigger to every DON node member [6](#0-5) .

### Citations

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

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-62)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L236-244)
```go
	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}

	requestProcessor, err := vaultcap.NewGatewayVaultRequestProcessor(requestValidator, authorizer, false, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```

**File:** core/services/gateway/network/httpserver.go (L195-245)
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
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
	if err != nil {
		s.lggr.Error("error when writing response", err)
	}
}
```
