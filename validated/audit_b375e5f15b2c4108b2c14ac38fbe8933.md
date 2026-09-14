This is exactly the bug class in the report: an on-chain "allowlist proof" (analog of the merkle proof) is consumed as soon as authorization succeeds, before the rest of the request pipeline (owner-binding checks, per-request structural validation, ciphertext-size limits, ID stamping) has run. If any of those *subsequent* steps fail, the client is left permanently unable to retry — because the digest is now recorded as "already seen" by the replay guard — exactly mirroring the VETH bug where the merkle proof is marked used even though the conversion itself failed.

### Title
Vault gateway consumes an on-chain allowlist proof before request-body validation succeeds, permanently locking the workflow owner out of retrying - (File: `core/capabilities/vault/authorizer.go`)

### Summary
`authorizer.AuthorizeRequest` records the request digest in the replay guard immediately after the on-chain allowlist (or JWT) check succeeds, but *before* the owner-binding check and the caller's downstream structural/size validation run. Because on-chain allowlisting (via `AllowlistRequest`) is a one-time, single-use action just like the VETH merkle proof, any failure that occurs after this point (owner mismatch, malformed params, oversized ciphertext, stamping failure) leaves the workflow owner with a burned allowlist entry and no way to resubmit the same request.

### Finding Description
`GatewayVaultRequestProcessor.authorizeAndStamp` calls `p.authorizer.AuthorizeRequest` first [1](#0-0) . Inside that call, `authorizer.AuthorizeRequest` performs the digest lookup, then immediately calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())`, which permanently marks the digest as "seen" — and only afterward does it validate that the payload owner matches the authorized workflow owner: [2](#0-1) .

For `AllowListBasedAuth`, the underlying authorization itself is backed by a single on-chain allowlist entry created via `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)`, keyed by the exact digest of the JSON-RPC request — this is functionally the same one-shot "proof" mechanism as the VETH merkle proof: it authorizes exactly one digest exactly once. [3](#0-2) [4](#0-3) 

Once `CheckAndRecord` succeeds, `ErrRequestAlreadySeen` will be returned for the *same digest* on every subsequent attempt until its expiry: [5](#0-4) .

But after replay-guard recording, the pipeline still performs owner-binding validation (`validateSecretOwnersMatchAuthorized`) inside the same `AuthorizeRequest` call, and, back in `GatewayVaultRequestProcessor`, further ID-stamping (`stamp(...)`) and ciphertext-size validation (`ValidateCiphertextSizes`) after `authorizeAndStamp` returns: [6](#0-5) . If any of these later checks fail — e.g., the workflow owner encoded a secret with a mismatched `Id.Owner`, or a ciphertext exceeds the size limit — the whole `ProcessRequest` call returns an error, but the digest has already been irreversibly consumed by the replay guard. Since the on-chain allowlist entry for that exact digest was also a single, already-used registration, the workflow owner cannot re-allowlist the *same* request digest again (allowlisting is bound to the specific digest of the original malformed request), and must go through an entirely new client-side flow to regenerate a request/digest and re-allowlist on-chain, exactly the "stuck, cannot retry" failure mode from the report.

Note: this "one digest = one shot" replay-guard behavior is used identically by the JWT-based auth path and is asserted directly in the gateway handler tests, which show the request being effectively "consumed" as soon as `AuthorizeRequest` records it, independent of whether the eventual handler logic on the node succeeds — a duplicate submission is rejected with "request was already authorized previously": [7](#0-6) .

### Impact Explanation
An unprivileged workflow owner (client of the Vault gateway) can lose the ability to execute a legitimately-intended, already-on-chain-allowlisted vault operation (secret create/update/delete/list) if any validation step downstream of authorization-but-still-within-the-same-request-cycle fails — e.g. a namespace-default mutation causing an owner mismatch, or a ciphertext exceeding size limits set independently of the on-chain allowlist. Because the on-chain allowlist entry is scoped to a specific request digest and marked used/consumed by the in-memory replay guard for the node/gateway lifetime (until expiry), the user is stuck: they cannot resend the identical request (replay guard rejects it), and the underlying allowlist entry cannot be "reused" for a corrected payload since it's digest-bound to the original (flawed) request bytes. This matches the report's core harm: loss of a one-time authorization right, with the impact borne by the individual user rather than the protocol.

### Likelihood Explanation
Moderate. It requires the client to submit a request whose digest is on-chain-allowlisted but where the actual param content fails a validation check performed strictly after replay-guard recording (owner-match, ciphertext size, or ID-stamping/marshal failure). This is plausible for manual/non-SDK callers or any client whose local request construction diverges from what was registered on-chain (similar to the "inattentive user" scenario in the original report), and is entirely user-triggered — no malicious peer or operator involvement is required, keeping it within the unprivileged-actor analog scope.

### Recommendation
Reorder the pipeline so that all payload-dependent structural/ownership/size validations that can be performed on the as-received (or digest-preserving) request run *before* `RequestReplayGuard.CheckAndRecord` is invoked, so replay-guard consumption only occurs once the request is known to be fully processable. Alternatively, decouple on-chain allowlist consumption from a single "digest is now permanently seen" event by allowing the replay guard to be rolled back (or the record deferred) if any subsequent stamping/validation step in the same `ProcessRequest` call fails before the request reaches the node's secrets service.

### Proof of Concept
1. Workflow owner constructs a `MethodSecretsCreate` JSON-RPC request whose `EncryptedSecrets[i].Id.Owner` does not exactly match their own normalized owner address (e.g. differing case/whitespace bug in client tooling), and computes its digest via `req.Digest()`.
2. Owner calls `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` on-chain, allowlisting exactly this digest — [8](#0-7) .
3. Owner submits the request to the gateway. `allowListBasedAuth.AuthorizeRequest` finds the allowlisted digest and returns success [9](#0-8) .
4. `authorizer.AuthorizeRequest` immediately calls `replayGuard.CheckAndRecord(digest, expiresAt)`, marking the digest as consumed [10](#0-9) .
5. `validateSecretOwnersMatchAuthorized` then runs and fails due to the owner mismatch, returning an error from `AuthorizeRequest` [11](#0-10) .
6. `ProcessRequest`/`authorizeAndStamp` propagates the failure to the caller as `"request not authorized: ..."` [12](#0-11) .
7. Owner fixes the payload owner field and resubmits the identical (or corrected) request with the same digest/allowlist entry. The `CheckAndRecord` call now returns `ErrRequestAlreadySeen` [13](#0-12) , so the request is rejected regardless of the fix, and the owner cannot re-allowlist the exact same digest (their only recourse is constructing an entirely new request/digest and re-paying gas for a fresh on-chain `AllowlistRequest` call) — the direct analog of the VETH user being stuck with a burned merkle proof and no VADER.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L137-149)
```go
	authorized, err := p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		createReq.RequestId = prefixedRequestID
		vaultutils.ApplyEncryptedSecretNamespaceDefaults(createReq.EncryptedSecrets)
		return marshalVaultParams(req, &createReq)
	})
	if err != nil {
		return nil, err
	}

	if err := p.validator.ValidateCiphertextSizes(ctx, authorized.AuthResult.AuthorizedOwner(), createReq.EncryptedSecrets); err != nil {
		return nil, p.validationError(req, err)
	}
	return authorized, nil
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-276)
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
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-77)
```go
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

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
}
```

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L881-903)
```go
func allowlistRequest(
	t *testing.T,
	th *testutils.EVMBackendTH,
	wfRegC *workflow_registry_wrapper_v2.WorkflowRegistry,
	input allowlistRequestParams,
) {
	t.Helper()
	totalAllowlistedRequestsBefore, err := wfRegC.TotalAllowlistedRequests(&bind.CallOpts{
		From: th.ContractsOwner.From,
	})
	require.NoError(t, err, "failed to get total allowlisted requests")

	requestDigest, err := input.Request.Digest()
	require.NoError(t, err)
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err)

	_, err = wfRegC.AllowlistRequest(
		th.ContractsOwner,
		[32]byte(requestDigestBytes),
		uint32(input.ExpiryTimestamp.Unix()), //nolint:gosec // safe conversion
	)
	require.NoError(t, err, "failed to register allowlisted request")
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L707-751)
```go
	t.Run("unhappy path - duplicate requestId", func(t *testing.T) {
		h, callback, don, _ := setupHandler(t)
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

		requestID := "1"
		reqData := &vaultcommon.ListSecretIdentifiersRequest{
			RequestId: requestID,
			Owner:     owner,
		}
		reqDataBytes, err := json.Marshal(reqData)
		require.NoError(t, err)

		validJSONRequest := jsonrpc.Request[json.RawMessage]{
			ID:     requestID,
			Method: vaulttypes.MethodSecretsList,
			Params: (*json.RawMessage)(&reqDataBytes),
		}

		responseData := &vaultcommon.ListSecretIdentifiersResponse{
			Identifiers: []*vaultcommon.SecretIdentifier{
				{
					Key:       "foo",
					Owner:     owner,
					Namespace: "default",
				},
			},
		}
		resultBytes, err := json.Marshal(responseData)
		require.NoError(t, err)
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
		response := jsonrpc.Response[json.RawMessage]{
			ID:     expectedRequestID,
			Result: (*json.RawMessage)(&resultBytes),
			Method: vaulttypes.MethodSecretsList,
		}
		resultBytes, err = json.Marshal(responseData)
		require.NoError(t, err)

		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.NoError(t, err)

		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")

```
