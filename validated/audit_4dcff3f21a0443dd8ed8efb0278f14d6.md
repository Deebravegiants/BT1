### Title
Unbounded, un-deduplicated growth of the Vault gateway's in-memory allowlist cache causes linear-scan authorization cost to increase without bound - ([File: core/services/workflows/syncer/v2/workflow_registry.go])

### Summary
`workflowRegistry.syncAllowlistedRequests` periodically merges newly-observed on-chain `AllowlistRequest` entries into the in-memory `w.allowListedRequests` slice used by the Vault gateway's `AllowListBasedAuth` to authorize every incoming, unprivileged-client vault request. The merge only prunes *expired* entries; it never checks whether an incoming entry (same `RequestDigest`/owner) already exists in the active set before appending. This mirrors the reported `ACOToken` bug class: a value that should be validated/deduplicated before being appended to an array is instead unconditionally appended, and that array is then iterated on every subsequent "hot path" operation (there, `_exerciseOwners`; here, `AuthorizeRequest`'s linear scan), causing gas/CPU cost to grow proportionally to the (unnecessarily inflated) array size.

### Finding Description
`syncAllowlistedRequests` builds the new active set as follows: [1](#0-0) 

```go
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
```

There is no digest-based deduplication against the already-active entries before the append, unlike the ACO fix which requires the minted amount to be non-zero before it's recorded and the account is added to `_collateralOwners`. Every request re-observed from `getActiveAllowlistedRequestsReverse` on subsequent ticks (or any repeated/duplicate on-chain allowlisting for the same digest before it expires) is appended again, growing the slice unbounded.

This slice is consumed on the hot path of every single Vault gateway request from an unprivileged client, via a plain linear scan with no early exit optimization beyond first match: [2](#0-1) 

```go
func (r *allowListBasedAuth) findAllowlistedItemWithRetry(...) (...) {
    for attempt := 0; attempt <= r.retryCount; attempt++ {
        allowedRequests := r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)
        ...
        allowlistedRequest := r.fetchAllowlistedItem(allowedRequests, requestDigestBytes32)
        ...
    }
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

Just as the ACO bug allowed a zero-token mint to still pass the `>0`-implied check and be recorded in `_collateralOwners` (an array iterated by `_exerciseOwners`), this code allows entries to be appended to `allowListedRequests` without any validation that they are new/unique, and that array is scanned on every unauthenticated/unprivileged-client authorization attempt reaching the gateway (`AuthorizeRequest` → `authorizeAllowListBasedAuth`, called from the internet-facing `GatewayVaultRequestProcessor`).

### Impact Explanation
As the allowlist cache grows unbounded due to duplicate/repeated entries never being deduplicated, every call to `AuthorizeRequest` for every incoming vault request (a path directly reachable by any unprivileged client hitting the gateway) becomes progressively more expensive, since `fetchAllowlistedItem` is O(n) over the accumulated slice and is executed inside a retry loop (`allowListBasedAuthRetryCount = 10`, each iteration re-fetching and re-scanning the whole slice) for every request that doesn't immediately match. This degrades gateway node performance/latency for legitimate users over time and increases memory consumption, matching the "freezing of this function" / gas-griefing impact class described in the original finding, translated to CPU/latency griefing for the gateway authorization hot path.

### Likelihood Explanation
The likelihood depends on how frequently the on-chain `WorkflowRegistry` contract emits duplicate/re-observed `AllowlistRequest` events for the same digest before expiry, and whether the on-chain contract itself already prevents duplicate submissions per digest. I was not able to locate or inspect the on-chain `AllowlistRequest`/`getActiveAllowlistedRequestsReverse` contract logic in this codebase to confirm whether duplicate submissions are rejected there. If the contract permits re-submission of the same digest (e.g., to refresh/extend expiry) or if syncer ticks can observe overlapping windows producing repeat entries, this in-memory client-side code has no defense-in-depth deduplication, unlike the recommended ACO fix of validating before appending.

### Recommendation
Before appending `newAllowListedRequests` in `syncAllowlistedRequests`, deduplicate against `activeAllowlistedRequests` (and against duplicates within `newAllowListedRequests` itself) by `RequestDigest`, keeping only the most recent/latest-expiry entry per digest. This keeps `w.allowListedRequests` clean, bounds its size to the number of distinct outstanding digests, and prevents the per-request linear scan in `fetchAllowlistedItem` from degrading under repeated/duplicate on-chain events — directly mirroring the ACO fix of validating the minted amount before recording state that is later iterated.

### Proof of Concept
Not verified end-to-end because the on-chain contract logic controlling `AllowlistRequest`/`getActiveAllowlistedRequestsReverse` was not available for inspection in this codebase (index does not include the Solidity contract or its exact duplicate-submission semantics). Conceptually: if a workflow owner (or any account permitted to call `AllowlistRequest`) submits the same request digest multiple times before its expiry, or if the syncer's polling window causes the same on-chain entry to be re-returned by `getActiveAllowlistedRequestsReverse` across ticks without the contract-side count strictly excluding already-returned entries, each occurrence is unconditionally appended to `w.allowListedRequests` in `syncAllowlistedRequests` (workflow_registry.go:792-794), inflating the slice scanned by every future `AuthorizeRequest` call in `allow_list_based_auth.go:113-120`. A Devin session with full repository/contract access would be needed to confirm the exact on-chain duplicate-submission behavior and construct a concrete reproduction.

### Citations

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L780-795)
```go
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
