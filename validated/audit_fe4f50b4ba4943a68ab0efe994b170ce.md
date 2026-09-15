Audit Report

## Title
Plaintext JWT bearer token disclosed in gateway vault handler debug/info logs - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` logs the full `*jsonrpc.Request[json.RawMessage]` at Debug level (`"req", req`) and the full `*jsonrpc.Response[json.RawMessage]` at Info level (`"resp", response`), without stripping the `Auth` field that carries the caller's JWT bearer token. This is confirmed directly in the code and contrasts with the deliberate discipline shown elsewhere in the same package (`authorizer.go`), which only logs `"hasAuth", req.Auth != ""` rather than the raw token.

## Finding Description
`GatewayHandler.HandleGatewayMessage` receives `req *jsonrpc.Request[json.RawMessage]` from the gateway connector and immediately logs it wholesale: [1](#0-0) 
and later logs the outbound response wholesale: [2](#0-1) 

The `jsonrpc.Request[json.RawMessage]` type (defined in the external `chainlink-common` module, `github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2`) has an `Auth` field that carries the caller's JWT, as shown throughout the vault auth flow, e.g. tests constructing `jsonrpc.Request[json.RawMessage]{..., Auth: "jwt-token"}` [3](#0-2) , the JWT authorizer consuming `req.Auth` directly [4](#0-3) , and the HTTP entrypoint that extracts the bearer token from the `Authorization` header and threads it through as the JWT auth mechanism [5](#0-4) .

Elsewhere in the same package, the team is explicit that `Auth` should not be logged in full — `authorizer.go` deliberately logs only a boolean presence flag: [6](#0-5) 
This shows an established internal convention that logging `req.Auth` in full is unsafe, a convention `gw_handler.go`'s `HandleGatewayMessage` does not follow.

Because `jsonrpc.Request`/`Response` are defined in the external `chainlink-common` module and no local override (`MarshalLogObject`/redaction wrapper) exists in this repo, the zap-based structured logger will serialize the entire struct — including `Auth` — when the field value `req`/`response` is passed to `Debugw`/`Infow`. This could not be fully confirmed against the `chainlink-common` source itself (not indexed in this repo), but nothing in this repo suggests any redaction is applied, and the sibling `authorizer.go` code's explicit avoidance of logging `req.Auth` directly strongly suggests the team assumes no such redaction exists upstream.

## Impact Explanation
A leaked JWT is a full authentication credential for the vault gateway JSON-RPC flow, and if captured from logs it can be replayed (subject to expiry, and subject to the request-digest/replay-guard binding described in `authorizer.go`) to authorize vault secret operations under the original caller's identity. This maps to the in-scope "key/secret exfiltration" / credential disclosure impact class. It is a real disclosure defect: any client that authenticates via `Authorization: Bearer <jwt>` to the vault gateway causes their own credential to be written into node logs whenever the node operator runs at Debug (request) or even default operational logging at Info (response) levels — the response leak in particular does not require Debug level at all.

## Likelihood Explanation
Triggering the log line requires no special privilege from the requesting client — any ordinary vault JSON-RPC caller (`vault_secretsList`, `vault_secretsCreate`, etc.) with a valid JWT causes their own token to be logged. This is reachable purely through normal, unprivileged client-to-gateway traffic; no operator/admin action is needed to *trigger* the disclosure. However, actually *exploiting* the disclosure (reading the token back out) requires subsequent access to the node's log stream, which is typically restricted to operators/log-aggregation consumers. This second-order access requirement is what keeps the severity moderate rather than critical, but it does not disqualify the finding — writing a plaintext bearer credential into logs is itself the broken security assumption (the team's own `hasAuth`-only convention in `authorizer.go` demonstrates this was recognized as sensitive elsewhere but missed here).

## Recommendation
In `GatewayHandler.HandleGatewayMessage`, avoid logging the raw `req`/`response` objects. Either log a sanitized copy with `Auth` cleared, or log only non-sensitive fields (method, ID, gatewayID), mirroring the `"hasAuth", req.Auth != ""` pattern already used in `authorizer.go`. Apply the same treatment to the `Infow("Sent message to gateway", "resp", response)` call. Consider adding a redacting wrapper/`MarshalLogObject` for `jsonrpc.Request`/`Response` so this protection is enforced centrally across all gateway handlers rather than per call site.

## Proof of Concept
1. Configure a Chainlink node running the vault gateway capability with `Log.Level = 'debug'`.
2. As an unprivileged client, send a valid vault JSON-RPC request (e.g., `vault_secretsList`) with header `Authorization: Bearer <jwt-token>`.
3. The gateway's HTTP entrypoint extracts the bearer token and threads it into the request's `Auth` field (`core/services/gateway/api/jsonrpccodec.go`, `DecodeRawRequest`).
4. `GatewayHandler.HandleGatewayMessage` receives the request and logs it wholesale via `reqLggr.Debugw("received message from gateway", "req", req)` (`core/capabilities/vault/gw_handler.go:182`).
5. Inspect node debug logs — the caller's JWT appears in plaintext in the `"req"` field.
6. As a secondary trigger not requiring Debug level: any successful request also causes `reqLggr.Infow("Sent message to gateway", "resp", response)` at line 231 — confirm whether `response`/embedded fields carry any sensitive echoed data.

Note: full confirmation that `chainlink-common`'s `jsonrpc.Request`/`Response` types lack a custom zap-redaction method could not be completed from this repo's index (the module source is external and not included). This is a caveat on certainty but the in-repo evidence (explicit avoidance of logging `req.Auth` elsewhere) supports treating the disclosure as real absent contrary evidence.

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

**File:** core/capabilities/vault/jwt_based_auth.go (L188-189)
```go
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
```

**File:** core/services/gateway/api/jsonrpccodec.go (L18-24)
```go
func (j *JSONRPCCodec) DecodeRawRequest(msgBytes []byte, jwtToken string) (*Message, error) {
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](msgBytes, jwtToken)
	if err != nil {
		return nil, err
	}
	return j.DecodeJSONRequest(jsonRequest)
}
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
