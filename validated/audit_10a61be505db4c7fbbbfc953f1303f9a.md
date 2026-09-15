Audit Report

## Title
Non-atomic JWT replay check-and-record in HTTP Trigger authorization allows concurrent JWT replay - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks JWT replay status via `isReplay` under an `RLock` and only records usage via `recordUsage` under a separate `Lock` at the end of the function, with unrelated authorized-key lookup logic executed in between. [1](#0-0) 
This is confirmed to be a genuine non-atomic check-then-act pattern, verified against `jwtReplayCache.isReplay`/`recordUsage`. [2](#0-1) 

## Finding Description
The race window exists exactly as described: two concurrent calls to `Authorize` with the identical signed JWT can both observe `isReplay(claims.ID) == false` before either calls `recordUsage`. However, `VerifyRequestJWT` binds the JWT's `Digest` claim to `req.Digest()` of the exact JSON-RPC request being authorized (including its `ID` field), meaning a replay of the identical JWT necessarily carries the identical `jsonrpc.Request.ID` (the workflow `requestID`). [3](#0-2) 
Downstream of `Authorize`, `httpTriggerHandler.HandleUserTriggerRequest` calls `setupCallback`, which performs an atomic check-and-insert on `requestID` under a single `callbacksMu.Lock()`: it checks `h.callbacks[requestID]` for existence and inserts the new callback within the same locked critical section, rejecting the request immediately if the ID is already in use. [4](#0-3) 
Because this second, properly atomic guard sits between the vulnerable `Authorize` race window and the actual dispatch to DON nodes (`sendWithRetries`/`sendToShard`), one of the two racing requests will be rejected with "requestID: ... has already been used" before any duplicate trigger is ever sent to nodes. The `Authorize` race by itself does not result in duplicate workflow execution dispatch — it can at most cause both requests to pass the JWT-replay check simultaneously and proceed to `setupCallback`, where the actual double-dispatch is blocked.

## Impact Explanation
The claimed impact — "duplicate/unintended execution of actions" via concurrent JWT replay — is not substantiated. While the `isReplay`/`recordUsage` pair is indeed non-atomic (a legitimate code-quality/defense-in-depth issue), the identical-JWT replay scenario described in the PoC cannot actually produce a duplicate execution because the `requestID` (bound into the JWT's digest) is deduplicated atomically in `setupCallback` before any request reaches the DON. At most, one of the racing requests would proceed and the other would fail with a "requestID already used" error — the same outcome as if the JWT check were atomic. There is no concrete unauthorized fund movement, job-run duplication, or gateway request impersonation demonstrated beyond this benign race.

## Likelihood Explanation
Even though the race condition in `Authorize` is technically real, it does not translate into an exploitable security impact given the atomic `requestID` dedup check downstream. The report's Proof of Concept only demonstrates that `isReplay`/`recordUsage` are not atomic in isolation; it does not account for or test the `setupCallback` atomic guard that prevents the claimed impact end-to-end.

## Recommendation
N/A — no vulnerability confirmed with the claimed impact. If desired, hardening `jwtReplayCache` with an atomic `checkAndRecord` method would still be reasonable defense-in-depth, but this is not a security-critical fix since duplicate execution is already prevented by the atomic `requestID` uniqueness check in `setupCallback`.

## Proof of Concept
N/A — the claimed PoC (two concurrent identical-JWT requests causing duplicate authorized dispatch) does not go through the additional atomic `requestID` dedup step in `setupCallback`, so it would not demonstrate duplicate execution; only one request would ultimately be dispatched to the DON regardless of the `Authorize`-level race.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L87-105)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/utils/jwt.go (L277-301)
```go
	reqDigest, err := req.Digest()
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	if verifiedClaims.ID == "" {
		return nil, gethcommon.Address{}, errors.New("JWT ID (jti) is required but missing")
	}
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
	if verifiedClaims.Digest != "0x"+reqDigest {
		return nil, gethcommon.Address{}, fmt.Errorf("claim digest '%s' does not match calculated request digest '0x%s'", verifiedClaims.Digest, reqDigest)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
