### Title
Unbounded per-owner allowlist growth causes linear-scan DoS on shared Vault authorization path - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
Any workflow owner can permissionlessly call `AllowlistRequest` on the on-chain `WorkflowRegistry` contract to add entries to a single, node-wide list of allowlisted request digests. This list is synced in full into node memory and is linearly scanned, with a multi-attempt retry loop, on **every** incoming Vault request from **every** user, not just the owner who added the entries. This mirrors the Juicebox `distributeReservedTokensOf` bug class: an unprivileged actor's cheap, permissionless write (creating many low-cost array entries) imposes a disproportionate, unbounded cost on other unrelated users who later have to iterate/process that array, without the attacker bearing any of that cost.

### Finding Description
The Vault gateway authorizes user JSON-RPC requests via `allowListBasedAuth.AuthorizeRequest`, which calls `findAllowlistedItemWithRetry`: [1](#0-0) 

This function fetches the **entire** allowlisted-requests list via `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and does a full **O(n) linear scan** (`fetchAllowlistedItem`) to find a matching digest: [2](#0-1) 

If the digest is not found, the code retries up to `allowListBasedAuthRetryCount` (10) times, each time re-fetching and re-scanning the **full list again**, sleeping `allowListBasedAuthRetryInterval` (3s) between attempts — i.e. up to 11 full linear scans and ~30 seconds of held processing per unauthorized/not-yet-visible request: [3](#0-2) 

The underlying list is populated from the `WorkflowRegistry` contract with **no cap** on the number of entries any owner can add — `AllowlistRequest` is a permissionless, per-owner write (as shown in the test helper calling `wfRegC.AllowlistRequest`): [4](#0-3) 

The syncer fetches and retains **all active (non-expired) entries from all owners** in a single in-memory slice, appending new entries onto old ones every sync tick, with no maximum size enforced: [5](#0-4) 

`GetAllowlistedRequests` then returns (and copies) this same unbounded, shared slice to every caller of the authorization path: [6](#0-5) 

The only quantity-related constant in this pipeline, `MaxResultsPerQuery = 1_000`, is merely a pagination page size for fetching from the chain — it does not cap the total number of entries retained in memory or scanned per request: [7](#0-6) 

A test even explicitly exercises "above MaxResultsPerQuery" entries as a supported/expected scenario, confirming there is no hard ceiling on total list size: [8](#0-7) 

### Impact Explanation
Because `AllowlistRequest` is permissionless and cheap for any owner to call repeatedly (bounded only by whatever gas/on-chain cost applies, which is a fixed, small, and attacker-controlled cost unrelated to the list's eventual size), a single low-privilege workflow owner can grow the allowlist to an arbitrarily large size. Every subsequent Vault request from **any other, unrelated user** then pays for:
1. A full copy of that oversized slice (`GetAllowlistedRequests`) on every authorization attempt, and
2. A full O(n) linear scan of that slice, repeated up to 11 times with 3-second sleeps in between if the caller's own digest happens not to be found immediately (e.g. due to normal sync propagation delay), directly and unnecessarily amplifying the per-request cost.

This degrades authorization latency/throughput for the shared Vault gateway/DON handling path for all users — a resource-exhaustion/gas-griefing analog to the Juicebox finding, where cheap attacker-controlled state growth imposes unbounded cost on unrelated, unprivileged callers of a shared function. Because this runs inside the node process (not on-chain gas), the "cost" manifests as CPU time, request latency, and potential request timeouts for legitimate users rather than direct ETH loss, but the underlying root cause (unbounded attacker-controlled array plus per-request linear iteration and retries) is identical in structure to the source finding.

### Likelihood Explanation
Likelihood is moderate to high in the reachable path: `AllowlistRequest` is exposed to any workflow owner without limits on call frequency or total entries per owner, and the syncer/auth code performs no defensive capping, indexing, or size limiting before use. The severity of impact scales with how many owners choose to exploit this and how large the DON's node population/tick cadence make the effective window, but no additional non-trivial privilege is required beyond being a workflow owner (an unprivileged, permissionless role from the platform's perspective, directly analogous to a Juicebox "project owner").

### Recommendation
- Enforce a hard cap on the total number of active allowlisted-request entries retained per owner and/or globally in `workflowRegistry.syncAllowlistedRequests`, rejecting/pruning beyond the cap.
- Replace the linear-scan lookup in `fetchAllowlistedItem` with an indexed map (e.g. `map[[32]byte]*WorkflowRegistryOwnerAllowlistedRequest`) built once per sync tick, turning lookups into O(1).
- Bound or eliminate the multi-attempt retry loop's cost amplification — e.g., short-circuit retries when the requester's owner has no allowlisted entries at all, or cap total scan work per request rather than repeating full scans.
- Consider rate-limiting or requiring bonded/staked cost for `AllowlistRequest` calls proportional to the number of outstanding entries, to disincentivize unbounded list growth by a single owner.

### Proof of Concept
Not independently executable in this ask-only review (no sandbox/chain access), but the code paths above demonstrate the mechanism:
1. An attacker-controlled workflow owner repeatedly calls `WorkflowRegistry.AllowlistRequest` (permissionless, as exercised in `allowlistRequest` test helper) to add a very large number of entries with long expiry timestamps.
2. `workflowRegistry.syncAllowlistedRequests` polls and accumulates all these entries into `w.allowListedRequests` with no size cap.
3. Every unrelated user's Vault request triggers `allowListBasedAuth.AuthorizeRequest` → `findAllowlistedItemWithRetry`, which copies and linearly scans the now-huge slice, and repeats this up to 11 times over ~30 seconds if not immediately found — degrading service for all Vault users on the node, not just the attacker.

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

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-111)
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

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L67-92)
```go
	// Add requests to ensure we go above the MaxResultsPerQuery
	activeAllowlistedRequestsCount := int(MaxResultsPerQuery + 1)
	expiryTimestamp := time.Now().Add(24 * time.Hour)
	for i := range activeAllowlistedRequestsCount {
		createSecretsRequestParams, marshalErr := json.Marshal(vaultcommon.CreateSecretsRequest{
			EncryptedSecrets: []*vaultcommon.EncryptedSecret{
				{
					Id: &vaultcommon.SecretIdentifier{
						Key:       strconv.Itoa(i),
						Namespace: "active",
					},
					EncryptedValue: "encrypted-value",
				},
			},
		})
		require.NoError(t, marshalErr)

		allowlistRequest(t, backendTH, wfRegistryC, allowlistRequestParams{
			Request: jsonrpc.Request[json.RawMessage]{
				Method: vaulttypes.MethodSecretsCreate,
				Params: (*json.RawMessage)(&createSecretsRequestParams),
			},
			Owner:           backendTH.ContractsOwner.From,
			ExpiryTimestamp: expiryTimestamp,
		})
	}
```

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L881-911)
```go
func allowlistRequest(
	t *testing.T,
	th *testutils.EVMBackendTH,
	wfRegC *workflow_registry_wrapper_v2.WorkflowRegistry,
	input allowlistRequestParams,
) {
	t.Helper()
	totalAllowlistedRequestsBefore, err := wfRegC.TotalAllowlistedRequests(&bind.CallOpts{
		From: th.ContractsOwner.From,
	})
	require.NoError(t, err, "failed to get total allowlisted requests")

	requestDigest, err := input.Request.Digest()
	require.NoError(t, err)
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err)

	_, err = wfRegC.AllowlistRequest(
		th.ContractsOwner,
		[32]byte(requestDigestBytes),
		uint32(input.ExpiryTimestamp.Unix()), //nolint:gosec // safe conversion
	)
	require.NoError(t, err, "failed to register allowlisted request")
	th.Backend.Commit()

	totalAllowlistedRequestsAfter, err := wfRegC.TotalAllowlistedRequests(&bind.CallOpts{
		From: th.ContractsOwner.From,
	})
	require.NoError(t, err, "failed to get total allowlisted requests")
	require.Equal(t, totalAllowlistedRequestsBefore.Uint64()+1, totalAllowlistedRequestsAfter.Uint64(), "total allowlisted requests mismatch")
}
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
