### Title
Unbounded on-chain-controlled allowlist causes O(n) work (with up to 11x retry amplification) on every Vault authorization request - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`AllowListBasedAuth`, the primary authorizer for every Vault gateway request (`vault.secrets.create/list/delete/update`), authorizes a request by pulling the *entire* on-chain allowlist into memory and linearly scanning it, and — worse — unconditionally building a full debug string for every entry, on every single request, and doing so up to `allowListBasedAuthRetryCount+1` (11) times per request. The size of this list is controlled by any account that can self-link as a workflow owner and call the low-privilege `AllowlistRequest` contract method with a long expiry, so an unprivileged actor can grow the list without bound (similar in structure to the reported "blacklisted vector NamedKey" issue: an ever-growing collection that is fully scanned/formatted on every core-functionality call).

### Finding Description
`AllowListBasedAuth.AuthorizeRequest` is invoked for authorizing every incoming Vault gateway JSON-RPC request from clients: [1](#0-0) 

It delegates to `findAllowlistedItemWithRetry`, which loops up to `retryCount+1` (default 11) times. On **every** attempt it: (1) fetches the entire in-memory allowlist via `GetAllowlistedRequests` (which locks a mutex and copies the whole slice), and (2) unconditionally builds a `[]string` of `fmt.Sprintf` formatted strings for **every single entry**, regardless of log level, purely to pass to a `Debugw` call: [2](#0-1) 

It then performs an O(n) linear scan via `fetchAllowlistedItem`: [3](#0-2) 

The backing slice `w.allowListedRequests` is populated by the `workflowRegistry` syncer, which appends every still-unexpired entry read from the on-chain `WorkflowRegistry` contract's `AllowlistRequest`/`GetActiveAllowlistedRequestsReverse` state: [4](#0-3) [5](#0-4) 

Crucially, entries are only pruned when their `ExpiryTimestamp` passes; a caller fully controls the expiry value it submits: [6](#0-5) 

`AllowlistRequest` on the contract is a normal user-facing operation, exposed via `UserAllowlistRequestOp`/`UserAllowlistRequest` changeset, callable by any account (no admin/owner gating beyond standard workflow-owner linking, itself a self-service signature-based operation): [7](#0-6) 

Because expiry is attacker-chosen (e.g., years in the future) and there is no cap observed on the number of entries a single owner (or many self-linked owners) may add, an unprivileged party can grow `allowListedRequests` arbitrarily large at modest, predictable on-chain gas cost. Every subsequent Vault request from *any* user then pays the O(n) cost of copying, string-formatting, and scanning that list — multiplied by up to 11 retry attempts inside a single `AuthorizeRequest` call whenever the digest isn't found (e.g., any invalid/malicious/random request, or any request under network propagation delay).

### Impact Explanation
This directly threatens availability of core Vault functionality (secret create/list/delete/update) for all users of a DON, mirroring the reported bug class: a vector/slice that is fully iterated (and, worse, fully string-formatted) on every core-path call, whose size is influenced by data an unprivileged actor can write. As the allowlist grows (via cheap, repeated on-chain calls with far-future expiries), CPU and allocation cost per Vault request grows linearly and is amplified up to 11x by the retry loop, degrading or effectively denying the Vault gateway handler for the entire DON — a broad availability impact from an unprivileged, low-cost action.

### Likelihood Explanation
Moderate-to-high. Exploitation requires only: (1) linking as a workflow owner (self-service, signature based, no special privilege), and (2) repeatedly calling the public `AllowlistRequest` contract method with a far-future `ExpiryTimestamp`. Both actions are unprivileged, low-cost (bounded by ordinary chain gas), and available to any registered workflow owner. There is no visible per-owner or global cap on outstanding allowlisted requests, and pruning only removes expired entries, so the attack is straightforward to sustain over time.

### Recommendation
- Bound the size of `allowListedRequests` (e.g., per-owner and global caps enforced on-chain and/or filtered client-side), and/or replace the linear vector scan with a map/dictionary keyed by request digest for O(1) lookup, mirroring the audited remediation (index+dictionary pattern) for the original blacklist bug.
- Remove the unconditional `fmt.Sprintf`/slice-building of `allowedRequestsStrs` from the hot authorization path; only construct it when the debug log level is actually enabled, or omit it entirely and log only counts/samples.
- Consider capping/rate-limiting `AllowlistRequest` calls per owner and enforcing a maximum reasonable expiry window on-chain to bound growth of the in-memory list and force natural pruning.
- Reduce retry amplification or short-circuit the retry loop earlier when the request digest clearly cannot be present (e.g., first pass a hashed lookup before falling back to expensive logging).

### Proof of Concept
Conceptual (no live chain access in this analysis):
1. Link ownership for an arbitrary EOA via the standard signature-based `LinkOwner` flow (self-service, unprivileged).
2. Repeatedly call `WorkflowRegistry.AllowlistRequest(requestDigest, farFutureExpiry)` with distinct random digests, growing the on-chain (and therefore node-side `allowListedRequests`) list to a large size (analogous to the original PoC that inflated a blacklist vector to 1230+ entries and observed gas/time blow-up).
3. Observe that `workflowRegistry.syncAllowlistedRequests` (ticker-driven) pulls and retains all unexpired entries node-side.
4. Issue any Vault request (e.g., a `vault.secrets.list` call with a request digest not present in the allowlist, or under normal propagation delay) and observe `AllowListBasedAuth.findAllowlistedItemWithRetry` performing up to 11 full-list scans and full-list `Sprintf` formatting per authorization attempt, causing measurable CPU/latency growth in the Vault gateway handler proportional to allowlist size — the same class of resource-exhaustion regression described in the original report, but reachable via an unprivileged, cheap on-chain write rather than a privileged blacklist operation.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-51)
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
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-93)
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-806)
```go
func (w *workflowRegistry) syncAllowlistedRequests(ctx context.Context) {
	ticker := w.getTicker(defaultTickIntervalForAllowlistedRequests)
	w.lggr.Debug("starting syncAllowlistedRequests")
	for {
		select {
		case <-ctx.Done():
			w.lggr.Debug("shutting down syncAllowlistedRequests, %s", ctx.Err())
			return
		case <-ticker:
			newAllowListedRequests, totalAllowlistedRequests, head, err := w.getAllowlistedRequests(ctx, w.contractReader)
			if err != nil {
				w.lggr.Errorw("failed to call getAllowlistedRequests", "err", err)
				continue
			}
			w.allowListedMu.Lock()
			// Prune expired requests
			activeAllowlistedRequests := []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}
			expiredRequestsCount := 0
			for _, request := range w.allowListedRequests {
				if int64(request.ExpiryTimestamp) > time.Now().Unix() {
					activeAllowlistedRequests = append(activeAllowlistedRequests, request)
				} else {
					expiredRequestsCount++
				}
			}

			// Add new requests
			activeAllowlistedRequests = append(activeAllowlistedRequests, newAllowListedRequests...)
			w.allowListedRequests = activeAllowlistedRequests
			w.lastSeenAllowlistedRequestsCount = totalAllowlistedRequests
			w.lggr.Debugw("synced allowlisted requests",
				"newRequestsNum", len(newAllowListedRequests),
				"expiredRequestsNum", expiredRequestsCount,
				"activeRequestsNum", len(w.allowListedRequests),
				"lastSeenOnchainRequestsNum", w.lastSeenAllowlistedRequestsCount,
				"blockHeight", head.Height,
			)
			w.allowListedMu.Unlock()
		}
	}
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

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L345-387)
```go
type UserAllowlistRequestOpInput struct {
	RequestDigest   [32]byte `json:"requestDigest"`
	ExpiryTimestamp uint32   `json:"expiryTimestamp"`

	ChainSelector uint64                `json:"chainSelector"`
	MCMSConfig    *contracts.MCMSConfig `json:"mcmsConfig,omitempty"`
	Qualifier     string                `json:"qualifier"`
}

type UserAllowlistRequestOpOutput struct {
	Success         bool                      `json:"success"`
	RegistryAddress common.Address            `json:"registryAddress"`
	MCMSOperation   *mcmstypes.BatchOperation `json:"mcmsOperation"`
}

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
