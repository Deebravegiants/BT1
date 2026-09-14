### Title
Vault gateway handler logs the raw JWT/bearer `Auth` credential from every user request at Debug level - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The gateway-side Vault `handler.HandleJSONRPCUserMessage` logs the entire incoming JSON-RPC request object — including the caller-supplied `Auth` field used for JWT/bearer authentication — at `Debug` level before authorization has even been evaluated. This mirrors the GitLab bug class in BIT-gitlab-2021-22184, where sensitive request data was written to server logs without redaction.

### Finding Description
When an unprivileged client sends a request to the Vault gateway handler (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`, or `MethodPublicKeyGet`), the handler immediately logs the full request object: [1](#0-0) 

```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	...
	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
```

The `req` struct includes an `Auth` field that is later checked to determine whether the caller supplied a credential: [2](#0-1) 

That `Auth` field is the bearer/JWT credential consumed by `vaultcap.Authorizer` / `JWTBasedAuth` to authenticate and authorize the caller as a specific owner (see the `authorizer.go` / `jwt_based_auth.go` usages of `Auth` found while investigating). Because `req` is passed wholesale to the structured logger via `"request", req`, whatever serialization the logger applies to the `jsonrpc.Request` struct will include this `Auth` value in plaintext in the node's Debug logs — before authorization succeeds, and regardless of whether the request is ultimately accepted or rejected.

This is distinct from the test `TestVaultHandler_InvalidParamsDoesNotLogRawParams` at `core/services/gateway/handlers/vault/handler_test.go:1016-1059`, which only verifies that *unparseable* params aren't logged after the fact — it does not cover this earlier `Debugw("handling vault request", ..., "request", req)` call, which runs unconditionally on every incoming message and logs the whole request, credential included.

Compare this to the sibling gateway request-logging path in `server_request.go`, which explicitly avoids putting raw payload/error content in logs or responses because "it may contain sensitive information": [3](#0-2) 

The Vault handler does not apply the same discipline to the `Auth` credential.

### Impact Explanation
If Debug-level logging is enabled on a Gateway node (a common operational/debugging configuration, and one node operators are told is safe for "forensic debugging" per `docs/CONFIG.md`), every caller's authentication credential passed to the Vault capability is written to that node's logs in the clear. Anyone with read access to Gateway node logs (log aggregation systems, support staff, misconfigured log shipping, etc.) could extract a live `Auth` token and replay it to impersonate the original caller against the Vault DON — i.e., a session/credential disclosure leading to request impersonation, matching the "Accept" criteria of concrete authentication/credential disclosure enabling impersonation.

### Likelihood Explanation
The log statement executes unconditionally on every `HandleJSONRPCUserMessage` call, gated only by the Debug log level being enabled — not by any error condition, malicious node, or privileged operator action. Debug logging is a standard, supported node configuration, making this reachable by any unprivileged client whose requests get processed while the Gateway operator has Debug logging on.

### Recommendation
Do not log the raw `req` object (or specifically strip/redact `req.Auth`) in `HandleJSONRPCUserMessage` before logging. Log only non-sensitive fields (method, ID) as is already done a few lines later, and apply the same "must not log raw params/credentials" discipline enforced elsewhere (see `handler_test.go`'s `TestVaultHandler_InvalidParamsDoesNotLogRawParams`) to this earlier debug statement as well.

### Proof of Concept
1. Enable `Log.Level = 'debug'` on a Gateway node running the Vault handler.
2. Send any JSON-RPC request to the vault DON with a populated `Auth` (JWT) field, e.g. a `secrets/list` or `secrets/create` request.
3. Observe the node's log output for the entry `"handling vault request"` at `core/services/gateway/handlers/vault/handler.go:403` — the serialized `request` field contains the caller's raw `Auth` token.
4. Extract that token from logs and replay it in a new request to the Gateway to act as the original caller (impersonation), since `req.Auth` is what `vaultcap.Authorizer` uses to establish `AuthorizedOwner()` at `core/services/gateway/handlers/vault/handler.go:435`.

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

**File:** core/services/gateway/handlers/vault/handler.go (L426-434)
```go
	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/capabilities/remote/executable/request/server_request.go (L386-393)
```go
func executeCapabilityRequest(ctx context.Context, lggr logger.Logger, capability capabilities.ExecutableCapability, payload []byte, callingDonID uint32, workflowDONBindingGate limits.GateLimiter) ([]byte, error) {
	capabilityRequest, err := pb.UnmarshalCapabilityRequest(payload)
	if err != nil {
		lggr.Errorw("failed to unmarshal capability request", "err", err)

		// Do not include the unmarshal error in the response as it may contain sensitive information
		return nil, errors.New("failed to unmarshal capability request")
	}
```
