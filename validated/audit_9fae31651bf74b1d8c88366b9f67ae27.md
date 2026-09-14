## Finding

Based on the report's bug class — an unprivileged actor cheaply occupying a shared identifier slot to cause another party's legitimate action to fail — I found a directly analogous pattern in the Vault gateway's request-ID handling.

### Title
Unauthenticated request-ID squatting can block another caller's vault secrets operation - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway-side Vault handler tracks in-flight requests in a single, handler-wide map keyed only by the caller-supplied JSON-RPC `req.ID`. Requests for `MethodPublicKeyGet` are processed **without any authorization check**, yet they claim a slot in the same global map used by authorized `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList` requests. Any unauthenticated caller can therefore occupy an arbitrary `req.ID` for up to the configured request timeout, causing a legitimate (authorized) request that later arrives with the same ID to be rejected.

### Finding Description
`HandleJSONRPCUserMessage` special-cases `MethodPublicKeyGet` to skip authorization entirely ("Public key requests don't require authorization") and immediately calls `newActiveRequest(req, callback)`: [1](#0-0) 

`newActiveRequest` stores the request in a single map, `h.activeRequests`, keyed purely by the attacker-controlled `req.ID`, and rejects the request outright if that ID is already present: [2](#0-1) 

Crucially, this map is **not scoped per-method or per-caller** — the same map and the same uniqueness check apply to authorized secret-mutation methods. For those methods, authorization is performed first, and only *after* it succeeds does the handler call `newActiveRequest`: [3](#0-2) 

Because `MethodPublicKeyGet` requires no authorization and no proof of ownership over any secret, an attacker can send a stream of `PublicKeyGet` requests using arbitrary or predictable `req.ID` values (e.g., small integers or UUIDs that another integration happens to reuse) at essentially zero cost, occupying each ID in `activeRequests` for up to `RequestTimeoutSec` (configurable, e.g. 30s in tests). If a legitimate, already-authorized `SecretsCreate`/`Update`/`Delete`/`List` request for a *different* workflow owner happens to use the same `req.ID`, `newActiveRequest` fails with `"request ID already exists"`, and the whole authorized request is rejected even though authorization already succeeded: [4](#0-3) 

This mirrors the report's bug class: an unprivileged, low/no-cost action (unauthenticated `PublicKeyGet`) manipulates shared state (a global identifier namespace) to cause a legitimate, authorized action by another party to revert/fail, and the griefer's own action is cheap to repeat.

### Impact Explanation
Impact is Denial-of-Service / griefing on a specific request, not fund loss or secret disclosure: a legitimate caller's authorized `SecretsCreate`/`Update`/`Delete`/`List` call can be transiently blocked if its `req.ID` collides with one squatted by an unauthenticated attacker via `PublicKeyGet`. Severity is bounded by the fact that most integrations use random UUIDs for `req.ID` (as shown in the system-tests helpers), which makes collision hard to target deliberately unless the victim uses low-entropy/sequential IDs — but nothing in the code enforces ID unpredictability or per-caller/per-method scoping, so the primitive exists and is fully attacker-reachable without authentication.

### Likelihood Explanation
Likelihood is Low-to-Medium: exploitation requires the attacker to guess or observe the victim's chosen `req.ID` ahead of time. It is trivially reachable (no auth needed) and cheap to repeat, but not automatically effective against callers using high-entropy IDs. It is more concerning for any client library or integration that uses predictable/sequential IDs.

### Recommendation
- Scope `activeRequests` (and the duplicate-ID check) either per authenticated owner/DON or separately for unauthenticated methods (`PublicKeyGet`) vs. authorized secret-mutation methods, so an unauthenticated request can never collide with an authorized one.
- Alternatively, require `PublicKeyGet` requests to also pass through `newActiveRequest`'s uniqueness check keyed by a namespaced ID incorporating the method (e.g., `method + ":" + req.ID`) rather than the raw client-supplied ID.

### Proof of Concept
1. Attacker sends `{"method":"vault_publicKeyGet","id":"X"}` to the gateway with no `Auth` field — accepted without authorization and inserted into `activeRequests["X"]` per [1](#0-0) .
2. Before that entry expires (`RequestTimeoutSec`), the victim submits an authorized `{"method":"vault_secretsCreate","id":"X", ...}` request; authorization succeeds, but `newActiveRequest` returns `"request ID already exists: X"` per [4](#0-3) , causing the victim's authorized create-secret operation to fail.

### Citations

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
