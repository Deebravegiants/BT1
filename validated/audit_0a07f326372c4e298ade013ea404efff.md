### Title
Vault request replay protection is per-node, in-memory only, and reset on restart, allowing a signed request to be reused - (File: `core/capabilities/vault/request_replay_guard.go`)

### Summary
Chainlink's Vault DON authorizes off-chain-signed/allowlisted client requests (e.g. `secrets/create`, `secrets/update`, `secrets/delete`) via `Authorizer.AuthorizeRequest` in `core/capabilities/vault/authorizer.go`, which delegates to `allowListBasedAuth`/`jwtBasedAuth` and then calls a `RequestReplayGuard` to prevent the same authorized request from being processed twice. This mirrors the audited Gondi `emitLoan()` bug class: a validly signed/authorized payload (the "borrower signature") can be resubmitted to trigger the privileged action again unless a persistent, tamper-proof one-time-use mechanism (nonce) exists.

### Finding Description
`Authorizer.AuthorizeRequest` in `core/capabilities/vault/authorizer.go` calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` to reject a previously-seen request digest. [1](#0-0) 

However, `RequestReplayGuard` is a purely in-process, in-memory map (`seen map[string]int64`) constructed fresh via `NewRequestReplayGuard()` with no persistence backend: [2](#0-1) 

Each Vault DON node runs its own `authorizer` instance with its own independent `replayGuard`, as documented in the comment above `AuthorizeRequest`/`RequestReplayGuard` ("Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow"). Because the guard state lives only in process memory, it is wiped on any node restart (crash, redeploy, upgrade). The underlying allowlist entry from the workflow registry (`WorkflowRegistryOwnerAllowlistedRequest`) is keyed only by `RequestDigest` and an `ExpiryTimestamp`, and it is *not* consumed/invalidated once used: [3](#0-2) 

The test suite itself acknowledges the allowlist auth alone provides no one-time-use guarantee: "Same request is still authorized here; replay protection lives in the generic Authorizer" — i.e., the *only* line of defense against reuse of a previously authorized/signed request is the volatile, non-persistent `RequestReplayGuard`. [4](#0-3) 

This is the direct analog of the `emitLoan()` finding: there, a signed `LoanExecutionData` had no nonce and could be replayed until `expirationTime`; here, an allowlisted/JWT-authorized vault request digest has no persisted nonce and can be replayed until `ExpiryTimestamp`, bounded only by whether the specific node process has retained its in-memory `seen` map since the first use.

### Impact Explanation
If a node restarts (a routine, unprivileged-actor-observable event — deploys, crashes, OOM, upgrades) before the allowlisted request's `ExpiryTimestamp` elapses, any actor who previously observed the authorized JSON-RPC envelope (e.g. captured from gateway traffic, logs, or as the original submitter) can resubmit the identical request. Because the digest is no longer "seen" post-restart, `AuthorizeRequest` will succeed again, letting privileged vault mutation operations (`secrets/create`, `secrets/update`, `secrets/delete`) re-execute without a fresh authorization/signature — directly causing "unauthorized job run" style re-execution of secret-store mutations. This is an unprivileged-actor concern in the internet-facing gateway/DON authentication path, matching the report's severity class (unprivileged action being forced to repeat) though scoped to Vault secret operations rather than fund movement.

### Likelihood Explanation
Medium: exploitation requires (1) capturing or retaining a previously valid, still-unexpired authorized request payload, and (2) a node restart occurring within that expiry window — both plausible in production operations (rolling deploys/restarts are common) and not attacker-controlled but not rare either. No cryptographic nonce or persisted replay ledger is enforced at the source-of-truth (the allowlist / workflow registry) level, so the security property depends entirely on process uptime of each individual DON node.

### Recommendation
- Bind the one-time-use property to the authoritative source (workflow registry allowlist entry or JWT) rather than to node-local memory, e.g., mark/consume the allowlisted request on first successful use on-chain or in a shared, persistent store (similar to adding a nonce in `emitLoan()`).
- Alternatively, persist `RequestReplayGuard` state (or a hash-set of consumed digests) to durable storage shared across node restarts/DON members, or require a client-supplied monotonically increasing nonce per authorized request tied to the owner, invalidated after single use.
- Shorten default `ExpiryTimestamp` windows for allowlisted vault requests to minimize the exploitable window between authorization and consumption.

### Proof of Concept
1. Client obtains authorization for a vault request (e.g. `secrets/create`) with digest `D` and `ExpiryTimestamp = T`.
2. Node processes the request; `RequestReplayGuard.CheckAndRecord(D, T)` records `D` in memory. Secret is created.
3. Node process restarts (deploy/crash) before `T` elapses; in-memory `seen` map is cleared.
4. Attacker (or the same client) resubmits the identical JSON-RPC request with digest `D` to the gateway/DON.
5. `allowListBasedAuth.AuthorizeRequest` finds the allowlist entry still valid (`ExpiryTimestamp` unexpired, entry not consumed) at `core/capabilities/vault/allow_list_based_auth.go:64-77`; `RequestReplayGuard.CheckAndRecord` no longer has `D` recorded, so it succeeds at `core/capabilities/vault/request_replay_guard.go:35-47`.
6. The privileged operation is executed a second time without any new signature/authorization from the legitimate owner.

### Citations

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

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-189)
```go

	// Same request is still authorized here; replay protection lives in the generic Authorizer.
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())
```
