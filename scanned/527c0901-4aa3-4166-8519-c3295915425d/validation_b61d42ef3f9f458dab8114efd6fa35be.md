### Title
Vault gateway replay guard is per-node, in-memory, and unbounded-reuse-capable across node restarts, allowing a single-use allowlisted request to be re-authorized and re-processed - (File: core/capabilities/vault/request_replay_guard.go)

### Summary
The Vault DON's `Authorizer` treats an on-chain allowlisted request digest as reusable at the allowlist layer, and delegates the *only* single-use ("already consumed") enforcement to `RequestReplayGuard`, an in-process, non-persistent map keyed by digest. [1](#0-0)  This mirrors the audit report's root cause: state that is supposed to prevent repetition of a privileged action ("has this withdrawal/request already been consumed?") is not durably retained, so the same previously-authorized artifact can be replayed once that transient state is lost.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` explicitly does **not** enforce single-use; the allowlist check only verifies the digest is present and unexpired on-chain, and the test suite documents that the same request is authorized twice at this layer ("Same request is still authorized here; replay protection lives in the generic Authorizer.") [2](#0-1) 

The actual single-use guarantee is implemented entirely by `RequestReplayGuard`, which stores `seen map[string]int64` purely in memory, with no persistence to disk/DB: [3](#0-2) 

This guard is instantiated fresh every time `NewAuthorizer` is constructed [4](#0-3) , which itself is created fresh whenever a `GatewayHandler` is (re)started [5](#0-4) . Consequently, any node restart, redeploy, or process crash silently wipes the "already used" bookkeeping for every digest that node has seen. Because the on-chain allowlist entry itself is not consumed/removed on use — it simply expires after its `ExpiryTimestamp` — a request digest that was legitimately authorized once remains authorizable indefinitely (up to expiry) from the allowlist's point of view. [6](#0-5) 

The `GatewayVaultRequestProcessor` pipeline funnels `SecretsCreate`/`SecretsUpdate`/`SecretsDelete` requests through `authorizeAndStamp`, which calls `p.authorizer.AuthorizeRequest` as the sole gate before the request is forwarded into OCR consensus for the actual state mutation (write to the vault KV store). [7](#0-6)  There is no independent idempotency check downstream of authorization keyed to "has this exact digest already produced a write" — the OCR aggregation logic (`stateTransitionCreateSecrets`/`stateTransitionCreateSecretsRequest`) processes whatever observations reach F+1 consensus, driven by whichever nodes' `GatewayHandler` accepted the (now-replayable) request.

This is directly analogous to the reported bug class: a request-consumption record ("already requested/withdrawn") that should persist to prevent repeated use of the same authorization is instead ephemeral/incompletely tracked, enabling the same privileged action to be repeated by an unprivileged client simply by waiting for the tracking state to reset (there: cycle rollover / no deletion of old requests; here: node restart / process recycling wiping the in-memory map).

### Impact Explanation
An external, unprivileged client that has been granted a single on-chain allowlist entry (one workflow-owner request, once) can resubmit the identical JSON-RPC request to the gateway after any handling node restarts (deploys, crashes, upgrades, autoscaling events, etc.), and that node will treat it as newly authorized and forward it again for OCR processing. If enough nodes in the DON have independently lost their in-memory replay state (a realistic operational scenario during rolling deploys), the same previously-consumed request digest can reach F+1 consensus again, causing a duplicate/unauthorized re-execution of a privileged vault operation (secret create/update/delete) using stale authorization — a request-impersonation/authorization-bypass outcome for an operation that was supposed to be single-use.

### Likelihood Explanation
Moderate-to-high: node restarts are routine operational events (deploys, OOM kills, upgrades) and are entirely outside the control or knowledge of the client holding the allowlisted digest; no special privilege is needed by the attacker beyond having once obtained a legitimate single-use allowlist entry (which they always have, since they are the workflow owner who requested it). The attacker only needs to retain the original signed/allowlisted request payload and resend it — no cryptographic material needs to be forged.

### Recommendation
Persist replay/consumption state for authorized Vault request digests outside of node-local memory (e.g., a durable store shared across restarts, or consumption tracked on-chain in the workflow registry alongside the allowlist entry), so that a digest cannot be re-authorized after it has been used once, regardless of process restarts. Alternatively, make the on-chain allowlist entry itself single-use (removed/marked consumed on successful authorization) rather than relying solely on an ephemeral node-side guard, closing the gap the tests explicitly acknowledge ("replay protection lives in the generic Authorizer").

### Proof of Concept
1. Workflow owner requests allowlisting of a specific `CreateSecrets`/`UpdateSecrets` request digest via `AllowlistRequest` on `WorkflowRegistry`.
2. Client sends the request to the gateway; a DON node's `GatewayHandler.HandleGatewayMessage` authorizes it via `Authorizer.AuthorizeRequest`, which records the digest in that node's in-memory `RequestReplayGuard` and forwards it for consensus processing. [8](#0-7) 
3. The node process restarts (deploy/crash/upgrade) — a fresh `RequestReplayGuard` map is created, losing the record of the previously-seen digest. [9](#0-8) 
4. The client resends the exact same original request (same digest, still unexpired on-chain). `allowListBasedAuth.AuthorizeRequest` re-authorizes it (allowlist check alone permits reuse, as demonstrated in the test), and the now-empty `RequestReplayGuard` no longer rejects it. [2](#0-1) 
5. The replayed request is forwarded again into the OCR pipeline as a "new" authorized request, potentially reaching consensus a second time if a sufficient number of nodes have similarly lost their local replay state.

### Citations

**File:** core/capabilities/vault/authorizer.go (L90-97)
```go
func NewAuthorizer(allowListBasedAuth Authorizer, jwtBasedAuth Authorizer, lggr logger.Logger) Authorizer {
	return &authorizer{
		allowListBasedAuth: allowListBasedAuth,
		jwtBasedAuth:       jwtBasedAuth,
		replayGuard:        NewRequestReplayGuard(),
		lggr:               logger.Named(lggr, "VaultAuthorizer"),
	}
}
```

**File:** core/capabilities/vault/authorizer.go (L99-118)
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
```

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-190)
```go

	// Same request is still authorized here; replay protection lives in the generic Authorizer.
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())

```

**File:** core/capabilities/vault/request_replay_guard.go (L16-47)
```go
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}

// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
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

**File:** core/capabilities/vault/gw_handler.go (L108-111)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L63-76)
```go

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
