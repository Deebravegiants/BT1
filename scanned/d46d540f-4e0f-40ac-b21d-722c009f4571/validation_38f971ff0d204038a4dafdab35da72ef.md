### Title
Unbounded growth of the in-memory allowlisted-requests list causes linear-scan DoS in Vault request authorization - ([File: core/services/workflows/syncer/v2/workflow_registry.go])

### Summary
The Vault DON's request-authorization path relies on an in-memory list, `workflowRegistry.allowListedRequests`, that is populated from on-chain `AllowlistedRequest` entries and is only pruned based on each entry's own `ExpiryTimestamp`. Any workflow owner can add entries to this list (via the `allowlistRequest`-style contract calls consumed by `getAllowlistedRequests`), and since pruning only removes entries whose owner-chosen expiry has passed, an owner can keep the list growing indefinitely by supplying many entries with distant expiry timestamps. This list is then linearly scanned for every incoming Vault request in `allow_list_based_auth.go`, directly mirroring the reported bug class: an attacker-growable list that is iterated in a critical path, eventually causing out-of-gas/DoS-style resource exhaustion.

### Finding Description
`syncAllowlistedRequests` periodically fetches newly allowlisted requests and merges them into `w.allowListedRequests`, pruning only entries whose `ExpiryTimestamp` has already elapsed: [1](#0-0) 

Because the expiry timestamp is chosen by the caller when the on-chain request is created, and there is no visible enforcement of a maximum active-entries cap per owner or globally in this Go-side logic, an owner (or many owners) can continuously submit requests with far-future expiry timestamps. This causes `w.allowListedRequests` to grow without bound over time, analogous to `HoldefiSettings.marketsList` growing without bound because `removeMarket` never truly shrinks the list.

The growing list is then consumed on the authorization hot path. `AuthorizeRequest`/`findAllowlistedItemWithRetry` fetches the entire list and performs a **linear scan** (`fetchAllowlistedItem`) for every single incoming request, with retries: [2](#0-1) 

As the list grows, the cost of `fetchAllowlistedItem`, and the cost of building the debug log string (`allowedRequestsStrs`) on every attempt, grows linearly (and with the retry loop, effectively O(retryCount × listSize)) per request. This authorization function runs for every unprivileged client request destined for the Vault capability, so unbounded list growth degrades or eventually denies request processing for all users, not just the attacker.

The syncer also fetches allowlisted requests from the contract in a paginated loop bounded by `MaxResultsPerQuery` per round, which mitigates the "endless single-call loop" pattern from the original report, but does **not** bound the total size of `w.allowListedRequests` retained in memory or the corresponding per-request linear scan.

### Impact Explanation
This is a denial-of-service condition against the Vault DON's request authorization path, reachable by any actor able to submit allowlist requests on-chain (an unprivileged, non-operator role relative to node operation). As the allowlist grows, CPU cost per incoming Vault request authorization increases linearly, degrading throughput and potentially causing legitimate requests to time out (mirrors the "clearing debts" DoS scenario in the original report, where growth of an unbounded list degrades or blocks legitimate operations for all users).

### Likelihood Explanation
Likelihood is moderate: exploitation requires an actor to be able to repeatedly submit allowlist entries with long expiry timestamps, incurring on-chain gas costs. Because I could not access the Solidity `WorkflowRegistry` contract source in this repo (it is referenced only via the generated Go bindings `workflow_registry_wrapper_v2`), I could not verify whether the contract itself enforces a maximum number of active allowlisted requests per owner or in aggregate. If such a cap exists on-chain, the practical growth is bounded and the severity of this analog is much lower; if no such cap exists, the growth is effectively unbounded, limited only by attacker gas budget.

### Recommendation
- Enforce a maximum number of concurrently active allowlisted requests (globally and/or per owner) both on-chain (in the `WorkflowRegistry` contract, out of scope here) and defensively in `workflowRegistry.syncAllowlistedRequests`, rejecting/dropping oldest or lowest-priority entries beyond the cap.
- Replace the O(n) linear scan in `fetchAllowlistedItem` with an indexed lookup (e.g., a `map[[32]byte]*WorkflowRegistryOwnerAllowlistedRequest` keyed by request digest) maintained alongside pruning, so authorization cost does not scale with total registry size.
- Avoid building the full `allowedRequestsStrs` debug slice on every authorization attempt in production paths; gate it behind a debug/verbose flag or compute lazily only on failure.

### Proof of Concept
Conceptual (on-chain interaction not verifiable from this repo alone):
1. As a workflow owner, repeatedly call the on-chain `allowlistRequest`-equivalent function, each time supplying a distinct request digest and an `ExpiryTimestamp` far in the future.
2. Observe `syncAllowlistedRequests` in `workflow_registry.go` continuously appending these entries to `w.allowListedRequests` on each tick, with `expiredRequestsCount` remaining 0 for these entries (see log line "synced allowlisted requests" at [3](#0-2) ).
3. As `len(w.allowListedRequests)` grows over many iterations, measure increasing latency of `allowListBasedAuth.AuthorizeRequest`/`findAllowlistedItemWithRetry` for unrelated legitimate Vault requests, due to the linear scan in `fetchAllowlistedItem`.

Note: because the on-chain `WorkflowRegistry` contract source (and any caps it may enforce) is not present in this Go repository, this PoC is based on the Go-side consumption/authorization logic only, and the actual exploitability depends on on-chain contract constraints I was unable to inspect.

### Citations

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
