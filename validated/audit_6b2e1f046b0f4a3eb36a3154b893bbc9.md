### Title
Bearer/JWT authentication token logged in plaintext via Debug-level request logging in the Vault gateway handlers - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
Both the connector-side and the OCR-plugin-facing Vault gateway handlers log the entire inbound `jsonrpc.Request[json.RawMessage]` object — including its `Auth` field, which carries the caller-supplied bearer/JWT token used to authenticate unprivileged HTTP clients to the Vault DON — before that request has been authorized or the token has been stripped/redacted. This mirrors the CVE-2019-11549 bug class: request/connection-handling code paths writing raw credentials into node logs.

### Finding Description
The public HTTP-facing Vault handler logs the complete request object, including the caller's bearer token, immediately upon receipt, prior to authorization: [1](#0-0) 

The gateway-connector-facing handler for the same Vault capability does the same for messages arriving from/being relayed through the gateway: [2](#0-1) 
and again logs the full outgoing response object: [3](#0-2) 

That the request object legitimately carries a live bearer/JWT credential is confirmed by the system tests, which explicitly extract `jsonRequest.Auth` and set it as an `Authorization: Bearer <token>` header before sending to the gateway: [4](#0-3) [5](#0-4) 

By contrast, the authorization pipeline itself is careful to log only a boolean `hasAuth` flag rather than the raw token, showing that the developers were otherwise aware credentials should not be logged: [6](#0-5) 

This inconsistency means the two `Debugw("... req ...")` / `Debugw("... request ...")` calls above are the exception that leaks the raw credential into the log stream whenever Debug-level logging is enabled, which is exactly the connection/request-handling logging bug class described by CVE-2019-11549 (credentials captured incidentally by generic request/error logging).

### Impact Explanation
If Debug-level logging is enabled on a node/gateway operating the Vault capability, an unprivileged client's bearer/JWT authentication token — used to authorize `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList` operations against the Vault DON — is written verbatim to the node's log output. Anyone with read access to logs (log aggregation systems, support bundles, misconfigured log shipping, or an operator with lesser trust than the credential owner) could extract the token and replay it to impersonate the original caller, enabling unauthorized creation, update, deletion, or listing of vault secrets under that owner's identity — a concrete authentication/credential-disclosure and request-impersonation vector.

### Likelihood Explanation
Exploitability is gated on the log level: these are `Debugw` calls, so the token is only written to logs when the node/gateway is running with Debug verbosity, which is not the production default. This limits, but does not eliminate, real-world exposure — Debug logging is commonly enabled temporarily for troubleshooting in production environments, and once enabled, every Vault request routed through these two handlers exposes its token unconditionally and unavoidably (no configuration can suppress just this field).

### Recommendation
- Remove `req`/`request`/`resp` (the raw struct) from the `Debugw` log statements in `core/services/gateway/handlers/vault/handler.go:403` and `core/capabilities/vault/gw_handler.go:182,231`.
- Replace with an explicit, minimal field list (e.g., `method`, `requestID`, `hasAuth`) as is already done correctly in `gateway_vault_request_processor.go`.
- If a `String()`/`LogValue()` method exists or can be added on the `jsonrpc.Request`/`Response` types, ensure it redacts the `Auth` field by default so any future ad-hoc logging of the whole struct is safe.

### Proof of Concept
1. Start a chainlink node/gateway with the Vault capability enabled and `Log.Level = 'debug'`.
2. Send any authorized `SecretsCreate` request to the gateway HTTP endpoint with `Authorization: Bearer <token>` (as constructed in `sendVaultSignedOCRRequestToGateway`, `system-tests/tests/smoke/cre/vault_don_test_helpers.go:547-559`).
3. Inspect the node/gateway logs: the `Debugw("handling vault request", ..., "request", req)` (or `"received message from gateway", "req", req"`) line contains the full request struct, including the plaintext `Auth` bearer token, which can then be reused by anyone with log access.

Note: I could not locate the `jsonrpc.Request`/`Response` type definitions themselves in this repository's index (they appear to come from an external `chainlink-common`-style dependency not fully indexed here), so I was unable to directly confirm the `Auth` field's exact type/tag from source in this repo — this was inferred from its confirmed usage (`jsonRequest.Auth`) in the system tests cited above. If you need the authoritative struct definition, a full Devin session with repository access would be required to inspect the dependency module.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-403)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
```

**File:** core/capabilities/vault/gw_handler.go (L180-182)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/capabilities/vault/gw_handler.go (L226-231)
```go
	if err = h.gatewayConnector.SendToGateway(ctx, gatewayID, response); err != nil {
		reqLggr.Errorw("Failed to send message to gateway", "error", err)
		return err
	}

	reqLggr.Infow("Sent message to gateway", "resp", response)
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L547-559)
```go
func sendVaultSignedOCRRequestToGateway(t *testing.T, gatewayURL string, jsonRequest jsonrpc.Request[json.RawMessage], authorizedOwner string) jsonrpc.Response[vaulttypes.SignedOCRResponse] {
	t.Helper()

	authToken := jsonRequest.Auth
	jsonRequest = outboundRequestWithoutAuth(jsonRequest)

	requestBody, err := json.Marshal(jsonRequest)
	require.NoError(t, err, "failed to marshal vault request")

	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test.go (L644-654)
```go
func sendConcurrentVaultCreate(t *testing.T, gwURL, requestID string, jsonRequest jsonrpc.Request[json.RawMessage], authorizedOwner, expectedResponseOwner string, namespaces []string) {
	t.Helper()

	authToken := jsonRequest.Auth
	stripped := outboundRequestWithoutAuth(jsonRequest)
	requestBody, err := json.Marshal(stripped)
	require.NoError(t, err, "failed to marshal vault request")
	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L270-276)
```go
	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```
