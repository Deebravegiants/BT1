### Title
Unauthorized workflow execution via JWT replay when a signer's authorization is transiently toggled - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The `WorkflowMetadataHandler.Authorize` function in the gateway's HTTP trigger path only marks a JWT's `jti` as "used" after a request passes *all* authorization checks. If authorization fails because the signer is not currently in the `authorizedKeys` set (a state that is externally mutable via workflow-registry key updates), the `jti` is never recorded. The exact same signed JSON-RPC request/JWT can therefore be resubmitted later, and if the signer becomes authorized again before the token expires, the previously-rejected request will now succeed — mirroring the Dharma "key reuse" bug class where a signature that failed due to a transient key state can later succeed unexpectedly if that key state reverts.

### Finding Description
`Authorize` checks JWT replay, then checks if the recovered signer is currently in `h.authorizedKeys[workflowID]`, and only calls `h.jwtCache.recordUsage(claims.ID)` on the success path: [1](#0-0) 

`authorizedKeys` is populated from `syncMetadata`, which aggregates workflow-registry state reported by DON nodes/shards — i.e., it can change over time as workflows are updated (e.g., a signing key temporarily removed and re-added, akin to `setSpecificKey`/`setGlobalKey` reuse in the original report): [2](#0-1) 

The request-level dedup in the HTTP trigger handler (`setupCallback`) only protects against *concurrent* in-flight requests with the same `requestID`; the entry is removed once processed or reaped after `CleanUpPeriodMs`, after which the same `requestID` can be submitted again: [3](#0-2) [4](#0-3) 

The only hard bound on replay is the JWT's own expiration, capped at `maxJWTExpiryDuration` (5 minutes) and enforced in `VerifyRequestJWT`: [5](#0-4) [6](#0-5) 

So within that up-to-5-minute window, the vulnerability is: a request signed and submitted while its signer is authorized, that fails for an *unrelated transient reason coinciding with a temporary loss of authorization* (or is submitted while the signer is briefly deauthorized during a key-rotation window), leaves its `jti` unconsumed. If the signer is re-authorized (e.g., workflow definition update reverted, or eventual-consistency sync catches up) before expiry, an attacker who observed the wire-visible JWT/request (it is not a secret — the JWT and digest travel in the request itself) can resubmit it and have it accepted and executed, exactly matching the "signature swap[s] between valid/invalid across states" pattern from the report.

### Impact Explanation
Successful replay causes an **unauthorized workflow (job) execution** — the gateway forwards the trigger request to all DON nodes and it is treated as a normal, authorized `workflows.execute` call, indistinguishable from a legitimate one. This can be used to duplicate/re-trigger workflow executions outside of the timing and intent of the original signer, which may have side effects (e.g., pipeline runs, on-chain calls made by the workflow) depending on what the workflow does — this is the same "unauthorized job run" impact class called out as acceptable in the validation rules.

### Likelihood Explanation
Exploitability requires: (1) an attacker/observer to capture a valid signed JWT request that was rejected due to the signer not being currently authorized, and (2) the signer becoming authorized again before the JWT's `exp` (bounded to ≤5 minutes). Because workflow-registry syncing across shards is asynchronous (`syncMetadata` runs periodically and depends on F+1 node agreement), transient authorization gaps/flaps are plausible during normal workflow key updates, not just attacker-induced races. However, the tight ≤5-minute window and the requirement that authorization revert to the exact same key state make this a moderate-likelihood, narrow-window issue rather than an easily/broadly exploitable one.

### Recommendation
- Record the JWT `jti` as used as soon as it passes replay/signature/digest checks, *before* the authorization-set lookup, so a signature can never be reprocessed regardless of whether the signer's authorization state happens to change between attempts.
- Alternatively/additionally, bind authorization decisions to a monotonic epoch/version of the `authorizedKeys` set (similar to a wallet nonce) so that once a key is removed, any previously valid but now-rejected signature for that workflow cannot become valid again without a fresh JWT bound to the new epoch.
- Ensure `requestID`/JWT `jti` cache retention is at least as long as the maximum JWT expiry to close any gap introduced by callback reaping.

### Proof of Concept
1. Client signs and submits `workflows.execute` JWT `T` (jti=J, digest=D, exp = now+5m) for `workflowID=W`, where signer `S` is currently in `authorizedKeys[W]`.
2. Due to an in-flight workflow-registry update (e.g., owner rotates/removes key `S` momentarily), `syncMetadata` refreshes `authorizedKeys[W]` and `S` is temporarily absent when `Authorize` runs; the request is rejected with `"signer ... is not authorized"` and, per `Authorize`, `jtiCache.recordUsage` is never called for `J` (see lines 92-108 above).
3. An observer/attacker who has visibility into the rejected request (e.g., via logs, network capture, or is the original less-trusted caller relay) retains the full JWT `T` and original JSON-RPC request bytes.
4. Before `T` expires (within 5 minutes), the workflow registry update completes another cycle and `S` is re-added to `authorizedKeys[W]` (key reuse/revert).
5. Attacker resubmits the identical JSON-RPC request + JWT `T` to `HandleUserTriggerRequest`. `Authorize` now finds `S` authorized, `jti=J` not yet in the replay cache, and accepts it — the workflow is executed a second time from a signature that had already been rejected once, without the original signer's renewed intent at that moment.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L110-120)
```go
// syncMetadata aggregates the authorized keys and workflow selectors from each
// shard's WorkflowMetadataAggregator and updates the local cache. A workflow is
// considered assigned to a shard once that shard's aggregator reports it (i.e.
// F+1 of the shard's nodes observed it).
func (h *WorkflowMetadataHandler) syncMetadata(ctx context.Context) {
	authorizedKeys := make(map[string]map[gateway.AuthorizedKey]struct{})
	workflowRefToID := make(map[workflowReference]string)
	workflowIDToRef := make(map[string]workflowReference)
	workflowShards := make(map[string][]*shardEndpoint)

	for _, shard := range h.shards {
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-456)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

	// Build one response aggregator per shard the workflow is assigned to.
	assigned := h.workflowMetadataHandler.WorkflowShards(workflowID)
	if len(assigned) == 0 {
		// this shouldn't happen because we checked it in authorizeRequest()
		h.handleUserError(ctx, requestID, jsonrpc.ErrInternal, fmt.Sprintf("Workflow %s is not assigned to any DONs", workflowID), callback)
		return nil, errors.New("workflow is not assigned to any shards")
	}

	aggregators := make(map[string]*aggregation.IdenticalNodeResponseAggregator, len(assigned))
	for _, shard := range assigned {
		// (N+F)//2 + 1 threshold where N = number of nodes, F = number of faulty nodes
		threshold := (len(shard.members)+shard.f)/2 + 1
		agg, err := aggregation.NewIdenticalNodeResponseAggregator(threshold)
		if err != nil {
			return nil, errors.New("failed to create response aggregator: " + err.Error())
		}
		aggregators[shard.donID] = agg
	}

	doneCh := make(chan struct{})
	h.callbacks[requestID] = savedCallback{
		Callback:            callback,
		requestStartTime:    requestStartTime,
		createdAt:           time.Now(),
		responseAggregators: aggregators,
		doneCh:              doneCh,
	}
	return doneCh, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L463-472)
```go
func (h *httpTriggerHandler) cleanupCallback(requestID string) {
	saved, exists := h.callbacks[requestID]
	if !exists {
		return
	}
	if !saved.processed {
		close(saved.doneCh)
	}
	delete(h.callbacks, requestID)
}
```

**File:** core/utils/jwt.go (L19-22)
```go
const (
	maxJWTExpiryDuration     = 5 * time.Minute // Maximum allowed expiry duration
	defaultIssuedAtTolerance = 5 * time.Minute // Default tolerance for issuedAt validation to handle clock drift
)
```

**File:** core/utils/jwt.go (L284-298)
```go
	if verifiedClaims.ExpiresAt == nil {
		return nil, gethcommon.Address{}, errors.New("expiredAt (exp) is required but missing")
	}
	if verifiedClaims.IssuedAt == nil {
		return nil, gethcommon.Address{}, errors.New("issuedAt (iat) is required but missing")
	}
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
```
