Audit Report

## Title
Unauthenticated flooding of `MethodPublicKeyGet` requests causes unbounded growth of the gateway vault handler's `activeRequests` map - ([File: core/services/gateway/handlers/vault/handler.go])

## Summary
`HandleJSONRPCUserMessage` in the Vault gateway handler explicitly bypasses authorization for `vaulttypes.MethodPublicKeyGet` requests, and whenever `getCachedPublicKey()` returns `nil`, it calls `h.newActiveRequest(req, callback)`, inserting an attacker-controlled `req.ID` into the shared `h.activeRequests` map with no authentication, no rate limiting, and no bound other than a 30-second (default) TTL enforced by a periodic reaper. An unauthenticated caller who sends a stream of requests with unique IDs during any window where the public key cache is empty (which is guaranteed for up to 1 minute after gateway startup, and indefinitely if `fetchVaultPublicKey` keeps failing) can grow this map — and the associated per-entry `responses` maps and `callback` references — without bound, limited only by attacker throughput versus the reaper's fixed cleanup interval.

## Finding Description
The code path is exactly as cited: [1](#0-0)  shows that `MethodPublicKeyGet` is processed "right away" without authorization, and when the cache misses, `h.newActiveRequest(req, callback)` is invoked before any auth/rate-limit check. `newActiveRequest` performs only a duplicate-ID check and inserts unconditionally: [2](#0-1) . The only pre-insertion validation on `req.ID` is emptiness/length (≤200 chars), performed generically for all methods: [3](#0-2) .

Contrast this with the other Vault methods (`MethodSecretsCreate/Update/Delete/List`), which only reach `newActiveRequest` after `h.requestProcessor.ProcessRequest` authorizes the caller: [4](#0-3) . `MethodPublicKeyGet` is the only method that reaches `newActiveRequest` with zero authorization.

Cleanup is purely time-based, not count/rate-based: entries are reaped by a fixed ticker only after they exceed `requestTimeout` (30s default): [5](#0-4) [6](#0-5) [7](#0-6) .

Critically, the cache-population window is not a narrow race. On `Start`, the public-key refresh ticker only fires after its first full interval (1 minute) — there is no immediate/eager population call — so `cachedPublicKeyGetResponse`/`cachedPublicKeyObject` remain `nil` for up to 1 minute after every gateway (re)start, and indefinitely longer if `fetchVaultPublicKey` keeps failing/timing out: [8](#0-7) [9](#0-8) . During that window, every incoming `MethodPublicKeyGet` request — from any unauthenticated caller — falls into the vulnerable insertion path.

I confirmed there is no upstream mitigation: the gateway's top-level HTTP request path (`ProcessRequest` in `core/services/gateway/gateway.go`) applies no general per-request-ID rate limiting or authentication gate before dispatching to `HandleJSONRPCUserMessage`; the only universal control is a request body size limiter (`MaxRequestBytesLimiter`) at the HTTP server layer, which does not bound the number of distinct requests/IDs an unauthenticated client can send.

## Impact Explanation
This allows an unauthenticated network client to drive unbounded server-side memory allocation on the gateway, keyed by attacker-chosen request IDs, during the (non-trivial, recurring) window in which the vault public key cache is unpopulated. Each entry allocates an `activeRequest` struct plus a `responses` map and retains a `callback` reference, so sustained flooding can exhaust gateway memory and degrade or crash the gateway process — a denial-of-service against an internet-facing gateway component, consistent with the in-scope "gateway/handlers/caches" DoS impact class.

## Likelihood Explanation
Exploitation requires no credentials, JWT, or allowlist membership — only network reachability to the gateway's Vault JSON-RPC endpoint and the ability to vary `req.ID` (≤200 chars) per request. The vulnerable window is deterministically present on every gateway startup (up to the first successful key fetch, occurring no earlier than the first 1-minute ticker tick) and can be perpetuated by causing/observing `fetchVaultPublicKey` failures. This makes the exploit straightforward, repeatable, and not dependent on a narrow timing race.

## Recommendation
- Apply a per-IP/per-connection rate limit (or a small global unauthenticated-request quota) to `MethodPublicKeyGet` requests before they reach `newActiveRequest`, independent of the caching optimization.
- Bound the number of concurrently outstanding unauthenticated `activeRequests` entries, or use a separate, capped data structure for public-key-get bookkeeping instead of sharing the general `activeRequests` map.
- Coalesce concurrent unauthenticated public-key fetches into a single in-flight request (e.g., via a `singleflight.Group`, as already used in `core/services/gateway/handlers/capabilities/v2/response_cache.go`) rather than creating one `activeRequest` per caller/per unique ID.
- Eagerly populate the public key cache at `Start` (rather than waiting for the first 1-minute ticker) to shrink the always-present post-restart exposure window, and revisit the comment asserting that caching alone is sufficient to prevent DoS.

## Proof of Concept
1. Start a gateway Vault handler instance (or wait for a restart) so that `cachedPublicKeyGetResponse`/`cachedPublicKeyObject` are `nil` (guaranteed for up to 1 minute post-start, per `Start`'s ticker configuration), or force repeated `fetchVaultPublicKey` failures.
2. As an unauthenticated client, repeatedly POST JSON-RPC requests to the gateway's Vault DON endpoint:
```json
{"jsonrpc":"2.0","id":"<unique-value-N>","method":"secrets_getPublicKey","params":{}}
```
varying `<unique-value-N>` (e.g., UUIDs, ≤200 chars) on each request, at a rate exceeding the reaper's effective throughput (entries persist up to `requestTimeout`, default 30s, before the periodic cleanup removes them).
3. Each request enters `HandleJSONRPCUserMessage`, observes `cachedPublicKey == nil`, and calls `newActiveRequest`, adding an entry to `h.activeRequests` — no `req.Auth` check occurs for this method.
4. Observe `h.activeRequests` map size and process memory grow in proportion to the flood rate for as long as the cache-miss window persists.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L217-219)
```go
	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = 30
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L271-300)
```go
func (h *handler) Start(_ context.Context) error {
	return h.StartOnce("VaultHandler", func() error {
		h.lggr.Debug("starting vault handler")
		if h.jwtAuth != nil {
			if err := h.jwtAuth.Start(context.Background()); err != nil {
				return fmt.Errorf("failed to start JWTBasedAuth: %w", err)
			}
		}
		go func() {
			ctx, cancel := h.stopCh.NewCtx()
			defer cancel()
			ticker := h.clock.NewTicker(defaultCleanUpPeriod)
			tickerVaultPublicKeyRefresh := h.clock.NewTicker(1 * time.Minute)
			defer ticker.Stop()
			defer tickerVaultPublicKeyRefresh.Stop()
			for {
				select {
				case <-ticker.Chan():
					h.removeExpiredRequests(ctx)
				case <-tickerVaultPublicKeyRefresh.Chan():
					// periodically, fetch vault public key, so we can cache it
					h.fetchVaultPublicKey(ctx)
				case <-h.stopCh:
					return
				}
			}
		}()
		return nil
	})
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L318-358)
```go
func (h *handler) fetchVaultPublicKey(ctx context.Context) {
	ctx, cancel := context.WithDeadline(ctx, h.clock.Now().Add(10*time.Second))
	defer cancel()
	param := vaultcommon.GetPublicKeyRequest{}
	paramBytes, err := json.Marshal(param)
	if err != nil {
		h.lggr.Errorw("fetchVaultPublicKey: failed to marshal get public key request", "error", err)
		return
	}
	getPublicKeyRequest := jsonrpc.Request[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      uuid.New().String(),
		Method:  vaulttypes.MethodPublicKeyGet,
		Params:  (*json.RawMessage)(&paramBytes),
	}
	h.lggr.Debugw("fetchVaultPublicKey: trying to fetch vault public key", "request", getPublicKeyRequest)
	callback := handlerscommon.NewCallback()
	ar, err := h.newActiveRequest(getPublicKeyRequest, callback)
	if err != nil {
		h.lggr.Errorw("fetchVaultPublicKey: failed to create new activeRequest", "error", err)
		return
	}
	err = h.handlePublicKeyGet(ctx, ar)
	if err != nil {
		h.lggr.Errorw("fetchVaultPublicKey: failed to fetch vault public key", "request", getPublicKeyRequest, "error", err)
		return
	}
	response, err := callback.Wait(ctx)
	if err != nil {
		h.lggr.Errorw("fetchVaultPublicKey: failed to fetch vault public key", "request", getPublicKeyRequest, "error", err)
		return
	}
	httpStatus := api.ToHTTPErrorCode(response.ErrorCode)
	jsonCodec := api.JSONRPCCodec{}
	jsonResp, _ := jsonCodec.DecodeRawRequest(response.RawResponse, "")
	if httpStatus != http.StatusOK {
		h.lggr.Errorw("fetchVaultPublicKey: failed to fetch vault public key", "request", getPublicKeyRequest, "httpStatusCode", httpStatus, "rawResponse", jsonResp)
		return
	}
	h.lggr.Debugw("fetchVaultPublicKey: successfully fetched vault public key", "request", getPublicKeyRequest, "rawResponse", jsonResp)
}
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-401)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
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

**File:** core/services/gateway/handlers/vault/handler.go (L426-441)
```go
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
