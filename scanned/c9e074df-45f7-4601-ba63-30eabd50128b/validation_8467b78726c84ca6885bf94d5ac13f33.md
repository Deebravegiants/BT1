### Title
Internal Vault JWT AuthToken Logged in Full at Debug Level - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway's Vault handler logs the entire incoming `jsonrpc.Request[json.RawMessage]` struct—including its `Auth` field, which carries the raw JWT bearer token used for request authorization—at `Debug` log level, before the request has even been authorized. This mirrors the root cause of CVE-2021-3528 (noobaa-operator leaking internal RPC AuthTokens into log files), where a caller-supplied auth credential is captured verbatim by application logging rather than being redacted.

### Finding Description
`HandleJSONRPCUserMessage` in the gateway's Vault handler logs the full request object on every inbound Vault JSON-RPC message: [1](#0-0) 

The `req` value is a `jsonrpc.Request[json.RawMessage]`, which carries an `Auth` string field populated with the caller's JWT bearer token, as demonstrated by test and production code that reads/writes `req.Auth` directly (`req.Auth = token`, `req.Auth != ""`, `req.Auth == ""`): [2](#0-1) [3](#0-2) 

Because `logger.Debugw("...", "request", req, ...)` serializes the whole struct (not a redacted subset), the `Auth` field—the bearer token minted by the identity provider and used to authorize workflow-owner-scoped Vault operations (create/update/delete/list secrets)—is written into the node's log stream whenever debug-level logging is enabled. Elsewhere in the same file and in `authorizer.go`, the authors are clearly aware `Auth` is sensitive, since they deliberately log only `"hasAuth", req.Auth != ""` (a boolean) rather than the token itself: [4](#0-3) [5](#0-4) 

This inconsistency shows the line at 403 is a redaction gap in an otherwise auth-aware codebase — the exact bug class in CVE-2021-3528, where a supposedly internal auth token ends up in a log file instead of being scrubbed like it is at other call sites.

### Impact Explanation
An attacker (or any party) with read access to gateway node logs at debug level can harvest live JWT auth tokens for Vault requests. Since these tokens authorize workflow-owner-scoped secret operations (`vault.secrets.create/update/delete/list`), obtaining a leaked, still-valid token lets an attacker impersonate the legitimate workflow owner/org and create, overwrite, or delete secrets in the Vault DON, or list secret identifiers, before the token's expiry. This matches the "unauthorized... fund movement / cross-user response confusion" bar via secret disclosure/modification and directly parallels the noobaa AuthToken-leak CVE, where log access enabled further impersonation into the RPC control plane.

### Likelihood Explanation
Requires the debug log level to be enabled on the gateway (a supported, non-default-but-common operational configuration) and for an unprivileged actor (or compromised log aggregation pipeline) to obtain read access to those logs. No special network position, node compromise, or malicious-peer capability is needed — the token is captured purely because an ordinary Vault client request was routed through `HandleJSONRPCUserMessage`.

### Recommendation
Remove `"request", req` from the debug log at `core/services/gateway/handlers/vault/handler.go:403`, or replace it with an explicitly redacted projection (e.g., `"hasAuth", req.Auth != ""` as done elsewhere in this file and in `authorizer.go`) so the raw `Auth` token is never serialized into logs.

### Proof of Concept
1. Run the gateway/Vault handler with `Debug` log level enabled.
2. Send any Vault JSON-RPC request (e.g., `vault.secrets.list`) with a valid `Auth` JWT bearer token to the gateway's public endpoint, as in `HandleJSONRPCUserMessage`.
3. Inspect the node's log output: the `"handling vault request"` debug entry at line 403 contains the fully serialized `req` struct, including the raw `Auth` JWT string, before any authorization check occurs.
4. Extract the token from the log file and replay it against the gateway (within its validity window / before replay-guard digest is consumed) to perform actions as the original workflow owner.

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

**File:** core/services/gateway/handlers/vault/handler.go (L432-432)
```go
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
```

**File:** core/capabilities/vault/authorizer.go (L106-106)
```go
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
```

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}
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
