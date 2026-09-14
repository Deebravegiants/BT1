## Confirmed analog: TOCTOU race in JWT replay protection allows token reuse

### Title
JWT replay-cache check-then-act race allows a single-use HTTP-trigger JWT to be reused by concurrent requests - (`core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The LooksRare bug is a classic check-then-act race: a limit (`MAXIMUM_NUMBER_OF_DEPOSITS_PER_ROUND`) is checked at one point but the state that would make the check meaningful is mutated by an unrelated async event before the "commit" happens, letting the invariant be exceeded. The `WorkflowMetadataHandler.Authorize` function in the chainlink gateway has the same structural bug for JWT replay protection: it checks `isReplay` and only records usage (`recordUsage`) after several more (non-atomic) steps, using two separate lock acquisitions instead of a single atomic check-and-set.

### Finding Description
`Authorize` is the entry point used to validate HTTP-trigger JWTs from workflow senders [1](#0-0) . It performs:
1. `h.jwtCache.isReplay(claims.ID)` — read-only check under `jwtReplayCache.mu.RLock()` [2](#0-1) .
2. Several unrelated map lookups (`h.authorizedKeys[workflowID]`, key membership check) [3](#0-2) .
3. Only then `h.jwtCache.recordUsage(claims.ID)` — a separate write under `jwtReplayCache.mu.Lock()` [4](#0-3) .

Because `isReplay` and `recordUsage` are two independent, non-atomic critical sections (`jwtReplayCache` uses `sync.RWMutex`, and the check happens with its own lock that is released before `recordUsage` acquires a new lock), two (or more) concurrent requests carrying the identical JWT (same `jti`) can both pass `isReplay` == false before either calls `recordUsage`. This mirrors the LooksRare pattern exactly: the "should I allow this" check and the "commit that it happened" step are separated by an intervening window during which concurrent/asynchronous activity (in LooksRare: pause/unpause + VRF callback; here: a second in-flight HTTP request with the same token) can invalidate the assumption made at check time.

### Impact Explanation
JWTs used for HTTP-trigger authentication are meant to be single-use (`jti` claim, replay cache) to prevent request replay. If the race is won, an attacker (or a legitimate but naive client resending in parallel) can get one JWT accepted by the gateway multiple times concurrently, each of which is forwarded to the DON member nodes as a distinct authorized trigger invocation of the workflow (`gateway.AuthorizedKey`-scoped access, see `Authorize`'s return value used downstream). This breaks the intended single-use invariant of the token and could let an attacker who intercepts/replays a single valid signed JWT trigger a workflow run more than once within the same authorization window, i.e., an authentication/quota bypass on the internet-facing gateway.

### Likelihood Explanation
This requires two requests carrying the same JWT to arrive concurrently, which an attacker (or a client with automatic retries) fully controls by simply firing multiple simultaneous requests with an intercepted/leaked JWT before the legitimate token expiry. No node compromise or special privilege is required — it is exploitable from an unprivileged HTTP client hitting the gateway's trigger endpoint. This makes it a real, if narrow-window, race condition reachable purely from client-controlled concurrency, matching the "unprivileged actor" scope of this bug class.

### Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-set operation performed under one lock acquisition (e.g., add a method like `checkAndRecord(jti string) bool` on `jwtReplayCache` that takes the write lock once, checks existence, and inserts atomically, returning false if already present). Replace the current two-call pattern in `Authorize` with this atomic call, performed as early as possible (ideally immediately after JWT signature verification) so that only one of the racing requests can proceed.

### Proof of Concept
Conceptual (Go, illustrating the race window in `Authorize`):
```go
// Two goroutines call Authorize with the same JWT (same claims.ID) concurrently.
go handler.Authorize(workflowID, sameToken, req1)
go handler.Authorize(workflowID, sameToken, req2)

// Inside jwtReplayCache:
// goroutine A: isReplay(jti) -> false (RLock/RUnlock)
// goroutine B: isReplay(jti) -> false (RLock/RUnlock)   <- race window, both pass
// goroutine A: recordUsage(jti)                          (Lock/Unlock)
// goroutine B: recordUsage(jti)                          (Lock/Unlock) -- too late, already authorized
```
Both requests pass authorization and are forwarded downstream as valid authorized trigger invocations, defeating the intended single-use replay protection — the same "check happens, but the enforcing side-effect committed too late relative to a concurrent event" pattern as the LooksRare deposit-count bypass.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-90)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-104)
```go
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
