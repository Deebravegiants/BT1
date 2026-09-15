### Title
Plaintext JWT bearer token disclosed in gateway vault handler debug/info logs - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` logs the entire inbound `jsonrpc.Request[json.RawMessage]` object at Debug level, and the entire outbound `jsonrpc.Response` at Info level. The request type carries an `Auth` field holding the raw JWT bearer token used to authenticate/authorize the caller. No redaction of this field is applied before logging, so any client-supplied credential is written to node logs in plaintext, analogous to CVE-2018-16889 where Ceph's debug logging leaked auth-related key material in plaintext.

### Finding Description
`GatewayHandler.HandleGatewayMessage` does: [1](#0-0) 
```
reqLggr := h.requestLogger(req, gatewayID)
reqLggr.Debugw("received message from gateway", "req", req)
```
and later: [2](#0-1) 

`req` is a `*jsonrpc.Request[json.RawMessage]`, which has an `Auth` field populated with the caller's bearer/JWT token, as demonstrated throughout the vault JWT auth flow, e.g.: [3](#0-2) 
and the HTTP entrypoint that extracts the bearer token from the `Authorization` header and forwards it as `req.Auth`: [4](#0-3) 

Elsewhere in the same vault authorization code, developers are careful to avoid logging `req.Auth` directly and instead log only a boolean presence flag (`"hasAuth", req.Auth != ""`): [5](#0-4) 

This shows the team recognizes `Auth` as sensitive, yet `GatewayHandler.HandleGatewayMessage` bypasses that discipline by logging the whole `req`/`response` struct wholesale via the structured (zap) logger's key-value field mechanism, which will serialize all struct fields — including the plaintext `Auth` token — unless `jsonrpc.Request` implements custom log redaction. No `MarshalLogObject`/`String()` override was found for the `jsonrpc.Request`/`Response` types in this repo (they are defined in the external `chainlink-common` module and not overridden here), so the field is logged as-is when `Log.Level = 'debug'` (request) or at Info level (response).

This is reachable directly from an unprivileged actor: any external client calling the gateway's vault JSON-RPC endpoint (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`, `MethodPublicKeyGet`) with a JWT `Authorization: Bearer <token>` header triggers this log line with their own token embedded, and if the node operator has debug logging enabled the token ends up in disk/console logs.

### Impact Explanation
A JWT bearer token is a full authentication credential for the vault gateway JSON-RPC flow (used to authorize secret create/update/delete/list operations against a specific workflow owner/org). If it leaks via log files (which are frequently shared for support/debugging, shipped to log aggregation systems, or accessible to less-privileged log-viewing roles), an attacker who can read the logs can replay the token (subject to expiry) to impersonate the original caller and perform unauthorized vault secret operations — directly matching the CVE's "leaking of ... key/credential information in log files via plaintext" bug class. This is a credential/secret disclosure issue rather than a direct RCE, but downstream impact can include unauthorized secret access/mutation under a compromised identity.

### Likelihood Explanation
Likelihood is moderate: the log line fires only at Debug (request) and Info (response) levels, so exploitation requires the operator to run with debug logging enabled (or Info level for the response leak) and requires the attacker (or an insider) to have subsequent read access to the emitted logs — not a purely remote, log-free compromise. However, no additional privilege is required from the requesting client itself: it is triggered by ordinary, unprivileged/authenticated end-user vault JSON-RPC traffic through the gateway, and the existing test suite (`TestVaultHandler_InvalidParamsDoesNotLogRawParams`) demonstrates the team is aware of and defends against a related "don't log sensitive raw fields" concern for `params`, but that protection was not extended to this whole-`req`/whole-`response` log statement.

### Recommendation
Remove or redact the `Auth` field before logging the request/response in `GatewayHandler.HandleGatewayMessage` (e.g., log a sanitized copy with `Auth` cleared, or log only non-sensitive fields such as method/ID/gatewayID, mirroring the pattern already used in `authorizer.go` with `"hasAuth", req.Auth != ""`). Apply the same treatment to the `resp` object logged at `Infow("Sent message to gateway", "resp", response)` if response payloads can carry any sensitive material. Consider adding a custom `MarshalLogObject`/redacting wrapper type for `jsonrpc.Request`/`Response` used across gateway handlers so this protection is enforced centrally instead of per call site.

### Proof of Concept
1. Configure a Chainlink node running the vault gateway capability with `Log.Level = 'debug'`.
2. As an unprivileged client, send a valid vault JSON-RPC request (e.g., `vault_secretsList`) to the gateway HTTP endpoint with header `Authorization: Bearer <jwt-token>`.
3. `httpserver.go` extracts the bearer token into `jwtToken` and forwards it into the `jsonrpc.Request.Auth` field: [4](#0-3) 
4. `GatewayHandler.HandleGatewayMessage` receives this request and logs it wholesale: [1](#0-0) 
5. Inspect the node's debug log output — the caller's JWT bearer token appears in plaintext in the `"req"` field, confirming the disclosure.

Note: I was unable to verify from the indexed code whether the `jsonrpc.Request`/`Response` types (defined in the external `chainlink-common` module) implement any custom zap-marshaling/redaction that might suppress the `Auth` field automatically; that module's source was not available in this repo's index. If such redaction exists upstream, this finding would be mitigated — a Devin session with full repository/dependency access should confirm the `jsonrpc.Request` field-logging behavior in `chainlink-common` before treating this as conclusively exploitable.

### Citations

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

**File:** core/capabilities/vault/authorizer_test.go (L48-53)
```go
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "1",
		Method: vaulttypes.MethodSecretsCreate,
		Params: (*json.RawMessage)(&params),
		Auth:   "jwt-token",
	}
```

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
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
