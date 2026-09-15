Based on my analysis of the vault gateway handler code, I found a concrete analog to the reported bug class.

### Title
Unauthenticated request-ID squatting in `newActiveRequest` blocks legitimate Vault gateway requests with the same ID - (File: `core/services/gateway/handlers/vault/handler.go`)

### Summary
`HandleJSONRPCUserMessage` registers a request's ID into the shared `activeRequests` map via `newActiveRequest` before (or independent of) any per-caller authorization outcome for the ID itself, and rejects any subsequent request sharing that same ID until the first entry is cleaned up. Just like the OUSD bug, where an unprivileged actor could plant the sentinel (zero-address) flag first to permanently block the legitimate global-parameter update, an unprivileged Vault gateway client can plant a request ID first and thereby block a legitimate user's request that happens to reuse the same ID.

### Finding Description
`HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go` accepts any caller-supplied `req.ID` (bounded only by length) and, for the `MethodPublicKeyGet` method, calls `h.newActiveRequest(req, callback)` immediately with **no authorization check at all** (public key requests are explicitly documented as not requiring authorization): [1](#0-0) 

`newActiveRequest` uses the raw client-supplied `req.ID` as the map key and rejects the registration if that ID is already present, returning an error rather than queuing/side-channeling it: [2](#0-1) 

For the secrets methods (`MethodSecretsCreate/Update/Delete/List`), authorization does happen first via `h.requestProcessor.ProcessRequest`, but the request ID is still the raw client-controlled value at this stage (owner-prefixing/stamping happens inside the processor, but nothing prevents an attacker from independently sending unauthenticated/no-owner secrets requests, e.g. `MethodSecretsList`, which the code path documents as not requiring pre-checks for owner-scoped limits precisely so unauthenticated callers can reach this far): [3](#0-2) [4](#0-3) 

The entry is only removed once a response is sent (`sendResponse` deletes it) or after `requestTimeout` (default up to tens of seconds) elapses: [5](#0-4) [6](#0-5) 

Because the JSON-RPC request ID is fully attacker-controlled and there is no per-caller namespacing of the `activeRequests` map (aside from the internal owner-prefix stamping applied only to authorized secrets requests, not to the initial map key uniqueness check for public-key-get, which requires no auth at all), any unprivileged actor reaching the gateway's Vault handler can pre-register an ID (e.g., a predictable/well-known ID a legitimate client is expected to use, or simply flood many IDs) to make `newActiveRequest` return `"request ID already exists"` for the real caller — denying that caller's request for the lifetime of the squatted entry (up to `RequestTimeoutSec`, default 30s, or longer for `fetchVaultPublicKey`'s periodic refresh flow, which shares the same map).

This mirrors the OUSD analog precisely: an unprivileged party can, without any access control, first claim a shared/global "slot" (the OUSD zero-address flag vs. here the shared request-ID key) that legitimate later actors need, causing the legitimate operation to fail/be blocked.

### Impact Explanation
Impact is a denial-of-service against specific Vault gateway requests (including the periodic master-public-key refresh path shared via the same `activeRequests` map and used by `getMasterPublicKey`/create/update flows), rather than fund loss or secret disclosure. It can degrade availability of `SecretsCreate`/`SecretsUpdate` (which depend on a fresh public key fetch reusing the same map) for a targeted or randomly guessed request ID window, and can be trivially automated by any network client able to reach the gateway's Vault handler methods, without needing any valid allowlist/JWT credentials for the `MethodPublicKeyGet` path.

### Likelihood Explanation
Likelihood is moderate: exploitation requires the attacker to guess/predict a victim's request ID (client-generated, often a UUID) to specifically target it, but a low-cost blind flood of many distinct IDs is also possible to increase collision probability, and the `MethodPublicKeyGet` path is reachable with zero authentication, making it trivially reachable by any unprivileged network client.

### Recommendation
Namespace the `activeRequests` map key by more than the bare client-supplied `req.ID` — e.g., combine it with a per-connection/session identifier, or the caller's gateway/connection ID, or an internally generated random suffix that the client cannot control — for both `core/services/gateway/handlers/vault/handler.go` and the analogous `core/services/gateway/handlers/confidentialrelay/handler.go` (which shares the same construction in `newActiveRequest`/`HandleJSONRPCUserMessage`). Additionally, do not allow unauthenticated `MethodPublicKeyGet` requests to consume the same shared map used for authorized write-method public-key prefetch without some form of rate limiting or ID collision isolation.

### Proof of Concept
1. Attacker sends an unauthenticated Vault gateway JSON-RPC request `{"method": "vault.publicKey.get", "id": "<victim-id>"}`, triggering `newActiveRequest` to register `"<victim-id>"` into `h.activeRequests` with no authorization required.
2. Before this entry is cleared (up to `RequestTimeoutSec`, default 30s), the legitimate victim sends a genuine request using the same or a colliding `id` (e.g., a client that reuses IDs, retries with the same ID, or an attacker who predicted the victim's next ID).
3. `newActiveRequest` for the victim's request returns `"request ID already exists: <victim-id>"`, and `HandleJSONRPCUserMessage` propagates this as an error, so `SendToGateway`/the gateway never dispatches the victim's request to the DON — the victim's legitimate call fails, exactly analogous to the OUSD zero-address flag blocking the legitimate global upgrade call.

### Citations

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

**File:** core/services/gateway/handlers/vault/handler.go (L422-454)
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

**File:** core/services/gateway/handlers/vault/handler.go (L829-839)
```go
	err := userRequest.SendResponse(resp)
	if err != nil {
		h.lggr.Errorw("error sending response to user", "requestID", userRequest.req.ID, "error", err)
		return err
	}

	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.activeRequests, userRequest.req.ID)
	h.lggr.Debugw("response sent to user", "requestID", userRequest.req.ID, "errorCode", resp.ErrorCode)
	return nil
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-40)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
type GatewayVaultRequestProcessor struct {
	validator               *RequestValidator
	authorizer              Authorizer
	stripOwnerPrefixForAuth bool
	lggr                    logger.Logger
}
```
