Based on my investigation, I found the strongest analog: in the gateway Vault handler, `req.ID` is fully attacker-supplied *before* authorization and is used as the key into a single, DON-wide shared map (`h.activeRequests`), with the owner-prefix being stamped only *after* authorization.

### Title
Unauthenticated public-key requests can collide on attacker-chosen request IDs in the shared `activeRequests` map, allowing pre-auth request-slot squatting/DOS in the Vault gateway handler - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway `handler` keeps a single map, `activeRequests`, keyed by `req.ID` and shared across **all** callers of the DON [1](#0-0) . For `MethodPublicKeyGet` — which explicitly "don't require authorization" — the raw, fully user-controlled `req.ID` is used to create the entry directly, with no owner prefixing at all [2](#0-1) . `newActiveRequest` only guards against an ID that is already present, returning an error otherwise [3](#0-2) .

This mirrors the reported bug class: a shared, unpartitioned piece of state (`totalDebt` / here, `activeRequests` keyed by a caller-chosen identifier) can be manipulated by an unprivileged actor to interfere with another caller's in-flight request, because the code assumes IDs are effectively private/unique per caller but does not enforce that before the entry is created.

### Finding Description
For all *authorized* vault methods (`SecretsCreate/Update/Delete/List`), the request ID is only namespaced by owner **after** `AuthorizeRequest` succeeds, inside `authorizeAndStamp`: `prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID` [4](#0-3) . This happens before `h.newActiveRequest` is ever called in `HandleJSONRPCUserMessage`, so by the time the map entry is created, the key is namespaced and different owners naturally can't collide.

However, `MethodPublicKeyGet` explicitly bypasses the whole `requestProcessor.ProcessRequest` / authorization / prefixing pipeline: "Public key requests don't require authorization... Let's process this request right away" [2](#0-1) . The raw `req.ID` supplied by the caller is inserted straight into the shared `activeRequests` map. Since `newActiveRequest` rejects duplicate IDs with `"request ID already exists: " + req.ID` [3](#0-2) , an unprivileged caller who can guess or observe another caller's chosen `req.ID` (e.g. sequential/low-entropy client IDs, or via race conditions) can pre-register that same ID for a `PublicKeyGet` call, causing the legitimate caller's subsequent request with the same ID to be rejected outright — a request-level denial of service, analogous to how `repayDebt()` let anyone touch shared accounting state (`totalDebt`) that should have been partitioned per borrower.

### Impact Explanation
This is scoped to `MethodPublicKeyGet`, which the handler already treats as low-risk from a data standpoint (no secrets involved) and heavily caches (`cachedPublicKeyGetResponse`) to make repeated collisions unlikely in practice, since it is normally served synchronously once cached [2](#0-1) . Before the cache is warm (e.g., right after DON startup, or if cache invalidation code paths clear it), an attacker sending public-key requests with colliding IDs could cause other callers' concurrent public-key requests to fail with "request ID already exists," a targeted denial of service against specific request IDs rather than the whole system.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires (a) the public key not being cached, and (b) the attacker guessing or observing another caller's exact `req.ID` before that caller's request lands, which is a race and depends on caller-side ID entropy/predictability that this codebase does not control or document. This is a narrower, less impactful analog than the original `repayDebt` finding (no fund loss, no borrowing-market-wide DOS — only isolated public-key request collisions), and is only reachable while the vault public key is not yet cached.

### Recommendation
Prefix or namespace `req.ID` before inserting into `activeRequests` even for `MethodPublicKeyGet` (e.g., using a gateway-generated UUID or a per-connection/per-caller namespace), rather than trusting the raw caller-supplied ID for a globally shared map, consistent with how authorized vault methods already get an owner-prefixed ID before insertion.

### Proof of Concept
1. Ensure the gateway's cached public key is empty (fresh DON/gateway restart, before any `PublicKeyGet` succeeds).
2. Attacker sends `HandleJSONRPCUserMessage` with `Method: vaulttypes.MethodPublicKeyGet` and a guessed `ID` equal to a value the attacker expects a victim client to use next (e.g. `"1"`), which enters `h.newActiveRequest` unmodified [5](#0-4) .
3. Victim sends its own `PublicKeyGet` request using ID `"1"` before the attacker's request completes/expires; `newActiveRequest` returns `"request ID already exists: 1"` [6](#0-5) , denying the victim's request.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L134-152)
```go
type handler struct {
	services.StateMachine
	methodConfig     Config
	donConfig        *config.DONConfig
	don              gwhandlers.DON
	lggr             logger.Logger
	codec            api.JSONRPCCodec
	mu               sync.RWMutex
	stopCh           services.StopChan
	authorizer       vaultcap.Authorizer
	jwtAuth          services.Service
	requestProcessor *vaultcap.GatewayVaultRequestProcessor

	nodeRateLimiter *ratelimit.RateLimiter
	requestTimeout  time.Duration

	writeMethodsEnabled limits.GateLimiter
	activeRequests      map[string]*activeRequest
	metrics             *metrics
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-281)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID
```
