### Title
Unbounded linear scan over the on-chain allowlist causes O(n) authorization cost per Vault request, enabling DoS by any workflow owner - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
Every incoming Vault DON JSON-RPC request that is authorized via the allowlist path calls `AuthorizeRequest`, which performs a full linear scan (`fetchAllowlistedItem`) over the entire in-memory `allowedRequests` slice, retried up to `retryCount+1` times per request. This slice mirrors the on-chain `WorkflowRegistry` allowlist and is only pruned by expiry timestamp, not by size. Because adding an entry to the allowlist (`AllowlistRequest`) is a permissionless action available to any workflow owner, an unprivileged actor can keep the list large by continuously registering many not-yet-expired allowlist entries, directly increasing the CPU cost of authorizing every legitimate request handled by every Vault DON node.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` digests the incoming request and calls `findAllowlistedItemWithRetry`, which repeatedly (up to `r.retryCount+1` times) fetches the full allowlist via `workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and scans it linearly with `fetchAllowlistedItem`: [1](#0-0) 

The backing list, `w.allowListedRequests`, is maintained by `workflowRegistry.syncAllowlistedRequests`, which only removes entries once their `ExpiryTimestamp` has passed — it never bounds the total size of the list: [2](#0-1) 

`GetAllowlistedRequests` simply returns a full copy of this unbounded slice on every call: [3](#0-2) 

`AuthorizeRequest` is invoked for every incoming Vault gateway request that lacks a JWT auth token (the default/back-compat path), via `authorizer.authorizeAllowListBasedAuth`, which is itself called for every JSON-RPC user request the Vault gateway handler processes: [4](#0-3) [5](#0-4) 

Adding entries to the allowlist (`AllowlistRequest`) is exercised in the test helper against the on-chain `WorkflowRegistry` contract, with no apparent additional privilege check beyond being a workflow owner/caller of the contract: [6](#0-5) 

This mirrors the reported vulnerability class: an unbounded array is linearly scanned to find a specific element, and the array's growth is attacker-influenced, so the per-request cost of a security-critical operation (authorization) scales with attacker-controlled state rather than being bounded.

### Impact Explanation
Any party capable of calling `AllowlistRequest` on the `WorkflowRegistry` contract (which appears open to workflow owners generally, not restricted to node operators) can inflate the size of `w.allowListedRequests` by submitting many distinct allowlist entries with a future expiry. Since every Vault DON node independently syncs and scans this full list for every incoming non-JWT request (multiplied by the retry loop), this increases the CPU/latency cost of authorizing *all* legitimate vault requests processed by the DON — including from unrelated, honest users — potentially degrading availability of the Vault capability across the DON. This is a resource-exhaustion/availability risk rather than a direct fund-loss or secret-disclosure bug, but it directly affects the internet-facing gateway's request-authorization path for an unprivileged, permissionless actor.

### Likelihood Explanation
Medium. Exploitation requires only the ability to submit `AllowlistRequest` transactions repeatedly (paying gas), which is a normal, apparently permissionless workflow-owner action, and does not require compromising the gateway, a node, or any privileged role. The severity of the resulting slowdown depends on how large the list can realistically grow before entries expire (default TTLs used in tests were 1 hour) and how the retry loop (`retryCount`) amplifies cost; without an explicit cap on the allowlist size the scan cost grows unboundedly with attacker-submitted volume within the expiry window.

### Recommendation
- Replace the linear scan in `fetchAllowlistedItem` with a map/index keyed by `RequestDigest` (or by owner+digest) so lookups are O(1) regardless of allowlist size.
- Introduce and enforce a maximum size (or per-owner rate limit) on the number of concurrently active allowlisted requests tracked in memory, evicting or rejecting excess entries rather than allowing unbounded growth until natural expiry.
- Consider capping/limiting the retry loop's total work (e.g., avoid re-scanning the full list on every retry attempt when the underlying data hasn't changed).

### Proof of Concept
1. An attacker with a valid workflow-owner key repeatedly calls `WorkflowRegistry.AllowlistRequest(digest_i, futureExpiry)` for many distinct `digest_i` values, each with an expiry far enough in the future to avoid pruning by `syncAllowlistedRequests`.
2. Each Vault DON node's `workflowRegistry.syncAllowlistedRequests` ticker pulls and retains all of these entries in `w.allowListedRequests` (see `getAllowlistedRequests`/`syncAllowlistedRequests`), growing the in-memory slice.
3. Every subsequent legitimate Vault request through `core/services/gateway/handlers/vault/handler.go`'s `HandleJSONRPCUserMessage` → `GatewayVaultRequestProcessor.ProcessRequest` → `authorizer.AuthorizeRequest` → `allowListBasedAuth.AuthorizeRequest` now performs a full O(n) scan of the inflated list (`fetchAllowlistedItem`), repeated up to `retryCount+1` times, increasing per-request authorization latency/CPU for all Vault DON traffic as `n` grows.

### Citations

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

**File:** core/capabilities/vault/authorizer.go (L121-137)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}

func (a *authorizer) authorizeAllowListBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.allowListBasedAuth == nil {
		err := errors.New("AllowListBasedAuth authorizer is nil")
		a.lggr.Errorw("AllowListBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.allowListBasedAuth.AuthorizeRequest(ctx, req)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1518)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")

```
