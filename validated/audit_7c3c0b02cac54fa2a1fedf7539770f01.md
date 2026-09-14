## Title
Unprivileged front-running of the Vault AllowList-based-auth digest replay guard causes permanent DoS of a legitimate owner's one-time allowlisted request - (File: `core/capabilities/vault/allow_list_based_auth.go`, `core/capabilities/vault/authorizer.go`, `core/capabilities/vault/request_replay_guard.go`)

### Summary
The Vault gateway's `AllowListBasedAuth` path authorizes a JSON-RPC request purely by matching its content-derived digest against an on-chain allowlist entry — it performs **no signature check** when `req.Auth == ""`. Because the digest is a deterministic hash of the request's method/params, and the matching allowlist entry (owner, digest, expiry) is public on-chain state, any unprivileged actor who can predict or learn the exact request bytes for a given digest can submit that request to the gateway *before* the legitimate owner does. The shared `RequestReplayGuard` then marks that digest as "seen" until the on-chain expiry, so when the real owner's request later arrives it is rejected with `ErrRequestAlreadySeen`, permanently blocking that one-time authorized action for the remainder of its validity window — the exact same front-running DoS pattern described in the `AllocationVesting.transferPoints()` report, where a state check tied to another party's mutable/observable data can be consumed first by a griefer.

### Finding Description
The composite `Authorizer.authorizeRequest` routes any request without a signed JWT (`req.Auth == ""`) to `allowListBasedAuth`, which is explicitly kept "for backwards compatibility" and relies solely on digest matching: [1](#0-0) 

`AllowListBasedAuth.AuthorizeRequest` computes the digest of the incoming request and checks it against `GetAllowlistedRequests()` (public on-chain `WorkflowRegistry` state, keyed only by digest/owner/expiry, with no per-submission nonce or signature binding the *caller* of the gateway request to the owner): [2](#0-1) 

Once authorized (by digest match alone), the composite authorizer immediately consumes the digest in the shared, DON-node-local `RequestReplayGuard`, keyed by digest and expiring with the on-chain expiry timestamp: [3](#0-2) [4](#0-3) 

Because `CheckAndRecord` is a first-come-first-served check with no notion of "was this the legitimate owner's device," **whoever's identical request bytes reach a given DON node first wins**. Any unprivileged party who can reconstruct or predict the exact request content that hashes to a publicly-visible allowlisted digest (e.g., for `vault.secrets.list` requests, whose params are just `{owner, namespace}` with commonly-used/guessable namespace strings, or by simply observing the request traverse the internet-facing gateway HTTP endpoint) can pre-submit it. This consumes the replay-guard slot for that digest, and the real owner's subsequent submission of the same content is rejected with `ErrRequestAlreadySeen`, with no mechanism for the legitimate owner to reset or retry other than re-allowlisting a brand-new digest on-chain.

This mirrors the `AllocationVesting.transferPoints()` bug class precisely: a state-comparison guard (`toAllocation.numberOfWeeks` / digest-in-replay-guard) that depends on externally observable/mutable state can be pre-empted by an unrelated, unprivileged actor to permanently block a legitimate one-time action for the remainder of its validity window.

### Impact Explanation
A griefer can deny a legitimate DON node operator/workflow owner the ability to execute an already-authorized (on-chain allowlisted), time-bound Vault secrets operation (`vault.secrets.create/update/delete/list`) for the whole duration of its expiry window, since the replay guard's negative result (`ErrRequestAlreadySeen`) is sticky until the recorded expiry. Because `writeMethodsEnabled`/`AllowListRequest` allowlisting flows are one-shot per digest, the owner has no self-service recovery besides re-allowlisting (an on-chain transaction) with different content, which is not always feasible for automated pipelines using fixed request shapes.

### Likelihood Explanation
Medium: the attacker needs to reconstruct the exact request bytes that hash to the observed on-chain digest. For simple, low-entropy request shapes (e.g., `ListSecretIdentifiersRequest{Owner, Namespace}` with a commonly used namespace, or any request whose id/params an attacker can infer from public data/patterns), this is feasible without any privileged access — it only requires unprivileged read access to the on-chain allowlist and the ability to submit arbitrary JSON-RPC requests to the internet-facing Vault gateway endpoint, exactly the class of "unprivileged actor" access this scan is scoped to.

### Recommendation
Do not rely on digest-only matching combined with a global, first-come-first-served replay guard for the non-JWT `AllowListBasedAuth` path. Bind the allowlist authorization to a caller-specific proof (e.g., require a signature over the request digest by the allowlisted owner even on this legacy path), or scope the replay guard per authenticated owner/session rather than as a bare content-digest race, so that an attacker guessing/observing the digest cannot consume another party's authorization slot.

### Proof of Concept
1. Workflow owner O calls `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` on-chain for a `vault.secrets.list` request with `{owner: O, namespace: "main"}` — `requestDigest` and `expiryTimestamp` become publicly readable on-chain state, as consumed by: [5](#0-4) 
2. Attacker A, having no relationship to O, constructs the identical JSON-RPC request `{"method":"vault.secrets.list","params":{"owner":"O","namespace":"main"}}` (guessable/observable), and POSTs it to the gateway before O does.
3. The gateway forwards it; on the DON node, `AllowListBasedAuth.AuthorizeRequest` matches the digest and authorizes it (no signature required), and `authorizer.replayGuard.CheckAndRecord(digest, expiry)` succeeds and records the digest, per: [6](#0-5) 
4. O's genuine request with identical content later arrives and is rejected at the same replay-guard check with `ErrRequestAlreadySeen`, per: [7](#0-6) 
5. O cannot retry the same allowlisted digest again until it expires — a DoS of a legitimately allowlisted, unprivileged-facing Vault action.

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

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
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

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1296-1308)
```go
		w.lggr.Debugw("contract call response",
			"fetchedAllowlistedRequestsNum", len(response.AllowlistedRequests),
			"searchComplete", response.SearchComplete,
			"error", response.err,
			"blockHeight", headAtLastRead.Height)

		for _, request := range response.AllowlistedRequests {
			newAllowlistedRequests = append(newAllowlistedRequests, workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{
				RequestDigest:   request.RequestDigest,
				Owner:           request.Owner,
				ExpiryTimestamp: request.ExpiryTimestamp,
			})
		}
```
