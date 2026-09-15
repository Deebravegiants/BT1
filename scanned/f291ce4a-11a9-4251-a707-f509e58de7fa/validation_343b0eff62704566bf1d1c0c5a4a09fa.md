### Title
Nil pointer dereference in Vault node-side gateway handler's `handlePublicKeyGet` crashes the node process on a malformed request - (File: core/capabilities/vault/gw_handler.go)

### Summary
The Hyperledger Fabric CVE describes a malformed gateway client request crashing a peer node because the peer failed to validate request shape before processing it. An analogous unprivileged-reachable pattern exists in the chainlink Vault capability's node-side gateway handler: `handlePublicKeyGet` unmarshal-dereferences `req.Params` without a nil check, unlike every sibling code path in the same file.

### Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches on `req.Method` and, for `vaulttypes.MethodPublicKeyGet`, calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly — bypassing `h.requestProcessor.ProcessRequest`, which is the only place in this flow that validates `req.Params != nil` (see `processCreateSecretsRequest`/`processUpdateSecretsRequest` nil checks) [1](#0-0) .

`handlePublicKeyGet` immediately dereferences `req.Params` without any nil guard: [2](#0-1) 

Compare this to `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, and `handleSecretsList`, which are only reached *after* `ProcessRequest` has already validated `req.Params != nil` for those methods: [3](#0-2) 

Since `Params` is typed as `*json.RawMessage`, if the incoming JSON-RPC request has no `"params"` field (or an explicit `"params": null`... though JSON `null` would still leave a non-nil pointer to a `null` raw message — the true crash case is `"params"` field absent entirely, producing a nil `*json.RawMessage`), `*req.Params` dereferences a nil pointer, causing a Go runtime panic.

This handler is invoked from `gatewayConnector.readLoop`, which reads and dispatches each inbound gateway message inline within its own goroutine, with no `recover()` wrapper around the `handler.HandleGatewayMessage` call: [4](#0-3) 

In Go, an unrecovered panic in any goroutine terminates the entire process, not just that goroutine. Because this handler runs inside the chainlink node process (not inside the separate gateway process), a crash here takes down the node itself — the same blast radius described in the Fabric CVE (a malformed client message crashing a peer/node process).

### Impact Explanation
An unauthenticated request forwarded by the gateway (which itself does not require prior authorization for `vault.publicKey.get`, matching the intentional design comment "Public key requests don't require authorization" in the gateway-side handler [5](#0-4) ) reaching the node with a missing `params` field will panic the node-side `GatewayHandler.handlePublicKeyGet` call. Since the panic occurs unguarded in the connector's read loop goroutine, it crashes the entire chainlink node process — a remote, unauthenticated denial of service, directly analogous to CVE-2022-36023.

### Likelihood Explanation
The trigger requires only a single JSON-RPC request with `method: "vault.publicKeyGet"` (or whatever `vaulttypes.MethodPublicKeyGet` resolves to) and an omitted `params` field, sent to a Vault-DON gateway that routes to a node running this handler. No authentication, allowlist membership, or JWT is required for this method by design. This makes the likelihood high for any deployment exposing the Vault capability's gateway endpoint.

### Recommendation
Add an explicit `req.Params == nil` check in `handlePublicKeyGet` (mirroring the checks already present in `GatewayVaultRequestProcessor.processCreateSecretsRequest`/`processUpdateSecretsRequest`) before dereferencing, returning a `api.UserMessageParseError` response instead of panicking. Additionally, consider wrapping `handler.HandleGatewayMessage` invocations in `gatewayConnector.readLoop` with a `recover()` (as already used elsewhere in the codebase, e.g. `core/recovery/recover.go` and `core/capabilities/remote/dispatcher.go`) as defense-in-depth against similar future nil-dereference or panic bugs in any gateway handler.

### Proof of Concept
1. Deploy a chainlink node with the Vault capability's `GatewayHandler` registered against a gateway connector.
2. As an unprivileged client, send (or have the gateway forward) a JSON-RPC request over the gateway connection with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKeyGet"}
```
   i.e., omitting the `"params"` field entirely, so that `req.Params` decodes to a nil `*json.RawMessage`.
3. `gatewayConnector.readLoop` dispatches this to `GatewayHandler.HandleGatewayMessage`, which routes to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` — dereferencing the nil pointer.
4. The panic is unrecovered in the read loop goroutine, crashing the node process.

Note: I was not able to fully trace whether an additional decode-layer (outside this repo scope, e.g., `chainlink-common`'s `jsonrpc2` package) might reject a request with an entirely missing `params` field before it reaches the handler; this codebase's index does not include that dependency's source. If `chainlink-common`'s decoder guarantees `Params` is always non-nil (e.g., defaults to an empty `json.RawMessage`), the nil-dereference precondition would not hold and this finding should be downgraded — this should be verified by a Devin session with full access to the `chainlink-common` module.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-122)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var createReq vaultcommon.CreateSecretsRequest
	if err := json.Unmarshal(*req.Params, &createReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
```

**File:** core/capabilities/vault/gw_handler.go (L180-224)
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

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
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

**File:** core/services/gateway/connector/connector.go (L268-297)
```go
func (c *gatewayConnector) readLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		select {
		case <-c.shutdownCh:
			return
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
		}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-408)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
```
