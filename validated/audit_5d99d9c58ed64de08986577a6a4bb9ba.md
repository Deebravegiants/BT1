Based on my investigation, I found a plausible analog but cannot fully confirm the exploitability of the sensitive field within the token budget available. I'll report what is verified and flag the uncertainty rather than overclaim.

### Title
Full JSON-RPC request (including bearer `Auth` token) logged at Debug level - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` logs the entire inbound `jsonrpc.Request[json.RawMessage]` object, and the entire outbound `jsonrpc.Response[json.RawMessage]`, to the node's structured logger.

### Finding Description
In `HandleGatewayMessage`, the handler logs the whole request and response structs rather than selected safe fields: [1](#0-0)  and [2](#0-1) . Elsewhere in the same package, requests are shown to carry an `Auth` field that is populated with a bearer/JWT credential used for request authentication/impersonation, e.g. `jwtAuth.apply(t, &jsonRequest)` and `outboundRequestWithoutAuth` explicitly zeroing `req.Auth` before further use [3](#0-2) , and `req.Auth = createTestJWTToken(t, req, privateKey)` in the gateway HTTP trigger handler tests. The `jsonrpc.Request`/`Response` types live in the external `chainlink-common` package (`jsonrpc "github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2"`), so I could not directly inspect their field definitions or confirm whether Go's structured logger (`zap`/`slog`) would serialize the `Auth` field when the struct is passed as a log value (this depends on the type's exported fields and any `MarshalLogObject`/`String()` redaction implementation, which I was unable to locate in this repo since the type is vendored externally).

A related, more clearly scoped case is `core/services/chainlink/config.go`, where `Secrets.TOMLString()` intentionally redacts secret values before rendering for logs [4](#0-3) , and the web router already blacklists known password-bearing keys before logging HTTP bodies [5](#0-4) . No equivalent redaction exists for the `Auth` field of `jsonrpc.Request` at the two log call sites identified above.

### Impact Explanation
If the `Auth` field (or ciphertext/other sensitive payload fields) is in fact serialized by the logger when passing the full `req`/`response` struct, then any external caller's authentication token (JWT signed by the workflow owner, used to authorize vault/gateway operations) would be persisted to node logs, which are typically readable by node administrators/operators — directly analogous to the referenced CVE-2025-2092 pattern (remote-session secrets written to logs).

### Likelihood Explanation
Likelihood is uncertain: the affected log calls are at `Debugw`/`Infow` level, so exposure depends on operator log-level configuration, and I could not confirm from this repo's index whether `jsonrpc.Request.Auth` is an exported field that a JSON/structured encoder would actually serialize, or whether `chainlink-common` already implements safe stringification for these types.

### Recommendation
Because I could not verify the external type's field layout and serialization behavior, I cannot assert this as a confirmed vulnerability. Verifying `jsonrpc.Request`/`Response` definitions in `chainlink-common` (specifically whether `Auth` and any secret-bearing fields are excluded from default logging) requires direct access to that dependency's source, which is outside what my current tools indexed. If the user wants a confirmed answer, a Devin session with full filesystem/module access would be needed to inspect the vendored `chainlink-common/pkg/jsonrpc2` package and trace whether `Debugw("received message from gateway", "req", req)` actually renders the `Auth` token into log output.

### Proof of Concept
Not established — reachability of the sensitive field through the logger's serialization path was not confirmed with certainty due to the external dependency limitation noted above.

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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1263-1266)
```go
func outboundRequestWithoutAuth(req jsonrpc.Request[json.RawMessage]) jsonrpc.Request[json.RawMessage] {
	req.Auth = ""
	return req
}
```

**File:** core/services/chainlink/config.go (L448-455)
```go
// TOMLString returns a TOML encoded string with secret values redacted.
func (s *Secrets) TOMLString() (string, error) {
	b, err := gotoml.Marshal(s)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
```

**File:** core/web/router.go (L643-658)
```go
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
