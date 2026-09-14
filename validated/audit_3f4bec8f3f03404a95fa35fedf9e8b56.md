### Title
Front-runnable replay-guard digest lets an unprivileged caller griefing-DoS a legitimate Vault gateway request - (File: `core/capabilities/vault/authorizer.go`, `core/capabilities/vault/request_replay_guard.go`)

### Summary
The Vault gateway authorization pipeline authorizes a request by matching an on-chain, publicly-readable allowlisted "request digest," then immediately consumes that same digest in a single-use `RequestReplayGuard`. Because the digest is derived only from public request content (method + params, not from any secret held by the workflow owner), any unprivileged client who can read the on-chain allowlist entry can construct and submit a JSON-RPC request with the identical digest through the public gateway before the legitimate workflow owner's request arrives, permanently consuming that allowlist slot for the guard's lifetime (until `ExpiryTimestamp`). This mirrors the reported bug class: a fixed, publicly-computable "amount" (here, digest) that only ever needs to appear once, and any outsider can front-run and consume it to grief the legitimate actor's call.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `requestDigest := req.Digest()` from the raw request and checks it against the on-chain `WorkflowRegistryOwnerAllowlistedRequest` entries fetched via `workflowRegistrySyncer.GetAllowlistedRequests` [1](#0-0) . If a matching, non-expired digest is found, it returns an `AuthResult` carrying that same digest string [2](#0-1) .

The shared `authorizer.AuthorizeRequest` wraps this call and immediately records the digest in a process-wide `RequestReplayGuard`, rejecting any second use of the same digest with `ErrRequestAlreadySeen` until it expires [3](#0-2) [4](#0-3) .

Because the allowlist entry (`Owner`, `RequestDigest`, `ExpiryTimestamp`) is stored on-chain in the Workflow Registry and readable by anyone (e.g. via `UserAllowlistRequestOp`/the registry's public state) [5](#0-4) , and the digest is a deterministic hash of the request's public JSON-RPC method/params rather than something requiring the owner's private key or a per-call secret, an unprivileged attacker who observes the allowlisted digest (and can reconstruct the exact request payload it corresponds to, since the digest is computed the same way client-side) can submit that same request to the public gateway first. The `GatewayVaultRequestProcessor`/`GatewayHandler` pipeline documented at the top of `gateway_vault_request_processor.go` shows `AuthorizeRequest` runs on raw, unauthenticated request bytes before any owner-specific mutation, i.e., authorization is purely digest-based and reachable by any caller hitting the gateway endpoint [6](#0-5) .

Once the attacker's copy is authorized and its digest recorded by `RequestReplayGuard.CheckAndRecord`, the legitimate owner's subsequent (identical) request will fail with `ErrRequestAlreadySeen` — "request was already authorized previously" — for the remaining lifetime of the allowlist entry, exactly analogous to the Stakehouse bug where an attacker consumes the single allowed "slot" (12 ETH cap / one-time digest) ahead of the legitimate actor, causing the legitimate transaction to revert/fail.

### Impact Explanation
This is a denial-of-service / griefing vector against an unprivileged-reachable authenticated flow: a workflow owner's legitimate, pre-approved secret create/update/delete/list request can be permanently blocked (until on-chain expiry) by any third party who front-runs the digest through the public gateway, without needing the owner's credentials. This does not directly leak secrets or funds, but it denies service and can be used to grief specific workflow owners' Vault operations reliably and repeatedly (an attacker can pre-emptively "burn" digests as soon as new allowlist entries are observed on-chain).

### Likelihood Explanation
Likelihood depends on: (1) the digest being computable purely from public/observable data (method + params content that mirrors what the owner intends to send, which itself must match the on-chain allowlisted digest exactly since the on-chain registration presumably records a hash of the same content) and (2) attacker being able to submit arbitrary JSON-RPC requests through the gateway's public endpoint unauthenticated. Both conditions appear structurally true from the code inspected, but full confirmation of exactly how the on-chain `RequestDigest` is derived (i.e., whether it's solely a hash of public request fields, or whether it embeds anything the attacker cannot reconstruct) could not be fully verified from the indexed code — the `req.Digest()` implementation itself was not found in the indexed files.

### Recommendation
Do not let an unprivileged caller consume the replay-guard slot before the intended owner. Options: (a) bind replay-guard consumption to an authenticated owner-specific channel (e.g., require request signing so the digest cannot be replayed by a party other than the workflow owner), or (b) make the on-chain allowlist entry single-use but resolvable only in favor of the actual owner's session/connection, or (c) allow the replay guard to be owner-scoped rather than digest-scoped, so a duplicate digest submitted by a non-owner does not consume the intended owner's authorization slot.

### Proof of Concept
Conceptual PoC (not fully verified against `req.Digest()` internals, which were not available in the index):
1. Workflow owner registers an allowlisted request on-chain via `UserAllowlistRequestOp`, producing a public `RequestDigest` value readable by anyone monitoring the Workflow Registry contract [5](#0-4) .
2. An attacker observes the on-chain event/state and reconstructs a JSON-RPC request whose `req.Digest()` matches the allowlisted `RequestDigest`.
3. Attacker submits this crafted request to the gateway's public Vault endpoint before the legitimate owner does.
4. `allowListBasedAuth.AuthorizeRequest` finds the matching digest, authorizes it, and `authorizer.AuthorizeRequest` records it in `RequestReplayGuard` [7](#0-6) .
5. When the legitimate owner submits the same (intended) request, `CheckAndRecord` returns `ErrRequestAlreadySeen`, and the request is rejected until the allowlist entry's `ExpiryTimestamp` passes [4](#0-3) .

**Uncertainty**: I could not locate the implementation of `jsonrpc.Request.Digest()` in the indexed codebase (it likely lives in the external `chainlink-common` module), so I cannot fully confirm whether the digest is derivable purely from public data without the owner's private input. This should be verified directly (e.g., via a Devin session with full repo/dependency access) before treating this as a confirmed exploitable finding.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-62)
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
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-76)
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

**File:** deployment/cre/workflow_registry/v2/changeset/user_workflow_registry.go (L716-736)
```go
// UserAllowlistRequest allows a user to request allowlist status
type UserAllowlistRequest struct{}

type UserAllowlistRequestInput struct {
	ExpiryTimestamp uint32 `json:"expiryTimestamp"`
	RequestDigest   string `json:"requestDigest"`

	ChainSelector             uint64                   `json:"chainSelector"`             // Chain Selector
	MCMSConfig                *crecontracts.MCMSConfig `json:"mcmsConfig,omitempty"`      // MCMS configuration
	WorkflowRegistryQualifier string                   `json:"workflowRegistryQualifier"` // Qualifier to identify the specific workflow registry
}

func (u UserAllowlistRequest) VerifyPreconditions(e cldf.Environment, config UserAllowlistRequestInput) error {
	if config.ExpiryTimestamp == 0 {
		return errors.New("expiry timestamp cannot be zero")
	}
	if len(config.RequestDigest) == 0 {
		return errors.New("request digest cannot be empty")
	}
	return nil
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-34)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```
