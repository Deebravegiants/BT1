### Title
Per-request linear allowlist scan with unbounded retry loop grows with allowlist size, enabling DoS on Vault gateway requests - (File: `core/capabilities/vault/allow_list_based_auth.go`)

### Summary
The External Report's bug class is an unbounded loop whose cost scales with a chain-wide, ever-growing collection (`settleFunding` iterating all markets, each doing an unbounded twap scan), exceeding resource limits as the system grows. The `AYontt/chainlink--024` gateway-facing Vault authorization path (`allowListBasedAuth.AuthorizeRequest` → `findAllowlistedItemWithRetry`) has the same growth-with-activity shape: every unauthenticated request reaching the gateway triggers a full linear scan of the entire in-memory allowlisted-requests slice, repeated up to 10 times with 3-second sleeps between attempts, and this per-request cost grows as more workflows/owners get allowlisted on-chain over time.

### Finding Description
`GatewayHandler.HandleGatewayMessage` [1](#0-0)  calls `requestProcessor.ProcessRequest`, which invokes `Authorizer.AuthorizeRequest` for every incoming Vault request from the gateway (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`) before any authentication succeeds — this is reachable by any unprivileged client that can reach the gateway.

For the allowlist-backed authorizer, `AuthorizeRequest` calls `findAllowlistedItemWithRetry` [2](#0-1) , which on each of up to `allowListBasedAuthRetryCount` (10) attempts:
- calls `GetAllowlistedRequests` to fetch the full in-memory slice,
- builds a debug string for every entry (`allowedRequestsStrs`),
- linearly scans the entire slice via `fetchAllowlistedItem` [3](#0-2) ,
- and, if not found, sleeps `allowListBasedAuthRetryInterval` (3s) before retrying.

The allowlisted-requests slice (`w.allowListedRequests`) is populated by `workflowRegistry.syncAllowlistedRequests`, which appends newly discovered on-chain allowlist entries every tick and only prunes entries once their `ExpiryTimestamp` passes [4](#0-3) . As more workflow owners register requests (a normal, permissionless on-chain action any workflow owner can take), this slice grows without any node-side cap, so the per-authorization-attempt linear scan cost grows correspondingly — directly analogous to `settleFunding`'s per-market loop growing with more markets.

Because a caller who supplies an unregistered/garbage request digest forces the authorizer through the *entire* 10-attempt/30-second retry loop (each attempt rescanning the full, ever-growing list) before failing, this unprivileged-reachable code path has cost that scales both with (a) the number of concurrent bogus requests an attacker sends and (b) the size of the allowlist, which itself grows monotonically over the system's lifetime absent aggressive pruning.

### Impact Explanation
An unprivileged client can hold a goroutine and CPU cycles per bogus/unauthorized request for up to 30 seconds while repeatedly scanning the full allowlist (with debug-string construction for every entry each pass). Sent concurrently at scale, and compounded by the allowlist's unbounded on-chain-driven growth, this degrades the Vault gateway handler's throughput and resource usage for legitimate requests, mirroring the "wide-spread DoS as activity/collection size grows" pattern in the source report. This does not directly leak secrets or bypass authorization by itself, but it is a resource-exhaustion vector on an internet-facing, unauthenticated code path.

### Likelihood Explanation
Moderate. Reaching the vulnerable path requires no privileges — any request routed through the gateway to the Vault handler triggers it prior to authorization succeeding. The magnitude of the issue increases naturally over time as more owners get added to the on-chain allowlist (a permissionless, expected operation), and is amplified by attacker-controlled concurrency and repeated bogus requests.

### Recommendation
- Cap and index the in-memory allowlist (e.g., map by digest) instead of a linear-scan slice so lookup is O(1) regardless of allowlist size.
- Prune expired/stale entries proactively and bound the maximum retained entries.
- Reduce/limit the retry-with-sleep behavior for unauthenticated requests (e.g., fail fast on clearly-invalid digests, or apply per-IP/per-connection concurrency limits before invoking the expensive retry loop) so cost does not scale with attacker-controlled concurrency or allowlist growth.

### Proof of Concept
1. Observe that `GetAllowlistedRequests`/`fetchAllowlistedItem` performs `O(n)` scans, `n` = size of `w.allowListedRequests`, which only grows as on-chain owners call `AllowlistRequest` (see test helper `allowlistRequest`) [5](#0-4) .
2. Send an unauthenticated `MethodSecretsCreate`/`MethodSecretsList` request to the gateway with a digest that never gets allowlisted.
3. `findAllowlistedItemWithRetry` executes 10 full scans of `w.allowListedRequests` with 3s sleeps between each, per request [6](#0-5) .
4. Repeat concurrently with many such requests; per-request cost (goroutine lifetime × scan cost) scales with both attacker concurrency and allowlist size, degrading the handler for legitimate traffic — the same "grows with more activity/entries" DoS shape described in the source report.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-206)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1520)
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
```
