Found: `allowListBasedAuth.findAllowlistedItemWithRetry` in the Vault gateway path does an **unbounded linear scan over the entire on-chain allowlist for every single incoming vault request**, and any unprivileged caller can add entries to that allowlist by calling `AllowlistRequest` on the `WorkflowRegistry` contract (as shown in `system-tests/tests/smoke/cre/vault_don_test_helpers.go:1510-1527`). This mirrors the `MAX_DELEGATES` bug class: an unbounded/attacker-growable list is walked on the hot authentication path of every unprivileged request, so an attacker can inflate the list to degrade or deny service for legitimate requests.

### Title
Unbounded linear scan over attacker-growable on-chain allowlist on every Vault gateway request enables DoS - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest` authorizes every incoming vault gateway request by fetching the full list of allowlisted requests from the `WorkflowRegistrySyncer` and performing an O(n) linear scan (`fetchAllowlistedItem`) to find a matching digest, retried up to 10 times with 3s sleeps between attempts if not found. Any unprivileged owner can call `AllowlistRequest` on the on-chain `WorkflowRegistry` contract to add entries to this list, without bound, growing `n` arbitrarily.

### Finding Description
`AuthorizeRequest` calls `findAllowlistedItemWithRetry`, which on every attempt fetches `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and loops over all entries in `fetchAllowlistedItem` to find a matching digest: [1](#0-0) 

This is invoked from `AuthorizeRequest` on every single vault request that reaches this authorizer: [2](#0-1) 

The list being scanned is populated on-chain via `AllowlistRequest`, callable by any workflow owner, and readable/enumerable off-chain, as exercised in the test helper: [3](#0-2) 

Because there is no cap on the number of allowlist entries a single owner (or many owners) can create, and each vault request authorization walks the *entire* list (not scoped to the caller's owner) up to 11 times (`retryCount+1`) with `fmt.Sprintf` string-building for every entry on every attempt for logging (`allowedRequestsStrs`), the CPU/latency cost of authorizing any legitimate request grows linearly with the total number of allowlisted requests across the whole system. This is directly analogous to the `MAX_DELEGATES` bug: an unbounded, attacker-controllable list is walked on a hot path that gates a victim's ability to complete an otherwise legitimate, authorized operation.

### Impact Explanation
Impact is High: an unprivileged actor (any address able to call the on-chain `AllowlistRequest`) can inflate the allowlist to a very large size. Since every vault request authorization — regardless of caller — walks the full list (and rebuilds a full debug string of every entry per retry attempt), this can significantly increase authorization latency/CPU for all legitimate vault users, potentially causing request timeouts, degraded throughput, or effective denial of service for the whole vault node/gateway.

### Likelihood Explanation
Likelihood is Low-Medium: requires the attacker to spend gas repeatedly calling `AllowlistRequest`, and the exact growth threshold needed to cause meaningful service degradation in Go code (versus the strict EVM gas-limit failure mode in the original finding) was not verified in this codebase — I could not confirm hard performance numbers, only that the algorithm is O(n) with no upper bound enforced in `allow_list_based_auth.go`. This differs somewhat from the original finding's precise gas-cap failure mode, so treat the likelihood/impact severity as a plausible analog rather than a confirmed reproduction.

### Recommendation
- Index the allowlist by request digest (e.g., a map keyed by digest) inside `WorkflowRegistrySyncer` rather than exposing/scanning a flat slice, so lookups are O(1).
- Enforce a maximum number of outstanding allowlisted requests per owner (and/or globally) either on-chain in `WorkflowRegistry.AllowlistRequest` or by pruning expired entries proactively in the syncer.
- Avoid building the full `allowedRequestsStrs` debug slice on every retry attempt in production paths; gate it behind a debug-log-enabled check.

### Proof of Concept
Not independently reproduced against a live environment; based on static code analysis: repeatedly call the `WorkflowRegistry.AllowlistRequest` contract method (unprivileged, as shown in the test helper) to add a large number of allowlist entries, then observe `allowListBasedAuth.fetchAllowlistedItem`'s per-request linear scan cost/latency scale with the number of entries for unrelated legitimate vault requests.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-62)
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
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
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
