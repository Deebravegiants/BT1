### Title
JWT replay-protection check-then-act race in `WorkflowMetadataHandler.Authorize` allows concurrent replay of a single-use HTTP-trigger JWT - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The PoolTogether report describes a race/front-run against a mechanism that is supposed to guarantee "claim once" semantics; an unprivileged actor exploits the gap between validation and state update to defeat the intended single-use guarantee, causing wasted/duplicate work. The closest analog reachable from an unprivileged client in this codebase's internet-facing gateway is the JWT replay-protection cache used to authorize `workflows.execute` HTTP trigger requests: the "already used?" check and the "mark as used" write are two separate, non-atomic critical sections, so two requests carrying the same JWT that arrive concurrently can both pass the replay check before either records the `jti` as used.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the entry point that authenticates inbound HTTP trigger requests reaching the gateway from unauthenticated internet clients, via `httpTriggerHandler.authorizeRequest` → `HandleUserTriggerRequest`. [1](#0-0) 

The replay check is implemented as two independently-locked operations on the `jwtReplayCache`: [2](#0-1) 

`isReplay` takes an `RLock`, checks map membership, and releases the lock; separately, `recordUsage` later takes a full `Lock` and inserts the `jti`: [3](#0-2) 

Between the `isReplay` read and the `recordUsage` write, `Authorize` performs additional work (looking up `h.authorizedKeys[workflowID]`, building the `AuthorizedKey`) with no lock held that spans both operations. This is a classic check-then-act (TOCTOU) race: if two requests carrying the identical signed JWT (`tokenString`, tied to a specific `jti` and request digest) are submitted concurrently, both can call `isReplay(claims.ID)` before either calls `recordUsage(claims.ID)`, so both pass authorization and are forwarded to the DON as legitimate `workflows.execute` invocations.

This is directly analogous to the front-run described in the report: the intended invariant ("this credential/claim can be consumed exactly once") is enforced by a check that is not atomic with the corresponding state mutation, and an actor who can replay/duplicate the observed request within that window defeats the single-use guarantee.

### Impact Explanation
A JWT is meant to authorize exactly one execution of a workflow via the HTTP trigger (the `jti` replay cache exists specifically to prevent re-use). Successfully racing the check allows an unprivileged actor who obtains/observes a valid signed JWT (e.g., a legitimate but unauthenticated request in flight, since HTTP triggers are internet-facing and the JWT/body could be captured or reused by anyone able to submit the same bytes to the gateway before the legitimate request completes) to trigger a duplicate workflow execution with the same authorization. This is an unauthorized job run / authentication-guarantee bypass: the workflow executes more times than the number of valid, distinct JWTs issued, potentially causing duplicate side effects (e.g., duplicate on-chain actions, duplicate downstream charges) attributable to the workflow owner, and consuming rate-limit/compute budget intended to bound a single authorized action.

### Likelihood Explanation
Exploitation requires only the ability to send the same (or an in-flight-captured) signed JWT + request twice, essentially concurrently, to the gateway HTTP trigger endpoint — no privileged access, no valid signing key of one's own, and no cryptographic break is needed since the attacker only needs to duplicate bytes that are already valid and in transit/observable. The race window is bounded by the time between the `RLock`-protected `isReplay` check and the `Lock`-protected `recordUsage` call, but because the intervening work performs a map lookup, a JSON marshal in the caller, and network dispatch, the window is non-trivial and remotely triggerable by firing duplicate requests in parallel.

### Recommendation
Make the "check-and-mark-used" operation atomic under a single critical section (e.g., a single mutex-guarded function that checks presence and inserts the `jti` in one step, returning whether it was already present — i.e., a compare-and-swap-style `checkAndSet`), rather than exposing `isReplay` and `recordUsage` as two separately lockable steps called from `Authorize`.

### Proof of Concept
1. Client issues a valid signed HTTP trigger request `R` with JWT claims `{jti: X, digest: D}` per `CreateRequestJWT`/`VerifyRequestJWT`. [4](#0-3) 
2. An actor captures/duplicates the exact same request bytes (same `tokenString` and same JSON-RPC request body) and fires it at the gateway concurrently with the original.
3. Both requests reach `WorkflowMetadataHandler.Authorize` at nearly the same time; goroutine A executes `h.jwtCache.isReplay(X)` returning `false`, then goroutine B — before A reaches `recordUsage` — also executes `isReplay(X)` and gets `false`.
4. Both goroutines pass the authorized-key check and both call `h.jwtCache.recordUsage(X)`; both requests are forwarded via `sendWithRetries`/DON dispatch as authorized `workflows.execute` calls, resulting in two executions from one JWT. [5](#0-4)

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

**File:** core/utils/jwt.go (L168-216)
```go
func CreateRequestJWT[T any](req jsonrpc.Request[T], opts ...Option) (*jwt.Token, error) {
	// Apply options
	options := &jwtOptions{}
	for _, opt := range opts {
		opt(options)
	}

	expiryDuration := maxJWTExpiryDuration
	if options.expiryDuration != nil {
		expiryDuration = *options.expiryDuration
	}

	digest, err := req.Digest()
	if err != nil {
		return nil, err
	}

	var issuer string
	if options.issuer != nil {
		issuer = *options.issuer
	}

	var subject string
	if options.subject != nil {
		subject = *options.subject
	}

	var audience []string
	if options.audience != nil {
		audience = options.audience
	}

	now := time.Now()
	jti := uuid.New().String()

	claims := JWTClaims{
		Digest: "0x" + digest,
		RegisteredClaims: jwt.RegisteredClaims{
			ID:        jti,
			Issuer:    issuer,
			Subject:   subject,
			Audience:  jwt.ClaimStrings(audience),
			ExpiresAt: jwt.NewNumericDate(now.Add(expiryDuration)),
			IssuedAt:  jwt.NewNumericDate(now),
		},
	}

	return jwt.NewWithClaims(&SigningMethodEth{}, claims), nil
}
```
