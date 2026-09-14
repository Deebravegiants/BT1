### Title
Unbounded Per-Request Linear Scan Over Growing Allowlist Causes Amplified DoS in Vault Authorization Path - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
Every Vault secrets operation (`create`, `update`, `delete`, `list`) routed through the node-side `GatewayHandler` is authorized via `allowListBasedAuth.AuthorizeRequest`, which repeatedly copies and linearly scans the *entire* on-chain allowlist (`w.allowListedRequests`) for every single request, up to 11 times (`retryCount+1`), and unconditionally builds a formatted debug string for every entry on every pass — regardless of log level. The allowlist is populated by workflow owners calling the public `WorkflowRegistry` contract to allowlist requests, an unprivileged, permissionless action from the node's perspective. As the allowlist grows (which any workflow owner can drive by allowlisting arbitrary numbers of requests), the per-request authorization cost for *every other user's* Vault request grows linearly with it, mirroring the reported bug class of unbounded batch/loop operations over attacker-influenced growing collections reachable from an unprivileged actor.

### Finding Description
`allowListBasedAuth.findAllowlistedItemWithRetry` fetches the full allowlist via `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and, for each of up to `retryCount+1` (11) attempts, builds a formatted string for *every* entry in the returned slice before calling `fetchAllowlistedItem`, which itself does a full linear `for` scan looking for a single digest match: [1](#0-0) 

`GetAllowlistedRequests` on the syncer side allocates and copies the entire in-memory allowlist slice on every call: [2](#0-1) 

The allowlist itself (`w.allowListedRequests`) is populated from on-chain events emitted by the `WorkflowRegistry` contract via `syncAllowlistedRequests`, which appends newly-observed on-chain allowlist entries without pruning anything except already-expired ones: [3](#0-2) 

This authorization path is invoked from `GatewayHandler.HandleGatewayMessage` for every `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList` request received from the gateway (i.e., from any client submitting requests to the vault DON): [4](#0-3) 

There is no cap found on the total number of active allowlisted requests kept in memory; `MaxResultsPerQuery` only governs the on-chain pagination batch size used when *fetching* new entries, not a ceiling on total accumulated entries. Any workflow owner can call the on-chain allowlist function repeatedly (an unprivileged, permissionless action relative to the node) to grow this in-memory list without bound, analogous to the vault's user list in the reported Move issue growing without bound and being fully iterated on every batch operation.

### Impact Explanation
Because `GetAllowlistedRequests`/`fetchAllowlistedItem` are invoked on the hot path of every Vault secrets request from every workflow owner, and the cost (list copy + Sprintf-based string construction of every element + linear scan) scales linearly with the allowlist size and is multiplied by up to 11 retry attempts, an attacker able to allowlist a large number of entries can degrade or effectively deny Vault service (CPU/memory amplification) for all workflow owners interacting with the Vault DON — a cross-user availability impact consistent with the reported bug class, though bounded by Go's lack of a hard "1000 dynamic field" style protocol limit (so it manifests as growing latency/CPU cost rather than a hard transaction failure).

### Likelihood Explanation
Allowlisting a request on the `WorkflowRegistry` contract is a standard, permissionless workflow-owner action (not gated by node-operator privilege), so an attacker controlling many workflow-owner keys, or a single owner submitting many allowlist requests, can grow the list arbitrarily over time with routine transactions. Every subsequent Vault authorization check for any user is affected, making the degradation cumulative and increasingly likely to matter as protocol usage grows — consistent with the original report's framing of "problematic through natural protocol growth."

### Recommendation
1. Replace the linear-scan lookup in `fetchAllowlistedItem` with a map (e.g., `map[[32]byte]WorkflowRegistryOwnerAllowlistedRequest`) keyed by `RequestDigest`, maintained incrementally by `syncAllowlistedRequests`, to make lookups O(1).
2. Avoid unconditionally building the full debug-log string of all allowlisted requests on every authorization attempt; only construct it when debug logging is actually enabled, or omit it entirely.
3. Enforce and monitor a maximum number of active allowlisted requests retained in memory, evicting/pruning aggressively (not just by expiry) and/or rate-limiting how quickly a single owner can add allowlist entries.

### Proof of Concept
Conceptual sequence (concrete PoC would require a running Vault DON + WorkflowRegistry deployment, which is outside static analysis scope):
1. As a workflow owner, repeatedly call the `WorkflowRegistry` contract's allowlist-request function to add a large number (e.g., tens of thousands) of allowlist entries with future expiry timestamps.
2. `workflowRegistry.syncAllowlistedRequests` will ingest all of these into `w.allowListedRequests` in memory on the Vault DON nodes: [5](#0-4) 
3. Any subsequent Vault secrets request (from this or any other owner) triggers `AuthorizeRequest` → `findAllowlistedItemWithRetry`, which on each of up to 11 attempts copies and iterates the now-huge list, building a formatted string per entry: [6](#0-5) 
4. Measure increasing latency/CPU usage of `HandleGatewayMessage` for unrelated users' Vault requests as the allowlist size grows, demonstrating the amplification.

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

**File:** core/capabilities/vault/gw_handler.go (L187-211)
```go
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
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```
