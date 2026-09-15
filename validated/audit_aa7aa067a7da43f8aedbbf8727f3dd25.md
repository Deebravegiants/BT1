Audit Report

## Title
Nil pointer dereference panic in `handlePublicKeyGet` on both Gateway and node when `vault.publicKey.get` is sent without a `params` field - (File: `core/services/gateway/handlers/vault/handler.go`, `core/capabilities/vault/gw_handler.go`)

## Summary
An unprivileged client can send a JSON-RPC request over the Gateway's public HTTP endpoint with `method: "vault.publicKey.get"` and no (or `null`) `params` field. This request is decoded via `jsonrpc2.DecodeRequest[json.RawMessage]` in `gateway.go`'s `ProcessRequest` [1](#0-0)  and routed directly to `handler.HandleJSONRPCUserMessage`, which for `MethodPublicKeyGet` performs **no validation of `req.Params`** before forwarding the raw request to nodes via `fanOutToVaultNodes` → `h.don.SendToNode(ctx, node.Address, &ar.req)` [2](#0-1) [3](#0-2) [4](#0-3) . On the node side, `GatewayHandler.handlePublicKeyGet` unconditionally dereferences `*req.Params` [5](#0-4) , causing a nil pointer dereference panic if `Params` is nil.

## Finding Description
Unlike every other vault method path — `HandleJSONRPCUserMessage`'s secrets branch calls `h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)` which performs parameter validation before fan-out [6](#0-5)  — the `MethodPublicKeyGet` branch explicitly skips authorization/validation ("Public key requests don't require authorization... Let's process this request right away") [2](#0-1) . It goes straight to `h.newActiveRequest(req, callback)` and `h.handlePublicKeyGet(ctx, ar)`, which — if there's no cached public key yet (e.g., right after gateway restart, before the 1-minute refresh ticker in `Start` populates the cache [7](#0-6) ) — calls `fanOutToVaultNodes`, forwarding the client-supplied `ar.req` (including a nil `Params`) verbatim to every DON node [4](#0-3) .

On the node side, the connector's `readLoop` unmarshals the wire bytes into `jsonrpc.Request[json.RawMessage]` with no nil-params check and dispatches to the registered handler [8](#0-7) . `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` directly to `handlePublicKeyGet` [9](#0-8) , which dereferences `*req.Params` without a nil guard [5](#0-4)  — in contrast to `common.ValidatedMessageFromReq`, which explicitly checks `if req.Params == nil` [10](#0-9) .

This confirms the reachability chain the original report could not verify: there is no upstream guarantee that `Params` is non-nil for `vault.publicKey.get`. Both the Gateway-side `handler.HandleJSONRPCUserMessage`/`handlePublicKeyGet` and the node-side `GatewayHandler.handlePublicKeyGet` dereference `req.Params` (or forward it) without a nil check, so a bare/omitted `params` field will panic at `json.Unmarshal(*req.Params, r)` — first on the Gateway itself (since the Gateway's own periodic `fetchVaultPublicKey` call constructs its own params object, but the untrusted user-triggered path in `HandleJSONRPCUserMessage` does not construct or validate params at all before fan-out).

## Impact Explanation
This is a crash-on-malformed-input Denial of Service (CWE-476) reachable by any unauthenticated/unprivileged client able to reach the Gateway's public HTTP JSON-RPC endpoint, since `MethodPublicKeyGet` explicitly bypasses the authorization pipeline by design (it's meant to be a public, unauthenticated endpoint for fetching the vault's public key). A panic in the request-handling goroutine, if unrecovered, can crash the Gateway process and/or Vault-capable node process, disrupting the DON's vault service availability for all workflows relying on it. This maps to an in-scope availability/DoS impact against Gateway/node request handling.

## Likelihood Explanation
High feasibility for triggering the panic itself (a single malformed HTTP POST to the Gateway with `method: "vault.publicKey.get"` and no `params` field), and repeatable. However, actual process-crash impact depends on whether the surrounding HTTP server / goroutine has panic recovery (common Go HTTP servers recover panics per-request via middleware); if such recovery exists, the practical impact is limited to a single failed request/response 500 rather than full process crash, downgrading severity from crash-DoS to a benign error response. This could not be confirmed from the files reviewed (the HTTP server's panic-recovery middleware, if any, was not inspected).

## Recommendation
Add nil checks for `req.Params` in both:
1. `core/services/gateway/handlers/vault/handler.go`'s `HandleJSONRPCUserMessage` `MethodPublicKeyGet` branch, rejecting requests with nil/missing params via `sendImmediateUserResponse` with `api.InvalidParamsError` before calling `newActiveRequest`/`handlePublicKeyGet`.
2. `core/capabilities/vault/gw_handler.go`'s `handlePublicKeyGet`, mirroring the `if req.Params == nil` guard pattern already used in `common.ValidatedMessageFromReq` [10](#0-9) , returning a structured error response instead of panicking.

## Proof of Concept
1. Start a Gateway configured with the vault handler and a Vault-capable DON, ensuring the public-key cache is empty (fresh start, before the periodic `fetchVaultPublicKey` populates `cachedPublicKeyGetResponse`).
2. Send an HTTP POST to the Gateway's user-facing endpoint with body: `{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` (no `params` field, or `"params": null`).
3. Observe: `gateway.go`'s `ProcessRequest` decodes this via `jsonrpc2.DecodeRequest` (no params-required enforcement observed for this method) and calls `handler.HandleJSONRPCUserMessage` → `handlePublicKeyGet` → `fanOutToVaultNodes`, forwarding the request with nil `Params` to each node.
4. Each node's `GatewayHandler.handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, causing a nil pointer dereference panic.
5. A Go unit test constructing `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and passing it directly to `GatewayHandler.handlePublicKeyGet` would deterministically reproduce the panic, confirming the node-side half of the chain without needing the full Gateway-to-node wire path.

### Citations

**File:** core/services/gateway/gateway.go (L221-226)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L279-297)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-419)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
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

**File:** core/services/gateway/handlers/vault/handler.go (L736-752)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}

	l.Debugw("successfully forwarded request to Vault nodes")
	return nil
}
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/services/gateway/connector/connector.go (L277-296)
```go
		case item := <-gatewayState.conn.ReadChannel():
			var req jsonrpc.Request[json.RawMessage]
			err := json.Unmarshal(item.Data, &req)
			if err != nil {
				c.lggr.Errorw("parse error when reading from Gateway", "id", gatewayState.config.ID, "err", err)
				break
			}
			c.handlersMu.RLock()
			handler, exists := c.handlers[req.Method]
			c.handlersMu.RUnlock()
			if !exists {
				c.lggr.Errorw("no handler for method", "id", gatewayState.config.ID, "method", req.Method)
				break
			}
			// do not break on error. HandleGatewayMessage handles errors
			// by sending a response back to the Gateway.
			err = handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
```

**File:** core/services/gateway/handlers/common/message_util.go (L43-45)
```go
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
```
