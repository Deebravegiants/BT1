Audit Report

## Title
Global, unauthenticated request-ID namespace in the ConfidentialRelay gateway handler lets any caller squat another user's in-flight request ID and deny their relay request - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

## Summary
`HandleJSONRPCUserMessage` in the ConfidentialRelay gateway handler performs only trivial length/emptiness validation on `req.ID` before calling `newActiveRequest`, which inserts the raw, caller-supplied `req.ID` directly into a shared `activeRequests` map with no authentication, authorization, or owner-scoping step. This contrasts with the sibling Vault handler, which authorizes the request via `requestProcessor.ProcessRequest` and prefixes the ID with the authorized owner before ever touching its own map. Any client able to reach the gateway's public HTTP endpoint can pre-register a colliding ID, causing a legitimate concurrent request with the same ID to fail with `"request ID already exists"`.

## Finding Description
The gateway's user-facing HTTP endpoint (`gateway.ProcessRequest` in `core/services/gateway/gateway.go`, invoked from `httpserver.go`'s `handleRequest`) does not enforce authentication centrally — it only forwards an optional bearer token as `auth`/`jwtToken` to the per-method handler, leaving each handler responsible for its own authorization. [1](#0-0) [2](#0-1) 

For the ConfidentialRelay handler, `HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 characters before calling `newActiveRequest` and fanning the request out to DON nodes — there is no call to any `Authorizer`, allowlist, or JWT check. [3](#0-2) 

`newActiveRequest` keys the shared `activeRequests` map directly by the raw, attacker-controlled `req.ID`, rejecting the insert if the key is already occupied: [4](#0-3) 

By contrast, the Vault handler performs an `AuthorizeRequest`/`ProcessRequest` authorization step, which prefixes the request ID with the authorized owner (`owner + RequestIDSeparator + req.ID`) before it ever reaches the handler's own `activeRequests` map, effectively namespacing the ID per authenticated owner: [5](#0-4) [6](#0-5) 

The project's own regression test confirms the collision behavior for ConfidentialRelay: a second `HandleJSONRPCUserMessage` call with the same ID fails once the first is registered, with the error text `"request ID already exists"`. [7](#0-6) 

Note, however, that the actual security-sensitive checks for this handler's traffic (TEE attestation validation and Workflow-DON quorum authorization) live downstream, on the node side, in `core/capabilities/confidentialrelay/handler.go`'s `handleSecretsGet`/`verifyWorkflowAuthorization`, which are invoked only after the gateway relays the message via `HandleGatewayMessage`. [8](#0-7)  These checks verify content authorization but do not protect the gateway's `activeRequests` keyspace itself — the ID-collision rejection happens purely inside the gateway handler, before any node-side attestation/authorization logic runs.

## Impact Explanation
An unauthenticated caller who can predict or observe a legitimate request's `req.ID` before it is submitted can pre-register that ID via the gateway's ConfidentialRelay methods (`MethodSecretsGet`, `MethodCapabilityExec`), causing the legitimate submission to fail immediately with `"request ID already exists"`. This is a targeted denial-of-service against a specific in-flight secrets-fetch or capability-execution request, not a broader compromise of confidentiality/integrity — no secret material, keys, or authorization state are exposed or bypassed, and the downstream attestation/Workflow-DON-quorum checks remain intact and would still reject any attacker-forged payload. The severity is bounded: this is a first-come-first-served collision on a bookkeeping key, not an authentication or authorization bypass, and does not itself allow impersonation, fund movement, or key/secret exfiltration.

## Likelihood Explanation
Exploitability hinges entirely on whether an attacker can learn or predict the victim's exact `req.ID` before submitting it — this could not be conclusively verified: the tool budget was exhausted before locating the code that generates `req.ID` on the caller side (the confidential-compute enclave / workflow engine) to determine its entropy/format (e.g., random UUID vs. a predictable/derivable value tied to execution ID). If request IDs are high-entropy random values generated inside the TEE, the collision is not practically guessable, sharply limiting real-world likelihood despite the code-level absence of authorization. If IDs are derived deterministically from public execution/workflow identifiers, the attack is straightforward. This uncertainty is material to the claim's practical severity, though the underlying code defect (no auth before `activeRequests` insertion, no owner-scoping) is confirmed and reproducible via the existing unit test.

## Recommendation
Scope the `activeRequests` key (and any future related caches) in the ConfidentialRelay handler to include an authenticated/verifiable component of the request's identity — e.g., derive the key from a hash of `(WorkflowID, ExecutionID, req.ID)` extracted from `labels`, or require the downstream attestation/quorum data to be verified (or at least structurally validated) before the ID is inserted into the shared namespace, mirroring the Vault handler's owner-prefixing pattern. At minimum, ensure that a colliding ID from an unrelated workflow/execution cannot silently block a legitimate one.

## Proof of Concept
1. Attacker sends a JSON-RPC request to the gateway's ConfidentialRelay endpoint with `Method = MethodCapabilityExec` (or `MethodSecretsGet`) and `ID = X`, where `X` is a value the attacker believes a victim will soon use.
2. `HandleJSONRPCUserMessage` performs no authorization check, calls `newActiveRequest`, which succeeds and inserts key `X` into `activeRequests`. [3](#0-2) 
3. The legitimate caller's subsequent request with the same `ID = X` reaches `newActiveRequest`, finds the key occupied, and is rejected with `"request ID already exists: X"`.
4. Reproduced directly by the existing test `TestConfidentialRelayHandler_DuplicateRequestID`. [7](#0-6) 

Further validation (not completed due to tool-call limits) should confirm the exact generation mechanism for `req.ID` on the confidential-relay client side (in `core/capabilities/confidentialrelay/handler.go` or the workflow engine that invokes it) to establish whether IDs are attacker-predictable in practice, which determines whether this is a purely theoretical bookkeeping flaw or a practically exploitable DoS.

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

**File:** core/services/gateway/gateway.go (L267-276)
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-441)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}

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
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L362-404)
```go
	t.Run("forwards create secrets to DON when ciphertext matches identifier owner", func(t *testing.T) {
		_, pk, _, err := tdh2easy.GenerateKeys(1, 3)
		require.NoError(t, err)
		encryptedSecret, err := vaultutils.EncryptSecretWithWorkflowOwner("test_secret", pk, ethcommon.HexToAddress(owner))
		require.NoError(t, err)

		h, callback, don, _ := setupHandlerWithLimitsFactory(t, limits.Factory{Settings: cresettings.DefaultGetter})
		cacheVaultPublicKeyForTest(t, h.(*handler), pk)

		reqData := &vaultcommon.CreateSecretsRequest{
			EncryptedSecrets: []*vaultcommon.EncryptedSecret{
				{
					Id: &vaultcommon.SecretIdentifier{
						Key:   "test_id",
						Owner: owner,
					},
					EncryptedValue: encryptedSecret,
				},
			},
		}
		reqDataBytes, err := json.Marshal(reqData)
		require.NoError(t, err)

		req := jsonrpc.Request[json.RawMessage]{
			ID:     "matching-label-secret",
			Method: vaulttypes.MethodSecretsCreate,
			Params: (*json.RawMessage)(&reqDataBytes),
		}

		var forwarded jsonrpc.Request[json.RawMessage]
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			forwarded = *args.Get(2).(*jsonrpc.Request[json.RawMessage])
		}).Return(nil).Once()

		err = h.HandleJSONRPCUserMessage(t.Context(), req, callback)
		require.NoError(t, err)

		don.AssertExpectations(t)
		require.NotNil(t, forwarded.Params)
		var forwardedCreateRequest vaultcommon.CreateSecretsRequest
		require.NoError(t, json.Unmarshal(*forwarded.Params, &forwardedCreateRequest))
		require.Equal(t, owner+vaulttypes.RequestIDSeparator+req.ID, forwardedCreateRequest.RequestId)
	})
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

**File:** core/capabilities/confidentialrelay/handler.go (L357-381)
```go
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
