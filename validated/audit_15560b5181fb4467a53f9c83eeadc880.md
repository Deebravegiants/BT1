### Title
Unordered execution of owner-allowlisted Vault requests permits attacker-controlled reordering of pre-authorized operations - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
Chainlink's Vault gateway authorizes requests against a set of independently-allowlisted request digests (`WorkflowRegistryOwnerAllowlistedRequest`) that a workflow owner pushes on-chain via `AllowlistRequest`. Each entry is authorized purely on its content digest and its own independent expiry — there is no sequencing, nonce, or ordering relationship enforced between multiple digests allowlisted by the same owner. This is directly analogous to the reported PermitC "Unordered Nonces" issue: multiple independently-valid pre-authorizations exist simultaneously, and any unprivileged caller that has the plaintext request bytes can submit them to the public gateway in whatever order benefits them, rather than the order the owner intended.

### Finding Description
When a workflow owner wants to pre-authorize a Vault operation (create/update/delete secrets, or list) without a live JWT, it calls the `AllowlistRequest(requestDigest, expiryTimestamp)` on-chain function, recorded as a `WorkflowRegistryOwnerAllowlistedRequest{RequestDigest, Owner, ExpiryTimestamp}` entry [1](#0-0) . Multiple such entries can be outstanding for the same owner at once, e.g., pre-authorizing a `create`, an `update`, and a `delete` for related secrets.

On the gateway/DON side, `allowListBasedAuth.AuthorizeRequest` computes the digest of the incoming JSON-RPC request and simply checks membership against the current list of active allowlisted digests, with no notion of order or dependency between distinct digests belonging to the same owner: [2](#0-1) 

`fetchAllowlistedItem` performs a flat linear membership check by digest only: [3](#0-2) 

The generic `Authorizer.AuthorizeRequest` layer only adds a replay guard that rejects a *repeated* submission of the *same* digest — it does not enforce ordering across *different* allowlisted digests for the same owner: [4](#0-3) [5](#0-4) 

Because `AllowlistRequest` calls are on-chain transactions (public data) and the actual JSON-RPC request bytes needed to reproduce a given digest must be known to whoever submits them to the internet-facing gateway handler (`gw_handler.go` / `GatewayVaultRequestProcessor.ProcessRequest`), any unprivileged party who obtains the plaintext of a pending pre-authorized request (e.g., via the owner's own off-chain infrastructure broadcasting it, logs, or observing the workflow's automation) can submit any subset of the owner's currently-active allowlisted requests to the gateway, in any order, ahead of the owner's intended sequence — exactly the "unordered nonce" pattern described in the report, where a signer authorizes A, B, C intending sequence A→B→C, but an unprivileged submitter can front-run and reorder them (e.g., C→B→A) since each is independently valid until consumed or expired.

### Impact Explanation
Reordering owner-authorized Vault operations can change the final state in an unintended way: e.g., an owner might allowlist an `update` intended to run only after a `create` completes, or allowlist a `delete` intended to run last to clean up secrets that a preceding `create/update` populated. If a front-runner submits the `delete` before the `create`/`update` executes, or races two `update`s in reverse order, the vault's secret state ends up in the owner's non-intended configuration, potentially exposing stale/incorrect secret values to downstream workflow consumption, or wasting/blocking the intended operation (since the replay guard will reject the legitimate resubmission of the same digest once consumed). This mirrors the "keep allowances non-zero" / outstanding-authorization-misuse risk in the original report, applied to Vault's secret lifecycle instead of ERC20 allowances.

### Likelihood Explanation
Exploitation requires the attacker to (a) learn the plaintext bytes of a pending allowlisted request (feasible since the owner's own systems must transmit this request to the gateway, and the on-chain `AllowlistRequest` event only reveals the digest, but any observer with visibility into the owner's off-chain job dispatch, or a compromised/careless intermediary, can obtain it) and (b) submit it to the public gateway HTTP endpoint before the legitimate submitter does. This is a real but non-trivial condition — it requires request content leakage plus a race — placing likelihood as low-to-medium, consistent with the "MEV" classification of the original report.

### Recommendation
Add an explicit ordering/dependency mechanism for allowlisted requests belonging to the same owner — e.g., a per-owner monotonically increasing sequence number stored alongside each `WorkflowRegistryOwnerAllowlistedRequest`, and require `allowListBasedAuth.AuthorizeRequest` to only accept a digest if the owner's previous-in-sequence request has already been consumed (analogous to ordered nonces). Alternatively, bind related batches of allowlisted requests into a single atomic multi-request digest so partial/out-of-order execution is impossible, mirroring the `permitTransferFromWithAdditionalDataERC20`-style mitigation the Tapioca team ultimately adopted for `Pearlmit`.

### Proof of Concept
1. Workflow owner calls `AllowlistRequest(digestA, exp)` then `AllowlistRequest(digestB, exp)` on-chain, intending its automation to submit request A (e.g., `vault.secrets.create`) first and request B (e.g., `vault.secrets.delete` for the same identifier) second, once A's create has been externally confirmed.
2. An attacker who has observed/obtained the plaintext bytes of request B (whose digest equals `digestB`) submits B directly to the public Vault gateway endpoint before the owner's automation submits A.
3. `allowListBasedAuth.AuthorizeRequest` finds `digestB` in `GetAllowlistedRequests()` and authorizes it regardless of whether A has run yet [6](#0-5) ; the delete executes first, and when A's create later attempts to run, the secret manipulated no longer exists in the state the owner expected, or the deferred create silently re-creates a secret intended to have been deleted last — the owner's intended ordering has been violated with no enforcement mechanism to prevent it.

### Citations

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L360-372)
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

**File:** core/capabilities/vault/allow_list_based_auth.go (L113-120)
```go
func (r *allowListBasedAuth) fetchAllowlistedItem(allowListedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, digest [32]byte) *workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	for _, item := range allowListedRequests {
		if item.RequestDigest == digest {
			return &item
		}
	}
	return nil
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
