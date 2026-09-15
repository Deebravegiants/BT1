Based on my research, I found a structurally similar issue in the chainlink gateway's confidential relay handler, though with an important caveat about verification limits noted below.

### Title
Confidential relay gateway handler creates unowned, attacker-keyed active requests with no cache-size bound - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
`HandleJSONRPCUserMessage` in the confidential relay gateway handler creates an in-memory "active request" entry keyed solely by the client-supplied `req.ID`, with no ownership binding to the caller and no bound on the total number of concurrent entries, mirroring the UFO bug class of unowned, attacker-keyed session/state objects enabling squatting and resource-exhaustion denial of service.

### Finding Description
`HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and ≤200 characters before calling `newActiveRequest`, which inserts the request into `h.activeRequests` keyed purely by the raw `req.ID` string supplied by the caller: [1](#0-0) 

`newActiveRequest` performs a simple presence check and rejects only exact-duplicate IDs, but does not scope the key by sender/owner: [2](#0-1) 

This differs from two safer patterns elsewhere in the same codebase:
- The generic `common.RequestCache` scopes its cache key by `{sender, messageID}` (a compound `globalID`) rather than by message ID alone, and additionally enforces a `maxCacheSize` bound, rejecting new entries once the cache is full: [3](#0-2) 
- The vault handler performs authorization (`h.requestProcessor.ProcessRequest`) and rewrites/stamps the request ID with the authorized owner's identity *before* the ID is used as the active-request cache key, so IDs are effectively owner-namespaced: [4](#0-3) 

The confidential relay handler has neither protection: any caller who can reach `HandleJSONRPCUserMessage` can pick an arbitrary ID string (up to 200 chars) and immediately occupy that slot in `h.activeRequests` — an unowned, unbounded map — exactly analogous to the UFO `get_or_create_session` flaw where a session was created without an `owner_client_id` and keyed by an attacker-chosen `session_id`.

### Impact Explanation
Two consequences follow directly from the code:
1. **ID squatting / DoS against a legitimate caller**: if an attacker can predict or learn the request ID a legitimate workflow/execution will use (e.g., because IDs are derived from workflow/execution identifiers, as suggested by `requestLabels{WorkflowID, ExecutionID}`), they can submit it first. The legitimate caller's subsequent request then fails with `"request ID already exists"`, denying them service, similar to the UFO squatting scenario.
2. **Memory exhaustion via phantom entries**: because there is no `maxCacheSize`-style cap (unlike `common.RequestCache`), a client can keep inserting unique attacker-chosen IDs to grow `h.activeRequests` until `requestTimeout` (default 30s) sweeps them, but a sustained flood can still keep the map large indefinitely.

### Likelihood Explanation
This requires the attacker to be able to reach `HandleJSONRPCUserMessage` with a chosen `req.ID`. **I was not able to fully verify, within the available tool budget, what authentication/allowlist gate sits in front of this handler** (i.e., whether callers must already be an allowlisted/authenticated DON member or an arbitrary internet client can reach it directly through the gateway's public entrypoint). My search for `allowlist`/`Allowlist` references under `core/services/gateway/**` only turned up matches in the `capabilities` handler and test files, not in `confidentialrelay`, which is inconclusive rather than confirmatory — it may mean allowlisting happens elsewhere (e.g., in the gateway's routing/multihandler layer) rather than in this file.

### Recommendation
- Scope `activeRequests` keys by the authenticated caller identity (or by a value derived from an authorization step, similar to the vault handler's owner-prefixed ID) rather than by raw, unauthenticated `req.ID`.
- Add an explicit maximum size to `h.activeRequests` (mirroring `common.RequestCache.maxCacheSize`) so an attacker cannot grow it without bound even within the timeout window.

### Proof of Concept
Not independently executed; based on static code reading. A caller reaching `HandleJSONRPCUserMessage` with a chosen `req.ID` matching (or preceding) a legitimate caller's ID would occupy `h.activeRequests[req.ID]`, causing the legitimate caller's request with the same ID to fail with `"request ID already exists"` per [5](#0-4) , and repeated distinct IDs would grow the map without a size cap until the periodic `removeExpiredRequests` sweep runs.

**Caveat**: Given the scan rules require rejecting "no-impact" and requiring "the strongest reachable chainlink path from an unprivileged client request," and given I could not confirm the exact authentication boundary in front of this handler within my remaining tool budget, treat this finding as a plausible but not fully proven analog — a Devin session with broader code access could verify the gateway's dispatch/authentication path (`core/services/gateway/multihandler.go` and the gateway's HTTP/WS entrypoint) to confirm whether `confidentialrelay.HandleJSONRPCUserMessage` is reachable by an unprivileged/unallowlisted caller.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L34-66)
```go
type globalID struct {
	sender string
	id     string
}

type pendingRequest[T any] struct {
	handlers.Callback
	responseData *T
	timeoutTimer *time.Timer
	mu           sync.Mutex
}

func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-441)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```
