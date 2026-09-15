Found a valid analog.

### Title
Allowlist-based Vault request replay guard can be pre-consumed by any unprivileged client to invalidate a legitimate workflow owner's pre-authorized request - ([File: core/capabilities/vault/authorizer.go])

### Summary
The Vault gateway's `Authorizer.AuthorizeRequest` uses a shared, digest-keyed `RequestReplayGuard` to prevent replay of already-processed requests. For the allowlist-based auth path, the digest that gates a request is the deterministic hash of the request's method+params (`req.Digest()`), computed identically by anyone, and the owner's authorization for that digest is published on-chain via `AllowlistRequest` on the `WorkflowRegistry` contract before the real request is sent to the gateway. Because the digest is public (visible on-chain) and requires no secret to reproduce, and because the replay guard is a single shared cache consumed on first successful authorization regardless of who submitted the request, any unprivileged actor who observes the on-chain `AllowlistRequest` transaction can reconstruct or replay the exact same JSON-RPC request and submit it to the gateway first, burning the digest in the replay guard before the legitimate owner's request arrives.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` (core/capabilities/vault/allow_list_based_auth.go:34-77) computes `requestDigest := req.Digest()` from public request content and looks it up against on-chain allowlisted entries (`WorkflowRegistryOwnerAllowlistedRequest`) synced from the `WorkflowRegistry` contract via `AllowlistRequest`. This on-chain call (see `deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go` `UserAllowlistRequestOp`, and `system-tests/lib/cre/workflow/secrets.go` `ExecuteSecrets`) is a normal, publicly-observable transaction that stores `(RequestDigest, Owner, ExpiryTimestamp)` on-chain — i.e., the digest that will authorize a future request is broadcast to the world before the actual JSON-RPC call reaches the gateway.

`authorizer.AuthorizeRequest` (core/capabilities/vault/authorizer.go:99-119) then does:
```
authResult, err := a.authorizeRequest(ctx, req)
...
if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
    return nil, err  // ErrRequestAlreadySeen
}
```
`RequestReplayGuard.CheckAndRecord` (core/capabilities/vault/request_replay_guard.go:35-47) marks the digest "seen" on the very first successful authorization, independent of which caller supplied the request body — the guard has no binding to a specific caller/session, only to the digest. This mirrors the reported `checkOrder()` pattern: a shared once-only nonce/digest consumer is reachable through a path (here, submitting any JSON-RPC request whose params match a publicly-known digest) that lets an unrelated third party "use up" the single-use guarantee before the legitimate/privileged caller (the actual workflow owner's Vault client) submits its real request.

Because `req.Digest()` (core/capabilities/vault/*, exercised in `TestAllowListBasedAuth_ListSecrets` etc.) depends only on `Method` and `Params` — content that is either predictable (e.g., a `vault.secrets.list` request with known namespace/owner) or directly visible from the on-chain `AllowlistRequest` transaction's digest argument combined with the workflow owner's already-public address/namespace conventions — an attacker does not need to break any cryptographic primitive; they only need to reconstruct the exact JSON-RPC request body that hashes to the allowlisted digest and submit it to the gateway before the legitimate request lands.

### Impact Explanation
An unprivileged attacker can grief/DoS legitimate Vault requests (e.g., `vault.secrets.create`, `vault.secrets.list`, `vault.secrets.delete`) made by any workflow owner using the allowlist-based auth path: by front-running the gateway submission with the same request body/digest, the attacker consumes the one-time replay-guard entry, causing the legitimate owner's actual request to fail with `ErrRequestAlreadySeen` ("request was already authorized previously"). This can block secret creation/rotation/deletion operations for a targeted workflow owner, since the on-chain allowlist entry is now "used" and the owner must obtain a new allowlist entry and repeat the process (which can itself be griefed again). This matches the H-4 impact class: a public, unprivileged verification path consumes a shared once-only guard also required by privileged/legitimate operations.

### Likelihood Explanation
The `AllowlistRequest` transaction is a normal on-chain transaction and is inherently public (visible in mempool/blocks) before the gateway request is submitted, so the precondition (observing the digest before the legitimate request executes) is trivially satisfiable by any chain observer. No admin/operator access, no leaked secrets, and no protocol-level cryptographic break are required — only the ability to submit a JSON-RPC request to the public-facing Vault gateway with content matching the on-chain digest, which is realistically reconstructable from the workflow owner/namespace metadata that accompanies the on-chain allowlist entry and the well-known Vault request schemas.

### Recommendation
- Bind the replay-guard entry to the authorized owner/caller (not just the raw digest) so that only the legitimate owner's session can consume their own allowlisted digest, or require that the first successful authorization also validate a caller-specific credential in addition to the digest match.
- Alternatively, do not treat "digest observed and authorized once" as sufficient for consumption; instead have `AllowlistRequest`'s on-chain confirmation trigger reservation only for the specific request payload signed/submitted by the owner through an authenticated channel (e.g., requiring the owner to also present the JWT-based or session-based proof of identity even on the allowlist path), decoupling "know the digest" from "consume the one-time authorization."
- Consider rate-limiting/re-allowlisting flows so a griefed owner can cheaply re-establish a fresh allowlist entry with a fresh nonce that is not predictable/observable before use (e.g., using a per-request random salt not derivable purely from public on-chain data).

### Proof of Concept
1. Workflow owner `O` prepares a `vault.secrets.create` (or `vault.secrets.list`) JSON-RPC request `R` with known `Method`/`Params` (namespace/owner values are not secret).
2. `O` calls `WorkflowRegistry.AllowlistRequest(digest(R), expiry)` on-chain (as in `system-tests/lib/cre/workflow/secrets.go` `ExecuteSecrets` / `user_workflow_registry_ops.go` `UserAllowlistRequestOp`). This transaction is publicly visible (chain data/mempool) before it is even mined, exposing `digest(R)` and `O`'s address.
3. Attacker `A`, monitoring the chain, reconstructs `R'` — any JSON-RPC request with `Method`/`Params` that hash to the same `digest(R)` (trivial if `A` can guess or observe the exact request schema/values, e.g., a `vault.secrets.list` call for a known namespace) — and submits `R'` to the public Vault gateway endpoint before `O`'s real client does.
4. `allowListBasedAuth.AuthorizeRequest` finds the on-chain allowlisted entry matching `digest(R)` and returns a valid `AuthResult`; `authorizer.AuthorizeRequest` then calls `replayGuard.CheckAndRecord(digest(R), expiry)`, which succeeds and marks `digest(R)` as seen.
5. When `O`'s legitimate client subsequently submits the real `R` to the gateway, `allowListBasedAuth.AuthorizeRequest` again succeeds (same digest, still on-chain and unexpired), but `authorizer.AuthorizeRequest`'s `replayGuard.CheckAndRecord` now returns `ErrRequestAlreadySeen`, and `O`'s legitimate, pre-authorized request is rejected — exactly the "one invalidated order/nonce blocks the legitimate privileged operation" pattern described in H-4. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L360-387)
```go
var UserAllowlistRequestOp = operations.NewOperation(
	"user-allowlist-request-op",
	semver.MustParse("1.0.0"),
	"User Allowlist Request in WorkflowRegistry V2",
	func(b operations.Bundle, deps WorkflowRegistryOpDeps, input UserAllowlistRequestOpInput) (UserAllowlistRequestOpOutput, error) {
		// Execute the transaction using the strategy
		operation, _, err := deps.Strategy.Apply(func(opts *bind.TransactOpts) (*types.Transaction, error) {
			tx, err := deps.Registry.AllowlistRequest(opts, input.RequestDigest, input.ExpiryTimestamp)
			if err != nil {
				return nil, fmt.Errorf("failed to call AllowlistRequest: %w", err)
			}
			return tx, nil
		})
		if err != nil {
			return UserAllowlistRequestOpOutput{}, fmt.Errorf("failed to execute AllowlistRequest: %w", err)
		}
		if operation != nil {
			deps.Env.Logger.Infof("Created MCMS proposal for AllowlistRequest on chain %d", input.ChainSelector)
		} else {
			deps.Env.Logger.Infof("Successfully user allowlisted request on chain %d", input.ChainSelector)
		}
		return UserAllowlistRequestOpOutput{
			Success:         true,
			MCMSOperation:   operation,
			RegistryAddress: deps.Registry.Address(),
		}, nil
	},
)
```

**File:** system-tests/lib/cre/workflow/secrets.go (L186-211)
```go
	requestDigest, err := jsonRequest.Digest()
	if err != nil {
		return errors.Wrap(err, "failed to compute request digest")
	}

	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		return errors.Wrap(err, "failed to decode request digest hex")
	}
	if len(requestDigestBytes) != 32 {
		return errors.Errorf("invalid request digest length: got %d bytes, want 32", len(requestDigestBytes))
	}

	var reqDigestBytes [32]byte
	copy(reqDigestBytes[:], requestDigestBytes)

	wfReg, err := workflow_registry_v2_wrapper.NewWorkflowRegistry(workflowRegistryAddress, sethClient.Client)
	if err != nil {
		return errors.Wrap(err, "failed to instantiate workflow registry v2 wrapper")
	}

	expiry := uint32(time.Now().Add(time.Hour).Unix()) //nolint:gosec // G115: timestamp fits uint32 until year 2106
	_, decErr := sethClient.Decode(wfReg.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, expiry))
	if decErr != nil {
		return errors.Wrap(decErr, "failed to allowlist vault request in workflow registry")
	}
```
