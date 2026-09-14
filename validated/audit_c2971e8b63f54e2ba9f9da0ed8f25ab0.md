### Title
Full JSON-RPC gateway requests (including bearer `Auth` tokens) are written to node logs at Debug level - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` logs the entire incoming `jsonrpc.Request[json.RawMessage]` object via `reqLggr.Debugw("received message from gateway", "req", req)` before any authorization/authentication has been applied. The same pattern exists in the confidential-relay gateway handler. Because `jsonrpc.Request` carries an `Auth` field used to transport JWT/session credentials for the Vault JWT-based-auth flow (`core/capabilities/vault/jwt_based_auth.go`, `core/capabilities/vault/authorizer.go`), enabling debug-level logging on the node causes bearer tokens submitted by unprivileged external gateway/workflow clients to be written verbatim into the node's log stream. This mirrors the azure-file-csi-driver bug class (CVE-2024-3744): sensitive tokens are only logged when a particular log verbosity is enabled, and any actor with log access can then reuse the token to impersonate the legitimate caller.

### Finding Description
`GatewayHandler.HandleGatewayMessage` in [1](#0-0)  is the entry point for all Vault-capability messages relayed by the gateway from workflow/DON clients. It immediately logs the full request struct:
```go
reqLggr := h.requestLogger(req, gatewayID)
reqLggr.Debugw("received message from gateway", "req", req)
```
The `jsonrpc.Request` type carries an `Auth` field that is used as the credential channel for JWT-based authorization, confirmed by test assertions such as `req.Auth == ""` in [2](#0-1) , and by the JWT authorization pipeline in `core/capabilities/vault/jwt_based_auth.go` and `core/capabilities/vault/authorizer.go`. When `req.Auth` carries a populated bearer/JWT token, logging `req` as a structured field serializes that token into the node's log output.

The identical pattern recurs in the confidential-relay gateway handler:
```go
h.lggr.Debugw("received message from gateway", "gatewayID", gatewayID, "requestID", req.ID)
``` [3](#0-2)  — this instance only logs `req.ID`, not the full struct, so it is not itself vulnerable, but the vault handler's `"req", req` pairing is the concrete leak point.

This is directly analogous to the reported CVE: sensitive credential material is written to logs only when a particular log-level is enabled (`Debugw` requires debug verbosity, just as the CSI driver requires `-v 2` or higher), by design intended for diagnostics, but exposing tokens to anyone with log access.

### Impact Explanation
An actor with read access to node logs (operators, log aggregation pipelines, support/debug tooling) could recover JWT/auth tokens submitted by workflow DON participants or external gateway clients over the Vault path. Such tokens map to `AuthResult`/authorized owner identity in the Vault authorization pipeline (`core/capabilities/vault/gateway_vault_request_processor.go`), so recovering them could let an attacker replay requests and impersonate the legitimate token holder for secret create/update/delete/list operations, i.e., a credential-disclosure-driven authorization bypass — matching the CWE-532 classification of the source advisory.

### Likelihood Explanation
Exploitability requires: (1) the node/gateway handler running with debug-level logging enabled, and (2) an attacker having read access to the resulting logs. This is a realistic operational configuration for troubleshooting, and unlike the CSI driver's own admin-controlled `-v` flag, the log line is triggered automatically on every gateway message when the node's logger is at debug level — no additional operator action per-request is required. The trigger is an ordinary unprivileged gateway/workflow client message; no privileged or malicious-node position is needed to cause the token to be logged.

### Recommendation
- Do not log the raw `req` struct; log only non-sensitive fields (`req.ID`, `req.Method`, `gatewayID`) as already done in the confidential-relay handler.
- If the full payload must be retained for diagnostics, redact or omit the `Auth` field explicitly before logging (e.g., implement a custom `String()`/`MarshalLogObject` for `jsonrpc.Request` that masks `Auth`).
- Apply the same review to the "Sent message to gateway" / `"resp", response` log line to ensure no token or secret material is echoed back into logs.

### Proof of Concept
1. Configure the node/gateway with `Debug` log level enabled.
2. Submit a Vault gateway message (e.g., `MethodSecretsList` or `MethodSecretsCreate`) with a populated `Auth` header carrying a JWT token, routed through `GatewayHandler.HandleGatewayMessage`.
3. Observe the node log output for the entry `"received message from gateway" req=<full struct>`; the emitted JSON includes the `Auth` field value verbatim.
4. Any party able to read this log stream can extract the token and reuse it against the gateway to authenticate as the original caller.

Note: I could not directly inspect the `jsonrpc.Request` struct definition (it lives in an external `jsonrpc` package not fully indexed) to see the exact JSON tag name/casing for the `Auth` field, nor confirm whether it has a custom `String()`/`MarshalJSON` that might already redact it — this should be verified in a live session before treating the finding as fully confirmed.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-182)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/capabilities/vault/gw_handler_test.go (L192-196)
```go
				ra.EXPECT().AuthorizeRequest(mock.Anything, mock.MatchedBy(func(req jsonrpc.Request[json.RawMessage]) bool {
					return req.Method == vaulttypes.MethodSecretsCreate &&
						req.ID == "1" &&
						req.Auth == "" &&
						req.Params != nil
```

**File:** core/capabilities/confidentialrelay/handler.go (L269-270)
```go
func (h *Handler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	h.lggr.Debugw("received message from gateway", "gatewayID", gatewayID, "requestID", req.ID)
```
