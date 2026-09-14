This is a strong analog: the allowlist-based auth for Vault requests never marks a consumed digest as "used," permitting replay of a single-use allowlisted request until the on-chain `ExpiryTimestamp` elapses.

### Title
Allowlisted Vault requests can be replayed multiple times before expiry because `AuthorizeRequest` never consumes/decrements the allowlist entry - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest` [1](#0-0)  authorizes a Vault JSON-RPC request purely by matching its digest against the in-memory `allowListedRequests` slice fetched from `workflowRegistry.GetAllowlistedRequests` [2](#0-1) , checking only that it exists and has not expired. It never removes, marks-as-used, or decrements the matched entry, so the same allowlisted digest authorizes every request sent before the on-chain `ExpiryTimestamp`.

### Finding Description
The on-chain `WorkflowRegistry.AllowlistRequest` mechanism registers a `RequestDigest` with an `ExpiryTimestamp` [3](#0-2) , which is intended as a scoped, presumably single-use, authorization for one specific request. The gateway/vault node polls this state periodically via `syncAllowlistedRequests`, which only prunes entries by time-based expiry, never by consumption: [4](#0-3) 

`AuthorizeRequest` looks up the matching entry with `fetchAllowlistedItem` and, if found and unexpired, returns success — with no call back into the syncer or any local state to invalidate/consume the entry: [5](#0-4) [6](#0-5) 

This is the analog of the Cork Protocol bug: a "locked" resource (here, a single-use allowlisted authorization instead of locked `Ra`) is consumed by an unprivileged action (redeeming early / issuing a request) without the corresponding accounting/state decrement (`decLocked` in Cork; "consume/remove the allowlist entry" here). As a result, an unprivileged client holding (or intercepting/replaying) one valid allowlisted request digest can invoke it repeatedly for the full expiry window, rather than the single authorized use the allowlist entry represents.

### Impact Explanation
Any request matching an allowlisted digest can be resent an unbounded number of times until `ExpiryTimestamp`, since `AuthorizeRequest` performs no consumption/removal. If the allowlist model is meant to authorize a single vault operation (e.g., one secret write/read/create), this allows replay/duplication of privileged vault operations (secret creation, mutation, or retrieval) using a single authorization grant — a request/authorization impersonation and quota-bypass class of bug matching the analog's "withdraw more than entitled" pattern (repeated unauthorized use of a single grant).

### Likelihood Explanation
High, if the allowlist is intended to be single-use: any legitimate caller (or anyone who can reconstruct/observe the exact same JSON-RPC request, since the digest is derived deterministically from the request body via `req.Digest()`) can simply resend the identical request as many times as desired before expiry — no privileged access or race condition needed. This requires only unprivileged access to the gateway/vault entrypoint.

### Recommendation
After successful authorization in `AuthorizeRequest`, mark or remove the consumed `RequestDigest` from the in-memory allowlist set tracked by `workflowRegistry` (mirroring on-chain consumption if the contract supports it), so a given digest cannot be reused for a second, distinct incoming request. Alternatively, if this is a known/intended design (allowlist is a time-bound reusable authorization rather than single-use), this should be explicitly documented and is not a vulnerability — I could not confirm from the available code/comments which behavior is intended, and did not find contract-side single-use semantics in the accessible files.

### Proof of Concept
1. Workflow owner registers an allowlisted request via `AllowlistRequest(requestDigest, expiryTimestamp)` on-chain [3](#0-2) .
2. `workflowRegistry.syncAllowlistedRequests` picks it up into `allowListedRequests` [4](#0-3) .
3. Client sends the exact allowlisted JSON-RPC request to the Vault gateway handler; `allowListBasedAuth.AuthorizeRequest` matches the digest and authorizes it [7](#0-6) .
4. Client resends the identical request (same digest) any number of times before `ExpiryTimestamp` — each is authorized identically, since no consumption state exists.

Note: I was unable to locate the on-chain `WorkflowRegistry` Solidity contract's `AllowlistRequest`/consumption semantics in the indexed portion of this repo (only Go bindings/tests were available), so I cannot confirm whether the contract itself enforces single-use invalidation that the off-chain syncer/auth code fails to mirror, or whether reuse until expiry is the intended design. This should be verified against the actual `WorkflowRegistry.sol` contract source before treating this as a confirmed vulnerability.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-77)
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

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
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
