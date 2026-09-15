Audit Report

## Title
NULL Pointer Dereference via Unchecked `req.Params` in Vault `handlePublicKeyGet` - (File: core/capabilities/vault/gw_handler.go)

## Summary
`HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor.ProcessRequest`, which is the only place that performs the `req.Params == nil` check used by the other four vault methods. `handlePublicKeyGet` unconditionally executes `json.Unmarshal(*req.Params, r)`, so a JSON-RPC request for `vault.publicKey.get` with the `params` field omitted causes a nil-pointer dereference panic.

## Finding Description
In `HandleGatewayMessage`, `MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, and `MethodSecretsList` are all routed through `h.requestProcessor.ProcessRequest(...)` first [1](#0-0) , and that processor's per-method handlers explicitly guard against nil params before any subsequent handler dereferences `req.Params`, e.g. `processCreateSecretsRequest`/`processUpdateSecretsRequest`/`processDeleteSecretsRequest` at [2](#0-1) , [3](#0-2) , [4](#0-3) . Only if that check passes do the later `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`/`handleSecretsList` handlers dereference `*req.Params` at [5](#0-4) .

`MethodPublicKeyGet` bypasses this entirely — it is dispatched straight to `h.handlePublicKeyGet(ctx, gatewayID, req)` with no prior validation step [6](#0-5) . `handlePublicKeyGet` then unconditionally dereferences `req.Params`:

```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
``` [7](#0-6) 

`vault.publicKey.get` is registered as a handled method via `vaulttypes.Methods`, which includes `MethodPublicKeyGet` [8](#0-7) , and is added as a connector handler method in `Methods()` [9](#0-8) . A syntactically valid JSON-RPC request need not include `params`, so `req.Params` can legitimately be `nil` (a `*json.RawMessage`), and `*req.Params` is a nil-pointer dereference, which panics at runtime.

## Impact Explanation
A panic in `HandleGatewayMessage` crashes the goroutine processing that gateway message. I was not able to confirm within the available tools whether the connector's message-processing loop wraps handler invocation in a `recover()` (no such wrapper was found in the connector package during a targeted search of `core/services/gateway/connector/*.go`, but full coverage of the dispatch loop was not verified due to tool/time limits). If unrecovered, this is a genuine denial-of-service against the Vault gateway handler / node process, matching a DoS impact class. `GetPublicKeyRequest` returns only a public key (non-secret material), so no confidentiality impact beyond availability applies here.

## Likelihood Explanation
The trigger requires only a syntactically valid JSON-RPC request with method `vault.publicKey.get` and no `params` field, sent through the gateway connector — no prior authentication, session, or privileged role is needed to reach this code path, since routing to `handlePublicKeyGet` occurs before any authorization step in the switch statement. This is a low-effort, repeatable trigger for any actor able to reach the gateway connector's message dispatch for this handler.

## Recommendation
Add an explicit `if req.Params == nil` check at the top of `handlePublicKeyGet`, mirroring the checks in `gateway_vault_request_processor.go`, and return an `api.UserMessageParseError`/`InvalidVaultParamsError` response instead of dereferencing a nil pointer. As a defense-in-depth measure, consider adding panic recovery around `HandleGatewayMessage` dispatch in the connector, and auditing other JSON-RPC handlers for the same unguarded `*req.Params` dereference pattern.

## Proof of Concept
Send a JSON-RPC request through the gateway connector to a node running the Vault capability:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
(omitting `params`). `HandleGatewayMessage` routes this to `handlePublicKeyGet` at [6](#0-5) , which executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, at [7](#0-6) , triggering a nil-pointer dereference panic. A Go unit test can construct `req := &jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and call `HandleGatewayMessage` directly to reproduce the panic deterministically.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L172-174)
```go
func (h *GatewayHandler) Methods() []string {
	return vaulttypes.Methods
}
```

**File:** core/capabilities/vault/gw_handler.go (L187-206)
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
```

**File:** core/capabilities/vault/gw_handler.go (L207-208)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
```

**File:** core/capabilities/vault/gw_handler.go (L275-362)
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

func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to list secret identifiers: %w", err))
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

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L115-117)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L157-159)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L198-200)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/vaulttypes/types.go (L32-50)
```go
	MethodPublicKeyGet  = "vault.publicKey.get"

	// RequestIDSeparator is used to separate parts(owner, user-provided-requestId) of the request ID.
	RequestIDSeparator = "::"

	// MaxBatchSize is the maximum number of secrets that can be created/updated/deleted in a single request.
	MaxBatchSize = 10
)

// GatewaySecretsMethods are vault JSON-RPC methods reachable through the gateway that
// require authorization and carry owner-bound secret identifiers in params.
var GatewaySecretsMethods = []string{
	MethodSecretsCreate,
	MethodSecretsUpdate,
	MethodSecretsDelete,
	MethodSecretsList,
}

var Methods = append([]string{MethodPublicKeyGet}, GatewaySecretsMethods...)
```
