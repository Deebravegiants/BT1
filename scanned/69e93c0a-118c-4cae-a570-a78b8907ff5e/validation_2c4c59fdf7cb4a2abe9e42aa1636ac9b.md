Confirmed: `writeMethodsEnabled` is a feature-flag/kill-switch that only exists in the DON-side gateway handler `core/services/gateway/handlers/vault/handler.go` (the "gateway" internet-facing side) — checked in `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` [1](#0-0) . This is the analog of `whenNotPaused`: an operator-controlled "pause switch" for Vault write operations (create/update/delete secrets).

### Title
Node-side Vault `GatewayHandler` bypasses the `writeMethodsEnabled` kill-switch, allowing secret writes even when Vault write operations are paused - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
The Vault gateway architecture has two cooperating handlers: the internet-facing gateway `handler` (`core/services/gateway/handlers/vault/handler.go`) that fans requests out to DON nodes, and the node-side `GatewayHandler` (`core/capabilities/vault/gw_handler.go`) that receives forwarded requests via `HandleGatewayMessage` and actually executes them against `secretsService`. The gateway-side handler enforces a `writeMethodsEnabled` limiter check before allowing `CreateSecrets`/`UpdateSecrets`/`DeleteSecrets` to proceed [1](#0-0) , but the node-side `GatewayHandler.handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` perform no equivalent check before calling `h.secretsService.CreateSecrets` / `UpdateSecrets` / `DeleteSecrets` [2](#0-1) .

### Finding Description
`writeMethodsEnabled` is an operator "pause" mechanism intended to disable all Vault secret-write operations (create/update/delete) network-wide — exactly analogous to `whenNotPaused` in the OptimismPortal report. It is enforced only in the internet-facing gateway path (`core/services/gateway/handlers/vault/handler.go`, `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`, lines 613-656), which relays requests over the connector to individual nodes via `HandleGatewayMessage`. The node-side `GatewayHandler` in `core/capabilities/vault/gw_handler.go`, which is the code path actually invoked when a node receives a forwarded request (`HandleGatewayMessage`, lines 180-236), calls `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete` (lines 275-336) directly against `secretsService` with no `writeMethodsEnabled` (or any other kill-switch) check. Any client capable of reaching a node's `GatewayConnectorHandler` directly (rather than through the gateway's `handler.go` fan-out path) — or any deployment where the gateway-side flag is toggled to disable writes but the DON's per-node handler is invoked out-of-band — bypasses the intended pause.

### Impact Explanation
If write operations are meant to be globally disabled (e.g., during an incident or vault key-rotation freeze), an unprivileged workflow owner whose request is still allowlisted/authorized (`h.requestProcessor.ProcessRequest`, lines 194-206) can still create, update, or delete secrets on a node, since authorization and the write-pause are two independent, non-overlapping checks and only one code path enforces the pause. This defeats the purpose of the kill-switch and can lead to unauthorized secret mutation/deletion during a period explicitly meant to be frozen.

### Likelihood Explanation
Likelihood depends on whether `GatewayHandler.HandleGatewayMessage` can be triggered independently of the gateway-side `handler.go`'s `writeMethodsEnabled` check (e.g., a compromised/misconfigured gateway, multiple gateways where only one enforces the flag, or future direct-node access paths). Both handlers are wired to the same `vaulttypes.Methods` in a `GatewayConnectorHandler` design meant to be gateway-mediated, so exploitability depends on architecture assumptions not fully verifiable via static code alone.

### Recommendation
Add a `writeMethodsEnabled.AllowErr(ctx)` check (mirroring `core/services/gateway/handlers/vault/handler.go`) inside `GatewayHandler.handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` in `core/capabilities/vault/gw_handler.go`, so the pause is enforced defense-in-depth at the node layer, not solely at the gateway relay layer.

### Proof of Concept
1. Operator disables Vault writes by making `writeMethodsEnabled` return `limits.ErrorNotAllowed{}` (gateway-side settings).
2. A workflow owner sends a `MethodSecretsCreate` JSON-RPC request through the normal path — gateway `handler.go` correctly rejects it with `"vault write methods(create/update/delete) are disabled"` [3](#0-2) .
3. However, if the same request reaches a node's `GatewayHandler.HandleGatewayMessage` (e.g., via a gateway instance/connector path that does not share the same feature-flag config, or a future direct entry point), authorization still succeeds via `requestProcessor.ProcessRequest` [4](#0-3) , and `handleSecretsCreate` executes `secretsService.CreateSecrets` unconditionally [5](#0-4) , completing the write despite the global pause.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L613-626)
```go
func (h *handler) handleSecretsCreate(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}
```

**File:** core/capabilities/vault/gw_handler.go (L188-199)
```go
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
