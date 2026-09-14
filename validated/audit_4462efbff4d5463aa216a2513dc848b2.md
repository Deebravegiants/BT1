### Title
Full Secrets-Request Objects Logged via `.String()` in Vault Gateway Handler - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault DON's `GatewayHandler`, which processes `CreateSecrets`/`UpdateSecrets` JSON-RPC requests arriving over the gateway from workflow owners, logs the entire deserialized request object via `.String()` at `Debug` level before forwarding it to the secrets service.

### Finding Description
`handleSecretsCreate` and `handleSecretsUpdate` in `core/capabilities/vault/gw_handler.go` unmarshal the client-supplied JSON-RPC params into `vaultcommon.CreateSecretsRequest` / `vaultcommon.UpdateSecretsRequest` and immediately log the full stringified request: [1](#0-0) [2](#0-1) 

Both log calls follow the exact pattern flagged in the external report (`print`/log statements that dump entire request/response objects containing sensitive fields, e.g. `print(order_result)` / `print(response)`), except here it is `h.lggr.Debugw(..., "request", vaultCapRequest.String())` for a request whose entire purpose is to carry secret material (`SecretsCreate`/`SecretsUpdate`). The same pattern also appears in the delete/list handlers, which log the parsed request via `r.String()`: [3](#0-2) 

If the `EncryptedSecrets`/value fields inside these vault proto messages are ever populated with plaintext (e.g. before client-side TDH2 encryption is enforced, or if a caller sends malformed/plaintext payloads that still unmarshal successfully), that plaintext secret material is written directly to the node's Debug logs. Even if the value is normally pre-encrypted client-side, this is still an anti-pattern identical to the reported bug class: dumping full request/response payloads of secret-management endpoints into logs rather than logging only non-sensitive identifiers (e.g., secret ID, owner, namespace).

I was unable to fully verify the exact field layout of `vaultcommon.CreateSecretsRequest`/`UpdateSecretsRequest` (defined in the external `chainlink-common` module, not present in this repo's index), so I cannot conclusively confirm whether the `Value`/ciphertext field is guaranteed to always be pre-encrypted for every code path that reaches these handlers.

### Impact Explanation
If any caller-supplied `CreateSecrets`/`UpdateSecrets` request reaches this handler with plaintext secret material in its fields (whether due to malformed client behavior, a future code path, or a debugging/test client), that secret is persisted verbatim into the node's Debug logs. Log aggregation/shipping infrastructure (common in production node operators) would then retain the plaintext secret, allowing anyone with log access to obtain workflow secrets managed by the Vault DON capability — directly analogous to the private-key logging issue in the report, but for the Vault DON secrets management surface exposed through the gateway.

### Likelihood Explanation
`Debugw` logging is exercised on every `SecretsCreate`/`SecretsUpdate` request that reaches the handler, which is reachable via the gateway API from workflow owners (an external/unprivileged-relative-to-the-node actor, subject to the request processor's allowlist/JWT authorization prior to this call, per the surrounding `ProcessRequest` gating visible above these handlers). Since it requires `Debug` log level to be enabled in production, likelihood is moderate rather than certain, but it requires no attacker action beyond a normal Vault write operation and no misconfiguration beyond common Debug-level logging in staging/production nodes.

### Recommendation
Remove `vaultCapRequest.String()` / `r.String()` from the `Debugw` calls in `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, and `handleSecretsList` in `core/capabilities/vault/gw_handler.go`. Log only non-sensitive identifiers (e.g., request ID, method, owner/namespace, number of secrets) instead of the full request payload, and ensure the vault proto types implement a redacting `String()`/`LogValue()` so any future logging of these structs cannot leak encrypted or plaintext secret material.

### Proof of Concept
1. A workflow owner submits a `SecretsCreate` (or `SecretsUpdate`) request through the gateway targeting the Vault DON.
2. `GatewayHandler.HandleGatewayMessage` routes to `handleSecretsCreate`/`handleSecretsUpdate`.
3. `h.lggr.Debugw("Processing authorized create/update secrets request", "request", vaultCapRequest.String())` writes the full request object to the node's logs.
4. With Debug-level logging enabled (a common operational setting), the request contents are persisted in log storage/shipping systems accessible to anyone with log access, mirroring the `print(exchange.wallet._private_key)` / `print(order_result)` disclosure pattern from the original report. [4](#0-3) [5](#0-4)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L275-292)
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
```

**File:** core/capabilities/vault/gw_handler.go (L294-311)
```go
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
```

**File:** core/capabilities/vault/gw_handler.go (L313-346)
```go
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
```
