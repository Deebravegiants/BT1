### Title
Unauthenticated `PublicKeyGet` requests can reserve request IDs in the gateway vault handler's shared `activeRequests` map, blocking a legitimate authorized secrets request that later uses the same ID - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
In the report's ERC1155 bug, an unprivileged actor could occupy state at a not-yet-authorized/deployed address, and once the real party arrived, a strict "exactly one entry" check made the operation permanently revert (availability loss, no fund loss). The Chainlink gateway vault handler has an analogous pattern: a single, global `activeRequests` map keyed only by the client-supplied `req.ID` is used for *all* JSON-RPC vault methods, including `MethodPublicKeyGet`, which requires **no authorization at all**.

### Finding Description
`HandleJSONRPCUserMessage` special-cases `vaulttypes.MethodPublicKeyGet` and processes it immediately, without going through `h.requestProcessor.ProcessRequest` (the authorization step used for `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList`): [1](#0-0) 

When the cached public key is missing, it calls `h.newActiveRequest(req, callback)` directly, using the caller-supplied `req.ID` with no ownership or authentication check: [2](#0-1) 

`newActiveRequest` inserts into a single global map (`h.activeRequests`) keyed purely by `req.ID`, with a check-then-set that rejects the request if that ID already exists — regardless of which method or caller originally claimed it: [3](#0-2) 

For the authorized secrets methods, the same `newActiveRequest` call happens *after* authorization succeeds, using the same shared map/keyspace: [4](#0-3) 

Because the map is global and keyed only on a client-controlled string (bounded only by a 200-character length check, not by uniqueness/ownership scoping), an unauthenticated caller can pre-populate an entry for an arbitrary `req.ID` via a cost-free `MethodPublicKeyGet` request. If a legitimate, authorized `SecretsCreate`/`Update`/`Delete`/`List` request later arrives using that same ID, `newActiveRequest` returns `"request ID already exists"`, and `HandleJSONRPCUserMessage` aborts the authorized request entirely: [5](#0-4) 

The stale/attacker-planted entry is not evicted immediately; it lives until `removeExpiredRequests` reaps it after `requestTimeout` (default 30s), checked every `defaultCleanUpPeriod` (5s): [6](#0-5) [7](#0-6) 

An attacker can trivially re-arm the block by repeatedly re-sending `PublicKeyGet` for the same ID (or many IDs) before expiry, sustaining the denial for as long as desired — analogous to the report's "always revert" condition, except here it is a sustained denial rather than a fund-safe permanent one.

### Impact Explanation
This is an availability-only issue, matching the judged severity class of the referenced report (no funds at risk, no cross-user data disclosure): a legitimate, correctly authorized `Secrets*` request can be made to fail with `"request ID already exists"` if an unauthenticated attacker has claimed the same ID via the unauthenticated `PublicKeyGet` path, or an attacker can more generally flood the shared `activeRequests` map with many distinct unauthenticated entries to exhaust map capacity / create noise in the handler for the DON's public-facing gateway. No source code or test confirms an application-imposed rate limit or per-sender cap on the number of concurrently in-flight `PublicKeyGet` request IDs beyond the per-node rate limiter used for node *responses* (`h.nodeRateLimiter`, which limits inbound node messages, not inbound user requests) — I could not find a user-request-side rate limiter guarding this specific code path in the code inspected, so the extent of the flooding risk is not fully confirmed and should be verified in a live/staging environment.

### Likelihood Explanation
Likelihood is moderate: reaching this path requires no authentication (`PublicKeyGet` skips `ProcessRequest`), and any actor who can send JSON-RPC user messages to the gateway can attempt this. However, to specifically block a *particular* legitimate request, the attacker needs to predict or observe the victim's `req.ID` in advance, which may not always be practical depending on how the workflow layer generates IDs (this could not be fully verified from the indexed code — request-ID generation for `Secrets*` calls at the caller/workflow layer was not located in this pass). Without ID prediction, the attack still causes generalized noise/DoS on the shared map rather than a precisely targeted block.

### Recommendation
Scope the `activeRequests` map (or its ID collision check) so that unauthenticated `PublicKeyGet` requests cannot collide with authorized secrets requests — e.g., use a composite key that includes the method (or a namespace prefix) rather than a bare `req.ID`, and/or require `PublicKeyGet` requests to also pass through the request processor / a lightweight rate limiter before being allowed to occupy a slot in the shared map. Alternately, keep `PublicKeyGet` pending state in a separate map from the authorized `Secrets*` methods so no cross-method collision is possible at all.

### Proof of Concept
1. An unauthenticated client sends `{"method": "vault_publicKeyGet", "id": "victim-id-123", ...}` to the gateway before the cached public key is warm, causing `h.newActiveRequest` to insert `"victim-id-123"` into `h.activeRequests`: [2](#0-1) 
2. A legitimate, JWT/allowlist-authorized workflow subsequently sends `{"method": "vault_secretsCreate", "id": "victim-id-123", ...}`.
3. `HandleJSONRPCUserMessage` passes authorization, then calls `h.newActiveRequest(req, callback)`, which finds `h.activeRequests["victim-id-123"]` already populated and returns `errors.New("request ID already exists: victim-id-123")`, aborting the legitimate secrets-create call: [8](#0-7) 
4. The attacker can repeat step 1 every few seconds (well under the 30s `requestTimeout`) to keep the block in place indefinitely for that ID, or perform this against a range of IDs to generally interfere with the handler's request bookkeeping.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L43-46)
```go
const (
	defaultCleanUpPeriod                    = 5 * time.Second
	defaultPublicKeyGetCacheDurationSeconds = 300
)
```

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L437-472)
```go
	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}

	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return h.handleSecretsCreate(ctx, ar)
	case vaulttypes.MethodSecretsUpdate:
		return h.handleSecretsUpdate(ctx, ar)
	case vaulttypes.MethodSecretsDelete:
		return h.handleSecretsDelete(ctx, ar)
	case vaulttypes.MethodSecretsList:
		return h.handleSecretsList(ctx, ar)
	default:
		return h.sendResponse(ctx, ar, h.errorResponse(req, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method), nil))
	}
}

func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```
