### Title
Vault gateway handler logs the entire raw JSON-RPC request (including auth token and secret payload) at Debug level, before validation - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
`HandleJSONRPCUserMessage` unconditionally logs the full incoming request object — including the `Auth` token and the raw `Params` payload (which for `secrets_create`/`secrets_update` contains the client-submitted secret material) — at Debug level, before any authentication or validation has occurred. Chainlink's own test suite explicitly acknowledges this behavior exists and only patches a narrower, later logging path, leaving the primary leak intact whenever verbose/debug logging is enabled.

### Finding Description
In `HandleJSONRPCUserMessage`, the very first log line captures the entire unvalidated request: [1](#0-0) 

This happens for every JSON-RPC message the gateway receives from any client, prior to `h.requestProcessor.ProcessRequest` (authorization/validation) being called: [2](#0-1) 

The `req` object is `jsonrpc.Request[json.RawMessage]`, which carries an `Auth` field (used for authentication, referenced at line 432 as `req.Auth != ""`) and `Params json.RawMessage` — the raw, unredacted JSON body submitted by the caller. For `MethodSecretsCreate`/`MethodSecretsUpdate` requests this includes the caller-submitted secret/ciphertext payload; it also includes whatever bearer/auth token the client attached to authenticate the request.

Chainlink's own regression test for this handler confirms the log line is pre-existing and was intentionally left in place, only excluding it from its own assertions: [3](#0-2) 
The test comment states: "Observed at Info level so the pre-existing whole-request Debug log is excluded" — i.e., the fix applied only covers the later `errorResponse`/"invalid params" Error-level log (which now redacts raw params), while the earlier full-request Debug log at line 403 remains unredacted: [4](#0-3) 

This is structurally analogous to CVE-2018-16876: a verbose/debug logging mode captures sensitive request contents that a supposedly-safe higher-level control (here, the later redaction added for the "invalid params" path) does not actually cover, because the flaw is in an earlier, broader log statement.

### Impact Explanation
If a Chainlink node/gateway operator runs with `Log.Level = 'debug'` (a supported, documented configuration — see `Log.Level` in `docs/CONFIG.md`), every vault request from any client — including the caller's auth token and, for create/update secret calls, the raw secret payload — is written to the node's log file/stream in plaintext. This can lead to credential/secret disclosure to anyone with access to node logs (log aggregation systems, shared log storage, support/debug bundles), and could enable request impersonation via the leaked `Auth` token.

### Likelihood Explanation
Requires the node operator to have Debug-level logging enabled, which is a normal debugging/troubleshooting configuration and not unusual in production incident response. Once enabled, exploitation of the log leak requires no special privilege from the requester — any unprivileged client that sends a JSON-RPC vault request (even before authorization succeeds) triggers the log line, since it executes prior to `ProcessRequest`.

### Recommendation
Remove or redact the `"request", req` field from the initial Debug log in `HandleJSONRPCUserMessage` (and any other pre-authorization Debug logs of the raw request, e.g. line 437's context). At minimum, strip/redact `req.Auth` and `req.Params` before logging, consistent with the redaction already applied to the "invalid params" error path.

### Proof of Concept
1. Configure a Chainlink node/gateway with `Log.Level = 'debug'`.
2. Send a `secrets_create` (or `secrets_update`) JSON-RPC request to the vault gateway handler with an `Auth` token and a `Params` payload containing the secret material.
3. Observe the node's debug logs: the "handling vault request" entry logs the full `req` object, including `Auth` and `Params`, in plaintext — even if the request is subsequently rejected by validation/authorization.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-437)
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
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
```

**File:** core/services/gateway/handlers/vault/handler.go (L766-768)
```go
	case api.InvalidParamsError:
		h.lggr.Errorw("invalid params", "requestID", req.ID, "error", err.Error())
		err = errors.New("invalid params error: " + err.Error())
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1027)
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
```
