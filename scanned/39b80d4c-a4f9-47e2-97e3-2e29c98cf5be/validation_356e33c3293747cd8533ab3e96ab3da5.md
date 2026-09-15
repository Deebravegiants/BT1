### Title
Unbounded Growth of the Vault Allowlist Causes Linear-Scan DoS on Every Authorization Request - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
The Vault DON's request-authorization path (`allowListBasedAuth.AuthorizeRequest`) performs a full linear scan of the entire on-chain allowlisted-requests list for every single incoming, unprivileged client request, and this scan can be retried up to 11 times with 3-second sleeps between attempts. The size of this list is controlled by workflow owners calling `AllowlistRequest` on the `WorkflowRegistry` contract, and unlike other bounded resources in the codebase (e.g. `Workflows.Limits.Global`/`PerOwner` capped at 200), there is no upper bound on the number of allowlisted requests that can accumulate. This is the same bug class as the external report: an attacker-influenced, unbounded collection is iterated in full on every hot-path call that serves unprivileged requests.

### Finding Description
`AuthorizeRequest` is the entry point that authorizes every incoming Vault gateway JSON-RPC request from any client: [1](#0-0) 

It delegates to `findAllowlistedItemWithRetry`, which — for every single incoming request — calls `GetAllowlistedRequests`, builds a debug string for every entry, and then linearly scans the entire slice via `fetchAllowlistedItem`, retrying up to `allowListBasedAuthRetryCount` (10) additional times with `allowListBasedAuthRetryInterval` (3s) sleeps if the digest is not (yet) found: [2](#0-1) 

`GetAllowlistedRequests` itself copies the *entire* in-memory slice on every call: [3](#0-2) 

The backing list `w.allowListedRequests` is grown by `syncAllowlistedRequests`, which appends every active (non-expired) entry fetched from the `WorkflowRegistry` contract's `AllowlistRequest` calls, with no cap on total count: [4](#0-3) 

`AllowlistRequest` on the contract can be called by any linked workflow owner with only an expiry timestamp and a digest as constraints — no maximum count is enforced, either on-chain or off-chain: [5](#0-4) 

Compare this to the `Workflows.Limits` config, which explicitly caps `Global` and `PerOwner` workflow counts at 200 — no equivalent cap exists for allowlisted requests: [6](#0-5) 

This mirrors the reported bug class exactly: `BalanceSheetV2` bounded bond counts via `maxBonds` but left collateral asset counts unbounded, causing unbounded iteration in `getHypotheticalAccountLiquidity()`. Here, workflow counts are bounded but the allowlisted-request list is not, causing unbounded iteration in the Vault's per-request authorization hot path.

### Impact Explanation
Every unauthenticated/unprivileged Vault gateway request triggers `O(n)` work (slice copy + linear scan + string formatting for every entry) up to 11 times. As the list grows (via legitimate or adversarial repeated calls to `AllowlistRequest`, which is not gated by any global/per-owner quota), the per-request cost of the Vault DON's authorization path grows unboundedly. This can degrade to the point of making the Vault DON's request handling effectively unusable for all clients (a shared, unbounded resource degrading a hot path reachable by any request), which is a direct availability impact on the internet-facing Vault gateway authorization mechanism.

### Likelihood Explanation
Reaching this requires only the ability to call `AllowlistRequest` on the `WorkflowRegistry` contract repeatedly (a linked workflow owner action, not a node-operator/privileged action) enough times to grow the list; there is no rate limit or cap preventing this, and the resulting cost is paid by every unrelated incoming Vault request via `AuthorizeRequest`.

### Recommendation
Introduce an explicit upper bound on the number of allowlisted requests (globally and/or per owner), analogous to `Workflows.Limits.Global`/`PerOwner`, enforced either on-chain in `AllowlistRequest` or in the syncer before appending to `w.allowListedRequests`. Additionally, replace the linear scan in `fetchAllowlistedItem` with a map/index keyed by digest to avoid `O(n)` cost per authorization attempt, and avoid deep-copying the full list plus building debug strings for every entry on every request.

### Proof of Concept
1. As a linked workflow owner, repeatedly call `AllowlistRequest(requestDigest, expiryTimestamp)` on the `WorkflowRegistry` contract with far-future expiry timestamps and unique digests, with no upper bound enforced by the contract or the syncer (`core/services/workflows/syncer/v2/workflow_registry.go:766-803`).
2. The Vault DON's `syncAllowlistedRequests` ticker will pull and retain all of these active entries in `w.allowListedRequests` indefinitely (until expiry).
3. Any client sends a Vault JSON-RPC request; `AuthorizeRequest` → `findAllowlistedItemWithRetry` → `GetAllowlistedRequests` (full slice copy) → `fetchAllowlistedItem` (full linear scan) executes, and if the digest isn't found immediately, this repeats 11 times with 3s sleeps (`core/capabilities/vault/allow_list_based_auth.go:79-111`), multiplying the cost of the already-unbounded scan across all concurrent unauthorized requests.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-51)
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-803)
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

**File:** core/config/docs/core.toml (L590-595)
```text
[Workflows]
[Workflows.Limits]
# Global is the maximum number of workflows that can be registered globally.
Global = 200 # Default
# PerOwner is the maximum number of workflows that can be registered per owner.
PerOwner = 200 # Default
```
