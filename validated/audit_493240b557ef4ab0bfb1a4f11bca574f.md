Based on the investigation, there is a plausible structural analog to the OpenQ "unbounded loop grief" bug class within the Chainlink Vault capability's allowlist authorization path.

### Title
Unbounded linear scan over on-chain allowlisted requests enables authorization-latency grief attack on Vault - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
The Vault capability authorizes every incoming JSON-RPC request by fetching the entire on-chain allowlisted-requests list and performing an O(n) linear scan to find a matching digest, repeated up to `retryCount+1` times per authorization attempt. Because the size of this list grows with every `AllowlistRequest` call made against the `WorkflowRegistry` contract and entries are only pruned by their (attacker-chosen) expiry timestamp, an actor who can submit allowlist requests can inflate this list arbitrarily, directly increasing the per-request authorization cost for the entire Vault DON — mirroring the OpenQ pattern where any depositor could inflate the deposits array to make the refund loop unbounded.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` calls `findAllowlistedItemWithRetry`, which on each of up to `allowListBasedAuthRetryCount+1` (11) attempts calls `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and then linearly scans the returned slice via `fetchAllowlistedItem` looking for a digest match: [1](#0-0) [2](#0-1) 

The in-memory list that gets scanned is maintained by `workflowRegistry.syncAllowlistedRequests`, which periodically fetches new entries from the contract and only removes entries whose `ExpiryTimestamp` has passed — expiry is a caller-supplied value in the allowlist request itself: [3](#0-2) 

The underlying fetch, `getAllowlistedRequests`, paginates reads from the chain but has no cap on the *total* number of allowlisted requests it will accumulate over time into `w.allowListedRequests`: [4](#0-3) 

Any actor who can call `AllowlistRequest` on the `WorkflowRegistry` contract (this is analogous to "any depositor/funder" in the OpenQ bounty — a routine, largely unprivileged on-chain action gated only by paying gas and possessing a valid, otherwise-arbitrary request digest/expiry pair) can keep growing this list indefinitely by picking a far-future expiry, since nothing in the syncer or contract-fetch path caps the retained set size independent of expiry. Every subsequent Vault JSON-RPC request from any client then pays the cost of scanning this ever-growing list, multiplied by the retry loop, before the request can even be authorized or rejected.

### Impact Explanation
This does not cause fund loss directly, but it degrades the availability/latency of the Vault DON's request-authorization path for all users — every legitimate Vault RPC request incurs an O(n) scan (times up to 11 retry attempts) against a list an attacker fully controls the size of. As the allowlist grows unboundedly, authorization latency for legitimate secrets requests increases without bound, which can push authorization outside acceptable timeouts and effectively deny service for all Vault users, similar in spirit (though not identical in mechanism, since Go memory/CPU cost rather than a hard on-chain gas revert) to how the OpenQ bug denied bounty refunds to all funders.

### Likelihood Explanation
Likelihood is moderate: it requires an actor able to place calls into the `WorkflowRegistry` allowlist mechanism repeatedly with self-chosen long expiries, and requires sustained spam to meaningfully degrade performance since this is an in-memory linear scan (cheap per item) rather than an on-chain gas-capped loop. There's no indication in this codebase of a cap on the number of outstanding (non-expired) allowlist entries or of rate-limiting on `AllowlistRequest` calls at this layer.

### Recommendation
- Cap the number of allowlisted entries retained per owner and/or globally, independent of expiry, and reject/evict oldest entries beyond the cap.
- Replace or supplement the linear `fetchAllowlistedItem` scan with a digest-indexed map (`map[[32]byte]*WorkflowRegistryOwnerAllowlistedRequest`) maintained by the syncer for O(1) lookup.
- Consider bounding the maximum allowed `ExpiryTimestamp` window at allowlist-request time so entries cannot be kept alive indefinitely.

### Proof of Concept
1. Attacker (any address able to call `AllowlistRequest` on `WorkflowRegistry`) repeatedly calls `AllowlistRequest` with distinct arbitrary digests and a far-future `ExpiryTimestamp`.
2. `workflowRegistry.syncAllowlistedRequests` picks these up every tick and appends them to `w.allowListedRequests`, per `core/services/workflows/syncer/v2/workflow_registry.go:780-795`, with no upper bound on total active entries.
3. Every legitimate Vault RPC request thereafter triggers `allowListBasedAuth.findAllowlistedItemWithRetry`, which calls `GetAllowlistedRequests` and performs a full linear scan of the now-inflated list, up to 11 times per request (`core/capabilities/vault/allow_list_based_auth.go:80-108`), increasing per-request authorization latency proportionally to the attacker-controlled list size.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-92)
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-795)
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
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1236-1260)
```go
func (w *workflowRegistry) getAllowlistedRequests(ctx context.Context, contractReader types.ContractReader) ([]workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, *big.Int, *types.Head, error) {
	if contractReader == nil {
		return nil, nil, nil, errors.New("cannot fetch allow listed requests: nil contract reader")
	}
	contractBinding := types.BoundContract{
		Address: w.workflowRegistryAddress,
		Name:    WorkflowRegistryContractName,
	}

	// Read current total allowlisted requests
	var headAtLastRead *types.Head
	var totalAllowlistedRequestsResult *big.Int
	readIdentifier := contractBinding.ReadIdentifier(TotalAllowlistedRequestsMethodName)
	headAtLastRead, err := contractReader.GetLatestValueWithHeadData(
		ctx, readIdentifier, primitives.Unconfirmed, nil, &totalAllowlistedRequestsResult,
	)
	if err != nil {
		return []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}, w.lastSeenAllowlistedRequestsCount, &types.Head{Height: "0"}, errors.New("failed to get latest value with head data. error: " + err.Error())
	}

	if w.lastSeenAllowlistedRequestsCount.Cmp(totalAllowlistedRequestsResult) == 0 {
		return []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}, totalAllowlistedRequestsResult, headAtLastRead, nil
	}

	var newAllowlistedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest
```
