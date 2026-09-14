### Title
JWT replay-protection check-then-record TOCTOU allows double-authorization of HTTP trigger requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT ID (`jti`) has already been used via `jwtCache.isReplay`, and only marks it as used via `jwtCache.recordUsage` at the very end of the function, after signature verification and authorized-key lookup succeed. The check and the record are two independent, separately-locked operations with unrelated work (JWT verification, map lookups) executed in between, creating a classic time-of-check to time-of-use race window.

### Finding Description
`Authorize` verifies the JWT, checks replay status, validates the signer against the workflow's authorized keys, and finally records the `jti` as used: [1](#0-0) 

The replay cache's check and record primitives acquire the mutex independently and do not compose into a single atomic check-and-set: [2](#0-1) 

Because `isReplay` (line 87) and `recordUsage` (line 105) are not protected by a shared critical section, two concurrent `Authorize` calls carrying the exact same signed JWT (same `jti`) can both pass the `isReplay` check before either one calls `recordUsage`. Both requests then proceed to validate the signer against `authorizedKeys` and are both granted authorization, defeating the intended one-time-use replay protection.

### Impact Explanation
The `jti` replay cache exists specifically to prevent a valid signed workflow-trigger JWT from being used more than once. Successful exploitation causes concrete authorization bypass of the anti-replay control: an unprivileged external caller (whoever possesses one valid signed HTTP trigger JWT for a workflow) can cause the same request to be authorized and processed multiple times concurrently. If the triggered workflow performs a job run or an on-chain/fund-affecting action, this can result in duplicate/unauthorized job execution triggered from a single credential-use, which matches the "unauthorized job run" impact criteria. This is reachable from the internet-facing gateway's HTTP trigger path without any additional privilege beyond holding a single previously-issued token.

### Likelihood Explanation
The race window requires the attacker to send the same JWT concurrently (e.g., two parallel connections) so that both `Authorize` calls execute `isReplay` before either completes `recordUsage`. This is a narrow but readily achievable race for a network attacker who controls request timing (no privileged position needed), consistent with the CVE's AC:H / PR:L characterization — non-trivial but reliably triggerable with basic request racing techniques.

### Recommendation
Make the check-and-mark operation atomic: acquire the `jwtReplayCache` mutex once and perform both the existence check and the insertion under the same lock (i.e., implement a single `checkAndRecord(jti string) bool` method returning whether the token was already used, inserting it if not, all under one `Lock()`), and call it from `Authorize` instead of the separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Obtain (or have) one valid signed HTTP-trigger JWT with a given `jti` for a workflow.
2. Fire two (or more) concurrent HTTP trigger requests to the gateway carrying the identical JWT.
3. Both goroutines invoke `WorkflowMetadataHandler.Authorize`, which calls `h.jwtCache.isReplay(claims.ID)` (returns `false` for both if timed closely) before either calls `h.jwtCache.recordUsage(claims.ID)`.
4. Both requests pass authorization and both trigger the workflow, despite only one JWT/`jti` ever being issued — demonstrating the replay-protection bypass.

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
