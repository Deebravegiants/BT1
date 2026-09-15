Audit Report

## Title
Bearer/JWT authentication token logged in plaintext via Debug-level request logging in the Vault gateway handlers - (File: core/services/gateway/handlers/vault/handler.go, core/capabilities/vault/gw_handler.go)

## Summary
The public HTTP-facing Vault handler (`HandleJSONRPCUserMessage`) and the gateway-connector-facing Vault handler (`HandleGatewayMessage`) both log the entire `jsonrpc.Request[json.RawMessage]`/`jsonrpc.Response` struct via `Debugw`, which includes the caller-supplied `Auth` field carrying a live bearer/JWT credential used to authenticate the request. This occurs prior to authorization and is inconsistent with the authorization pipeline itself, which deliberately avoids logging the raw token and instead logs a boolean `hasAuth` flag.

## Finding Description
`core/services/gateway/handlers/vault/handler.go:403` logs the full inbound request object at Debug level immediately on receipt: `h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)`. [1](#0-0) 

`core/capabilities/vault/gw_handler.go:182` and `:231` do the same for both the inbound request relayed from the gateway and the outbound response sent back to the gateway: [2](#0-1) [3](#0-2) 

The `Auth` field on `jsonrpc.Request[json.RawMessage]` genuinely carries a live bearer/JWT credential — it is passed directly into token validation (`v.validateToken(ctx, req.Auth)`) in the JWT-based authorizer, and system-test helpers extract `jsonRequest.Auth` and inject it as an `Authorization: Bearer <token>` HTTP header before sending requests to the gateway (`outboundRequestWithoutAuth` strips it specifically before marshaling the request body, implying the developers were aware it must not travel in the request body/logs unredacted). [4](#0-3) [5](#0-4) [6](#0-5) 

By contrast, `core/capabilities/vault/authorizer.go` (`AuthorizeRequest`) deliberately logs only `"hasAuth", req.Auth != ""` rather than the raw token in every log line it emits, demonstrating that the codebase is otherwise careful about not leaking this specific field: [7](#0-6) 

No `String()`/`LogValue()`/redaction method was found on the `jsonrpc.Request`/`Response` type usage within this repo's index that would automatically mask `Auth` when the whole struct is passed to a structured logger, so the two `Debugw`/one `Infow`-adjacent call sites above leak the raw credential verbatim into the log stream whenever Debug-level logging is enabled.

## Impact Explanation
If Debug-level logging is enabled, the plaintext bearer/JWT token used to authorize `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList` operations against the Vault DON is written to node/gateway logs. Anyone with read access to those logs could extract and replay the token to impersonate the original caller, enabling unauthorized vault secret operations under that identity — a genuine credential-disclosure and request-impersonation risk in the Vault capability's authentication path. This maps to the in-scope "key/secret exfiltration" / "gateway request impersonation" impact classes.

## Likelihood Explanation
This is gated strictly behind Debug-level verbosity, which is not the production default; at default (non-Debug) log levels the vulnerable lines never execute and no token is exposed. However, Debug logging is commonly enabled temporarily for troubleshooting, and once enabled, every request/response routed through these two handlers unconditionally and unavoidably logs the raw token — there is no way to selectively suppress just this field. Exploitation additionally requires read access to logs, which in most deployments is an operator/log-infrastructure-level capability rather than something an unprivileged remote client can obtain directly; this narrows real-world exploitability to scenarios involving log aggregation exposure, misconfigured log shipping, or a lower-trust operator/support-engineer reading Debug logs of a higher-trust caller's session.

## Recommendation
- Remove the raw `req`/`request`/`resp` struct fields from the `Debugw`/`Infow` calls in `core/services/gateway/handlers/vault/handler.go:403` and `core/capabilities/vault/gw_handler.go:182,231`.
- Replace with an explicit, minimal field list (`method`, `requestID`, `hasAuth`), matching the pattern already used correctly in `core/capabilities/vault/authorizer.go` and `gateway_vault_request_processor.go`.
- If feasible, add a `LogValue()`/redacting `String()` method on the `jsonrpc.Request`/`Response` types (in the `chainlink-common` dependency) so any future ad-hoc logging of the whole struct redacts `Auth` by default.

## Proof of Concept
1. Start a chainlink node/gateway with the Vault capability enabled and `Log.Level = 'debug'`.
2. Send an authorized `SecretsCreate`/`SecretsList` request to the gateway HTTP endpoint with `Authorization: Bearer <token>`, as constructed by `sendVaultSignedOCRRequestToGateway` (`system-tests/tests/smoke/cre/vault_don_test_helpers.go:547-559`).
3. Inspect the node/gateway logs: the line `"handling vault request", ..., "request", req` (in `core/services/gateway/handlers/vault/handler.go:403`) or `"received message from gateway", "req", req` (in `core/capabilities/vault/gw_handler.go:182`) contains the full request struct including the plaintext bearer/JWT token in the `Auth` field.

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

**File:** core/capabilities/vault/jwt_based_auth.go (L187-193)
```go
// AuthorizeRequest verifies JWTBasedAuth state and token claims, and returns a common AuthResult.
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}
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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1263-1266)
```go
func outboundRequestWithoutAuth(req jsonrpc.Request[json.RawMessage]) jsonrpc.Request[json.RawMessage] {
	req.Auth = ""
	return req
}
```

**File:** core/capabilities/vault/authorizer.go (L99-118)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
```
