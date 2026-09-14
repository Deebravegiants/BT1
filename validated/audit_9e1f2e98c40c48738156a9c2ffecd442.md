### Title
Unbounded linear scan of the entire Vault allowlisted-requests set on every gateway request authorization - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest`, which authorizes every unprivileged JSON-RPC request the Vault gateway forwards to a node, performs a full O(n) linear scan of the entire in-memory allowlisted-requests set on **every** request, and repeats this up to 11 times (with 3s sleeps between attempts) when a digest isn't found yet. The set size `n` grows unbounded because any linked workflow owner can permissionlessly call `AllowlistRequest` on the `WorkflowRegistry` contract to add arbitrarily many entries with future expiries, and nothing in the syncer or auth path caps or paginates this set at authorization time.

### Finding Description
Every Vault gateway request that reaches a node goes through `GatewayHandler.HandleGatewayMessage` → `GatewayVaultRequestProcessor` → `Authorizer.AuthorizeRequest`, which for requests without `req.Auth` set falls back to `allowListBasedAuth.AuthorizeRequest`: [1](#0-0) 

`AuthorizeRequest` calls `findAllowlistedItemWithRetry`, which fetches the *entire* allowlisted-requests slice from the syncer and linearly scans it for a matching digest, retrying up to `allowListBasedAuthRetryCount` (10) times with `allowListBasedAuthRetryInterval` (3s) sleeps if not found: [2](#0-1) 

`WorkflowRegistrySyncer.GetAllowlistedRequests` returns a full copy of the entire tracked slice `w.allowListedRequests` on every call — there is no per-owner or global cap, and no pruning of expired entries is visible in the read path: [3](#0-2) 

The set is populated on-chain via `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)`, which is callable by any linked workflow owner (an unprivileged, non-node-operator actor) with an arbitrary digest and expiry far in the future: [4](#0-3) [5](#0-4) 

Because there is no limit on how many allowlist entries a workflow owner (or a set of colluding owners) can create, and the entire list is scanned (and even stringified for debug logs: `allowedRequestsStrs`) on **every single Vault request from every workflow owner**, the CPU/latency cost of authorizing any request grows linearly with the total number of active allowlist entries network-wide. This is a direct structural analog of the reported Solidity "unbounded operations on active protections enumerable set" bug class: an enumerable set that any unprivileged actor can grow without bound is iterated in full on a hot, per-request code path, degrading (or effectively denying) service for all other tenants of the shared Vault DON.

### Impact Explanation
As the number of active allowlisted requests grows (attacker-controllable via repeated cheap `AllowlistRequest` calls with far-future expiries), the per-request cost of `fetchAllowlistedItem`'s linear scan, the slice copy in `GetAllowlistedRequests`, and the debug-string building in `findAllowlistedItemWithRetry` all grow linearly. Combined with the retry loop (up to 11 scans × up to 3s sleep = ~30s additional latency per unauthorized/delayed-propagation request) and the fact that this occurs on the hot authorization path shared by all workflow owners submitting Vault requests through a given gateway/DON, a single or small set of unprivileged workflow owners can degrade Vault request-processing latency/throughput for every other tenant, potentially amounting to a shared-resource denial of service for the Vault capability.

### Likelihood Explanation
Medium. Triggering this requires an actor to already have a linked workflow owner (via `LinkOwner` with an ownership-proof signature) so it's not fully anonymous, but this is still an unprivileged, non-operator actor within the intended CRE self-service model. The `AllowlistRequest` contract call is cheap and has no observed cap on count or rate, so an owner (or several colluding owners) can grow the set arbitrarily over time with ordinary transactions, no special permissions, and no rate limiting visible in the reviewed code path.

### Recommendation
- Cap the number of active (non-expired) entries the syncer tracks and/or a workflow registry contract-level limit per owner/globally, rejecting `AllowlistRequest` calls beyond the cap.
- Replace the linear `fetchAllowlistedItem` scan with a map/index keyed by request digest (`map[[32]byte]WorkflowRegistryOwnerAllowlistedRequest`) inside `workflowRegistry`, maintained incrementally as entries are added/expired, so lookup is O(1) instead of O(n).
- Prune expired entries eagerly from `w.allowListedRequests` (or the underlying map) rather than only filtering them at use time, so the working set that must be scanned/copied stays proportional to genuinely active entries.
- Avoid building the full `allowedRequestsStrs` debug slice on every retry attempt in the hot path; only build it once, at Debug log level, and gate it behind an `IsDebug()` check.
- Consider bounding/backing off the retry loop's cost independent of set size, and moving to a per-digest lookup API on the syncer (`GetAllowlistedRequestByDigest(digest)`) instead of returning/scanning the entire collection.

### Proof of Concept
1. As a linked workflow owner, repeatedly call `WorkflowRegistry.AllowlistRequest(digest_i, farFutureExpiry)` for many distinct `digest_i` values (e.g., hundreds of thousands), which is a cheap, permissionless, unprivileged operation gated only by owning a linked workflow owner address: [5](#0-4) 
2. Each Vault DON node's `workflowRegistry` syncer will accumulate these into `w.allowListedRequests`, returned in full by `GetAllowlistedRequests` on every call: [3](#0-2) 
3. Any other workflow owner (victim) then submits a normal Vault request (e.g., `vault_secretsCreate`) through the gateway; `allowListBasedAuth.AuthorizeRequest` → `findAllowlistedItemWithRetry` → `fetchAllowlistedItem` must linearly scan the now-huge slice (potentially multiple times across retries) before authorizing or rejecting the request: [2](#0-1) 
4. As the attacker continues growing the set, authorization latency for all Vault requests (including the victim's) increases linearly, degrading throughput/latency for the shared Vault gateway/DON — a denial-of-service condition analogous to the reported unbounded-enumerable-set gas DoS.

### Citations

**File:** core/capabilities/vault/authorizer.go (L121-137)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}

func (a *authorizer) authorizeAllowListBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.allowListBasedAuth == nil {
		err := errors.New("AllowListBasedAuth authorizer is nil")
		a.lggr.Errorw("AllowListBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.allowListBasedAuth.AuthorizeRequest(ctx, req)
}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-120)
```go
func (r *allowListBasedAuth) findAllowlistedItemWithRetry(ctx context.Context, req jsonrpc.Request[json.RawMessage], requestDigest string, requestDigestBytes32 [32]byte) (*workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, []string, error) {
	for attempt := 0; attempt <= r.retryCount; attempt++ {
		allowedRequests := r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)
		allowedRequestsStrs := make([]string, 0, len(allowedRequests))
		for _, rr := range allowedRequests {
			allowedReqStr := fmt.Sprintf("AuthorizedOwner: %s, RequestDigest: %s, ExpiryTimestamp: %d", rr.Owner.Hex(), hex.EncodeToString(rr.RequestDigest[:]), rr.ExpiryTimestamp)
			allowedRequestsStrs = append(allowedRequestsStrs, allowedReqStr)
		}
		r.lggr.Debugw("AllowListBasedAuth loaded allowlisted requests", "method", req.Method, "requestID", req.ID, "attempt", attempt+1, "allowedRequests", allowedRequestsStrs)

		allowlistedRequest := r.fetchAllowlistedItem(allowedRequests, requestDigestBytes32)
		if allowlistedRequest != nil {
			return allowlistedRequest, allowedRequestsStrs, nil
		}
		if attempt == r.retryCount {
			return nil, allowedRequestsStrs, nil
		}

		r.lggr.Debugw("AllowListBasedAuth request digest not yet allowlisted, retrying",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"attempt", attempt+1,
			"maxAttempts", r.retryCount+1,
			"retryInterval", r.retryInterval)
		if err := sleepWithContext(ctx, r.retryInterval); err != nil {
			r.lggr.Debugw("AllowListBasedAuth retry canceled", "method", req.Method, "requestID", req.ID, "error", err)
			return nil, nil, err
		}
	}

	return nil, nil, nil // unreachable: loop always returns
}

func (r *allowListBasedAuth) fetchAllowlistedItem(allowListedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, digest [32]byte) *workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	for _, item := range allowListedRequests {
		if item.RequestDigest == digest {
			return &item
		}
	}
	return nil
}
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1218-1224)
```go
func (w *workflowRegistry) GetAllowlistedRequests(_ context.Context) []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	w.allowListedMu.RLock()
	defer w.allowListedMu.RUnlock()
	allowListedRequests := make([]workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, len(w.allowListedRequests))
	copy(allowListedRequests, w.allowListedRequests)
	return allowListedRequests
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

**File:** system-tests/lib/cre/workflow/secrets.go (L199-211)
```go
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
