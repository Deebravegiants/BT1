Audit Report

## Title
Unauthenticated Request-ID Squatting Causes Denial-of-Service on In-Flight Confidential Relay Requests - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
The gateway's confidential-relay handler claims an attacker-controlled `req.ID` as the sole key for in-flight request tracking before performing any authentication or attestation check, allowing any client that can reach the gateway's HTTP endpoint to pre-empt a legitimate enclave request that later arrives with the same ID. This is confirmed by direct code inspection: `HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and under 200 characters, then immediately calls `newActiveRequest`, which rejects any request whose ID is already claimed with no ownership check whatsoever.

## Finding Description
`gateway.ProcessRequest` decodes the raw HTTP body and dispatches directly to the target handler's `HandleJSONRPCUserMessage` with no caller authentication performed at the gateway layer [1](#0-0) . The HTTP server itself performs no authentication beyond optionally forwarding a bearer token string to the handler layer, leaving per-handler authorization entirely up to each handler [2](#0-1) .

For the confidential relay handler specifically, `HandleJSONRPCUserMessage` checks only ID length/non-emptiness before calling `newActiveRequest`, which claims the raw `req.ID` in the global `activeRequests` map with no ownership or authentication check [3](#0-2) . If an entry already exists for that ID, the call is rejected with `"request ID already exists"`.

Real authentication (Nitro attestation validation and Workflow-DON-signature verification) only happens later, on the DON-node side, inside `handleSecretsGet`/`handleCapabilityExecute` — code that is downstream of, and never reached before, the gateway's ID-claim step [4](#0-3) . By the time attestation would fail an attacker's bogus request, the ID slot has already been squatted and the legitimate concurrent/later request with the same ID is already rejected by the gateway.

The existing unit test confirms the ID collision is enforced purely on string equality, independent of any identity check: [5](#0-4) .

This is a real architectural gap relative to sibling gateway handlers: the `vault` handler authorizes the request *before* calling `newActiveRequest` [6](#0-5) , and the vault request processor further prefixes the ID with the cryptographically authorized owner before it is used as a key [7](#0-6) . The confidential-relay handler has neither mitigation.

## Impact Explanation
Any client able to reach the gateway's HTTP endpoint (this is the same public endpoint the confidential-compute enclave itself uses to submit `MethodSecretsGet`/`MethodCapabilityExec` requests, per the system-test harness pointing enclaves at `gatewayUrl` [8](#0-7) ) can submit a request carrying any `req.ID` string with zero authentication. If that ID matches (or is raced against) an ID the legitimate enclave is about to use, the legitimate request is rejected outright with `"request ID already exists"`, denying that specific in-flight confidential-relay operation (a secrets fetch or capability execution) and forcing a retry. This is a griefing/DoS-class issue rather than a data-exfiltration or fund-movement issue: the attacker cannot read secrets or forge results (attestation/workflow-authorization checks downstream still gate that), but they can transparently block a targeted request from completing.

## Likelihood Explanation
Exploitation requires no credentials — only the ability to send an HTTP POST to the gateway's confidential-relay-routed endpoint with a guessed or raced `req.ID`. The severity is bounded by how predictable/guessable a target's `req.ID` is in practice (this was not established in the report and is unverified here), which limits real-world reliability of the attack to opportunistic racing rather than deterministic targeting.

## Recommendation
Scope `activeRequests` keys by an authenticated identity, mirroring the vault handler's pattern of authorizing/attesting before the ID is claimed, or prefixing the key with an authenticated owner/enclave identity so that ID collisions can only occur within a single authenticated caller's namespace.

## Proof of Concept
The existing test `TestConfidentialRelayHandler_DuplicateRequestID` in `core/services/gateway/handlers/confidentialrelay/handler_test.go` already demonstrates the core issue: two calls to `HandleJSONRPCUserMessage` with the same `req.ID` and different callbacks (i.e., no shared identity) — the second is rejected purely due to ID collision, confirming no ownership/authentication check occurs before the ID is claimed [5](#0-4) . An external HTTP PoC would be: POST a JSON-RPC request with `method: "confidentialrelay.secretsGet"` and an `id` equal to a value expected to be used by a legitimate enclave request, prior to that request's arrival, then observe the legitimate request fail with `"request ID already exists"`.

### Citations

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-430)
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

**File:** core/capabilities/confidentialrelay/handler.go (L332-381)
```go
func (h *Handler) handleSecretsGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, errors.New("missing params"))
	}
	var params confidentialrelaytypes.SecretsRequestParams
	if err := json.Unmarshal(*req.Params, &params); err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}

	// Every line below carries the gateway request id together with the
	// workflow/execution identity, so a log can be correlated with the
	// enclave's and the gateway's own lines for the same execution. The
	// gateway request id changes per retry; the execution identity does not.
	l := logger.With(h.lggr,
		"requestID", req.ID,
		"workflowID", params.WorkflowID,
		"executionID", params.ExecutionID,
	)

	att := params.Attestation
	params.Attestation = ""
	if err := h.verifyAttestationHash(ctx, att, params, confidentialrelaytypes.DomainSecretsGet); err != nil {
		l.Warnw("rejecting secrets request: attestation validation failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}
	// Fetch the local node once: it provides the WorkflowDON snapshot for both the
	// enclave-config check and the Workflow-DON authorization check below, plus the DON
	// metadata on the vault request. A registry read failure is node-side, so ErrInternal.
	localNode, err := h.capRegistry.LocalNode(ctx)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, fmt.Errorf("failed to get local node: %w", err))
	}
	// Verify the enclave's reported config matches the onchain DON state
	// before treating the attested request as trusted: the Nitro attestation
	// binds the request hash, but a malicious host can produce a
	// genuinely-attested request over a forged enclave config unless we
	// compare the config value against the DON reference.
	if err = h.verifyEnclaveConfigMatchesDON(localNode, params.EnclaveConfig); err != nil {
		l.Warnw("rejecting secrets request: enclave config does not match DON", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}

	// Beyond attestation, verify the Workflow DON authorized this request: the enclave
	// forwards the Workflow-DON-signed compute requests (a 2*F+1 quorum), whose PublicData
	// names the authorized owner. A TEE breach passes attestation but cannot forge a Workflow
	// DON quorum over a different owner (PRIV-433).
	if err = h.verifyWorkflowAuthorization(localNode.WorkflowDON, params); err != nil {
		l.Warnw("rejecting secrets request: workflow DON authorization failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}
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

**File:** core/services/gateway/handlers/vault/handler.go (L426-441)
```go
	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-286)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}
```

**File:** system-tests/tests/smoke/cre/confidential_workflows_test.go (L107-112)
```go
		t.Setenv("ENCLAVE_SETTINGS", fmt.Sprintf(
			`{"storageKey":%q,"storageServiceUrl":%q,"storageServiceTls":false,"gatewayUrl":%q}`,
			confidentialStorageKeyHex,
			storageAddr,
			fmt.Sprintf("http://%s:%d", enclaveHost, confidentialGatewayProxyPort),
		))
```
