The claim is confirmed by the code. Line 403 in `HandleJSONRPCUserMessage` logs the full `req` object at Debug level, and `req.Auth` carries the bearer/JWT token used by clients (confirmed by `req.Auth` usage throughout `core/capabilities/vault/authorizer.go` and `jwt_based_auth.go`, and by test helpers constructing `Authorization: Bearer` headers directly from `jsonRequest.Auth`). This happens before authorization is performed, and there is no redaction applied to `Auth` unlike the existing regression test for `params` (`TestVaultHandler_InvalidParamsDoesNotLogRawParams`) which has no equivalent for `Auth`.

Audit Report

## Title
Bearer token disclosure in gateway vault handler debug logs - (File: core/services/gateway/handlers/vault/handler.go)

## Summary
`HandleJSONRPCUserMessage` in the gateway's vault handler logs the entire incoming JSON-RPC request struct at `Debug` level before authorization occurs, and this struct includes the caller-supplied `Auth` field (bearer/JWT token). Because the whole `req` is passed as a structured logging field, zap will serialize `Auth` in cleartext with no redaction applied.

## Finding Description
At [1](#0-0) , `HandleJSONRPCUserMessage` logs `"request", req` at Debug level immediately upon entry, prior to any call into `h.requestProcessor.ProcessRequest` (authorization). The `req` parameter is `jsonrpc.Request[json.RawMessage]`, which carries an `Auth` field used as the bearer/JWT token for both allowlist-based and JWT-based authorization, as seen throughout `core/capabilities/vault/authorizer.go` (e.g., [2](#0-1) ) and `core/capabilities/vault/jwt_based_auth.go` (e.g., [3](#0-2) ). Test helpers construct the actual HTTP `Authorization: Bearer <token>` header directly from this same `Auth` field, confirming it is the literal bearer credential ( [4](#0-3) ). No redaction, masking, or field-stripping is applied to `Auth` before the Debug log call, unlike the deliberate care taken elsewhere in the same handler for `params` (validated by the dedicated regression test `TestVaultHandler_InvalidParamsDoesNotLogRawParams`), for which there is no `Auth`-equivalent guard.

## Impact Explanation
If the gateway runs with Debug logging enabled (a supported, documented log level, common in troubleshooting/staging, and sometimes production), every caller's raw vault-auth bearer token is written to logs unconditionally on every incoming vault request. Anyone with read access to those logs (log-aggregation pipelines, SIEM, third-party log storage — a lower trust boundary than the vault DON/API) can extract and replay the token to impersonate the legitimate caller for vault secret operations (create/update/list/delete) until the token expires. This maps to an in-scope Chainlink impact category of key/secret exfiltration and gateway request impersonation.

## Likelihood Explanation
The log statement executes on every incoming vault request handled by the gateway, unconditionally, requiring no special conditions besides Debug-level logging being active — a routine and common deployment/operational configuration, not a privileged misconfiguration. Any unprivileged client that sends a JWT-authenticated vault request causes its own token to be written to the log; if logs are then accessible to a third party (log shipping, SIEM), that third party gains a directly replayable credential.

## Recommendation
Do not log the full `req` struct in `HandleJSONRPCUserMessage`. Log only non-sensitive fields (`method`, `requestID`), and explicitly omit or redact `req.Auth` (mirroring the existing `*REDACTED*` pattern in `core/web/router.go`). Add a regression test analogous to `TestVaultHandler_InvalidParamsDoesNotLogRawParams` that asserts no log entry (across all levels, not just the whole-request Debug line) contains the raw `Auth` token value.

## Proof of Concept
1. Run the chainlink gateway with the vault handler enabled and log level set to `Debug`.
2. Send a vault JSON-RPC request (e.g., `vault.secrets.list`) with a JWT bearer token set as `req.Auth`, using the `Authorization: Bearer <token>` header as constructed in `sendVaultJWTRequestToGatewayExpectError`/`sendVaultSignedOCRRequestToGateway`.
3. Observe the gateway log line `"handling vault request"` at [5](#0-4)  — the `request` field contains the full JSON-RPC request object, including the raw `Auth` token string, in cleartext.
4. Extract the token from the log and replay it in a new request's `Authorization: Bearer <token>` header before expiry to impersonate the original caller.

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

**File:** core/capabilities/vault/authorizer.go (L121-127)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
```

**File:** core/capabilities/vault/jwt_based_auth.go (L188-193)
```go
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
