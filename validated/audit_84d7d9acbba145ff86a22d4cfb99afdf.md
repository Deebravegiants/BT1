This confirms the report's central caveat: the gateway's public HTTP entrypoint (`gateway.go` `ProcessRequest`) reaches `HandleJSONRPCUserMessage` for non-legacy JSON-RPC requests without any per-handler authentication or allowlist check — auth is merely optional passthrough via `jwtToken` extracted from the header, and `confidentialrelay.HandleJSONRPCUserMessage` itself performs no signature/ownership verification before calling `newActiveRequest`, unlike the vault handler which calls `h.requestProcessor.ProcessRequest` for authorization first.This confirms the claim's technical accuracy: `gateway.go`'s `ProcessRequest` at [1](#0-0)  routes any JSON-RPC request whose method maps to the confidential relay handler straight into `HandleJSONRPCUserMessage` with no signature verification, allowlist check, or ownership binding — the `msg.Validate()`/signature check only applies to the legacy `DonID`-based path, not the JSON-RPC method-routed path used for `confidentialrelay`. `newActiveRequest` then keys purely on the caller-supplied `req.ID` with no owner scoping and no cache-size bound, confirmed by [2](#0-1) , and the handler's own test explicitly demonstrates the squatting behavior at [3](#0-2) .

Audit Report

## Title
Confidential relay gateway handler creates unowned, attacker-keyed active requests with no cache-size bound - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
`HandleJSONRPCUserMessage` in the confidential relay gateway handler accepts any caller-chosen `req.ID` (up to 200 chars) and uses it as the sole key into the shared `h.activeRequests` map, with no ownership binding and no bound on total concurrent entries. An unprivileged caller reaching the gateway's public HTTP endpoint can pre-occupy an ID to deny a legitimate workflow/enclave request, or flood the map with unique IDs to grow unbounded memory until the periodic timeout sweep runs.

## Finding Description
The gateway's public entrypoint `gateway.ProcessRequest` decodes any incoming JSON-RPC request and, for the non-legacy path (no `DonID` set on the decoded message), routes purely by JSON-RPC method name to the corresponding handler's `HandleJSONRPCUserMessage` — with no signature or allowlist check on this path (that validation, `msg.Validate()`, only runs for the legacy `DonID`-keyed branch): [1](#0-0) 

`confidentialrelay.HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 characters, then calls `newActiveRequest`, which does a plain presence check keyed by the raw `req.ID` and inserts unconditionally otherwise — no per-sender/owner scoping, no cap on map size: [4](#0-3) 

This contrasts with the safer patterns already present elsewhere in the codebase: `common.RequestCache` scopes its key by `{sender, messageID}` and enforces `maxCacheSize`, rejecting inserts once full, and the `vault` handler performs `h.requestProcessor.ProcessRequest` authorization before creating its active request, effectively owner-namespacing the ID. The confidential relay handler has neither protection. The handler's own test suite confirms the squatting behavior directly: submitting the same `req.ID` a second time returns `"request ID already exists"` rather than being scoped to the second (or first) caller's identity: [3](#0-2) 

## Impact Explanation
Two concrete consequences:
1. **ID squatting / DoS**: if an attacker can predict or learn the `req.ID` (e.g., a node/enclave retry ID) a legitimate request will use, they can occupy `h.activeRequests[req.ID]` first, causing the legitimate request's call to `newActiveRequest` to fail with `"request ID already exists"` [5](#0-4) , denying the confidential-compute node's relay request from completing.
2. **Unbounded memory growth**: because there's no `maxCacheSize`-style cap, an attacker can insert arbitrary unique IDs (up to 200 chars each) as fast as the gateway will accept them, growing `h.activeRequests` until the `requestTimeout` (default 30s, `defaultRequestTimeoutSec`) sweep runs; sustained flooding keeps the map large indefinitely.

This maps to a resource-exhaustion / availability impact against the gateway, and to request-completion denial for a legitimate confidential-relay caller — a plausible in-scope "gateway request impersonation/DoS"-adjacent finding, though notably weaker than key/secret exfiltration or fund-movement classes since no confidential data or funds are directly exposed.

## Likelihood Explanation
The attacker only needs to be able to send a JSON-RPC request to the gateway's public HTTP endpoint for a method the confidential relay handler serves (`MethodSecretsGet`, `MethodCapabilityExec`); the routing code shows this reaches `HandleJSONRPCUserMessage` without any signature or allowlist check on that path. The main uncertainty is whether the attacker can predict or learn a legitimate `req.ID` in advance to make the squatting scenario (rather than just the memory-growth scenario) practically damaging — the report does not establish how relay request IDs are generated/exposed to an outside attacker, so the squatting DoS is plausible but not concretely demonstrated end-to-end from an attacker's vantage point. The unbounded-growth concern is bounded in practice by the 30-second default timeout sweep (`defaultRequestTimeoutSec`/`removeExpiredRequests`), limiting sustained impact to a rolling window rather than permanent exhaustion.

## Recommendation
- Scope `activeRequests` keys by authenticated caller identity (sender) in addition to `req.ID`, mirroring `common.RequestCache`'s `{sender, id}` compound key.
- Add an explicit `maxCacheSize`-style bound on `h.activeRequests` so a flood of unique IDs cannot grow the map without limit even within the timeout window.
- Consider requiring/checking the same message-signature validation used on the legacy path for JSON-RPC-routed requests reaching handlers that maintain per-request server-side state.

## Proof of Concept
Existing repository test demonstrates the ID-collision behavior directly (unit-test level, not a live attacker/victim scenario):
`TestConfidentialRelayHandler_DuplicateRequestID` — send a request with `ID: "req-dup"`, then send a second request with the same ID; the second call returns `"request ID already exists"` [3](#0-2) . To fully substantiate the DoS-against-a-victim scenario, an additional test/PoC would need to show (a) how an external, unprivileged caller can reach `gateway.ProcessRequest` and route to this handler's method without prior authentication, and (b) how that caller can learn or predict a legitimate confidential-relay request's `req.ID` before the legitimate caller submits it.

### Citations

**File:** core/services/gateway/gateway.go (L221-276)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

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
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-430)
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
