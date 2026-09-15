Audit Report

## Title
Unbounded Growth of the Vault Allowlist Causes Linear-Scan DoS on Every Authorization Request - ([File: core/capabilities/vault/allow_list_based_auth.go])

## Summary
`allowListBasedAuth.AuthorizeRequest` authorizes every incoming Vault gateway JSON-RPC request by calling `findAllowlistedItemWithRetry`, which fetches the entire in-memory allowlisted-requests slice (`GetAllowlistedRequests`, which deep-copies it) and performs a full linear scan (`fetchAllowlistedItem`) plus per-entry debug-string formatting, retried up to 11 times with 3-second sleeps if not found. [1](#0-0)  The backing list `w.allowListedRequests` is appended to indefinitely by `syncAllowlistedRequests` based on active (non-expired) entries returned from the `WorkflowRegistry` contract, with no cap enforced in the syncer. [2](#0-1) 

## Finding Description
The code matches the claim as described: `AuthorizeRequest` is the entry point for every Vault gateway request and delegates to the retry-and-scan path. [3](#0-2)  `GetAllowlistedRequests` copies the full slice under a read lock on every call. [4](#0-3)  `syncAllowlistedRequests` prunes only expired entries and otherwise accumulates active ones without any global or per-owner cap, unlike `Workflows.Limits.Global`/`PerOwner` which explicitly cap workflow counts at 200. [5](#0-4) 

However, I was unable to verify the on-chain `WorkflowRegistry.sol` contract's `AllowlistRequest` implementation in this index — no `.sol` source for `WorkflowRegistry` was found, only Go-generated wrapper bindings and test/changeset code that calls `AllowlistRequest`. Based on the test helper `allowlistRequest` in `core/services/workflows/syncer/v2/workflow_syncer_v2_test.go:881-911`, calling `AllowlistRequest` requires the caller to be `th.ContractsOwner`, i.e., an address that has gone through `LinkOwner`/`UpdateAllowedSigners` — this is a linked/authenticated workflow-owner action, not an anonymous unprivileged call. This somewhat weakens (but does not eliminate) the "unprivileged" framing in the claim, since a linked owner is a real, gated on-chain role requiring proof-of-ownership signatures to obtain, not something any arbitrary internet client can do without first establishing an owner link.

Regardless of that nuance, the core mechanism is real: there is no cap on the number of allowlisted requests a linked owner (or many linked owners collectively) can create, and every one of those entries is scanned in full, on every single incoming Vault request, up to 11 times with 3-second sleeps between attempts if a match isn't found — a real algorithmic cost amplification affecting all clients' request-authorization latency, not just the party growing the list.

## Impact Explanation
This is a genuine availability/performance concern for the Vault DON's authorization hot path: `O(n)` slice copy + linear scan + string formatting per attempt, times up to 11 attempts, for every incoming request. As `n` grows, the per-request authorization cost increases for all Vault clients, not just the one causing growth. This matches an availability-degradation class of bug on a component reachable by (linked-owner-authorized) requests, though it is not a full compromise of confidentiality, authentication bypass, or fund movement — it's a resource-exhaustion/performance-degradation issue.

## Likelihood Explanation
The precondition is non-trivial: an attacker must first become a linked workflow owner (requires a valid ownership proof and signature verified on-chain via `LinkOwner`), then repeatedly call `AllowlistRequest` with unique digests and far-future expiries. This is more restrictive than "any unprivileged client," but it is still an action available to any external party willing to link an owner address (which appears to be a normal, low-barrier onboarding step for legitimate workflow developers, not an admin/node-operator privilege). Given no rate limit or cap exists either in the syncer or (as far as verifiable from this index) on-chain, this remains a realistic and repeatable growth vector, and the resulting cost is paid by all requests through `AuthorizeRequest`.

## Recommendation
Introduce an explicit upper bound on the number of allowlisted requests (global and/or per-owner), analogous to `Workflows.Limits.Global`/`PerOwner`, enforced in the syncer before appending to `w.allowListedRequests`, and ideally on-chain in the `WorkflowRegistry` contract's `AllowlistRequest` function as well. Replace the linear scan in `fetchAllowlistedItem` with a map keyed by digest for O(1) lookup, and avoid deep-copying the full list and building debug strings for every entry on every authorization attempt (defer stringification to only the failure path, and only when debug logging is actually enabled).

## Proof of Concept
1. Link a workflow-owner address via the `WorkflowRegistry` contract's `LinkOwner` flow (requires a valid ownership proof signature). [6](#0-5) 
2. As that linked owner, repeatedly call `AllowlistRequest(requestDigest, expiryTimestamp)` with unique digests and far-future expiries, with no cap enforced by the syncer's `syncAllowlistedRequests`. [7](#0-6) 
3. Observe `w.allowListedRequests` grow unboundedly across syncer ticks.
4. Issue Vault JSON-RPC requests and measure `AuthorizeRequest` latency growth as a function of list size; a Go benchmark exercising `findAllowlistedItemWithRetry` with `GetAllowlistedRequests` backed by lists of increasing size (e.g., 10, 10k, 100k entries) would directly demonstrate the linear-time degradation described. [1](#0-0)

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

**File:** core/config/docs/core.toml (L590-595)
```text
[Workflows]
[Workflows.Limits]
# Global is the maximum number of workflows that can be registered globally.
Global = 200 # Default
# PerOwner is the maximum number of workflows that can be registered per owner.
PerOwner = 200 # Default
```

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L702-726)
```go
// Links owner account to Workflow Registry contract
func updateAuthorizedAddressV2(
	t *testing.T,
	th *testutils.EVMBackendTH,
	wfRegC *workflow_registry_wrapper_v2.WorkflowRegistry,
	ownerAddress common.Address,
	donFamily string,
) {
	t.Helper()

	// First, allow signer
	_, err := wfRegC.UpdateAllowedSigners(th.ContractsOwner, []common.Address{ownerAddress}, true)
	require.NoError(t, err)

	th.Backend.Commit()
	th.Backend.Commit()
	th.Backend.Commit()

	// Double check that signer has been allowed
	isAllowed, err := wfRegC.IsAllowedSigner(&bind.CallOpts{
		From: th.ContractsOwner.From,
	}, ownerAddress)
	require.NoError(t, err)
	require.True(t, isAllowed)

```
