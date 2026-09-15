### Title
Vault gateway replay-guard permanently blocks legitimate request retries after a downstream failure - ([File: core/capabilities/vault/request_replay_guard.go])

### Summary
The Vault capability's replay-protection guard marks a request's digest as "seen" the moment JWT authorization succeeds, before the request has actually been executed by the Vault DON. If any step *after* authorization fails (fan-out to DON nodes fails, write-methods are gated off, node quorum can't be reached, etc.), the user callback returns an error, but the replay-guard entry is never rolled back. Because the JWT's `request_digest` claim is bound 1:1 to the exact request content, any retry of the identical operation is rejected with `ErrRequestAlreadySeen` until the guard entry naturally expires — even though the original operation never completed. This mirrors the SteadeFi bug class: a two-step flow where the first step's side effect (marking the digest consumed) is not rolled back when the second step (actually performing the operation) fails, leaving that specific operation permanently stuck for the client.

### Finding Description
`RequestReplayGuard.CheckAndRecord` records a digest with an expiry and returns `ErrRequestAlreadySeen` on any subsequent call with the same digest before that expiry: [1](#0-0) 

`jwtBasedAuth.AuthorizeRequest` computes the request digest, validates it against the JWT's claimed digest, and returns a successful `AuthResult` — this is the point where the replay guard is expected to consume the digest as "seen" (confirmed by the accompanying test showing a second identical `AuthorizeRequest` call is rejected as already-seen right after the first succeeds): [2](#0-1) [3](#0-2) 

Critically, authorization (and therefore replay-guard consumption) happens *before* the request is actually forwarded to and executed by the Vault DON. In the gateway handler, `ProcessRequest` (which performs authorization) runs, then a new `activeRequest` is registered, and only afterward is the request dispatched to `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`, which can still fail for independent reasons (write-methods gate disabled, or all DON members unreachable): [4](#0-3) [5](#0-4) [6](#0-5) 

None of these post-authorization failure paths (`sendResponse` calls) touch or clear the replay guard's `seen` map — only `RequestReplayGuard.ClearExpired`/time-based expiry removes an entry: [7](#0-6) 

The result: a legitimate, unprivileged workflow client whose vault write/read request fails for any transient, gateway-side reason *after* authorization succeeds (e.g. a brief DON connectivity blip, or the `writeMethodsEnabled` gate flipping momentarily) cannot successfully retry the exact same operation — every retry with a JWT re-asserting the same `request_digest` is rejected with `ErrRequestAlreadySeen`, even though the vault never actually processed it. The existing test suite explicitly documents and tolerates this exact behavior as an expected but disruptive side effect under load: [8](#0-7) 

### Impact Explanation
This is a request-level denial-of-service / stuck-state bug reachable by any unprivileged, properly-authorized client (no attacker privilege escalation needed to trigger it — ordinary operational hiccups on the gateway or DON side suffice). A client's legitimate `vault.secrets.create/update/delete` operation can be permanently un-retryable (until the JWT/digest expiry window elapses, bounded by `jwtValidationLeeway` plus JWT `exp`) after a transient gateway-side failure that has nothing to do with the client's request validity. Because the digest is derived from the request content and stamped into the JWT by an external auth service, the client generally cannot simply "change" the digest to retry the same logical operation — they are stuck waiting for expiry, exactly analogous to the reported vault being stuck waiting for an external state change it cannot control.

### Likelihood Explanation
Likelihood is moderate to high in the gateway's normal operating envelope: the flow requires only (a) authorization succeeding and (b) any single downstream failure — a fan-out failure to all DON members, or the `writeMethodsEnabled` gate becoming false mid-flight, or a quorum-unreachable node error — all of which are plausible without any malicious actor, purely from ordinary network flakiness or operational toggles. It does not require privileged access, node compromise, or peer misbehavior; it's triggerable from a normal client request path.

### Recommendation
Do not let `AuthorizeRequest`/`CheckAndRecord` permanently consume the replay-guard slot until the operation has actually reached a terminal success outcome on the Vault DON. Options: (1) move the replay-guard `CheckAndRecord` call to after successful DON quorum/response (i.e., record-on-success rather than record-on-authorize), or (2) on any downstream failure path in `handler.go` (`sendResponse` with a non-success error code originating from a gateway/DON-side failure rather than a user error), explicitly remove/unwind the corresponding replay-guard entry so the same digest can be retried. Distinguish "user error" (bad params, unauthorized) — which should keep the replay protection — from "gateway/infrastructure error" (fan-out failure, gate disabled, timeout, quorum unreachable) — which should not consume the replay slot.

### Proof of Concept
1. Client obtains a valid Auth0 JWT scoped with `authorization_details: [{type: "request_digest", value: D}]` for a specific `vault.secrets.create` request body whose digest is `D`.
2. Client sends the request to the gateway; `HandleJSONRPCUserMessage` → `ProcessRequest` → `jwtBasedAuth.AuthorizeRequest` succeeds and (per the guard's semantics) marks digest `D` as seen.
3. `fanOutToVaultNodes` subsequently fails because all DON members are temporarily unreachable (or `writeMethodsEnabled.AllowErr` returns not-allowed at that instant), and the handler returns a `FatalError`/`UnsupportedMethodError` to the client — the create never actually happens.
4. Client retries with the identical request body and a freshly issued JWT re-asserting the same `request_digest` `D` (the digest is a function of the request content, so any JWT authorizing this exact retried content carries the same digest).
5. `AuthorizeRequest` → `CheckAndRecord(D, ...)` returns `ErrRequestAlreadySeen`, and the retry is rejected — despite the original operation never completing — until the guard entry naturally expires.

### Citations

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

**File:** core/capabilities/vault/request_replay_guard.go (L49-63)
```go
// ClearExpired removes all entries whose expiry timestamp is in the past.
// Call this to eagerly reclaim memory even when CheckAndRecord is not invoked.
func (g *RequestReplayGuard) ClearExpired() {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.clearExpiredLocked()
}

func (g *RequestReplayGuard) clearExpiredLocked() {
	now := g.nowFunc().UTC().Unix()
	for digest, expiry := range g.seen {
		if now > expiry {
			delete(g.seen, digest)
		}
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L208-232)
```go
	requestDigest, err := req.Digest()
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to compute request digest", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "error", err)
		return nil, fmt.Errorf("failed to compute request digest: %w", err)
	}

	if !strings.EqualFold(requestDigest, claims.RequestDigest) {
		v.lggr.Debugw("JWTBasedAuth request digest mismatch", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "computedDigest", requestDigest, "claimedDigest", claims.RequestDigest)
		return nil, fmt.Errorf("request digest mismatch: computed=%s claimed=%s", requestDigest, claims.RequestDigest)
	}

	derivedWorkflowOwner, err := DeriveJWTAuthorizedVaultWorkflowOwner(claims.OrgID, claims.TenantID, claims.WorkflowOwner)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to derive authorized workflow owner", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}

	authExpiresAt := claims.ExpiresAt.UTC().Add(jwtValidationLeeway).Unix()
	v.lggr.Debugw("JWTBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", derivedWorkflowOwner, "digest", requestDigest, "expiresAt", authExpiresAt)
	return &AuthResult{
		orgID:         claims.OrgID,
		workflowOwner: derivedWorkflowOwner,
		digest:        requestDigest,
		expiresAt:     authExpiresAt,
	}, nil
```

**File:** core/capabilities/vault/jwt_based_auth_test.go (L296-309)
```go
	req, err = jsonrpc.DecodeRequest[json.RawMessage](rawRequest, token)
	require.NoError(t, err)

	a := NewAuthorizer(nil, v, logger.TestLogger(t))

	authResult, err := a.AuthorizeRequest(t.Context(), req)
	require.NoError(t, err)
	require.Equal(t, digest, authResult.Digest())
	require.Equal(t, tokenExp.UTC().Add(time.Minute).Unix(), authResult.ExpiresAt())

	authResult, err = a.AuthorizeRequest(t.Context(), req)
	require.Nil(t, authResult)
	require.ErrorIs(t, err, ErrRequestAlreadySeen)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-455)
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
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}

	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return h.handleSecretsCreate(ctx, ar)
	case vaulttypes.MethodSecretsUpdate:
		return h.handleSecretsUpdate(ctx, ar)
	case vaulttypes.MethodSecretsDelete:
		return h.handleSecretsDelete(ctx, ar)
	case vaulttypes.MethodSecretsList:
		return h.handleSecretsList(ctx, ar)
	default:
		return h.sendResponse(ctx, ar, h.errorResponse(req, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method), nil))
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L613-626)
```go
func (h *handler) handleSecretsCreate(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L736-748)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test.go (L638-669)
```go
// sendConcurrentVaultCreate sends an already-allowlisted create request to the gateway and tolerates
// the replay-guard outcome. Under burst load, the gateway can time out (503 "Request timed out") while
// DON still processes the create; the test's HTTP retry then re-sends the same request digest, which
// vault's replay guard rejects with "request was already authorized previously". That error proves the
// original request was accepted and processed, so we treat it as success — there is no later response
// payload to validate when this path fires.
func sendConcurrentVaultCreate(t *testing.T, gwURL, requestID string, jsonRequest jsonrpc.Request[json.RawMessage], authorizedOwner, expectedResponseOwner string, namespaces []string) {
	t.Helper()

	authToken := jsonRequest.Auth
	stripped := outboundRequestWithoutAuth(jsonRequest)
	requestBody, err := json.Marshal(stripped)
	require.NoError(t, err, "failed to marshal vault request")
	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}

	statusCode, body := sendVaultRequestToGatewayWithHeaders(t, gwURL, requestBody, headers)

	// Under burst load the gateway can return 503 "Request timed out" when it gives up relaying the
	// response, even though the DON has already processed the request. Tolerate that here — the goal
	// of this subtest is to drive concurrent load for the docker-log batching assertions below, not
	// to verify per-request response payloads.
	if statusCode == http.StatusServiceUnavailable && bytes.Contains(body, []byte("Request timed out")) {
		framework.L.Info().Str("requestID", requestID).Msg("vault create gateway-to-DON timeout; treating as success for batching load test")
		return
	}
	// Replay guard can arrive on a non-200 HTTP status after a retried gateway call; check before StatusOK.
	if bytes.Contains(body, []byte("request was already authorized previously")) {
		framework.L.Info().Str("requestID", requestID).Msg("vault create returned replay-guard error after retry; DON processed the original request — treating as success")
		return
```
