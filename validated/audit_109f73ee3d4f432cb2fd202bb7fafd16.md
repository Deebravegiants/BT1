This is a genuine analog to the CVE-2024-47141 bug class: separate, non-atomic check-then-act operations on shared state accessed by concurrent, unprivileged callers, allowing a TOCTOU race that defeats the intended protection.

### Title
JWT Replay Protection Bypass via TOCTOU Race in `Authorize` - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
`WorkflowMetadataHandler.Authorize` checks `h.jwtCache.isReplay(claims.ID)` and later calls `h.jwtCache.recordUsage(claims.ID)`, but these are two separate lock acquisitions on `jwtReplayCache.mu` rather than one atomic check-and-set operation, mirroring the kernel `pin_request()` bug where `desc->mux_usecount` and `desc->mux_owner` were updated non-atomically across two lock windows.

### Finding Description
`jwtReplayCache.isReplay` takes an `RLock`, checks map membership, and releases the lock [1](#0-0) . Later, `recordUsage` takes a separate `Lock` and writes the entry [2](#0-1) . In `Authorize`, these two calls are separated by additional logic (looking up authorized keys for the workflow, comparing signer to authorized key set) that does not hold the cache lock [3](#0-2) .

If two requests carrying the same JWT (same `jti`) arrive concurrently — analogous to the kernel's two CPUs racing on `pin_request()` — both can call `isReplay` before either calls `recordUsage`, observe `exists == false`, and both proceed to pass authorization and only afterward record usage. This is the same root-cause pattern as the CVE: a shared piece of state (`mux_usecount`/`mux_owner` in the kernel; the JWT replay cache entry here) is read and written in two disjoint critical sections instead of one atomic check-and-set, allowing another concurrent actor to observe a stale/incomplete state and bypass the intended single-use invariant.

### Impact Explanation
The JWT replay cache is the mechanism preventing a **valid, previously-used** JWT-authenticated request from being submitted again to the internet-facing gateway handler. A successful race allows the same signed JWT to authorize two (or more) concurrent workflow-metadata-related requests instead of one, undermining the anti-replay guarantee that the `Authorize` function is designed to enforce. This is an authentication/session control weakening reachable from an unprivileged caller providing an externally-issued token to the gateway's `Authorize` path.

### Likelihood Explanation
Exploitation requires an attacker to send two (or more) copies of the same signed JWT to the gateway at nearly the same time — a straightforward, purely-network-timing race with no special privileges, valid pre-conditions, or access beyond possessing one valid, previously obtained/observed JWT. The race window is bounded by the authorized-key lookup work between the `isReplay` check and `recordUsage` call, which is enough for concurrent goroutines handling parallel requests to interleave.

### Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-set operation performed under one lock acquisition (e.g., a `CheckAndRecord(jti string) (alreadyUsed bool)` method that takes the write lock once, checks membership, and inserts if absent, returning whether it was already present) — the same fix approach taken by the Linux kernel commit, which serialized the previously-split check and write into a single mutex-protected critical section.

### Proof of Concept
1. Obtain (or intercept) one valid JWT for `Authorize` targeting a given `workflowID`.
2. Fire two concurrent requests to the gateway's `Authorize` code path with the identical JWT (same `jti`) at the same time.
3. Both goroutines execute `h.jwtCache.isReplay(claims.ID)` before either has called `h.jwtCache.recordUsage(claims.ID)`; both observe `exists == false`.
4. Both requests pass the authorized-key check and both `Authorize` calls succeed, i.e., the single JWT is accepted twice, violating the single-use replay-protection guarantee that `Authorize` is documented to provide.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-405)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L407-412)
```go
func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```
