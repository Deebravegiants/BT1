### Title
DOS via unbounded global allowlist scan in Vault gateway request authorization - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest` authorizes every Vault JSON-RPC request routed through the gateway by linearly scanning the entire, globally-shared `allowListedRequests` slice maintained by the `WorkflowRegistrySyncer`. Because any workflow owner can grow this shared list on-chain (via `AllowlistRequest`), an unprivileged actor can inflate the list size, degrading/blocking authorization for all other users' requests — the same "unbounded iteration over an attacker-influenced, ever-growing collection reached from every unprivileged request" root cause identified in the referenced `Quest.claim`/`getOwnedTokenIdsOfQuest` finding.

### Finding Description
`AuthorizeRequest` (`core/capabilities/vault/allow_list_based_auth.go:34`) is invoked for every incoming Vault request from the gateway (an unprivileged, internet-facing entry point). It calls `findAllowlistedItemWithRetry`, which fetches `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and performs a full linear scan (`fetchAllowlistedItem`) over the returned slice to look for a matching digest: [1](#0-0) 

This scan happens up to `allowListBasedAuthRetryCount + 1` (11) times per single request, with a 3-second sleep between attempts, meaning a single authorization call can perform up to 11 full linear passes over the list: [2](#0-1) 

The underlying list (`w.allowListedRequests`) is a single global, in-memory slice populated on a ticker by `syncAllowlistedRequests`, which fetches new on-chain allowlist entries and appends them to the existing (pruned) list: [3](#0-2) 

This list is not scoped per requester or per digest — it aggregates every allowlisted request from every workflow owner across the whole registry, and is shared by the `allowListBasedAuth` instance used to authorize requests from *any* client.

The structural analog to the reported bug class is direct: just as `RabbitHoleReceipt.getOwnedTokenIdsOfQuest` iterates over an attacker-influenced, unbounded token set on every `claim()` call, `fetchAllowlistedItem`/`findAllowlistedItemWithRetry` iterates over an attacker-influenced, unbounded allowlist set on every Vault request authorization — except here the cost is paid by *every other user's request*, not just the party who grew the collection, because the collection is global rather than per-caller.

### Impact Explanation
Because `AllowlistRequest` on the workflow registry contract can be called cheaply and repeatedly by any workflow owner (an unprivileged actor from the node's perspective — no special role is required to register a workflow and allowlist requests for it), an attacker can flood the on-chain allowlist with a very large number of entries. Each new entry is synced into the in-memory `allowListedRequests` slice and never removed until expiry. Every subsequent Vault request from *any* user — not just the attacker — then pays the cost of scanning this bloated, shared list, up to 11 times per request. At sufficient scale this degrades gateway/node authorization throughput and latency for the entire DON, amounting to a availability/DOS impact on request processing (a form of resource-exhaustion analogous to the referenced report's block-gas-limit DOS, but here manifesting as CPU/latency degradation shared across all callers rather than a hard revert).

### Likelihood Explanation
Likelihood is limited by two factors that were not fully verifiable from the available index: (1) whether `AllowlistRequest` on the on-chain workflow registry enforces any rate limit, cap, or fee that would make mass allowlisting economically or practically expensive, and (2) whether `getAllowlistedRequests` paginates or otherwise bounds the amount fetched/retained in memory. Without confirming these on-chain/contract-side controls, the practical exploitability (how large the list can realistically grow, and how much scan cost that translates to) cannot be fully proven. If the registry allows cheap, high-volume allowlisting by any owner, likelihood is Medium; if strict per-owner limits or fees exist on-chain, likelihood is Low.

### Recommendation
- Index the in-memory allowlist by digest (e.g., `map[[32]byte]WorkflowRegistryOwnerAllowlistedRequest`) instead of scanning a slice, turning lookup from O(N) into O(1) per attempt.
- Bound the number of active allowlist entries retained per owner and/or globally, pruning aggressively and rejecting sync of excess entries.
- Consider scoping the lookup to the request's declared owner (already known before digest match) so a single caller's authorization cost only scales with that owner's own entries, mirroring the recommended fix of letting each caller only pay for its own claimable set.

### Proof of Concept
Not independently reproducible from the indexed code alone — verifying the concrete DOS threshold requires the on-chain `WorkflowRegistryOwnerAllowlistedRequest`/`AllowlistRequest` contract logic (rate limits/fees) and the pagination behavior of `getAllowlistedRequests`, neither of which is present in the indexed Go core files. Conceptually: (1) attacker calls `AllowlistRequest` on the workflow registry contract N times with distinct digests for their own workflow owner address; (2) `syncAllowlistedRequests` appends all N entries into the shared `w.allowListedRequests` slice; (3) every subsequent `AuthorizeRequest` call for any user's Vault request now performs up to 11 O(N) scans via `findAllowlistedItemWithRetry`/`fetchAllowlistedItem`, increasing authorization latency for the whole DON as N grows.

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

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-95)
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
