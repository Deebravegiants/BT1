### Title
Unauthenticated Request-ID Squatting Causes Denial-of-Service on In-Flight Confidential Relay Requests - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The gateway's confidential-relay handler accepts any client-supplied `req.ID` as the sole key for tracking an in-flight request, with no per-caller/per-owner namespacing and no authentication performed before the ID is claimed. An unprivileged attacker who can guess or observe another user's request ID (e.g. an ID derived from a public workflow/execution identifier, or simply raced) can pre-register that same ID first, causing the legitimate request to be rejected outright — the same "ID collision front-running" bug class as the reported `SpokeCommon.createAccount`/`AccountManager.createAccount` vulnerability, where an unvalidated, user-chosen ID could be squatted by a third party before the legitimate transaction landed.

### Finding Description
`gateway.ProcessRequest` decodes the raw HTTP body into a `jsonrpc.Request` and dispatches it directly to the target handler's `HandleJSONRPCUserMessage` without performing any caller authentication at the gateway layer: [1](#0-0) 

For the confidential relay handler, `HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and under 200 characters before immediately calling `newActiveRequest`: [2](#0-1) 

`newActiveRequest` claims the raw, attacker-controlled `req.ID` as the sole key in the global `activeRequests` map — there is no ownership check, no authentication, and no per-workflow/per-caller scoping of the ID space: [3](#0-2) 

If a request with the same `ID` is already active, the new request is rejected with `"request ID already exists"`, and this is enforced *before* any attestation/authorization check runs (those checks happen later inside `handleSecretsGet`/`handleCapabilityExecute`, which are downstream of this gateway-layer dedup, not upstream of it). This is confirmed by the existing test asserting the collision is rejected purely on ID equality regardless of caller identity: [4](#0-3) 

This mirrors the report's root cause exactly: `accountId`/`req.ID` is user-supplied, unvalidated in format or ownership, and used directly as a unique key that a third party can pre-empt. In the report, an attacker copies a pending Ethereum transaction's `accountId` and submits it first on the destination chain; here, an unprivileged network client can submit a request with the same `req.ID` as a legitimate in-flight relay request before (or racing) the legitimate sender, causing the legitimate request to fail with a hard error rather than being queued/retried transparently.

By contrast, the `vault` and `http_trigger` gateway handlers mitigate this either by requiring successful authorization *before* claiming the ID (`vault/handler.go`, which authorizes first then calls `newActiveRequest`) or by prefixing the ID with the cryptographically authorized owner (`gateway_vault_request_processor.go`'s `authorizeAndStamp`, producing `authorizedOwner + separator + originalRequestID`), which scopes ID collisions to a single authenticated owner: [5](#0-4) [6](#0-5) 

The confidential relay handler has no equivalent scoping, leaving the raw `activeRequests` map keyed purely on unauthenticated, attacker-controllable input.

### Impact Explanation
Any unprivileged network caller able to reach the gateway's HTTP endpoint can deny service to a specific in-flight confidential-relay request by racing/guessing its `req.ID` and submitting a colliding request first. The legitimate caller's request is rejected with a hard error (`"request ID already exists: <id>"`), forcing them to retry with a new ID and incurring wasted round trips, latency, and potential workflow-execution failures — a griefing impact with no profit motive required from the attacker, matching the report's "Griefing" and "Unbounded gas consumption"-class DoS pattern (here: unbounded wasted compute/latency rather than gas).

### Likelihood Explanation
The gateway's HTTP endpoint is internet-facing and this code path performs zero authentication before the ID-collision check runs, so exploitation requires only network access and knowledge (or a race) of the target's `req.ID`. Because `req.ID` is fully attacker-chosen and unscoped, any caller reachable by the gateway can attempt the collision at will, making this readily reachable from an unprivileged client.

### Recommendation
Scope `activeRequests` keys by an authenticated identity (e.g., prefix with the authorized/attested workflow or caller identity similar to the vault handler's `authorizedOwner + separator + originalRequestID` pattern) instead of trusting the raw client-supplied `req.ID`, and/or perform authentication/attestation checks before the ID uniqueness check so that only an already-authorized caller can claim or contend for a given ID.

### Proof of Concept
1. Attacker sends `HTTP POST` to the gateway with a JSON-RPC request using method `MethodSecretsGet`/`MethodCapabilityExec` and an `ID` equal to a value they expect (or observe) a victim to use for their own confidential-relay request, before the victim's request arrives, per `HandleJSONRPCUserMessage`/`newActiveRequest`: [7](#0-6) 
2. Victim's legitimate request with the same `ID` arrives shortly after and is rejected with `errors.New("request ID already exists: " + req.ID)`, denying the victim's request.
3. The existing unit test demonstrates this exact rejection behavior for colliding IDs with no ownership distinction: [4](#0-3)

### Citations

**File:** core/services/gateway/gateway.go (L267-279)
```go
	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
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

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L426-441)
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
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-286)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}
```
