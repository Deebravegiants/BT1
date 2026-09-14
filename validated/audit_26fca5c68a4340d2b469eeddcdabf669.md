### Title
Unauthenticated DoS via unbounded `MethodPublicKeyGet` requests filling the Vault gateway handler's `activeRequests` map - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` allows any unauthenticated caller to trigger creation of an in-memory `activeRequest` entry and a fan-out to DON nodes via the `vaulttypes.MethodPublicKeyGet` path, without any global or per-caller quota enforced before the entry is created. This mirrors the reported bug class: an attacker can flood the internal request queue/state with cheap requests, delaying or starving legitimate users, since eviction only happens on a fixed timer (`defaultCleanUpPeriod` = 5s) rather than being bounded by admission control.

### Finding Description
In `HandleJSONRPCUserMessage`, the `MethodPublicKeyGet` branch is explicitly carved out to skip authorization: [1](#0-0) 

If the cached public key is unavailable (e.g., cache expired, or handler state reset), every incoming request creates a new `activeRequest` and calls `handlePublicKeyGet`, which fans the request out to all DON nodes: [2](#0-1) 

`newActiveRequest` only rejects a request if its exact `req.ID` string already exists in the map — it performs no check on the total number of concurrently pending requests, nor any per-caller/global rate limit before insertion: [3](#0-2) 

Because request IDs are attacker-controlled (unique per request), an unauthenticated caller can submit an unbounded stream of distinct `MethodPublicKeyGet` requests, each one:
1. Acquiring `h.mu` (a single mutex shared by all active-request map operations, `HandleNodeMessage` lookups, and the cleanup sweep),
2. Growing the `activeRequests` map unboundedly,
3. Triggering `don.SendToNode` fan-out to every DON member for each request.

The only reclamation mechanism is a fixed 5-second ticker (`defaultCleanUpPeriod`) that walks the entire map and evicts entries older than `requestTimeout` (default 30s): [4](#0-3) [5](#0-4) 

This gives an attacker a 30-second window (per request) during which the map can grow arbitrarily, and the cleanup sweep itself must acquire the same `h.mu` lock used by every legitimate request path (`newActiveRequest`, `getActiveRequest`, `HandleNodeMessage`), so a large map directly increases lock-hold time and contention affecting concurrent legitimate `SecretsCreate`/`SecretsList`/etc. requests.

This is the internet-facing gateway equivalent of the reported relayer-queue DoS: an unprivileged actor floods an internal per-request state/queue with cheap, unauthenticated requests, degrading service for other users of the same DON-facing handler.

### Impact Explanation
An unauthenticated caller can:
- Force unbounded memory growth in the gateway process via the `activeRequests` map (bounded only by the 30s timeout × request rate, which is itself unbounded absent global admission control on this specific method).
- Force repeated fan-out traffic (`don.SendToNode`) to every DON member for each spam request, consuming DON-node bandwidth and gateway↔DON connection resources.
- Increase mutex contention on `h.mu`, which is shared with all other vault methods (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`), degrading availability for legitimate authorized users — directly analogous to Alice's request being delayed by Eve's flood in the original report.

### Likelihood Explanation
High: `MethodPublicKeyGet` is intentionally exempt from authorization (per the code comment "Public key requests don't require authorization"), reachable by any client that can send JSON-RPC requests to the gateway's public HTTP endpoint. The only mitigating factor is the aggressive public-key caching noted in the code comment, which reduces — but does not eliminate — the window in which this path is reachable (cache misses, handler restarts, or cache-population races still hit the uncapped path).

### Recommendation
- **Short term:** Apply a global (and/or per-source) rate limiter to the `MethodPublicKeyGet` code path before `newActiveRequest` is called, and/or cap the maximum size of `h.activeRequests`, rejecting new entries once the cap is reached.
- **Long term:** Move request admission control ahead of state creation for all methods that can be reached pre-authorization, and consider partitioning `activeRequests`/locks so that a single flood on one method cannot starve unrelated authorized request paths sharing the same mutex.

### Proof of Concept
1. An attacker (no credentials required) repeatedly sends JSON-RPC requests to the gateway with `method: "secrets_publicKey_get"` and a fresh unique `id` on each call.
2. As long as the cached public key is unset or a cache miss occurs, each call reaches `HandleJSONRPCUserMessage` → creates a new `activeRequest` in `h.activeRequests` and triggers `handlePublicKeyGet`, fanning out to every DON node [1](#0-0) .
3. Because IDs are unique and no quota check exists in `newActiveRequest` [3](#0-2) , the attacker can sustain this indefinitely, growing the map and increasing lock contention on `h.mu` until legitimate `SecretsCreate`/`SecretsList` calls from authorized users experience increased latency or failures.

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

**File:** core/services/gateway/handlers/vault/handler.go (L404-417)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
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
