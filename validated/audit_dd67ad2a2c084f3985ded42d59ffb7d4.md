### Title
Unbounded on-chain allowlist growth causes linear-scan DoS in Vault gateway request authorization - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
Any address can permissionlessly call `AllowlistRequest` on the WorkflowRegistry contract to add an entry to the on-chain allowlist, with no cap on the number of entries a single owner can register. The Vault DON's `allowListBasedAuth.AuthorizeRequest` path performs a linear scan (`fetchAllowlistedItem`) over the *entire* in-memory allowlist on every single incoming Vault JSON-RPC request (secrets create/update/delete/list), and this scan is repeated up to `retryCount+1` times per request. Because the list is unbounded and attacker-growable, this mirrors the Sherlock finding's bug class: an unprivileged actor inflating an array that a critical hot-path function must fully iterate.

### Finding Description
`AllowlistRequest(requestDigest, expiryTimestamp)` is exposed as a normal user-callable contract function [1](#0-0) , invoked with no apparent per-owner or global cap in the deployment tooling [2](#0-1) . Any address paying gas can call this repeatedly with distinct digests and far-future expiry timestamps to grow the on-chain allowlist without bound.

The Vault DON's `workflowRegistry.syncAllowlistedRequests` periodically pulls all *active* (non-expired) entries into an in-memory slice `w.allowListedRequests`, pruning only entries whose `ExpiryTimestamp` has passed [3](#0-2) . An attacker choosing a far-future expiry keeps their spam entries "active" indefinitely, so the array only grows.

On the hot path, every incoming Vault gateway request is authorized via `allowListBasedAuth.AuthorizeRequest` → `findAllowlistedItemWithRetry` → `fetchAllowlistedItem`, which does an O(n) linear scan over the full allowlist, once per retry attempt [4](#0-3) . This authorization path is reached directly from the internet-facing gateway handler for every `secrets.create`, `secrets.update`, `secrets.delete`, and `secrets.list` request [5](#0-4)  and [6](#0-5) .

Additionally, `findAllowlistedItemWithRetry` builds a full debug string representation of the entire allowlist (`allowedRequestsStrs`) on every attempt regardless of log level [7](#0-6) , compounding the CPU/allocation cost per request as the list grows.

### Impact Explanation
As the allowlist grows unbounded, every legitimate Vault request (from any workflow owner) incurs increasing CPU and memory overhead during authorization, since the scan and string-building work scale linearly with the total number of allowlisted entries system-wide, not just the requester's own entries. A sufficiently motivated attacker who registers a very large number of far-future-expiry entries can degrade or stall the Vault DON's request-authorization throughput for all tenants, since this scan sits directly in the critical path for every secrets create/update/delete/list request reaching the gateway. This is a shared-resource DoS analogous to the original report's "unbounded array iterated on a hot path preventing critical function execution," though the consequence here is node-level performance degradation/service disruption rather than an EVM out-of-gas revert.

### Likelihood Explanation
Likelihood is moderate: the attacker needs only to be a normal, unprivileged address able to submit transactions to the WorkflowRegistry contract and pay gas per `AllowlistRequest` call — no special role or node access is required. The batched retrieval (`MaxResultsPerQuery = 1000`) bounds each contract read but not the eventual in-memory total, and pruning only removes entries whose the attacker-chosen expiry has already passed.

### Recommendation
- Enforce an on-chain or off-chain cap on the number of *active* allowlisted requests per owner (and/or globally) in `AllowlistRequest`.
- Replace the linear `fetchAllowlistedItem` scan with a map/hash-indexed lookup (e.g., keyed by `RequestDigest`) so authorization cost is O(1) regardless of allowlist size.
- Avoid building the full `allowedRequestsStrs` debug slice unconditionally; only construct it when debug logging is actually enabled.
- Consider bounding total tracked entries in `syncAllowlistedRequests`/`w.allowListedRequests` with a hard ceiling and eviction/alerting when exceeded.

### Proof of Concept
1. Attacker address (no special privileges) repeatedly calls `WorkflowRegistry.AllowlistRequest(digest_i, farFutureExpiry)` for i = 1..N with large N (e.g., hundreds of thousands), each call being a cheap, permissionless transaction [8](#0-7) .
2. The Vault DON's `syncAllowlistedRequests` loop pulls these into `w.allowListedRequests`, and since expiry is far in the future, none are pruned, so the slice grows to size N [9](#0-8) .
3. Any legitimate user now sends a normal `secrets.list`/`secrets.create` request through the gateway; the gateway handler calls `ProcessRequest` → `AuthorizeRequest` → `findAllowlistedItemWithRetry`, which linearly scans all N entries (and rebuilds an N-element debug string slice) on every attempt [10](#0-9) .
4. As N grows, authorization latency/CPU cost per request grows linearly for all Vault users, degrading the shared Vault DON gateway service.

### Citations

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
