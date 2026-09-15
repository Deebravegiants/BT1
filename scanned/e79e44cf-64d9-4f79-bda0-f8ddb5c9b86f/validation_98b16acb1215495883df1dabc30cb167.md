## Finding: Unbounded Vault Allowlist Causes Linear-Scan DoS in the Gateway's Vault Request Authorization Path

### Title
Unbounded on-chain-sourced `allowListedRequests` cache causes O(n) linear-scan / full-slice-copy DoS on every internet-facing Vault gateway request - (File: `core/capabilities/vault/allow_list_based_auth.go`)

### Summary
The Vault gateway's default (non-JWT) authorization mechanism, `allowListBasedAuth`, authorizes every incoming JSON-RPC secrets request by copying and linearly scanning the *entire* in-memory `allowListedRequests` cache maintained by the `WorkflowRegistrySyncer`. This cache grows unbounded (bounded only by on-chain state, not by any client-side cap), and the scan is repeated up to 11 times per request (with 3-second sleeps between retries) whenever the digest isn't (yet) found. As the on-chain allowlist grows, every legitimate unprivileged user request routed through the internet-facing gateway (`core/services/gateway/handlers/vault/handler.go`) incurs increasingly expensive, repeated full-list copies/scans, degrading to a denial of service for the entire Vault gateway — directly analogous to the reported "unbonded `orgHash`" DoS pattern where unbounded state is iterated in reachable, hot-path functions.

### Finding Description
The gateway's `handler.HandleJSONRPCUserMessage` is the internet-facing entry point for all Vault secrets requests (`secrets_create`, `secrets_update`, `secrets_delete`, `secrets_list`) from unprivileged clients: [1](#0-0) 

It calls `h.requestProcessor.ProcessRequest`, which in turn calls `authorizer.AuthorizeRequest` for every request: [2](#0-1) 

When the request has no `Auth` field (the default, backward-compatible path for existing clients), authorization falls through to `allowListBasedAuth`: [3](#0-2) 

`allowListBasedAuth.findAllowlistedItemWithRetry` fetches the *entire* allowlist via `GetAllowlistedRequests` (which allocates a new slice and `copy`s every element) and then performs a full **linear scan** (`fetchAllowlistedItem`) to find a matching digest. If not found, it sleeps and repeats, up to `retryCount` (10) additional times: [4](#0-3) 

The underlying cache, `w.allowListedRequests`, is populated from on-chain data and only pruned by *expiry timestamp* — there is no cap on the number of active (non-expired) entries: [5](#0-4) 

`GetAllowlistedRequests` copies the full slice on every single call: [6](#0-5) 

Since any request digest not present in the current cache (e.g., a not-yet-allowlisted or malicious request) triggers the full retry loop — 11 total attempts, each doing an O(n) copy + O(n) scan, separated by 3-second sleeps — an attacker who can grow the number of active allowlisted requests on-chain (which requires no privileged Chainlink-node role, only on-chain interaction with the permissionless `WorkflowRegistry` contract) can make `n` arbitrarily large. Every subsequent legitimate/unauthorized request handled by the gateway then pays a cost proportional to `n`, and unauthorized/mismatched requests pay `~11n` cost plus up to 33 seconds of blocking latency, tying up gateway request-handling goroutines and causing cascading delays/backpressure for all Vault users.

### Impact Explanation
This directly threatens availability of the Vault gateway, an internet-facing surface shared by all workflow owners:
- Every Vault secrets request (create/update/delete/list) from any unprivileged user pays a cost proportional to the size of the on-chain allowlist.
- Unauthorized or as-yet-unpropagated requests incur up to 11 full copy+scan passes and up to 33 seconds of forced sleep per request, consuming goroutines/CPU on the gateway/node.
- As the allowlist grows (attacker-controllable via on-chain registration, not gated by any node-side cap), CPU and latency costs scale linearly, degrading or halting Vault request processing for all legitimate users — a direct denial-of-service, matching the severity class of the referenced "unbonded array" finding.

### Likelihood Explanation
The authorization code path is reached by every unauthenticated (non-JWT) Vault gateway request, which is the default/legacy path still supported for backward compatibility. Growing the on-chain allowlist requires only interaction with the (permissionless) `WorkflowRegistry` contract, not any privileged Chainlink-node role. No cap exists on the number of active allowlisted entries cached in memory, and the design already anticipates volumes: on-chain reads are paginated in batches of `MaxResultsPerQuery = 1,000`, implying the list is expected to be able to exceed thousands of entries — well beyond what a naive per-request linear scan can handle without impacting latency.

### Recommendation
- Replace the linear list scan with a keyed lookup: `WorkflowRegistrySyncer` should expose (and internally maintain) a `map[[32]byte]WorkflowRegistryOwnerAllowlistedRequest` indexed by `RequestDigest`, updated incrementally instead of full-slice-copy on every `GetAllowlistedRequests` call.
- Avoid copying the entire allowlist on every single authorization call; instead provide a `Lookup(digest)` method that performs a single map/index read under a read lock.
- Consider bounding retry cost independent of allowlist size, and add metrics/alerts on allowlist size growth so an anomalously large allowlist can be flagged operationally.

### Proof of Concept
1. An attacker (or any permissionless account able to interact with the `WorkflowRegistry` contract) repeatedly calls the on-chain allowlist-request function to register a large number (e.g., hundreds of thousands) of long-lived allowlisted requests with unique digests and far-future expiry timestamps.
2. `syncAllowlistedRequests` on each Chainlink node ingests all of these into `w.allowListedRequests`, which now holds a very large, unbounded slice: [7](#0-6) .
3. Any legitimate user sends a normal Vault `secrets_create`/`secrets_list` request to the gateway, hitting `handler.HandleJSONRPCUserMessage` → `ProcessRequest` → `AuthorizeRequest` → `allowListBasedAuth.findAllowlistedItemWithRetry`.
4. For every request whose digest isn't found on the first pass (or any not-yet-allowlisted digest), the node performs up to 11 full copies and linear scans of the now-huge slice, each separated by a 3-second sleep — resulting in tens of seconds of latency and elevated CPU/memory pressure per request: [8](#0-7) .
5. With sustained traffic and a sufficiently large attacker-inflated allowlist, the Vault gateway's request-handling capacity is exhausted, denying service to legitimate workflow owners.

### Citations

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L270-276)
```go
	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
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
