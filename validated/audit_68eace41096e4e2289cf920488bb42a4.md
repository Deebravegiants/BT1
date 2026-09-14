### Title
Unprivileged client can grief any other vault/relay request by squatting the JSON-RPC request ID before the legitimate caller uses it - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Tempus `depositAndFix` bug is a griefing attack where an attacker pre-populates shared mutable state (yield-share balance) with a value under their control, so that a later `assert` guarding a legitimate user's transaction always fails. The Chainlink Gateway's vault and confidential-relay JSON-RPC handlers contain the same bug-class: an `activeRequests` map keyed purely by the client-supplied JSON-RPC `req.ID` is checked with an "already exists" guard, and this key is *not* scoped to the caller's authenticated identity. Any unprivileged gateway client can pre-register a request with the same ID a victim will use, causing the victim's legitimate request to be rejected.

### Finding Description
In `core/services/gateway/handlers/vault/handler.go`, `HandleJSONRPCUserMessage` validates the request ID's length/emptiness, then (for authorization-requiring methods) authorizes the caller and only *afterward* calls `h.newActiveRequest(req, callback)`: [1](#0-0) 

`newActiveRequest` stores the pending request in a single handler-wide map keyed solely by the raw `req.ID` string supplied by the client, and errors out if a collision is detected: [2](#0-1) 

Crucially, `req.ID` is never namespaced by the authorized owner (`authorizedOwner`) before being used as the map key — it is the literal, attacker-controllable ID from the inbound JSON-RPC envelope. This means two different, unrelated owners hitting the same gateway node can collide on the same `req.ID` string. The exact same pattern (map keyed by unscoped `req.ID`, "already exists" rejection) exists in the confidential-relay handler: [3](#0-2) 

This mirrors the Tempus finding precisely: a check (`assert`/`if exists { return err }`) that is only correct in the absence of adversarial pre-population of shared state keyed by a value the attacker can also choose, allowing the attacker to make a legitimate call fail.

### Impact Explanation
An attacker who can reach the gateway's public JSON-RPC endpoint (any unprivileged/unauthenticated-enough client capable of sending a well-formed request, since `req.ID` validation and the collision check occur very early, in the vault handler even the `MethodPublicKeyGet` path hits `newActiveRequest` prior to any owner-specific authorization) can:
- Submit a request using a request ID they predict (e.g., sequential counters, workflow-generated deterministic IDs, or commonly reused literals like `"1"`) before the legitimate caller's request arrives.
- Cause the legitimate caller's `vault.secrets.create/update/delete/list` or confidential-relay `secrets.get`/`capability.exec` request to fail immediately with `"request ID already exists"`, denying service to that specific operation/workflow execution.

This is a denial-of-service/griefing vulnerability against specific vault or confidential-relay operations for other tenants sharing the same DON/gateway, without requiring the attacker to compromise any keys or bypass authentication.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or race the victim's `req.ID` before the collision window closes (the entry is removed once the request completes or times out). Likelihood is elevated where clients use predictable/sequential/short IDs (the code enforces only a 200-character max length and non-empty, no randomness/entropy requirement), or where an attacker can rapidly flood many candidate IDs. It is lower against clients using high-entropy UUIDs, but the underlying design flaw — an owner-unscoped, client-controlled global key used for a liveness-critical guard — is present regardless of ID entropy and represents the same root-cause fragility as the reported Tempus issue.

### Recommendation
- Scope the `activeRequests` key (and the confidential-relay equivalent) by authenticated owner/session in addition to `req.ID`, e.g. `ownerID + RequestIDSeparator + req.ID`, similar to the owner-prefixing already used elsewhere in the vault code path (`RequestIDSeparator`, seen in `vaulttypes.RequestIDSeparator` and `gateway_vault_request_processor.go`), so that one owner cannot collide with another's request ID.
- Perform the collision check for `newActiveRequest` after the owner has been authorized (not before), and never let a raw, unauthenticated caller occupy a slot capable of blocking another tenant's request.
- Consider generating/deriving a portion of the internal correlation key server-side (e.g., including a per-connection/session identifier) rather than trusting the full ID from the client for de-duplication.

### Proof of Concept
1. Attacker (owner B) sends a `vault.secrets.create` (or any supported method) JSON-RPC request to the gateway with `ID = "victim-req-42"` and syntactically valid but otherwise irrelevant params so it reaches `newActiveRequest` in `core/services/gateway/handlers/vault/handler.go:457-472`, registering that ID in the shared `h.activeRequests` map.
2. Victim (owner A), unaware of the collision, sends their own legitimate `vault.secrets.create` request using `ID = "victim-req-42"` (e.g., because their client uses simple/sequential/deterministic IDs).
3. `HandleJSONRPCUserMessage` authorizes owner A successfully, then calls `newActiveRequest`, which finds `h.activeRequests["victim-req-42"] != nil` and returns `"request ID already exists: victim-req-42"`, at `core/services/gateway/handlers/vault/handler.go:460-463`, causing owner A's legitimate request to fail even though owner A did nothing wrong.
4. The identical exploit path applies to `core/services/gateway/handlers/confidentialrelay/handler.go:414-430` for confidential-relay `secrets.get`/`capability.exec` traffic.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-441)
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
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```
