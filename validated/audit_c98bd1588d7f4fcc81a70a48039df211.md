### Title
Vault request replay guard is in-memory only, allowing an already-consumed, single-use gateway authorization to be reused after a node restart - ([File: core/capabilities/vault/request_replay_guard.go])

### Summary
The vault gateway authorization pipeline is designed to guarantee that a given authorized request (JWT- or allowlist-based) can be consumed exactly once, similarly to a single-use "escrow" of permission. That guarantee is enforced only by an in-process `RequestReplayGuard` map that is never persisted, so any node restart, crash, or redeploy wipes the "already used" state while the underlying on-chain allowlist entry (or JWT expiry) is still valid — allowing the same already-consumed request to be re-authorized and re-executed.

### Finding Description
`RequestReplayGuard` is documented as ensuring "a given request digest is only accepted once": [1](#0-0) 

It stores digests purely in a process-local `map[string]int64` protected by a `sync.Mutex`, with no database or durable backing store: [2](#0-1) 

The generic `authorizer.AuthorizeRequest` relies on this single in-memory guard, constructed fresh via `NewRequestReplayGuard()` every time an `Authorizer` is created, to convert the underlying allowlist/JWT authorization (which is intentionally reusable — see `allow_list_based_auth_test.go` comment "Same request is still authorized here; replay protection lives in the generic Authorizer") into a single-use guarantee: [3](#0-2) [4](#0-3) 

The underlying `AllowListBasedAuth.AuthorizeRequest` explicitly re-authorizes the *same* digest as many times as asked, as long as the on-chain allowlist entry (with its `ExpiryTimestamp`, e.g. a 1-hour window in tests, configurable by the caller in production) has not expired: [5](#0-4) 

Because `RequestReplayGuard` state lives only in process memory (`core/capabilities/vault/authorizer.go:94`, `NewAuthorizer` → `NewRequestReplayGuard()`), any process restart of the node (deploy, crash-and-recover, container replacement, gateway/DON node rotation) resets the "seen" map to empty. Any request digest that was consumed before the restart — and whose on-chain allowlist expiry (or JWT expiry) has not yet elapsed — becomes authorizable again, exactly reproducing the reported "escrow reuse" bug class: a resource meant to guarantee single consumption is reusable across "two consecutive executions" whenever the process boundary resets its bookkeeping.

This is reachable from an unprivileged client via the internet-facing gateway: `GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` routes `MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, and `MethodSecretsList` requests through `GatewayVaultRequestProcessor.ProcessRequest` → `Authorizer.AuthorizeRequest`, which is the sole point protecting against replay: [6](#0-5) 

### Impact Explanation
An attacker (or even the legitimate but replaying client) who captures a previously-authorized request (its JSON-RPC envelope, including the digest components) can resend it to the gateway after the node process restarts, and it will be executed again — creating/updating/deleting/listing vault secrets a second time under the same authorization — even though the system's intended security invariant is "each authorized digest executes exactly once." This undermines the request-level replay protection that the rest of the authorization pipeline (owner binding, allowlist expiry, JWT `jti` tracking) is built on top of, and could allow duplicate secret mutation operations outside of the single-execution guarantee the design relies on.

### Likelihood Explanation
Exploitation requires that: (1) an attacker has captured/retained a valid, previously-processed request (its digest and, for JWT auth, the token), and (2) the vault node process restarts while the underlying allowlist entry or JWT is still within its configured expiry window. Node restarts (deploys, crashes, rolling upgrades) are routine operational events, and allowlist/JWT expiry windows can be configured to be long relative to typical restart cadence, so the window of exposure is realistic, though it does depend on operational timing rather than being trivially always exploitable.

### Recommendation
Persist the replay-guard state (e.g., in the node's database, similar to how `sessions`/`oidc_sessions` tables persist session state) so that "already seen" digests survive process restarts, or reduce the authorization/allowlist expiry window to a value tightly bound to the expected request completion time so that a restart cannot reopen a meaningful replay window. At minimum, treat the in-memory `RequestReplayGuard` as insufficient on its own for the single-use guarantee and add a durable, cross-restart check before executing any vault mutation.

### Proof of Concept
1. Workflow owner (or gateway operator) allowlists a `SecretsCreate` request digest on-chain with an expiry of, e.g., 1 hour (`allowlistRequest` in `system-tests/tests/smoke/cre/vault_don_test_helpers.go:1510-1517`).
2. Client sends the request through the gateway; `GatewayHandler.HandleGatewayMessage` authorizes it via `Authorizer.AuthorizeRequest`, which records the digest in the in-memory `RequestReplayGuard` and executes `SecretsCreate` successfully.
3. Node process is restarted (deploy/crash) before the 1-hour allowlist expiry elapses. The new process constructs a fresh `Authorizer` via `NewAuthorizer(...)` → `NewRequestReplayGuard()`, whose `seen` map starts empty (`core/capabilities/vault/request_replay_guard.go:23-28`).
4. The same request (same digest) is resent to the gateway. `AllowListBasedAuth.AuthorizeRequest` re-authorizes it because the allowlist entry is still unexpired (`core/capabilities/vault/allow_list_based_auth.go:64-76`), and the replay guard has no memory of it, so `CheckAndRecord` succeeds again (`core/capabilities/vault/request_replay_guard.go:35-47`), letting `SecretsCreate` execute a second time.

### Citations

**File:** core/capabilities/vault/request_replay_guard.go (L9-47)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")

// RequestReplayGuard prevents replay of already-processed requests by tracking
// request digests with expiry timestamps. It is safe for concurrent use.
//
// Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow to ensure
// that a given request digest is only accepted once.
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

**File:** core/capabilities/vault/authorizer.go (L83-119)
```go
type authorizer struct {
	allowListBasedAuth Authorizer
	jwtBasedAuth       Authorizer
	replayGuard        *RequestReplayGuard
	lggr               logger.Logger
}

func NewAuthorizer(allowListBasedAuth Authorizer, jwtBasedAuth Authorizer, lggr logger.Logger) Authorizer {
	return &authorizer{
		allowListBasedAuth: allowListBasedAuth,
		jwtBasedAuth:       jwtBasedAuth,
		replayGuard:        NewRequestReplayGuard(),
		lggr:               logger.Named(lggr, "VaultAuthorizer"),
	}
}

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

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-189)
```go

	// Same request is still authorized here; replay protection lives in the generic Authorizer.
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-77)
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

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```
