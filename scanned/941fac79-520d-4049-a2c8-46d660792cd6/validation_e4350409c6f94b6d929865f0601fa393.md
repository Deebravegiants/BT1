### Title
Global allowlist authorization for Vault requests uses unbounded O(n) linear scan, allowing griefing/DoS of every Vault request across the DON - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`AllowListBasedAuth.AuthorizeRequest` authorizes every incoming Vault gateway request (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`, etc.) by fetching the **entire, global** list of on-chain allowlisted requests and performing a **linear scan** to find a matching digest. Unlike the LP-token-scoped array in the report, this list is not scoped per requester — it is shared by all Vault DON users, so any actor who can grow it (by having workflows/requests allowlisted on the `WorkflowRegistry` contract) increases the per-request authorization cost for every other user of the same Vault DON.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` calls `findAllowlistedItemWithRetry`, which repeatedly calls `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and then linearly scans the returned slice via `fetchAllowlistedItem`: [1](#0-0) 

`fetchAllowlistedItem` iterates every entry in `allowListedRequests` comparing digests one at a time — an O(n) scan with no early-exit optimization (e.g., no map keyed by digest): [2](#0-1) 

Critically, if a matching digest is not found on the first attempt, the code retries the full scan up to `allowListBasedAuthRetryCount` (10) additional times with a 3-second sleep between attempts, multiplying the cost of a miss by 11x: [3](#0-2) 

The backing list is populated by `workflowRegistry.allowListedRequests`, a single unbounded slice fetched from the on-chain `WorkflowRegistry` contract and shared across **all** owners/workflows served by the DON — it is not scoped or capped per caller: [4](#0-3) [5](#0-4) 

This mirrors the root cause of the reported issue: a data structure that (a) can be inflated by an unprivileged actor's normal, legitimate on-chain actions, and (b) is iterated in full on every subsequent unrelated operation, causing the cost of that operation to scale linearly with attacker-influenced growth. Here, because the allowlist is global rather than per-resource, the blast radius is worse than the original report — every Vault request from every workflow owner served by that DON pays the cost of the bloated list, not just requests touching one specific resource.

### Impact Explanation
As the number of allowlisted requests grows (via legitimate workflow-owner activity, which any workflow owner can generate at scale by requesting many allowlist entries on-chain), the CPU cost and gateway response latency of `AuthorizeRequest` grows linearly for every single Vault request handled by the node, for every user — not just the entity that grew the list. Because a cache miss triggers up to 11 full linear scans with 3-second sleeps between them, a sufficiently large list can push authorization latency well past the gateway's node-side/gateway-side request timeouts (`requestTimeout` in `core/services/gateway/handlers/vault/handler.go`), causing legitimate requests to time out. This is a DoS of the shared Vault DON authorization path, not merely of one victim's resource, which increases both likelihood of triggering and severity of impact relative to the original per-position bug.

### Likelihood Explanation
Likelihood depends on how cheaply/quickly an unprivileged workflow owner can cause many entries to be added to the on-chain allowlist and whether the `WorkflowRegistry` contract enforces any global/per-owner cap on allowlist entries (this contract's enforcement logic is out of scope of what I could verify in this codebase and was not found in the reviewed files). Absent such a cap, any workflow owner requesting a large number of Vault operations to be allowlisted would organically grow this shared list over time, and the linear-scan-with-retries design in `allow_list_based_auth.go` guarantees this growth degrades every future request's authorization latency for the whole DON.

### Recommendation
- Replace the linear scan in `fetchAllowlistedItem` with a `map[[32]byte]workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest` keyed by `RequestDigest`, built once when `GetAllowlistedRequests` refreshes, so lookup is O(1) regardless of list size.
- Evict/prune expired entries (`ExpiryTimestamp` already tracked) from the in-memory list on each sync tick, rather than carrying them forward indefinitely.
- Consider scoping the retry/miss cost: avoid retrying the full 11x scan blindly on every authorization miss — cap total wall-clock retry time independent of list size, and/or short-circuit when the digest owner is not present at all.
- If not already enforced on-chain, consider whether `WorkflowRegistry` should bound allowlist entries per owner/DON to prevent unbounded list growth in the first place.

### Proof of Concept
Not independently reproducible from the indexed code alone — reproducing this would require interacting with the on-chain `WorkflowRegistry` contract (`getActiveAllowlistedRequestsReverse` / `totalAllowlistedRequests`) to determine whether allowlist entry creation is rate-limited or capped per owner. Conceptually:
1. A workflow owner accumulates a large number of allowlisted request digests via normal `WorkflowRegistry` interactions (each valid Vault operation typically registers/expires an allowlist entry).
2. `workflowRegistry.allowListedRequests` (core/services/workflows/syncer/v2/workflow_registry.go:90) grows to N entries.
3. Every subsequent Vault request authorized via `allowListBasedAuth.AuthorizeRequest` (core/capabilities/vault/allow_list_based_auth.go:34) now performs an O(N) scan, multiplied up to 11x on any miss, for **every** user of the DON, degrading or timing out legitimate requests.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L17-23)
```go
const (
	// The workflow registry syncer polls every 12s by default. Keep the
	// retry window comfortably above that so newly allowlisted requests
	// can propagate to every node before auth gives up.
	allowListBasedAuthRetryCount    = 10
	allowListBasedAuthRetryInterval = 3 * time.Second
)
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L60-67)
```go
// WorkflowRegistrySyncer is the public interface of the package.
type WorkflowRegistrySyncer interface {
	services.Service

	// GetAllowlistedRequests returns the latest list of allowlisted requests. This list is fetched periodically
	// from the workflow registry contract.
	GetAllowlistedRequests(ctx context.Context) []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest
}
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L88-98)
```go
	// This value is stored in memory and not persisted to the database.
	lastSeenAllowlistedRequestsCount *big.Int
	allowListedRequests              []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest
	allowListedMu                    sync.RWMutex

	contractReaderFn versioning.ContractReaderFactory

	// contractReader is used exclusively for fetching allowlisted requests from the WorkflowRegistry
	// contract. This data is consumed by Vault DON nodes to authorize incoming vault requests.
	// Workflow metadata is fetched separately via workflowSources (see below).
	contractReader types.ContractReader
```
