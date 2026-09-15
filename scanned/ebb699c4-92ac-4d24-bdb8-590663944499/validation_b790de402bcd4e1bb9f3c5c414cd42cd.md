I found a genuine analog to the Teller front-running bug in `core/capabilities/vault/allow_list_based_auth.go`. The vault's `AllowListBasedAuth` authorizes user requests (e.g., `secrets/create`, `secrets/update`, `secrets/delete`) against a periodically-synced, in-memory snapshot of on-chain allowlisted requests, rather than the live on-chain state, and this snapshot is only refreshed on a fixed tick interval.

### Title
Stale allowlist snapshot lets a revoked/expired vault request authorization still be honored - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest` checks a caller-supplied JSON-RPC request against `w.allowListedRequests`, an in-memory cache of on-chain `AllowlistRequest` entries that is refreshed only once per `defaultTickIntervalForAllowlistedRequests` tick by `syncAllowlistedRequests`. Between ticks, an unprivileged attacker who observes an about-to-expire or about-to-be-invalidated allowlist entry (e.g., the workflow owner intends to let it expire, or a defensive off-chain revocation mechanism removes it) can still get their request authorized purely based on the stale in-memory copy, exactly mirroring the Teller bug class where a state-changing action (the lender's withdraw) does not retroactively invalidate a still-cached/derived authorization used by a second actor (the liquidator) racing against it. Here the roles are inverted but the root cause is identical: authorization decisions are made against a cache that can diverge from ground truth for a bounded but attacker-exploitable window.

### Finding Description
The authorization flow is:
1. `allowListBasedAuth.AuthorizeRequest` (core/capabilities/vault/allow_list_based_auth.go:34-77) computes the request digest and calls `findAllowlistedItemWithRetry`, which reads from `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)`. [1](#0-0) 
2. `GetAllowlistedRequests` is backed by `workflowRegistry.allowListedRequests`, which is populated exclusively by `syncAllowlistedRequests`, a background goroutine that polls on-chain state once per `defaultTickIntervalForAllowlistedRequests` and swaps in a new slice under `w.allowListedMu`. [2](#0-1) 
3. Expiry pruning also happens only at sync time — `for _, request := range w.allowListedRequests { if int64(request.ExpiryTimestamp) > time.Now().Unix() ... }` — so a request whose on-chain state has already been superseded (deleted/replaced by a new `AllowlistRequest` call, or removed by any off-chain compensating action) remains valid in the local cache until the next tick fires.
4. `AuthorizeRequest`'s own expiry check at line 64 (`time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp)`) only catches items whose `ExpiryTimestamp` field is stale/expired — it does nothing for items that were *replaced or invalidated on-chain* before their originally-recorded expiry, because the node's local view has not yet observed that change.

This is the same class of bug as the Teller report: a security-relevant decision (liquidation eligibility / request authorization) is made from state that a concurrent, legitimate on-chain action (collateral withdrawal / re-allowlisting or revocation) can invalidate, but the node consuming that decision has no mechanism to detect the invalidation within its polling window, allowing an unprivileged actor to exploit the race.

### Impact Explanation
An attacker with no special privileges who submits a vault `secrets/create`, `secrets/update`, or `secrets/delete` JSON-RPC request whose digest was legitimately allowlisted can continue to have that request authorized and processed by the vault gateway/DON for up to one full sync interval after the corresponding on-chain allowlist entry has been superseded or removed, because `allowListBasedAuth.AuthorizeRequest` never re-validates against live on-chain state — it trusts `w.allowListedRequests` unconditionally between ticks. This can allow secret creation/update/deletion actions to be executed after the workflow owner believed they had revoked authorization, i.e., an authorization bypass window. [3](#0-2) 

### Likelihood Explanation
The window is deterministic and always present (bounded by `defaultTickIntervalForAllowlistedRequests`), not a rare fluke — any unprivileged client that already possesses (or can guess ahead of time, since digests are pre-computable) a soon-to-be-superseded allowlist digest can exploit it during every sync cycle. No node compromise or special role is needed; only knowledge of a request whose allowlist status is about to change on-chain.

### Recommendation
Re-validate allowlist status against live on-chain state (or a much-shorter-lived, per-request confirmation) at authorization time rather than relying solely on the periodically-synced cache, or reduce `defaultTickIntervalForAllowlistedRequests` and add a secondary on-chain existence check for requests nearing their `ExpiryTimestamp` bound. Alternatively, have on-chain `AllowlistRequest`/revocation operations emit events that trigger an immediate out-of-band refresh of `w.allowListedRequests` rather than waiting for the next tick.

### Proof of Concept
1. A workflow owner calls `AllowlistRequest(digest, expiry)` on-chain for a `secrets/delete` request, then shortly after calls it again (or an equivalent revocation path) to replace/expire that digest early.
2. Because `syncAllowlistedRequests` only refreshes `w.allowListedRequests` once per tick [4](#0-3) , the old digest remains present in the in-memory cache until the next tick.
3. Within that window, an unprivileged actor submits the JSON-RPC request matching the old (now superseded) digest to the vault gateway.
4. `allowListBasedAuth.AuthorizeRequest` finds the stale entry via `fetchAllowlistedItem` and, since its `ExpiryTimestamp` has not yet passed, authorizes and executes the request — even though the owner's on-chain intent had already changed. [5](#0-4)

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L51-76)
```go
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
