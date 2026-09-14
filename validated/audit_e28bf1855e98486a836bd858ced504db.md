### Title
Vault Gateway Handler Logs Full JWT Bearer Auth Token at DEBUG Level - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
`jsonrpc.Request[json.RawMessage]` carries an `Auth` field that holds the caller-supplied JWT bearer token used to authorize Vault secret operations (`req.Auth = mustMintVaultJWTForRequest(...)` [1](#0-0) ). The gateway's Vault user-message handler logs the *entire* request struct—including this `Auth` field—at `Debugw` level before any authorization is performed:

```go
h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
``` [2](#0-1) 

The same pattern occurs in the second Vault gateway handler used by the OCR-facing side:
```go
reqLggr.Debugw("received message from gateway", "req", req)
``` [3](#0-2) 

This is directly analogous to CVE-2020-13881: pam_tacplus logged the TACACS+ shared secret to syslog when DEBUG loglevel was enabled. Here, an unprivileged client's bearer credential (the JWT that stands in for a password/API secret and is used to authorize Vault secret create/update/delete/list requests) is written verbatim to the node's structured logs whenever `Log.Level = 'debug'` is configured — the exact operator misconfiguration trigger from the original CVE.

### Finding Description
The Vault gateway handler's request-authorization flow is:
1. `HandleJSONRPCUserMessage` receives a `jsonrpc.Request[json.RawMessage]` from an untrusted client over the gateway's public HTTP endpoint.
2. Before checking authorization, it logs the full struct at Debug: `h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)` [4](#0-3) .
3. `req` is a value of type `jsonrpc.Request[json.RawMessage]`, which contains the exported `Auth` field populated directly from the client-supplied `Authorization: Bearer <token>` header (see test helpers building requests with `req.Auth = ...` and stripping it only for the outbound wire payload via `outboundRequestWithoutAuth` [5](#0-4) ).
4. Structured loggers (zap `SugaredLogger.Debugw`) serialize arbitrary struct values passed as fields via reflection, so the raw `Auth` token/JWT ends up in the log line whenever Debug logging is enabled.

Other parts of the same package show clear developer awareness that this field is sensitive and must not be logged raw — `authorizer.go` deliberately logs only `"hasAuth", req.Auth != ""` instead of the value [6](#0-5) , and a dedicated regression test (`TestVaultHandler_InvalidParamsDoesNotLogRawParams`) exists specifically to assert that sensitive request content is not logged at Info level or above [7](#0-6) . However, that test only inspects logs captured at `zapcore.InfoLevel` and explicitly excludes the pre-existing Debug log line at handler.go:403 from its assertions ("Observed at Info level so the pre-existing whole-request Debug log is excluded"), leaving the Debug-level full-request log unguarded.

### Impact Explanation
If a node operator enables `Log.Level = 'debug'` (a supported and documented configuration, see `testdata/scripts/node/validate/*.txtar` fixtures showing `Log.Level = 'debug'` as a normal setting) [8](#0-7) , every Vault-related request handled by the gateway will have its JWT bearer token written to the node's log output. Anyone with read access to those logs (log aggregation systems, support/on-call tooling, misconfigured log shipping, etc.) can extract a valid, unexpired JWT and replay it to impersonate the legitimate workflow owner for Vault secret create/update/delete/list operations, since the JWT is the authorization credential validated by `jwtBasedAuth.AuthorizeRequest` [9](#0-8) . This is a credential-disclosure/authentication-bypass-enabling issue, matching the "key/secret disclosure" and "request impersonation" categories.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: Debug logging is a normal, supported operational mode (not an edge case), the log statement fires unconditionally for every JSON-RPC Vault request before any authorization check, and no redaction is applied to the `Auth` field in this code path (in contrast to the redaction that does exist for HTTP form/body fields like `password` in `core/web/router.go`'s `isBlacklisted`/`redact` helpers [10](#0-9) ). An unprivileged remote client only needs to send a request through the gateway to have their own (or, if logs are exposed, someone else's) auth token recorded in plaintext logs.

### Recommendation
Redact the `Auth` field before logging the request, e.g. log only `"hasAuth", req.Auth != ""` (as already done in `authorizer.go`) or construct a sanitized copy of the request with `Auth` cleared before passing it to `Debugw`. Apply the same fix to both `core/services/gateway/handlers/vault/handler.go:403` and `core/capabilities/vault/gw_handler.go:182`, and extend `TestVaultHandler_InvalidParamsDoesNotLogRawParams` (or add a new test) to assert that no Debug-level log line contains the raw `Auth`/JWT value.

### Proof of Concept
1. Configure a chainlink node with `Log.Level = 'debug'`.
2. As an unprivileged client, send a `vault.secrets.list` (or create/update/delete) JSON-RPC request to the gateway's public HTTP endpoint with `Authorization: Bearer <jwt>`.
3. Observe the node's log output; the `Debugw("handling vault request", ..., "request", req)` line at `core/services/gateway/handlers/vault/handler.go:403` contains the full `jsonrpc.Request` struct, including the `Auth` field with the raw bearer token.
4. Extract the token from logs and replay it against the gateway before it expires to perform Vault operations as the original authorized owner.

### Citations

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L413-419)
```go
func newJWTVaultRequestAuth(issuer *stvault.TestJWTIssuer, orgID, derivedWorkflowOwner string, publicKey *tdh2easy.PublicKey, skipLabelValidation bool) vaultRequestAuth {
	return vaultRequestAuth{
		requestOwner: derivedWorkflowOwner,
		authorize: func(t *testing.T, req *jsonrpc.Request[json.RawMessage]) {
			req.Auth = mustMintVaultJWTForRequest(t, issuer, req, orgID, publicKey, skipLabelValidation)
		},
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1263-1266)
```go
func outboundRequestWithoutAuth(req jsonrpc.Request[json.RawMessage]) jsonrpc.Request[json.RawMessage] {
	req.Auth = ""
	return req
}
```

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

**File:** core/capabilities/vault/authorizer.go (L106-117)
```go
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
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1059)
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
}
```

**File:** testdata/scripts/node/validate/valid.txtar (L14-43)
```text
-- config.toml --
Log.Level = 'debug'

[[EVM]]
ChainID = '1'

[[EVM.Nodes]]
Name = 'fake'
WSURL = 'wss://foo.bar/ws'
HTTPURL = 'https://foo.bar'

-- secrets.toml --
[Database]
URL = 'postgresql://user:pass1234567890abcd@localhost:5432/dbname?sslmode=disable'

[Password]
Keystore = 'keystore_pass'

-- out.txt --
# Secrets:
[Database]
URL = 'xxxxx'
AllowSimplePasswords = false

[Password]
Keystore = 'xxxxx'

# Input Configuration:
[Log]
Level = 'debug'
```

**File:** core/capabilities/vault/jwt_based_auth.go (L187-199)
```go
// AuthorizeRequest verifies JWTBasedAuth state and token claims, and returns a common AuthResult.
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}

	if scopeErr := enforceVaultJWTOAuthScopes(req.Method, claims.OAuthScopes); scopeErr != nil {
		v.lggr.Debugw("JWTBasedAuth OAuth scope rejected request", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "scopes", claims.OAuthScopes, "error", scopeErr)
		return nil, fmt.Errorf("invalid JWT auth token: %w", scopeErr)
	}

```

**File:** core/web/router.go (L631-658)
```go
func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
