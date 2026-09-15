Based on my research, I found a concrete analog in the same idempotency/first-call-wins bug class as the TapiocaOptionBroker frontrunning issue, but manifesting as a check-then-act race in Chainlink's Gateway JWT replay guard rather than a direct frontrunning DoS.

### Title
JWT replay-guard check-then-act race allows a single-use HTTP trigger token to authorize concurrent duplicate workflow executions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The `emitForWeek()`/`newEpoch()` bug in the external report is a case of an "idempotent, once-per-period" state check whose read (`emissionForWeek[week] > 0`) and write are not atomic with the caller's later use of the result, letting an attacker race the legitimate caller and turn a one-time success into a silent no-op. The Gateway's `Authorize` function for HTTP-triggered workflow executions has the analogous shape: it treats a JWT `jti` as single-use by checking `isReplay` and then separately calling `recordUsage`, with no shared lock spanning both calls.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the unprivileged-facing entry point that authenticates HTTP trigger requests via a signed, single-use JWT before dispatching a workflow execution: [1](#0-0) 

The relevant sequence is: verify the JWT signature, then check `h.jwtCache.isReplay(claims.ID)` and reject if already used, then look up authorized keys, and only *after* all of that call `h.jwtCache.recordUsage(claims.ID)` to mark the `jti` consumed. `isReplay` and `recordUsage` are two independent calls on `jwtReplayCache`, each presumably taking its own internal lock, with no atomic "check-and-set" spanning the whole `Authorize` call the way `TapOFT.emitForWeek()`'s check (`if emissionForWeek[week] > 0`) and write (`emissionForWeek[week] = emission`) are also non-atomic with respect to the caller (`TapiocaOptionBroker.newEpoch()`).

This means two concurrent requests carrying the same valid, signed, single-use JWT can both pass `isReplay(claims.ID) == false` before either has called `recordUsage(claims.ID)`, exactly mirroring how two near-simultaneous callers of `emitForWeek()`/`newEpoch()` can race the one-time `emissionForWeek[week]` gate.

### Impact Explanation
If the race is won, the single-use JWT authorizes more than one workflow execution: this is a quota/one-time-token bypass on the internet-facing gateway's trigger handling path — a workflow that should be triggerable exactly once per issued token can instead be triggered multiple times concurrently, which can lead to duplicate fund-moving or state-changing workflow runs depending on what the triggered workflow does. This is the direct analog of the original bug's core weakness (a "should only succeed once" guard that isn't atomic with its use), just manifesting as a bypass (extra executions) instead of a block (zero rewards).

### Likelihood Explanation
Exploitation requires the attacker to possess (or intercept) one valid signed JWT for a workflow trigger and then submit it to the gateway multiple times in close succession (racing the check-then-act window, which is a matter of goroutine scheduling, not network timing). No special privilege beyond having a legitimately obtained/observed token is needed to attempt the race, and the check/record calls are visibly separated in the source with no evidence of a single atomic operation.

### Recommendation
Combine the replay check and usage record into a single atomic operation (e.g., a `CheckAndRecord`-style method, similar to the pattern already used correctly in `core/capabilities/vault/request_replay_guard.go`'s `RequestReplayGuard.CheckAndRecord`, which holds one mutex across both the existence check and the insert) [2](#0-1) , and use that unified primitive in `WorkflowMetadataHandler.Authorize` instead of separate `isReplay`/`recordUsage` calls.

### Proof of Concept
Not runnable from the indexed context — I could not retrieve the full implementation of `jwtReplayCache.isReplay`/`recordUsage` (their internal locking) to confirm the exact race window size, only the call-site evidence in `Authorize` showing the check and the record are two distinct, non-atomic calls. A concrete PoC would require two goroutines calling `Authorize` with the same JWT nearly simultaneously and asserting both succeed; I was not able to execute or fully verify this within the available tool access, so this should be validated with a live/staged race test before being treated as confirmed.

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

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```
