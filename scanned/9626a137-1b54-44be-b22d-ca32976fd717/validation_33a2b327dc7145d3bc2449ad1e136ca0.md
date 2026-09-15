### Title
JWT Bearer Token Exposed in Verbose Gateway Handler Logs - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The node-side Vault gateway handler logs the entire incoming JSON-RPC request object — including its authentication payload — at debug (`-v`/verbose) log level before that request has been parsed or its auth field redacted, mirroring the kube-router bug class of "raw credential struct dumped by a verbose log statement."

### Finding Description
`GatewayHandler.HandleGatewayMessage` is the entry point for messages routed from the internet-facing gateway to a node, keyed by the vault capability's JSON-RPC methods (`vaulttypes.Methods`) [1](#0-0) . Before any authorization or parsing occurs, it logs the raw request:

```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
``` [2](#0-1) 

`req` is a `*jsonrpc.Request[json.RawMessage]` that carries an `Auth` field used to transport a bearer/JWT credential for request authentication — this is evidenced by system tests that build a `jsonrpc.Request`, set `jsonRequest.Auth` to a signed token, and later forward it as an `Authorization: Bearer` HTTP header when talking to the gateway [3](#0-2) . The JWT-based authorizer (`jwt_based_auth.go`) and `authorizer.go` consume this same `Auth` value to authenticate the caller .

Because `Debugw("received message from gateway", "req", req)` logs the whole request object rather than a redacted view, enabling verbose/debug logging on the node (the exact operational scenario the kube-router advisory describes — collecting `-v=2`/debug logs for troubleshooting) will place the caller's JWT/auth credential into the node's log stream. This is the same bug class as the kube-router advisory: a diagnostic log statement dumps a structure holding a credential (`node.Annotations` there, `jsonrpc.Request.Auth` here) instead of using the credential-safe accessor/redacted view that exists elsewhere in the codebase for other message types (e.g. `PeerConfig.String()` masks passwords in the original report; no equivalent masking is applied to `req` here before logging).

An identical unredacted-request logging pattern also exists in the sibling confidential-relay gateway handler, `core/capabilities/confidentialrelay/handler.go`, which matched the same log pattern search, indicating this is a recurring pattern rather than an isolated instance [4](#0-3) .

### Impact Explanation
If the `Auth` value is a bearer/JWT token used to authenticate a caller against the Vault DON (as used by `AuthorizeRequest` in the gateway vault pipeline) [5](#0-4) , an operator or any party with access to node debug logs (log aggregation systems, support log bundles, `kubectl logs`-equivalent access) can extract a valid caller token and replay it to impersonate that caller/workflow-owner against the vault gateway, achieving unauthorized request impersonation — directly matching the "Accept only concrete authentication or role bypass ... request impersonation" criterion.

### Likelihood Explanation
Reaching this log statement requires no privilege beyond being a normal client sending a JSON-RPC request through the gateway to the Vault DON's node-side handler — every inbound message to `HandleGatewayMessage` triggers the log line regardless of subsequent authorization outcome, since the log happens before `ProcessRequest`/authorization runs [6](#0-5) . The only gating factor is that the node must have debug-level logging enabled, which is a common and documented troubleshooting configuration, exactly as in the source advisory.

### Recommendation
Do not log the raw `req` object. Log only non-sensitive fields (method, ID, gateway ID — already captured by `requestLogger`) and, if the raw payload is needed for debugging, construct a redacted copy that omits or masks the `Auth` field before passing it to `Debugw`, mirroring the safe `Stringer` pattern the original advisory recommends for password-bearing structures.

### Proof of Concept
1. Configure a node's Vault gateway handler logger at debug level (`--v=2` equivalent / debug log level enabled).
2. As an unprivileged client, send any JSON-RPC request to the gateway targeting the vault capability methods (e.g. `vaulttypes.MethodSecretsList`) with a valid `Authorization: Bearer <token>` / `Auth` field set, following the same construction as `tryJWTSignedVaultSecretsUpdate` [7](#0-6) .
3. Inspect the node's logs for the line `"received message from gateway" req=...`; the emitted structure includes the `Auth` field value, exposing the bearer token to anyone with log access — decode/reuse the token to impersonate the original caller.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L172-199)
```go
func (h *GatewayHandler) Methods() []string {
	return vaulttypes.Methods
}

func (h *GatewayHandler) requestLogger(req *jsonrpc.Request[json.RawMessage], gatewayID string) logger.Logger {
	return h.lggr.With("requestID", req.ID, "method", req.Method, "gatewayID", gatewayID)
}

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
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L753-776)
```go
func tryJWTSignedVaultSecretsUpdate(t *testing.T, jwtAuth vaultRequestAuth, identifierOwner, encryptedSecret, secretID, gatewayURL string, namespaces []string) {
	t.Helper()

	require.NotEmpty(t, namespaces)

	encryptedSecrets := buildEncryptedSecrets(secretID, identifierOwner, encryptedSecret, namespaces)
	uniqueRequestID := uuid.New().String()
	secretsUpdateRequest := vault_helpers.UpdateSecretsRequest{
		RequestId:        uniqueRequestID,
		EncryptedSecrets: encryptedSecrets,
	}
	jsonRequest := newVaultJSONRequest(t, uniqueRequestID, vaulttypes.MethodSecretsUpdate, &secretsUpdateRequest)
	jwtAuth.apply(t, &jsonRequest)

	authToken := jsonRequest.Auth
	outboundReq := outboundRequestWithoutAuth(jsonRequest)

	requestBody, err := json.Marshal(outboundReq)
	require.NoError(t, err)

	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L1-1)
```go
package confidentialrelay
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-30)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
```
