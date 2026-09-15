## Analysis

The reported Velodrome bug is a griefing pattern: because `proposalHash()` in OZ's Governor doesn't bind the proposal identity to the proposer, an attacker can front-run a legitimate proposal by submitting one with identical parameters and then immediately canceling it, denying the real proposer their expected proposal slot/ID.

Searching for the analogous pattern in chainlink — an internet-facing request-deduplication keyed purely on a caller-supplied identifier with no binding to an authenticated identity — surfaces the `ConfidentialRelayHandler`'s gateway entrypoint.

### Title
Unauthenticated Request-ID Squatting Enables Griefing of Confidential Relay Requests - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
`HandleJSONRPCUserMessage` in the gateway-facing `ConfidentialRelayHandler` registers an in-flight request in a global map keyed solely by the caller-supplied `req.ID`, with no authentication or ownership binding performed before that registration. Any unprivileged client hitting the public gateway can pre-register (front-run) an ID that a legitimate caller is about to use, causing the legitimate request to be rejected outright.

### Finding Description
`HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 chars, then immediately calls `h.newActiveRequest(req, labels, callback)` and fans the request out to nodes — no authorization, JWT validation, or owner check happens at the gateway layer before the ID is claimed: [1](#0-0) 

`newActiveRequest` performs the collision check purely against the raw, attacker-controlled `req.ID` string: [2](#0-1) 

`extractRequestLabels` only best-effort decodes `workflow_id`/`execution_id` for *logging* purposes — it explicitly does not authenticate or scope the request: [3](#0-2) 

This is confirmed by the existing test, which shows a bare duplicate `req.ID` submission (no auth headers at all) is rejected with "request ID already exists": [4](#0-3) 

Contrast this with the sibling `vault` gateway handler, which runs authorization/ownership resolution (`h.requestProcessor.ProcessRequest`) *before* creating the active request, and that pipeline explicitly prefixes the request ID with the authorized owner (`owner + RequestIDSeparator + originalID`) so IDs are namespaced per authenticated identity: [5](#0-4) [6](#0-5) 

The confidential relay handler has no equivalent ownership-scoping step, so its request-ID namespace is effectively global and unauthenticated — the same root cause as the reported bug: an identifier under attacker control, without any binding to the legitimate requester's identity, gates a scarce, one-shot resource (the map slot / proposal).

### Impact Explanation
An unprivileged actor with no relationship to a workflow can submit a `MethodCapabilityExec` or `MethodSecretsGet` request to the public gateway endpoint using an `ID` that a legitimate caller/enclave retry is about to use (or is known/predictable, e.g., a deterministic retry ID or execution-derived ID). Because the map entry is claimed on a first-come basis with no authentication gate, the legitimate request is rejected with "request ID already exists", denying that workflow execution's secrets/capability request. This is a denial-of-service/griefing vector against a specific execution rather than fund loss or key disclosure, matching the "Medium" severity class of the original report.

### Likelihood Explanation
Exploitability depends on the attacker's ability to guess or learn the victim's `req.ID` before it's submitted (e.g., via observing prior request/response traffic, logs, or a predictable ID-generation scheme on the caller side). Given the gateway is explicitly internet-facing and the ID check happens pre-authentication, no privileged access or node compromise is required — only network access to the gateway HTTP endpoint and knowledge/prediction of the target ID.

### Recommendation
Bind the in-flight request namespace to an authenticated identity (e.g., a verified caller/owner or workflow ID established via auth) before registering it in `activeRequests`, mirroring the vault handler's owner-prefixing pattern, rather than trusting the raw client-supplied `req.ID` as a global key. At minimum, perform request ID prefixing/scoping using an authenticated identity established prior to `newActiveRequest`.

### Proof of Concept
1. Attacker (no credentials required) sends an HTTP JSON-RPC request to the gateway with `method: "capabilityExecute"` (or `secretsGet`) and `id: "<guessed-or-known-victim-id>"`.
2. `HandleJSONRPCUserMessage` accepts it (ID length checks pass) and calls `newActiveRequest`, claiming the slot in `h.activeRequests` for that ID.
3. Shortly after, the legitimate caller submits the real request using the same `id` value.
4. `newActiveRequest` finds `h.activeRequests[req.ID] != nil` and returns `"request ID already exists: " + req.ID"`, so `HandleJSONRPCUserMessage` returns an error and the legitimate request is dropped/griefed — reproducible directly via the existing `TestConfidentialRelayHandler_DuplicateRequestID` test pattern, which requires no authentication on either call. [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L89-108)
```go
// extractRequestLabels best-effort decodes the logging identifiers from a
// request's params. Both relay methods' params carry these fields. A decode
// failure leaves them empty and is only logged: these labels are for
// correlation, and the params themselves are validated by the relay nodes,
// not here, so a request whose params do not decode is still fanned out and
// rejected there. ProcessRequest has already parsed the envelope as valid
// JSON by this point, so a failure here means params is not an object or
// carries non-string identifiers — malformed input rather than a gateway bug,
// hence debug level to avoid handing a caller a log-spam lever.
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
	if err := json.Unmarshal(*req.Params, &labels); err != nil {
		h.lggr.Debugw("could not decode relay request params for logging labels",
			"method", req.Method, "requestID", req.ID, "err", err)
	}
	return labels
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

**File:** core/services/gateway/handlers/vault/handler.go (L422-441)
```go
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L296-316)
```go
		rawPayload := json.RawMessage(`{"request_id":"test_request_id","encrypted_secrets":[{"id":{"key":"test_id","owner":"0xworkflow","namespace":"default"},"encrypted_value":"abc123"}]}`)

		var forwarded jsonrpc.Request[json.RawMessage]
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			forwarded = *args.Get(2).(*jsonrpc.Request[json.RawMessage])
		}).Return(nil)

		req := jsonrpc.Request[json.RawMessage]{
			ID:     "1",
			Method: vaulttypes.MethodSecretsCreate,
			Params: &rawPayload,
		}

		err = h.HandleJSONRPCUserMessage(t.Context(), req, common.NewCallback())
		require.NoError(t, err)

		require.NotNil(t, forwarded.Params)
		var forwardedCreateRequest vaultcommon.CreateSecretsRequest
		require.NoError(t, json.Unmarshal(*forwarded.Params, &forwardedCreateRequest))
		require.Equal(t, "0xworkflow"+vaulttypes.RequestIDSeparator+"1", forwardedCreateRequest.RequestId)
	})
```
