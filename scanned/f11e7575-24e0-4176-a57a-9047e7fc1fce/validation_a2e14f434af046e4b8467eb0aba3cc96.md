## Title
Global, unauthenticated request-ID namespace in the ConfidentialRelay gateway handler lets any caller squat another user's in-flight request ID and deny their relay request - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The ConfidentialRelay gateway handler stores all in-flight requests in a single map keyed only by the caller-supplied JSON-RPC `req.ID`, with **no authorization step and no per-owner/per-workflow namespacing** before the ID is inserted. Any unprivileged caller reaching this handler can submit a request with an ID that collides with another party's legitimate, concurrently in-flight request, causing that legitimate request to be rejected outright with "request ID already exists." This is the same root-cause pattern as the referenced AutoRoller bug: a shared, globally-unique resource key (maturity date there, request ID here) that any unprivileged actor can claim ahead of time to brick another actor's otherwise-valid operation.

### Finding Description
`HandleJSONRPCUserMessage` in the ConfidentialRelay handler performs only trivial validation (non-empty ID, length ≤ 200) before calling `newActiveRequest`, with **no call to any `Authorizer`/allowlist check** — contrast this with the sibling Vault handler, which runs `requestProcessor.ProcessRequest` (auth + owner-prefixing of the ID) before inserting into its own `activeRequests` map: [1](#0-0) 

`newActiveRequest` keys the shared `activeRequests` map directly by the raw, attacker-controlled `req.ID` and rejects the insert if that key is already present: [2](#0-1) 

There is no owner/workflow scoping mixed into this key (unlike the Vault handler, which prefixes the ID with the authorized owner via its `AuthorizeRequest` → `StampAuthorizedParams` pipeline before ever touching its own `activeRequests` map — see `sendSuccessResponse`'s owner-prefix stripping logic, which only exists in the Vault handler): [3](#0-2) 

Because the ConfidentialRelay handler has no such authorization or prefixing step, the request-ID namespace is effectively a single global keyspace shared across every caller reaching this method (`MethodSecretsGet`, `MethodCapabilityExec`). The project's own regression test confirms the exact collision behavior — a second `HandleJSONRPCUserMessage` call with the same ID fails once the first is registered: [4](#0-3) 

An adversary who can predict or learn another party's chosen request ID (e.g., by observing execution/workflow IDs surfaced in logs, telemetry, or simply racing with common ID patterns) can pre-register that same ID via their own call to the handler. The victim's subsequent legitimate `HandleJSONRPCUserMessage` call for the same ID will then fail with `"request ID already exists"` before it is ever fanned out to relay nodes, denying that specific request. This mirrors the AutoRoller bug class exactly: a permissionless, first-come-first-served claim over a shared identifier namespace used to gate a downstream, otherwise-legitimate operation.

### Impact Explanation
An unprivileged party able to reach the gateway's ConfidentialRelay JSON-RPC methods can selectively deny specific in-flight relay/capability-exec requests from other users by squatting their request ID first, causing those requests to fail immediately rather than being processed by the DON. This is a targeted denial-of-service on a specific legitimate request/execution rather than a full outage, but it can be used repeatedly to disrupt any workflow execution whose request ID becomes known or guessable to the attacker, exactly analogous to how AutoRoller B could brick AutoRoller A's roll by claiming its target maturity first.

### Likelihood Explanation
Exploitation requires only unauthenticated/unprivileged access to the gateway's ConfidentialRelay endpoint (no signature, allowlist, or JWT check gates `HandleJSONRPCUserMessage` for this handler, unlike Vault) and knowledge or a good guess of the victim's request ID. Because request IDs are plain caller-chosen strings with no owner binding enforced at this layer, and the collision check happens synchronously and deterministically ("already exists" test proves first-writer-wins), the race is straightforward to win if the attacker can observe or predict the ID before the legitimate caller submits it.

### Recommendation
Scope the `activeRequests` key (and any related caches) in the ConfidentialRelay handler to include an authenticated identity component (e.g., authorized workflow owner or DON/session identity), the same way the Vault handler binds the request ID to `AuthorizedOwner` via its authorization pipeline before insertion. At minimum, require some form of authorization/ownership binding for `MethodSecretsGet`/`MethodCapabilityExec` requests so that the request-ID namespace cannot be squatted by an unrelated, unprivileged caller.

### Proof of Concept
1. Attacker learns or guesses request ID `X` that a legitimate workflow execution is about to use (e.g., a predictable execution ID format).
2. Attacker sends a `vault`-relay-style JSON-RPC request (`MethodCapabilityExec`) to the gateway with `ID = X` before the legitimate caller does; `newActiveRequest` succeeds and inserts key `X` into `activeRequests`.
3. The legitimate caller's subsequent request with the same `ID = X` reaches `newActiveRequest`, finds the key already occupied, and is rejected with `"request ID already exists: X"` — reproduced exactly by the existing test `TestConfidentialRelayHandler_DuplicateRequestID`.
4. The legitimate execution fails to be relayed to the DON, denying that specific workflow request.

### Citations

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

**File:** core/services/gateway/handlers/vault/handler.go (L443-472)
```go
	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return h.handleSecretsCreate(ctx, ar)
	case vaulttypes.MethodSecretsUpdate:
		return h.handleSecretsUpdate(ctx, ar)
	case vaulttypes.MethodSecretsDelete:
		return h.handleSecretsDelete(ctx, ar)
	case vaulttypes.MethodSecretsList:
		return h.handleSecretsList(ctx, ar)
	default:
		return h.sendResponse(ctx, ar, h.errorResponse(req, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method), nil))
	}
}

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
