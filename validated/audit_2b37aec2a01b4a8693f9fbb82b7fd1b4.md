Based on the investigation, I have enough context to make a determination.

The code confirms the claim precisely: `newActiveRequest` in `core/services/gateway/handlers/confidentialrelay/handler.go` checks/stores `activeRequest` keyed purely by the caller-supplied `req.ID` in a single map shared across all callers, with no per-caller/tenant namespacing, unlike the vault handler's `authorizeAndStamp` pattern which prefixes the ID with `authorizedOwner`.Based on the investigation, the claim is confirmed by the code.

Audit Report

## Title
Global request-ID collision in `ConfidentialRelayHandler` allows unprivileged callers to DoS other users' gateway requests - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

## Summary
The confidential relay gateway handler's `newActiveRequest` stores in-flight requests in a single, handler-wide `activeRequests` map keyed only by the caller-supplied `req.ID`, with no per-caller identity binding and no authentication/authorization step preceding the collision check. This is confirmed at [1](#0-0)  and [2](#0-1) . Any caller reaching the gateway's HTTP endpoint for this handler can pre-register an ID and cause a legitimate request using the same ID to fail with `"request ID already exists"`, exactly as demonstrated in `TestConfidentialRelayHandler_DuplicateRequestID` at [3](#0-2) .

## Finding Description
`HandleJSONRPCUserMessage` performs only length/emptiness validation on `req.ID` before calling `newActiveRequest`, with no authorization or owner-derivation step: [1](#0-0) . `newActiveRequest` then checks/records the request purely by the raw `req.ID` string in a map shared across all callers of the DON: [2](#0-1) .

By contrast, the vault gateway handler (`core/capabilities/vault/gateway_vault_request_processor.go`) explicitly authorizes the request and rewrites `req.ID` to `authorizedOwner + RequestIDSeparator + originalRequestID` before it is ever used as a map key, so ID collisions can only occur within one authorized owner's own namespace: [4](#0-3) . The confidential relay handler has no analogous authorization/namespacing step at the gateway layer — it is a "dumb relay" by design (per its own comments), fanning out to DON nodes without making a trust decision itself: [5](#0-4) .

The HTTP entry point (`network/httpserver.go`'s `handleRequest`) forwards raw request bytes plus an optional JWT bearer token to `gateway.ProcessRequest`, which decodes the JSON-RPC envelope and dispatches directly to `HandleJSONRPCUserMessage` without any handler-agnostic authentication gate: [6](#0-5)  and [7](#0-6) . Whether authentication is performed is entirely up to the individual handler — the vault handler does this via `requestProcessor.ProcessRequest`/`AuthorizeRequest`, while the confidential relay handler does no such check at all. This confirms the root cause: the broken assumption that `req.ID` collisions are scoped per-caller is never enforced for this handler.

Real request identities that flow through this path (enclave `Owner`/`WorkflowID`/`ExecutionID`) do exist and are extracted into `requestLabels` purely for logging, but never used to scope the `activeRequests` map key: [8](#0-7) .

## Impact Explanation
The impact is a denial of service against a specific in-flight relay request: any caller reaching this handler's gateway endpoint can pre-register a target `req.ID`, causing the legitimate caller's genuine request with that ID to fail immediately with `"request ID already exists"` rather than being routed to the DON. This matches the reported bug class's DoS half. There is no evidence this leads to fund theft or cross-user data leakage — the map only gates admission, and node responses (`addResponseForNode`) are separately keyed by node address, not by caller.

## Likelihood Explanation
Exploitability hinges on whether `req.ID` values are practically guessable/observable by an attacker who is not the legitimate caller. The code itself imposes no entropy requirement on `req.ID` — it is fully attacker/caller supplied, checked only for non-emptiness and a 200-character length cap. No node/end-user identity or session context is required to reach `HandleJSONRPCUserMessage`, since the confidential relay handler performs no authentication at all (unlike the vault handler, which does JWT/authorizer-based authorization before touching its own request map). This makes the front-running primitive genuinely present in the code, independent of how the legitimate enclave/caller happens to generate its IDs (this repository's index does not show the ID-generation logic on the enclave/legitimate-caller side, so the actual entropy of `req.ID` in production could not be confirmed from available code, but the vulnerability in the gateway's collision-check code is intrinsic and does not depend on that).

## Recommendation
Namespace the `activeRequests` key by an authenticated/authorized caller identity, mirroring the vault gateway's owner-prefixed ID scheme (`authorizeAndStamp`), before performing the existence check in `newActiveRequest`, so ID collisions can only occur within a single caller's own request stream rather than globally across all gateway clients reaching this DON's confidential relay handler.

## Proof of Concept
1. Send a first JSON-RPC request to the gateway's confidential-relay-backed HTTP endpoint with `ID = "req-123"`, `Method = confidentialrelaytypes.MethodCapabilityExec` (or `MethodSecretsGet`), and arbitrary/attacker-controlled params.
2. `HandleJSONRPCUserMessage` → `newActiveRequest` succeeds, inserting `"req-123"` into `h.activeRequests` (per [2](#0-1) ).
3. Send a second, legitimate request reusing the same `ID = "req-123"` (as the real caller would, e.g., on retry or coincidentally colliding).
4. The second call returns `errors.New("request ID already exists: req-123")`, denying that request — directly reproduced by the existing unit test `TestConfidentialRelayHandler_DuplicateRequestID`: [3](#0-2) .

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L80-108)
```go
// requestLabels are the identifiers the gateway pulls out of a relay request's
// params purely for logging, so a gateway line can be correlated with the
// relay-DON's and the enclave's lines for the same workflow execution. The
// gateway stays a dumb relay: it does not otherwise interpret params.
type requestLabels struct {
	WorkflowID  string `json:"workflow_id"`
	ExecutionID string `json:"execution_id"`
}

// extractRequestLabels best-effort decodes the logging identifiers from a
// request's params. Both relay methods' params carry these fields. A decode
// failure leaves them empty and is only logged: these labels are for
// correlation, and the params themselves are validated by the relay nodes,
// not here, so a request whose params do not decode is still fanned out and
// rejected there. ProcessRequest has already parsed the envelope as valid
// JSON by this point, so a failure here means params is not an object or
// carries non-string identifiers — malformed input rather than a gateway bug,
// hence debug level to avoid handing a caller a log-spam lever.
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
	if err := json.Unmarshal(*req.Params, &labels); err != nil {
		h.lggr.Debugw("could not decode relay request params for logging labels",
			"method", req.Method, "requestID", req.ID, "err", err)
	}
	return labels
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L661-663)
```go
// forwardBundle sends a previously-built bundle to the enclave. The gateway makes
// no trust decision; the enclave verifies signatures and reaches quorum.
func (h *handler) forwardBundle(ctx context.Context, l logger.Logger, ar *activeRequest, summary *BundleSummary) error {
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-293)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
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

**File:** core/services/gateway/gateway.go (L267-279)
```go
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
