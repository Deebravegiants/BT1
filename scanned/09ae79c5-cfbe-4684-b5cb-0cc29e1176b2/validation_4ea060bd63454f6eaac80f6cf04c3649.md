### Title
JWT replay-check-then-record race in `WorkflowMetadataHandler.Authorize` allows request duplication - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Sherlock finding is a classic "check state, act, but update the deduping state too late" bug: `claimRewards()` read `lastRewardTime` to compute payout but never advanced it before returning, so a second call could reuse the same window. The Chainlink HTTP Trigger gateway path (`core/services/gateway/handlers/capabilities/v2`) has the same structural defect in its JWT single-use enforcement: the "already used" check and the "mark as used" write are two separate, non-atomically-coupled operations separated by unrelated work, so two requests carrying the same JWT can both pass the check before either records usage.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the JWT authentication entry point for unprivileged, internet-facing HTTP Trigger requests reaching the gateway (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` calls it from `authorizeRequest`, which is invoked directly from `HandleUserTriggerRequest`, the externally-reachable entry point for HTTP-triggered workflow executions): [1](#0-0) 

Inside `Authorize`, the single-use check (`isReplay`) and the single-use write (`recordUsage`) are split by intervening logic (workflow lookup, signer/key validation), and each acquires/releases its own lock independently rather than the whole check-act sequence being atomic: [2](#0-1) 

The underlying cache implementation confirms this: `isReplay` takes an `RLock`, reads, and releases; `recordUsage` separately takes a `Lock`, writes, and releases — there is no single critical section spanning "check-not-used" through "mark-used": [3](#0-2) 

If two requests bearing the identical signed JWT (same `jti`) arrive concurrently at the gateway — which an unprivileged external caller fully controls by simply sending the same signed trigger request twice in parallel — both goroutines can observe `isReplay(claims.ID) == false` before either calls `recordUsage`, letting both pass authorization and both trigger a workflow execution.

This directly mirrors the reported root cause: a piece of state meant to prevent double use of a single credit/authorization is checked but the update that would prevent re-use is deferred past other logic, opening a window for double consumption.

Note: the sibling `RequestReplayGuard.CheckAndRecord` in the Vault capability (`core/capabilities/vault/request_replay_guard.go`) correctly implements this as one atomic check-and-record under a single mutex, which is the safe pattern this handler should follow. [4](#0-3) 

### Impact Explanation
A single signed HTTP-trigger JWT — intended to authorize exactly one workflow execution — can be used to trigger the same (or, depending on timing, more) workflow execution(s) more than once by racing concurrent requests. Since `HandleUserTriggerRequest` fans the (now duplicate-authorized) request out to DON nodes and each execution consumes per-workflow rate-limit budget, compute, and potentially triggers side effects in downstream capabilities/actions, this is a double-dip of workflow execution "credit" analogous to the reward double-claim in the source report. It undermines the single-use guarantee stated in the code's own error message ("JWT token has already been used").

### Likelihood Explanation
Exploitation only requires an unprivileged external client capable of sending two HTTP requests with the same previously-issued signed JWT nearly simultaneously (trivial to script). No special network position, no privileged role, and no cooperation from any node is required — it purely exploits a TOCTOU window in gateway-side in-memory state that any external caller of the HTTP Trigger endpoint controls the timing of.

### Recommendation
Make the check-and-record operation atomic under a single lock, similar to `RequestReplayGuard.CheckAndRecord` in the vault package: acquire the write lock once, check `jti` existence, and if absent immediately insert it before releasing the lock and continuing with the remaining authorization/authorization key-lookup steps. For example, collapse `isReplay`/`recordUsage` into a single `checkAndRecordJTI(jti string) error` method on `jwtReplayCache` that performs both operations while holding `cache.mu.Lock()`, and call it immediately after JWT signature verification succeeds (before any other authorization logic), returning early on failure so no other code path can slip in between.

### Proof of Concept
1. A workflow owner obtains a valid signed HTTP Trigger JWT with `jti = "X"` for a registered workflow.
2. Attacker (or legitimate but concurrent client bug) sends two HTTP requests carrying `Auth = jwt(jti=X)` to the gateway at nearly the same time (e.g., via two parallel goroutines/HTTP clients).
3. Both requests reach `WorkflowMetadataHandler.Authorize` concurrently. Goroutine A calls `h.jwtCache.isReplay("X")` → `false` (not yet recorded). Before Goroutine A reaches `h.jwtCache.recordUsage("X")` (which runs only after workflow/key lookups succeed), Goroutine B also calls `isReplay("X")` → still `false`.
4. Both goroutines pass authorization, and both proceed through `checkRateLimit`/`sendWithRetries`, resulting in the same JWT authorizing two separate workflow executions instead of one.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

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
