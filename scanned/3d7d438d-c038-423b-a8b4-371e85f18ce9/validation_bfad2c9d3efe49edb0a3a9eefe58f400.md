Based on my investigation, I found a concrete nil-pointer dereference bug reachable from an unprivileged actor's JSON-RPC request, analogous to the ATS ACL segfault (a crafted request reaching an unchecked code path causes a crash).

### Title
Unprivileged crash of node's Vault gateway handler via nil `Params` on `vault.publicKey.get` - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` dispatches `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without going through `requestProcessor.ProcessRequest`, which is the only place that validates `req.Params != nil` for the other vault methods. `handlePublicKeyGet` then unconditionally dereferences `*req.Params`, causing a nil-pointer dereference panic if a caller sends this method with no `params` field.

### Finding Description
In `HandleGatewayMessage` [1](#0-0) , the switch statement routes `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList` through `h.requestProcessor.ProcessRequest`, which performs a nil-params check before any unmarshalling (e.g. `processCreateSecretsRequest` and `processDeleteSecretsRequest` both check `if req.Params == nil { return ... }` in `core/capabilities/vault/gateway_vault_request_processor.go`) [2](#0-1) [3](#0-2) .

However, `MethodPublicKeyGet` is handled as a special case that bypasses this validator entirely: `response = h.handlePublicKeyGet(ctx, gatewayID, req)` [4](#0-3) . `handlePublicKeyGet` immediately does:
```go
r := &vaultcommon.GetPublicKeyRequest{}
if err := json.Unmarshal(*req.Params, r); err != nil {
``` [5](#0-4) 

If `req.Params` is `nil` (i.e., the JSON-RPC request omits the `params` field entirely, which is valid per JSON-RPC 2.0 for parameterless calls), dereferencing `*req.Params` panics with a nil-pointer dereference, rather than returning a graceful `UserMessageParseError` as intended by the `if err :=` check.

The `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, and `handleSecretsList` functions have the identical unguarded `*req.Params` dereference pattern [6](#0-5) , but those are protected because `ProcessRequest`'s nil-check runs first and short-circuits with an error response before those handlers are ever reached. `handlePublicKeyGet` lacks this upstream guard, making it the sole exploitable path.

This request path is reachable from an unprivileged client: the gateway's user-facing vault handler (`core/services/gateway/handlers/vault/handler.go`) forwards user JSON-RPC requests, including `vault.publicKey.get`, to DON member nodes via `SendToNode`, and each node's `GatewayHandler.HandleGatewayMessage` processes the forwarded envelope directly — `MethodPublicKeyGet` requires no prior authorization, since the vault authorizer/allowlist logic is also skipped for this method in the switch statement.

### Impact Explanation
A crash in `GatewayHandler.HandleGatewayMessage` triggered by a single malformed unprivileged request causes a panic on the node process handling vault gateway messages. Depending on whether this handler path runs inside a goroutine with panic recovery (`core/recovery/recover.go` provides `HandleFn`/`WrapRecover` utilities used elsewhere in the codebase, but I could not confirm from the available context whether `HandleGatewayMessage`'s call chain is wrapped in one of these recover helpers), this could crash the node service or at minimum disrupt in-flight vault request processing for that node — a availability impact analogous to the ATS segfault, reachable by any unauthenticated/unprivileged caller able to reach the gateway's vault user-message endpoint with no special permissions.

### Likelihood Explanation
High: the trigger is a single JSON-RPC request with method `vault.publicKey.get` and an omitted/null `params` field — no authentication, authorization, or specific state is required, since `MethodPublicKeyGet` bypasses both `requestProcessor.ProcessRequest` (nil-params validation) and the authorizer/allowlist chain entirely.

### Recommendation
Add the same nil-params guard used by `GatewayVaultRequestProcessor` before calling `handlePublicKeyGet`, e.g.:
```go
case vaulttypes.MethodPublicKeyGet:
    if req.Params == nil {
        response = h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
        break
    }
    response = h.handlePublicKeyGet(ctx, gatewayID, req)
```
More robustly, route `MethodPublicKeyGet` through a shared params-nil-check helper (or through `requestProcessor`) so all vault methods share one validated entry point, preventing similar omissions in the future.

### Proof of Concept
Send a JSON-RPC request to the gateway's vault handler (or directly emulate a gateway-forwarded message to a node) with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
i.e. omitting the `params` field. This reaches `GatewayHandler.HandleGatewayMessage` → `case vaulttypes.MethodPublicKeyGet: response = h.handlePublicKeyGet(...)` → `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, causing a nil-pointer dereference panic [5](#0-4) .

### Citations

**File:** core/capabilities/vault/gw_handler.go (L187-211)
```go
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

**File:** core/capabilities/vault/gw_handler.go (L275-336)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsUpdate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.UpdateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized update secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.UpdateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&resultBytes),
	}
}
```

**File:** core/capabilities/vault/gw_handler.go (L364-369)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-117)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-201)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

```
