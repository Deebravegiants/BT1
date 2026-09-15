### Title
Bearer token disclosure in gateway vault handler debug logs - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
`HandleJSONRPCUserMessage` in the gateway's vault handler logs the entire incoming JSON-RPC request struct — including its `Auth` field (the bearer/JWT token used for authentication) — at `Debug` level for every request received by the internet-facing gateway, before authorization is even performed.

### Finding Description
In `core/services/gateway/handlers/vault/handler.go`, the handler for incoming vault JSON-RPC requests does: [1](#0-0) 

```go
h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
```

`req` is a `jsonrpc.Request[json.RawMessage]` which carries the caller-supplied `Auth` string — the exact same bearer token that is sent as `Authorization: Bearer <token>` by clients (e.g. as constructed in test helpers at [2](#0-1) ). By passing the whole `req` object as a structured log field, the zap-backed logger serializes it in full, and there is no redaction, masking, or field-stripping applied to `Auth` before it hits the log sink — unlike the deliberate redaction pattern used elsewhere in the codebase for HTTP body fields (`isBlacklisted`/`*REDACTED*` in `core/web/router.go`) and unlike the vault handler's own later care to avoid logging raw params (see the dedicated regression test `TestVaultHandler_InvalidParamsDoesNotLogRawParams` at [3](#0-2) , which explicitly asserts that raw `params` are *not* logged — but no equivalent test/guard exists for `Auth`).

This is directly analogous to CVE-2024-9453: the OpenShift Jenkins bug where a long-lived bearer token was written unobfuscated into logs that could be centrally collected, creating a token-leak risk for anyone with log access. Here, any operator, log-aggregation pipeline, or downstream consumer of the gateway's debug logs gains the caller's raw vault-auth bearer token/JWT, which can then be replayed to impersonate that caller against the gateway (subject to JWT validity window and any request-digest binding).

### Impact Explanation
If the gateway is run with `Debug` log level (a supported, documented logging level, not privileged/operator-only misconfiguration) or logs are captured/aggregated at that level, every unprivileged client's raw vault-auth bearer token is written to logs. Anyone with read access to those logs (a lower trust boundary than the vault DON/API itself — e.g., log-shipping infrastructure, SIEM, third-party log storage) can extract and replay the token to impersonate the legitimate caller and perform vault secret operations (create/update/list/delete) as that owner until the token expires. This is a credential/secret-disclosure vulnerability with a direct escalation path to unauthorized vault operations.

### Likelihood Explanation
Likelihood is moderate to high in any deployment where debug logging is enabled (common during troubleshooting, staging, or misconfigured production) or where logs are shipped to centralized/third-party sinks without additional filtering — the same root cause called out in the Jenkins CVE. The log statement fires unconditionally on every incoming vault request, requiring no special conditions beyond `Debug` level being active.

### Recommendation
Do not log the full `req` struct. Explicitly redact or omit `req.Auth` before logging, e.g., log only `method`, `requestID`, and non-sensitive fields, or replace `Auth` with a fixed redacted placeholder (mirroring the existing `isBlacklisted`/`*REDACTED*` pattern in `core/web/router.go`). Add a regression test analogous to `TestVaultHandler_InvalidParamsDoesNotLogRawParams` asserting no log entry contains the `Auth` token value.

### Proof of Concept
1. Run the chainlink gateway with the vault handler enabled and log level set to `Debug`.
2. Send any vault JSON-RPC request (e.g., `vault.secrets.list`) with a valid bearer/JWT token in `req.Auth` (as constructed by `sendVaultJWTRequestToGatewayExpectError`/`sendVaultSignedOCRRequestToGateway` helpers, which set header `Authorization: Bearer <token>` from `jsonRequest.Auth`).
3. Observe the gateway log line `"handling vault request"` — the `request` field will contain the full JSON-RPC request object, including the raw `Auth` token string, in cleartext.
4. Extract the token from the log line and replay it in a new request's `Authorization: Bearer <token>` header before expiry to impersonate the original caller.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L403-403)
```go
	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L773-777)
```go
	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}
	statusCode, body := sendVaultRequestToGatewayWithHeaders(t, gatewayURL, requestBody, headers)
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1058)
```go
func TestVaultHandler_InvalidParamsDoesNotLogRawParams(t *testing.T) {
	t.Parallel()

	// Observed at Info level so the pre-existing whole-request Debug log is excluded.
	lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
	h, callback, don, _ := setupHandlerWithLogger(t, lggr, limits.Factory{Settings: cresettings.DefaultGetter})
	// Don't expect SendToNode to be called for invalid params
	don.AssertNotCalled(t, "SendToNode")

	const marker = "SENSITIVE_MARKER_123"
	invalidParams := json.RawMessage(`{"request_id":"req-1","injected":"` + marker + `"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "invalid-params-logs",
		Method: vaulttypes.MethodSecretsCreate,
		Params: &invalidParams,
	}

	// The invalid-params response is sent synchronously, so no goroutine is needed.
	err := h.HandleJSONRPCUserMessage(t.Context(), req, callback)
	require.NoError(t, err)

	resp, err := callback.Wait(t.Context())
	require.NoError(t, err)
	var secretsResponse jsonrpc.Response[vaultcommon.CreateSecretsResponse]
	require.NoError(t, json.Unmarshal(resp.RawResponse, &secretsResponse))
	assert.Equal(t, req.ID, secretsResponse.ID, "Request ID should match")
	assert.Equal(t, api.ToJSONRPCErrorCode(api.InvalidParamsError), secretsResponse.Error.Code, "Error code should match")

	invalidParamsLogs := logs.FilterMessage("invalid params")
	entries := invalidParamsLogs.All()
	require.Len(t, entries, 1, "expected exactly one 'invalid params' log entry")
	assert.Equal(t, zapcore.ErrorLevel, entries[0].Level)
	assert.Equal(t, req.ID, entries[0].ContextMap()["requestID"])
	assert.NotContains(t, entries[0].ContextMap(), "params", "raw params must not be logged")

	for _, e := range logs.All() {
		assert.NotContains(t, e.Message, marker)
		for k, v := range e.ContextMap() {
			if s, ok := v.(string); ok {
				assert.NotContains(t, s, marker, "log field %q must not contain raw request params", k)
			}
		}
	}
```
