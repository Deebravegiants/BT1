Audit Report

## Title
Unbounded linear scan over attacker-growable on-chain allowlist on every Vault gateway request enables DoS - ([File: core/capabilities/vault/allow_list_based_auth.go])

## Summary
`allowListBasedAuth.AuthorizeRequest` authorizes every incoming vault gateway request by calling `findAllowlistedItemWithRetry`, which fetches the in-memory copy of the on-chain allowlist via `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and performs an O(n) linear scan (`fetchAllowlistedItem`) to find a matching digest, retried up to `r.retryCount+1` (11) times with 3s sleeps between attempts if not found. [1](#0-0)  The allowlist itself is populated by any workflow owner calling `AllowlistRequest` on-chain, with no cap on the number of entries, and only pruned by expiry timestamp during periodic sync. [2](#0-1) 

## Finding Description
`AuthorizeRequest` computes a digest for the incoming request and calls `findAllowlistedItemWithRetry`, which on each attempt fetches the full allowlisted-requests slice and iterates over it twice per attempt: once to build a debug log string (`allowedRequestsStrs`, using `fmt.Sprintf` per entry) and once inside `fetchAllowlistedItem` to linearly search for the matching digest. [3](#0-2) 

The in-memory allowlist (`w.allowListedRequests`) held by `workflowRegistry` (the `WorkflowRegistrySyncer` implementation) is synced from the chain every 5 seconds via `syncAllowlistedRequests`, which appends newly-read entries (fetched in batches of up to `MaxResultsPerQuery` = 1,000 via `getAllowlistedRequests`) to the existing set, pruning only entries whose `ExpiryTimestamp` has passed. [2](#0-1) [4](#0-3)  There is no cap in this Go code on the total number of active (non-expired) entries that can accumulate — an attacker who repeatedly calls the on-chain `AllowlistRequest` with distinct digests and long expiries (as demonstrated unprivileged in the test helper) can grow this list arbitrarily, up to whatever bound the on-chain contract itself imposes. [5](#0-4) 

Because every single vault gateway request triggers this full-list scan (and debug-string rebuild) regardless of which owner or digest is being authorized, an attacker inflating the list size increases the CPU cost of every other user's authorization, and holding the `allowListedMu` read-lock during scans of `GetAllowlistedRequests` compounds contention as the list grows. [6](#0-5) 

However, I was unable to confirm two things critical to a valid, in-scope finding via static analysis of this codebase:
1. **Whether the on-chain `WorkflowRegistry.AllowlistRequest` Solidity function itself enforces any per-owner cap, rate limit, or fee** that would bound attacker growth of the list — the Solidity source for this contract is not present/indexed in this repository (only the Go binding/wrapper and deployment/test helpers are visible), so I cannot verify whether unbounded growth is actually permitted on-chain.
2. **Whether the resulting Go-side linear scan cost, even at large list sizes, is realistically capable of causing meaningful service degradation** — Go slice iteration over tens of thousands of small structs is inexpensive (sub-millisecond to low-millisecond range even at very large N), unlike the original `MAX_DELEGATES` EVM gas-limit analog where unbounded on-chain iteration causes a hard, permanent transaction-revert failure mode. The claim itself concedes this uncertainty ("exact growth threshold needed to cause meaningful service degradation... was not verified").

This second point is significant: the original `MAX_DELEGATES` bug class produces a hard failure (transactions permanently revert due to EVM gas limits), which is a qualitatively different and more severe impact than an in-memory Go slice scan whose cost scales linearly but remains cheap per-entry. Without concrete benchmarking or a demonstrated on-chain growth-cost asymmetry (e.g., showing the attacker's cost of adding N entries is trivial relative to the victim-side cost of scanning them), this reads as a theoretical algorithmic inefficiency rather than a demonstrated DoS.

## Impact Explanation
The claimed impact (degraded/denied service to legitimate vault users) is a plausible impact category if realized, but the report does not establish that the linear-scan overhead reaches a magnitude capable of causing practical service degradation, nor that the on-chain `AllowlistRequest` function lacks bounds/costs that would make large-scale growth impractical for an attacker. Without contract-level rate-limiting analysis or a benchmark/PoC demonstrating actual latency degradation at a realistic list size, the severity claimed (High) is not substantiated.

## Likelihood Explanation
The report itself acknowledges likelihood is Low-Medium and that the precise growth threshold needed for meaningful degradation was not verified, which is consistent with what I found: no cap enforcement is visible in the Go code, but the actual severity depends on on-chain contract behavior not present in this codebase's indexed files, and the per-request scan cost in Go is unlikely to be as devastating as the EVM gas-limit failure mode of the analog bug it is being compared to.

## Recommendation
- Index the allowlist by request digest (map keyed by digest) in `workflowRegistry` rather than storing/scanning a flat slice, to make lookups O(1) regardless of list size.
- Avoid building the full `allowedRequestsStrs` debug slice on every retry attempt (`allow_list_based_auth.go:82-86`) in production; gate it behind a debug-log-enabled check.
- Verify and, if necessary, add on-chain limits (per-owner cap, rate limiting, or fee) on `WorkflowRegistry.AllowlistRequest` to bound growth of the allowlist.

## Proof of Concept
Not reproduced with concrete performance numbers. To validate, an actual benchmark would be needed: populate `workflowRegistry.allowListedRequests` with a large number (e.g., 100k+) of entries via a test double, then measure `findAllowlistedItemWithRetry`/`fetchAllowlistedItem` latency per call, and separately confirm via the on-chain `WorkflowRegistry` contract source (not available in this index) whether `AllowlistRequest` permits unbounded growth by an unprivileged caller at negligible gas cost.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-119)
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
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L55-57)
```go
	// MaxResultsPerQuery defines the maximum number of results that can be queried in a single request.
	// The default value of 1,000 was chosen based on expected system performance and typical use cases.
	MaxResultsPerQuery = int64(1_000)
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-805)
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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1527)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")

	framework.L.Info().Msgf("Allowlisting request digest at contract %s, for owner: %s, digestHexStr: %s", wfRegistryContract.Address().Hex(), owner, requestDigest)
	allowedList, err := wfRegistryContract.GetAllowlistedRequests(&bind.CallOpts{}, big.NewInt(0), big.NewInt(100))
	require.NoError(t, err, "failed to validate allowlisted request")
	for _, req := range allowedList {
		if req.RequestDigest == reqDigestBytes {
			framework.L.Info().Msgf("Request digest found in allowlist")
		}
		framework.L.Info().Msgf("Allowlisted request digestHexStr: %s, owner: %s, expiry: %d", hex.EncodeToString(req.RequestDigest[:]), req.Owner.Hex(), req.ExpiryTimestamp)
	}
```
