### Title
Vault request "allowlist approval" is never consumed on grant/use and replay protection relies solely on volatile, per-process memory — ([File: core/capabilities/vault/request_replay_guard.go])

### Summary
This is the closest present-day analog to the Visor "stale, non-revocable NFT approval" bug class. In Visor, `approveTransferERC721()` grants a standing approval that is never cleared after use, so the same approval can be exercised again later. In the Vault capability's `AllowListBasedAuth`, an on-chain "approval" (an allowlisted request digest with a future `ExpiryTimestamp`) is likewise never consumed, revoked, or marked used on-chain when it is exercised. The *only* mechanism that prevents the same digest from being authorized twice is an in-memory `RequestReplayGuard` that is recreated empty every time the authorizer is constructed (i.e., on every gateway/node process start).

### Finding Description
`AllowListBasedAuth.AuthorizeRequest` checks only whether a request digest is present in the on-chain allowlist and unexpired — it performs no state mutation and does not remove/consume the allowlist entry: [1](#0-0) 

The code and its own tests explicitly document that this authorizer alone permits the *same* allowlisted request to be authorized more than once, deferring all "single-use" protection to a separate component: [2](#0-1) 

That separate component is `RequestReplayGuard`, a purely in-memory `map[string]int64` with no persistence to disk/DB: [3](#0-2) 

The guard is instantiated fresh (empty) every time `NewAuthorizer` is called: [4](#0-3) 

`NewAuthorizer` is invoked once during construction of both the gateway-side Vault handler (`core/services/gateway/handlers/vault/handler.go` `NewHandler`) and the node-side `GatewayHandler` (`core/capabilities/vault/gw_handler.go` `NewGatewayHandler`) — i.e., on every process startup: [5](#0-4) [6](#0-5) 

Because the on-chain allowlist entry (the "approval") is never revoked/consumed and remains valid for its full `ExpiryTimestamp` window (which can be set arbitrarily far in the future, e.g. one hour or more, as shown in test helpers requesting `time.Now().Add(1*time.Hour)`), any process restart of a gateway or DON node — a routine event during deploys, crashes, OOM kills, or rolling upgrades — wipes the in-memory replay guard and makes every previously-processed allowlisted request digest authorizable again, exactly like Visor's stale, un-revocable NFT approval being exercisable again once state resets.

### Impact Explanation
An unprivileged party who has observed one valid signed/allowlisted Vault JSON-RPC request (e.g., a `vault.secrets.create`/`update`/`delete` request, which travels through the public, internet-facing gateway) can replay it after any gateway or node restart occurring within the request's on-chain expiry window, and it will be re-authorized and reprocessed as if fresh. This is a concrete allowlist/replay bypass reachable from an unprivileged client via the internet-facing gateway's message-handling path, directly analogous to the report's "approval not removed after use" root cause.

### Likelihood Explanation
Process restarts (deploys, crashes, rolling upgrades, autoscaling) are routine operational events, not attacker-controlled, but they are frequent enough in production DON/gateway fleets that the window for replay is realistic, especially since `ExpiryTimestamp` can be set far in the future. The design is also explicitly acknowledged in code comments/tests as delegating all single-use enforcement to the in-memory guard, confirming this is a genuine gap rather than a misreading of intent.

### Recommendation
Persist consumed/authorized request digests (or mark allowlist entries as consumed on-chain, or in a durable, shared store) so that replay protection survives process restarts and is consistent across all gateway/node instances, rather than relying solely on a per-process, in-memory `RequestReplayGuard`.

### Proof of Concept
1. Client obtains on-chain allowlisting for a request digest `D` with `ExpiryTimestamp = now + 1h` via `AllowlistRequest` (as done in `allowlistRequest` test helper) — [7](#0-6) .
2. Client sends the allowlisted request to the gateway; `AllowListBasedAuth.AuthorizeRequest` succeeds and `RequestReplayGuard.CheckAndRecord` records digest `D` in memory — [8](#0-7) .
3. Gateway or DON node process restarts (deploy/crash/upgrade) before `D`'s on-chain expiry; a fresh `RequestReplayGuard` is created via `NewAuthorizer` — [4](#0-3) .
4. Client (or anyone who captured the original request) resends the identical request with digest `D`. `AllowListBasedAuth.AuthorizeRequest` finds it still allowlisted and unexpired on-chain and re-authorizes it, and the empty in-memory guard no longer contains `D`, so it is processed again.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L51-77)
```go
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

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-189)
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

**File:** core/capabilities/vault/authorizer.go (L99-112)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L185-209)
```go
func NewHandler(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, capabilitiesRegistry capabilitiesRegistry, workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	allowListBasedAuth := vaultcap.NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
	var jwtBasedAuth vaultcap.Authorizer
	var jwtAuth services.Service
	if cfg.Auth0 != nil {
		validator, err := vaultcap.NewJWTBasedAuth(vaultcap.JWTBasedAuthConfig{
			IssuerURL: cfg.Auth0.IssuerURL,
			Audience:  cfg.Auth0.Audience,
			TenantID:  cfg.Auth0.TenantID,
		}, limitsFactory, lggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create JWTBasedAuth: %w", err)
		}
		jwtBasedAuth = validator
		jwtAuth = validator
	}
	authorizer := vaultcap.NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)

	return newHandlerWithAuthorizer(methodConfig, donConfig, don, capabilitiesRegistry, authorizer, jwtAuth, lggr, clock, limitsFactory)
}
```

**File:** core/capabilities/vault/gw_handler.go (L81-90)
```go
// NewGatewayHandler creates a Vault gateway connector handler with internal auth wiring.
// Pass a non-nil authorizer only in tests or other cases that need to override the default
// allowlist/JWT authorization chain.
func NewGatewayHandler(
	secretsService vaulttypes.SecretsService,
	connector gatewayConnector,
	workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer,
	lggr logger.Logger,
	limitsFactory limits.Factory,
	authorizer Authorizer,
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1517)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")
```
