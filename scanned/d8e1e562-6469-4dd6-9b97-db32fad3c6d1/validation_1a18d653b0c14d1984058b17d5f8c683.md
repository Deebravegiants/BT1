### Title
Replay guard permanently marks a Vault write request digest as "seen" before the write is authorized/stamped or actually committed by the DON, causing legitimate retries to be irrecoverably rejected - (File: core/capabilities/vault/authorizer.go)

### Summary
`FootiumPrizeDistributor` increases `totalERC20Claimed` before confirming the ERC20 transfer succeeded, so a failed-but-unreverted transfer leaves the claim permanently "used up" with no way to retry. The Chainlink Vault gateway pipeline has the same root-cause pattern: `RequestReplayGuard.CheckAndRecord` marks a request digest as consumed *before* the pipeline steps that determine whether the request will actually be honored (owner-binding validation, ID-stamping, and ultimately DON-side OCR processing/state transition) have completed successfully.

### Finding Description
`authorizer.AuthorizeRequest` calls the replay guard immediately after obtaining an `authResult`, and only *afterwards* performs the owner-binding check: [1](#0-0) 

```
authResult, err := a.authorizeRequest(ctx, req)
...
if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
    ...
    return nil, err
}
if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
    ...
    return nil, ownerErr   // digest already recorded as "seen" above!
}
```

`CheckAndRecord` is a pure "first writer wins" map insert keyed by digest, with no rollback path: [2](#0-1) 

Once inserted, the digest can never be reused, even though the request never became `AuthorizedGatewayVaultRequest` and never reached the DON: [3](#0-2) 

The same "record success, then possibly fail" pattern repeats one layer up in `GatewayVaultRequestProcessor.authorizeAndStamp`: `p.authorizer.AuthorizeRequest` (which internally calls `CheckAndRecord`) runs first, and only afterwards is `stamp(prefixedRequestID)` invoked, which can itself fail (e.g. `marshalVaultParams` errors): [4](#0-3) 

If `stamp` fails, `authorizeAndStamp` returns an error and the caller never dispatches the request to the DON, yet the digest is already permanently burned in the in-process replay guard.

The comments in the codebase itself acknowledge that "successful" replay-guard rejection is used as a proxy for "the DON already processed the request", which is an assumption, not a guarantee: [5](#0-4) 

```
// ... the gateway can time out (503 "Request timed out") while
// DON still processes the create; the test's HTTP retry then re-sends the same request digest, which
// vault's replay guard rejects with "request was already authorized previously". That error proves the
// original request was accepted and processed, ...
```

But this is only true when the failure happens strictly *after* the DON has fully committed the write. If the failure instead happens between `CheckAndRecord` and the actual DON-side commit — e.g. the post-`CheckAndRecord` owner-binding check fails, the post-authorization `stamp()`/marshaling step fails, the gateway cannot reach a quorum of DON responses, or the DON-side OCR `StateTransition` for `CreateSecrets`/`UpdateSecrets` errors out (see `stateTransitionCreateSecretsRequest`, which can fail on `GetSecretIdentifiersCountForOwner`/`WriteSecret` errors) — the write was never actually applied, yet the exact same request digest is now permanently rejected by the in-memory replay guard with `ErrRequestAlreadySeen` for the remainder of its expiry window.

### Impact Explanation
An unprivileged workflow owner submitting a `vault.secrets.create` / `vault.secrets.update` request through the internet-facing gateway can have their write request "claimed" (replay-guard consumed) without the corresponding secret actually being created/updated, if any step after `CheckAndRecord` but before durable commit fails transiently (network blip to the DON, a marshaling/stamping error, or a DON-side quorum/state-transition failure). The caller cannot resubmit that exact request (same ID/params, hence same digest) — the gateway will reject it with "request not authorized: request was already authorized previously" — and the only recovery is to mint a brand-new request with a different ID/nonce and get it freshly authorized/allowlisted, exactly analogous to Footium's owner needing a new merkle root. This is a self-inflicted denial-of-service on a specific idempotency key that silently masks write failures as "already handled," which can confuse clients into believing a secret was written when it was not.

### Likelihood Explanation
This is reachable by any unprivileged client with a valid (allowlisted or JWT-authorized) vault write request — no special privilege beyond normal workflow-owner authorization is required. The triggering conditions (owner-binding mismatch after auth, transient gateway/DON communication failure, or DON-side write failure) are realistic operational events, not adversary-controlled exploits, making likelihood moderate: it manifests under normal failure conditions rather than requiring an attacker to engineer a specific state.

### Recommendation
Move `replayGuard.CheckAndRecord` to occur only after all pre-dispatch validation (owner-binding, ID stamping, param marshaling) has succeeded, or make the replay-guard insertion transactional with those steps (insert-then-rollback-on-failure). Additionally, consider only marking a digest "seen" once the DON confirms the write was durably applied (e.g., via signed OCR outcome), rather than at gateway-side authorization time, so transient failures before actual commit do not permanently consume the idempotency key.

### Proof of Concept
1. Client submits a valid `vault.secrets.create` request; `AuthorizeRequest` succeeds and `CheckAndRecord(digest, expiry)` records the digest as seen.
2. Immediately after, `validateSecretOwnersMatchAuthorized` fails (e.g., because of an owner-casing/derivation edge case) — this is checked in `authorizer.AuthorizeRequest` *after* `CheckAndRecord` already succeeded (`core/capabilities/vault/authorizer.go:109-116`). `AuthorizeRequest` returns an error and the request is never dispatched to the DON — no secret is written.
3. Client legitimately retries the identical request (same ID/params, so same digest) expecting it to be processed.
4. `replayGuard.CheckAndRecord` now returns `ErrRequestAlreadySeen` (`core/capabilities/vault/request_replay_guard.go:41-43`), so `AuthorizeRequest` fails again with "request not authorized: request was already authorized previously", even though no secret was ever created.
5. The client is permanently blocked from writing that secret under that request ID for the remainder of the digest's expiry window, and must fabricate an entirely new request (new ID) to succeed — mirroring the Footium report's "owner must set a new merkle root" workaround.

### Citations

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

**File:** core/capabilities/vault/request_replay_guard.go (L9-9)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")
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
