Found a valid analog.

### Title
Unauthenticated request-ID griefing DOS on the confidential relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The `confidentialrelay` gateway handler registers every incoming JSON-RPC request into a shared `activeRequests` map keyed solely by the attacker-controlled `req.ID` field, with no authentication or per-user namespacing applied before the check. Any unprivileged caller of the gateway's `HandleJSONRPCUserMessage` entry point can pre-register a request ID and block a legitimate request with the same ID from ever being processed, mirroring the Dinari `OrderProcessor` griefing pattern where order IDs derived purely from user-supplied inputs allowed a front-runner to occupy the same ID and DOS the legitimate submitter.

### Finding Description
`HandleJSONRPCUserMessage` accepts the raw JSON-RPC request (only checking that `req.ID` is non-empty and ≤200 chars) and immediately calls `newActiveRequest`: [1](#0-0) 

`newActiveRequest` performs the duplicate check purely against the raw, caller-supplied ID: [2](#0-1) 

There is no authentication step, no owner/tenant binding, and no server-side ID derivation before this uniqueness check — unlike the sibling `vault` gateway handler, which routes every request through `GatewayVaultRequestProcessor.authorizeAndStamp`, prefixes the request ID with the cryptographically authorized owner (`authorizedOwner + RequestIDSeparator + originalRequestID`), and only then checks `activeRequests` for collisions: [3](#0-2) [4](#0-3) 

In the confidential relay handler, the map key is the bare client-supplied `req.ID`. This is precisely the Dinari `OrderProcessor.requestOrder` bug class: a value derived (or in this case simply equal to) attacker-controllable input is used as a global-state key without binding it to the authenticated identity of the caller, so anyone can occupy a slot before the legitimate party's request arrives.

### Impact Explanation
An unauthenticated/unprivileged client of the gateway can:
1. Predict or observe (e.g., via workflow logs, telemetry, or shared conventions such as UUID-based IDs used elsewhere in the codebase, or simply flood with many IDs) the `req.ID` a victim workflow/enclave is about to submit for a `secrets_get` or `capability_exec` relay call.
2. Submit their own request with that exact ID first.
3. The victim's subsequent legitimate request with the same ID is rejected with `"request ID already exists"` at `newActiveRequest`, permanently blocking that specific relay request until the attacker's entry expires (bounded by `requestTimeout`, default 30s, via `removeExpiredRequests`).

This is a denial-of-service against a specific in-flight secret-fetch or capability-execution request routed through the internet-facing gateway, which can stall workflow executions dependent on the relay's quorum response. Because `req.ID` is not bound to any authenticated caller/session, the attack requires no privilege beyond being able to send JSON-RPC messages to the gateway's public HTTP endpoint.

### Likelihood Explanation
Exploitability depends on the attacker being able to guess or observe the exact `req.ID` the victim will use, which is a real but non-trivial precondition (severity Medium in the original Dinari-style class as well). If IDs are generated with low entropy, are sequential, or are otherwise observable (e.g., logged, or transmitted over a channel the attacker can watch/predict), this becomes practically exploitable at negligible cost to the attacker (a single well-timed request). The absence of an authenticated-owner binding on the ID (present in the sibling vault handler) makes this class of collision entirely feasible where the vault handler already closes it off.

### Recommendation
Bind the `activeRequests` key to something the gateway can attribute to an authenticated party rather than to the raw client-supplied `req.ID`, following the same pattern already used in `core/capabilities/vault/gateway_vault_request_processor.go` (`authorizeAndStamp`): derive or prefix the internal tracking key with an authenticated owner/session/connection identifier before the duplicate check in `newActiveRequest`, and only accept the bare ID back-compat for the wire-level response correlation (stripped before returning to the caller, as `sendSuccessResponse`/`errorResponse` already do in the vault handler). At minimum, scope the collision check per originating connection/DON member rather than globally across all callers.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-286)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
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
