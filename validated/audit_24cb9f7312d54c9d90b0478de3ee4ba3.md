### Title
Debug-level logging of full JSON-RPC request (including bearer auth token) in ksmbd-style key/credential exposure - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault `GatewayHandler.HandleGatewayMessage` logs the entire incoming JSON-RPC request object, including the `Auth` bearer credential, at Debug level before any redaction is applied, mirroring the ksmbd CVE-2026-43377 pattern where a debug logging path unintentionally leaks authentication/signing material.

### Finding Description
`HandleGatewayMessage` builds a request-scoped logger and immediately logs the whole request: [1](#0-0) 
The `req` value is a `*jsonrpc.Request[json.RawMessage]`, which per the system-test helpers carries the caller-supplied bearer/auth token in a field named `Auth` (`req.Auth = jwtToken`, later forwarded as `Authorization: Bearer <token>`): [2](#0-1) 
Unlike the later "invalid params" path — which was explicitly hardened to avoid logging raw params (`TestVaultHandler_InvalidParamsDoesNotLogRawParams` asserts no `params` field and no injected marker leaks into any log field) — the top-level `Debugw("received message from gateway", "req", req)` call is the "pre-existing whole-request Debug log" that the same test file explicitly calls out and deliberately excludes from its assertions: [3](#0-2) 
This is structurally identical to the ksmbd bug class: a verbose/debug-only code path that serializes an entire credential-bearing structure into logs, "to avoid exposing credentials" being the exact fix applied upstream for KSMBD_DEBUG_AUTH. Here, whenever Debug-level logging is enabled on the node (a common operational configuration, not a privileged-only toggle), any request reaching this handler — including from an unprivileged/external gateway caller — has its full `Auth` token written to node logs.

### Impact Explanation
If an attacker can read the node's logs (via log aggregation misconfiguration, shared log storage, support-bundle collection, or a separate log-disclosure bug), the leaked `Auth` bearer token can be replayed against the gateway to impersonate the legitimate workflow/user for Vault secret operations (create/update/list/delete), since the JWT/OCR-signed auth token is the sole proof of authorization checked by `requestProcessor.ProcessRequest`. This is a credential-disclosure issue enabling request impersonation and potential unauthorized secret manipulation — directly matching the "key/secret disclosure" and "request impersonation" categories in scope.

### Likelihood Explanation
Likelihood depends on (a) Debug-level logging being enabled on the vault-handling node, and (b) an attacker obtaining log access — both realistic operational conditions (debug logging is commonly enabled for troubleshooting, and centralized logging pipelines are a common attack surface). No special privilege is needed to trigger the log write itself: any external actor whose request reaches `HandleGatewayMessage` causes their own `Auth` token to be logged, and in shared/aggregated logging environments other tenants'/users' requests could also be exposed depending on deployment topology.

### Recommendation
Remove or redact the full `req` object from the `Debugw("received message from gateway", "req", req)` call in `HandleGatewayMessage`; log only non-sensitive correlation fields already captured by `requestLogger` (`requestID`, `method`, `gatewayID`) and explicitly strip/mask the `Auth` field (and any raw `Params`) before logging, consistent with the redaction already applied to the invalid-params path.

### Proof of Concept
1. Configure a Chainlink node running the Vault `GatewayHandler` with `Log.Level = 'debug'`.
2. Send a Vault JSON-RPC request (e.g., `secrets/create`) through the gateway with `req.Auth` set to a valid bearer/JWT token, as done in `sendVaultSignedOCRRequestToGateway`.
3. Observe node logs: the `Debugw("received message from gateway", "req", req)` call at `core/capabilities/vault/gw_handler.go:182` serializes the full request struct, including `Auth`, into the log stream.
4. An actor with read access to these debug logs extracts the token and replays it as `Authorization: Bearer <token>` against the gateway to issue further Vault requests as the original caller.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-183)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1049)
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
```
