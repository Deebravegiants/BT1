## Analysis

The reported bug class is: **a "consult"/read function returns a cached value without ever triggering the update path, so the cache never becomes fresh.**

The strongest analog reachable from an unprivileged client request in this repo is in the Vault gateway handler's public-key cache: [1](#0-0) .

### Title
Vault gateway `handlePublicKeyGet` cache never refreshes because the periodic refresh ticker short-circuits on its own cache check - (File: `core/services/gateway/handlers/vault/handler.go`)

### Summary
`handlePublicKeyGet` is the "consult"-equivalent function: it is supposed to serve a cached master public key while periodically refreshing it from the DON nodes. Instead, once the cache is populated a single time, it can never be refreshed again for the lifetime of the gateway process, because the periodic refresh path re-uses the very same cache-check that short-circuits the refresh.

### Finding Description
On startup and every subsequent minute, a ticker calls `fetchVaultPublicKey`, which builds a synthetic `MethodPublicKeyGet` request and calls `h.handlePublicKeyGet(ctx, ar)` to "periodically, fetch vault public key, so we can cache it": [2](#0-1)  and [3](#0-2) .

However, `handlePublicKeyGet` itself checks the cache first and returns immediately if it is non-nil, *without ever forwarding the request to the vault nodes*: [4](#0-3) 

This means the "refresh" ticker's call to `handlePublicKeyGet` is a no-op once the cache is warm: it just returns the already-cached bytes and never calls `fanOutToVaultNodes`. The only way the cache is ever actually updated is via `tryCachePublicKeyResponse`, which is only invoked from `HandleNodeMessage` in response to a *real* node round trip: [5](#0-4)  and [6](#0-5) .

Since the first successful population of the cache happens on gateway startup (assuming nodes respond), the periodic refresh ticker degenerates into "read the cache" forever, and the cache is populated exactly once, never invalidated by TTL. Notably, a constant `defaultPublicKeyGetCacheDurationSeconds = 300` is declared, suggesting the intended design was a 5-minute TTL-based cache, but this constant is never referenced anywhere else in the file — confirming the TTL/invalidation logic was never wired up: [1](#0-0) .

The same stale cached key is also used to authorize/decrypt every subsequent unprivileged user request via `getCachedPublicKey()`, which only checks for nil, not for staleness: [7](#0-6)  and is passed into request authorization here: [8](#0-7) .

### Impact Explanation
If the underlying Vault DON's master public key is ever rotated (e.g., due to a compromised key, DON membership/config change, or scheduled key rotation), the gateway will continue to hand out the stale/old public key to every unprivileged client calling `MethodPublicKeyGet` indefinitely (until process restart), and will continue to use that stale key object for authorizing/validating all subsequent `secrets.*` requests via `requestProcessor.ProcessRequest`. This can cause:
- Clients encrypting new secrets under a rotated-out (potentially compromised) master key.
- The gateway rejecting legitimate requests that were correctly encoded against the new key, or, depending on `ProcessRequest`'s semantics, accepting/validating requests against stale key material rather than the currently valid one.

This is a direct, unprivileged-client-facing correctness/security issue in gateway key-material handling — not a peer/network/mocked-only issue.

### Likelihood Explanation
This triggers deterministically any time the vault DON's public key changes after the gateway process has already cached one successfully (which will typically happen on the very first successful fetch after startup). No attacker action is required to reach the code path — every `MethodPublicKeyGet` request and every authorized `secrets.*` request goes through this stale cache. The only variable is whether/when a key rotation event occurs upstream, but the code guarantees the gateway will never observe it without a restart.

### Recommendation
Decouple "read from cache" from "refresh cache": the ticker-driven `fetchVaultPublicKey` path must bypass the cache-check in `handlePublicKeyGet` and always fan out to nodes, updating the cache via `tryCachePublicKeyResponse` on success. Additionally, wire up the already-declared `defaultPublicKeyGetCacheDurationSeconds` TTL so `getCachedPublicKey` treats an entry as stale after that duration and forces a real refresh, similar to how `consult()` in the referenced report should call `update()` before reading stored averages.

### Proof of Concept
1. Start the gateway; on the first `tickerVaultPublicKeyRefresh` tick (or the first user `MethodPublicKeyGet` request), `tryCachePublicKeyResponse` populates `h.cachedPublicKeyGetResponse`/`h.cachedPublicKeyObject`.
2. Rotate the Vault DON's master key on the node side (out of scope for this repo, but a supported operational event).
3. Every subsequent minute, `fetchVaultPublicKey` → `handlePublicKeyGet` sees `cachedPublicKey != nil` at [9](#0-8)  and returns the old cached bytes without calling `fanOutToVaultNodes`, so `tryCachePublicKeyResponse` is never invoked again.
4. All future unprivileged `MethodPublicKeyGet` responses and `secrets.*` authorization checks continue to use the old key indefinitely, confirmed by the absence of any TTL check in `getCachedPublicKey` at [7](#0-6) .

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L43-46)
```go
const (
	defaultCleanUpPeriod                    = 5 * time.Second
	defaultPublicKeyGetCacheDurationSeconds = 300
)
```

**File:** core/services/gateway/handlers/vault/handler.go (L279-298)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L404-427)
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

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
```

**File:** core/services/gateway/handlers/vault/handler.go (L526-533)
```go
	switch resp.Method {
	case vaulttypes.MethodPublicKeyGet:
		h.tryCachePublicKeyResponse(resp, l)
	default:
		// Do nothing for other methods
	}

	return h.sendSuccessResponse(ctx, l, ar, resp)
```

**File:** core/services/gateway/handlers/vault/handler.go (L549-583)
```go
func (h *handler) tryCachePublicKeyResponse(resp *jsonrpc.Response[json.RawMessage], l logger.Logger) {
	if resp.Result == nil {
		l.Debugw("no result in public key response, not caching")
		return
	}

	r := &vaultcommon.GetPublicKeyResponse{}
	err := h.unmarshal(bytes.NewReader(*resp.Result), r)
	if err != nil {
		l.Debugw("failed to unmarshal public key response, not caching", "error", err)
		return
	}

	if r.PublicKey == "" {
		l.Debugw("no public key in unmarshaled response, not caching", "response", resp, "result", r)
		return
	}
	masterPublicKey := tdh2easy.PublicKey{}
	masterPublicKeyBytes, err := hex.DecodeString(r.PublicKey)
	if err != nil {
		l.Debugw("failed to decode master public key string", "error", err)
		return
	}
	err = masterPublicKey.Unmarshal(masterPublicKeyBytes)
	if err != nil {
		l.Debugw("failed to unmarshal master public key", "error", err)
		return
	}

	h.mu.Lock()
	h.cachedPublicKeyGetResponse = *resp.Result
	h.cachedPublicKeyObject = &masterPublicKey
	h.mu.Unlock()
	l.Debugw("successfully cached public key response")
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L680-690)
```go
func (h *handler) getCachedPublicKey() ([]byte, *tdh2easy.PublicKey) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if h.cachedPublicKeyGetResponse == nil {
		return nil, nil
	}
	copied := make([]byte, len(h.cachedPublicKeyGetResponse))
	copy(copied, h.cachedPublicKeyGetResponse)
	cachedPublicKeyCopy := *h.cachedPublicKeyObject
	return copied, &cachedPublicKeyCopy
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L692-708)
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		l.Debugw("returning cached public key response")
		return h.sendSuccessResponse(ctx, l, ar, &jsonrpc.Response[json.RawMessage]{
			Version: jsonrpc.JsonRpcVersion,
			ID:      ar.req.ID,
			Method:  ar.req.Method,
			Result:  (*json.RawMessage)(&publicKeyResponseBytes),
		})
	}

	l.Debugw("cache stale: forwarding request to nodes", "now", h.clock.Now())
	return h.fanOutToVaultNodes(ctx, l, ar)
}
```
