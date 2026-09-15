## Title
Vault DON allowlist authorization is O(n) per request with no cap on allowlisted-request count, allowing an unbounded-allowlist DoS - (File: `core/capabilities/vault/allow_list_based_auth.go`)

### Summary
The Vault DON's `AllowListBasedAuth.AuthorizeRequest` path performs a full linear scan (and a full slice copy plus unconditional string formatting) over the entire in-memory allowlist for **every single incoming Vault request**, and that allowlist is populated by `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` on-chain calls that any linked workflow owner (an unprivileged, non-admin actor) can invoke an unbounded number of times. There is no cap on the number of allowlist entries fetched, cached, or scanned. This mirrors the reported bug class: an attacker-controllable, unbounded collection that is iterated on every privileged operation, eventually causing denial of service for all users of the affected subsystem.

### Finding Description
`allowListBasedAuth.findAllowlistedItemWithRetry` calls `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and then, **unconditionally** (not gated behind a log-level check), builds a `[]string` by `fmt.Sprintf`-ing every entry, before doing a further O(n) linear scan via `fetchAllowlistedItem`: [1](#0-0) 

`fetchAllowlistedItem` itself is a plain linear scan: [2](#0-1) 

`GetAllowlistedRequests` returns a fresh copy of the *entire* in-memory allowlist on every call: [3](#0-2) 

This allowlist is populated purely by syncing on-chain state and only prunes expired entries; there is no maximum size enforced anywhere in the syncing loop: [4](#0-3) 

Crucially, adding entries to this allowlist is a permissionless, per-owner action exposed via `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)`, callable by any linked (non-admin) workflow owner with no batch/count limit visible in the Go wrapper/tooling: [5](#0-4) 

Every Vault gateway request (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) is routed through this authorization path in `GatewayHandler.HandleGatewayMessage` → `GatewayVaultRequestProcessor.ProcessRequest` → `authorizeAndStamp` → `AuthorizeRequest`: [6](#0-5) [7](#0-6) 

When a digest is not found (e.g., a slow-to-propagate legitimate request, or any request from a different/unallowlisted caller), the retry loop repeats the full O(n) copy + O(n) string-format + O(n) scan up to `allowListBasedAuthRetryCount+1` (11) times, sleeping 3s between attempts: [8](#0-7) 

### Impact Explanation
Because the allowlist has no size cap and is populated by any linked (unprivileged, non-operator) workflow owner via unlimited on-chain `AllowlistRequest` calls, a malicious owner can grow the shared, node-local allowlist arbitrarily large. Every subsequent Vault request from **any** user then pays the full O(n) cost (slice copy, unconditional string construction of every entry, and linear digest scan) on every one of up to 11 retry attempts. As the allowlist grows, this directly increases CPU, memory allocation, and latency for every Vault secret operation (create/update/delete/list) processed by every Vault DON node (since each node independently maintains and scans its own copy of the same on-chain-derived allowlist). This can degrade or deny legitimate Vault operations network-wide — the same class of impact as the original `_sendFees()` DoS blocking `withdraw()`/`destroy()`, but here it can block secret create/update/delete/list operations for all Vault users.

### Likelihood Explanation
Likelihood is limited by two factors: (1) adding entries costs on-chain gas for the attacker via `AllowlistRequest`, and (2) the attacker must be a linked workflow owner rather than a fully anonymous actor. However, since this action is otherwise unprivileged (no admin/DON approval required) and the code performs the expensive operations unconditionally (the string-formatting for logs happens regardless of log level, and the linear scan happens on every retry), a moderately funded attacker can degrade the shared authorization path for all Vault users at a cost proportional only to gas, with no protocol-level limit preventing it.

### Recommendation
- Enforce a maximum number of allowlisted requests (globally and/or per-owner) that will be synced/cached in `workflowRegistry.allowListedRequests`, and reject/drop or rate-limit new entries beyond a sane cap.
- Replace the linear scan in `fetchAllowlistedItem` with an indexed lookup (e.g., a `map[[32]byte]...]` keyed by digest) to avoid O(n) per-request cost.
- Guard the `allowedRequestsStrs` string-construction loop in `findAllowlistedItemWithRetry` behind an actual debug-log-level check so it isn't unconditionally executed on every request/retry.
- Consider avoiding a full slice copy in `GetAllowlistedRequests` on every authorization call; expose a read-only view or a map snapshot instead.

### Proof of Concept
1. A workflow owner links their address to the `WorkflowRegistry` (a low-barrier, unprivileged action).
2. The owner repeatedly calls `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` on-chain with many distinct random digests and far-future expiry timestamps, with no limit enforced by the contract wrapper/tooling shown in `deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go`.
3. `workflowRegistry.syncAllowlistedRequests` periodically ingests all of these into `w.allowListedRequests` with no cap, as shown in `core/services/workflows/syncer/v2/workflow_registry.go`.
4. Any subsequent Vault request handled by `GatewayHandler.HandleGatewayMessage` triggers `AllowListBasedAuth.AuthorizeRequest`, which now must copy, string-format, and linearly scan the bloated allowlist (up to 11 times per unauthorized/slow request), increasing latency and resource consumption for every Vault DON node handling every user's secret operations.

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

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L360-387)
```go
var UserAllowlistRequestOp = operations.NewOperation(
	"user-allowlist-request-op",
	semver.MustParse("1.0.0"),
	"User Allowlist Request in WorkflowRegistry V2",
	func(b operations.Bundle, deps WorkflowRegistryOpDeps, input UserAllowlistRequestOpInput) (UserAllowlistRequestOpOutput, error) {
		// Execute the transaction using the strategy
		operation, _, err := deps.Strategy.Apply(func(opts *bind.TransactOpts) (*types.Transaction, error) {
			tx, err := deps.Registry.AllowlistRequest(opts, input.RequestDigest, input.ExpiryTimestamp)
			if err != nil {
				return nil, fmt.Errorf("failed to call AllowlistRequest: %w", err)
			}
			return tx, nil
		})
		if err != nil {
			return UserAllowlistRequestOpOutput{}, fmt.Errorf("failed to execute AllowlistRequest: %w", err)
		}
		if operation != nil {
			deps.Env.Logger.Infof("Created MCMS proposal for AllowlistRequest on chain %d", input.ChainSelector)
		} else {
			deps.Env.Logger.Infof("Successfully user allowlisted request on chain %d", input.ChainSelector)
		}
		return UserAllowlistRequestOpOutput{
			Success:         true,
			MCMSOperation:   operation,
			RegistryAddress: deps.Registry.Address(),
		}, nil
	},
)
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
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
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-276)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```
