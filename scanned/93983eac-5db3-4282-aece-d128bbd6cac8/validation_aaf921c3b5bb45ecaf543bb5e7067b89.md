### Title
In-memory-only Vault request replay guard loses all state on node/gateway restart, permitting replay of previously-authorized `vault.secrets.*` requests - ([File: core/capabilities/vault/request_replay_guard.go])

### Summary
The reported bug class is: security-relevant state (voting state) is updated in memory and the action is propagated, but the durable copy of that state is not guaranteed to be persisted, so a restart causes the node to "forget" that the action already happened and allows it to be repeated (double-vote). The chainlink Vault capability contains a direct architectural analog: the replay-protection state that prevents an already-authorized `vault.secrets.{create,update,delete,list}` request from being processed twice is kept **only in an in-process map with no persistence at all**, so *every* restart of the authorizer (DON node or gateway process) unconditionally resets replay protection to empty — not merely on a rare disk-full edge case, but on every routine restart.

### Finding Description
`RequestReplayGuard` tracks previously-authorized request digests purely in memory: [1](#0-0) 

`CheckAndRecord` is the sole mechanism preventing an already-authorized request digest from being accepted a second time before its expiry: [2](#0-1) 

The guard is instantiated fresh, with an empty `seen` map, every time an `authorizer` is constructed: [3](#0-2) 

`AuthorizeRequest` calls `replayGuard.CheckAndRecord` immediately after allowlist- or JWT-based authorization succeeds, and this is the *only* gate against replay for both authentication paths: [4](#0-3) 

This `Authorizer`/`authorizer` is wired into both the gateway-side vault handler and the node-side `GatewayHandler`, both of which are reachable from unprivileged, internet-facing gateway HTTP clients: [5](#0-4) [6](#0-5) 

Because the map is never written to disk (unlike, e.g., the Omni voter state that at least attempts `WriteFileAtomic`), *any* restart of the process hosting the `authorizer` — a routine node upgrade, pod restart, crash/recovery, or gateway redeploy — clears all recorded digests. Any previously-authorized request whose `ExpiresAt` window has not yet elapsed (allowlist entries and JWT `authorization_details` requests both carry forward-looking expiry timestamps) can then be resubmitted and will pass `AuthorizeRequest` a second time, exactly as if it had never been seen. The existing test suite's own comment acknowledges the guard is the sole safety net for duplicate requests ("Same request is still authorized here; replay protection lives in the generic Authorizer"), confirming there is no independent idempotency layer relied upon for authorization-level replay defense: [7](#0-6) 

This mirrors the report's root cause precisely: a state store meant to prevent double-processing of an already-authorized action is not durably persisted, so a process restart re-opens a window for the same action to be re-authorized and re-executed.

### Impact Explanation
Downstream, `stateTransitionCreateSecrets` does have an idempotency check (`secret != nil` → "key already exists") that partially masks impact for `CreateSecrets` replays: [8](#0-7) 

However, `UpdateSecrets` and `DeleteSecrets` requests do not have an equivalent "no-op if unchanged" idempotency guard visible in the reviewed code paths — a replayed, previously-valid `UpdateSecrets` request could silently reapply a stale ciphertext over a value a user has since legitimately updated (a downgrade/rollback), and a replayed `DeleteSecrets` request could delete a secret that was deleted and later legitimately recreated under the same identifier by its owner. Both scenarios represent unauthorized state mutation triggered purely by process restart timing rather than by any new authorized action, which is the same class of harm (state corruption from lost persisted anti-replay state) the reported bug identifies for double-voting.

### Likelihood Explanation
Likelihood is moderate: it requires (1) an attacker or observer to have captured a prior valid, unexpired, already-processed Vault management request (its JSON body, since these travel over the gateway HTTP API), and (2) the DON node or gateway process to restart before that request's `ExpiresAt`. Node/gateway restarts for routine operational reasons (deploys, upgrades, crash recovery) are common in production DON operation, and expiry windows for allowlisted/JWT requests can be on the order of minutes, so the restart-timing precondition is realistic rather than purely theoretical.

### Recommendation
Persist the replay-guard state (or at minimum a durable, cross-restart record of consumed request digests with their expiries) so that a restart cannot silently reopen the replay window — analogous to the report's own recommendation to fail safe (e.g., refuse to authorize/serve Vault requests) rather than silently proceeding with an authorizer whose anti-replay state cannot be guaranteed intact after restart. At minimum, add idempotency checks in `stateTransitionUpdateSecretsRequest`/delete-secret state transitions equivalent to the existing "already exists" check in `stateTransitionCreateSecretsRequest`, so a replayed request cannot mutate state that has since progressed.

### Proof of Concept
1. A legitimate workflow owner submits a valid `vault.secrets.update` request; it is authorized (allowlist/JWT valid, digest recorded in `RequestReplayGuard.seen`) and successfully processed by the DON via OCR consensus.
2. The owner (or any party who has kept a copy of the outbound request body) submits a subsequent legitimate `vault.secrets.update` for the same secret with a new value; this also succeeds.
3. Before the first request's `ExpiresAt` elapses, the DON node or gateway process hosting the `authorizer` restarts (e.g., a routine deployment), reinitializing `RequestReplayGuard` with an empty `seen` map per `NewAuthorizer`/`NewRequestReplayGuard`.
4. The captured original (step 1) request is resubmitted to the gateway. `AuthorizeRequest` re-validates it against the allowlist/JWT (still not expired) and, because `CheckAndRecord` finds no matching entry in the now-empty map, authorizes it again, causing the secret to be reverted to its stale (step-1) value — overwriting the newer, legitimate update from step 2 without any new authorization from the owner.

### Citations

**File:** core/capabilities/vault/request_replay_guard.go (L16-28)
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

**File:** core/capabilities/vault/gw_handler.go (L84-126)
```go
func NewGatewayHandler(
	secretsService vaulttypes.SecretsService,
	connector gatewayConnector,
	workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer,
	lggr logger.Logger,
	limitsFactory limits.Factory,
	authorizer Authorizer,
	auth0 *Auth0Config,
) (*GatewayHandler, error) {
	var jwtAuthService services.Service
	var jwtBasedAuth Authorizer
	if auth0 != nil {
		var err error
		jwtAuthService, err = NewJWTBasedAuth(JWTBasedAuthConfig{
			IssuerURL: auth0.IssuerURL,
			Audience:  auth0.Audience,
			TenantID:  auth0.TenantID,
		}, limitsFactory, lggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create JWTBasedAuth: %w", err)
		}
		jwtBasedAuth = jwtAuthService.(Authorizer)
	}

	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}

	requestValidator, err := NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, fmt.Errorf("failed to create request validator: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestProcessor, err := NewGatewayVaultRequestProcessor(requestValidator, authorizer, true, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L211-244)
```go
func newHandlerWithAuthorizer(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, capabilitiesRegistry capabilitiesRegistry, authorizer vaultcap.Authorizer, jwtAuth services.Service, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = 30
	}

	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, fmt.Errorf("failed to create node rate limiter: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestValidator, err := vaultcap.NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, err
	}

	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}

	requestProcessor, err := vaultcap.NewGatewayVaultRequestProcessor(requestValidator, authorizer, false, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-189)
```go

	// Same request is still authorized here; replay protection lives in the generic Authorizer.
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L2043-2050)
```go
	secret, err := store.GetSecret(ctx, req.Id)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret from key-value store: %w", err)
	}

	if secret != nil {
		return nil, vaulttypes.NewUserError("could not write to key value store: key already exists")
	}
```
