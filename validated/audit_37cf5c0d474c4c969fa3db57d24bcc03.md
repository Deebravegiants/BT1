This confirms the finding: the gateway's HTTP ingress (`core/services/gateway/network/httpserver.go`) is a generic public endpoint with no built-in authentication — the `auth` string is simply passed through to `ProcessRequest`, and `gateway.go`'s `ProcessRequest` dispatches directly to `h.HandleJSONRPCUserMessage` without any per-handler authorization gate. Unlike the `vault` handler, which performs its own internal `requestProcessor.ProcessRequest` authorization/allowlist check and re-keys in-flight requests by `owner + RequestIDSeparator + requestID` before touching a shared map, the `confidentialrelay` handler's `HandleJSONRPCUserMessage` only validates ID length/non-emptiness and then calls `newActiveRequest`, which keys `h.activeRequests` directly by the raw client-supplied `req.ID` and rejects any request whose ID is already claimed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

This satisfies the claim's own stated caveat: there is no upstream allowlist/auth layer filtering callers before dispatch to the `confidentialrelay` handler — `multiHandler.HandleJSONRPCUserMessage` (`core/services/gateway/multihandler.go:62-69`) simply routes by method name to the target handler with no authorization step, and `gateway.ProcessRequest` performs no caller identity check either.

Audit Report

## Title
Unauthenticated request-ID squatting causes griefing DoS in Confidential Relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
The `confidentialrelay` gateway handler's `HandleJSONRPCUserMessage` uses the raw, client-supplied `req.ID` as a global map key in `h.activeRequests` with no authentication, authorization, or per-caller namespacing, unlike the sibling `vault` handler which authorizes callers and re-keys entries by `owner + RequestIDSeparator + requestID`. Any unprivileged actor able to reach the gateway's public JSON-RPC HTTP ingress can pre-claim an arbitrary/predictable `req.ID` before the legitimate caller, causing the legitimate request to be rejected with `"request ID already exists"`.

## Finding Description
`HandleJSONRPCUserMessage` (`core/services/gateway/handlers/confidentialrelay/handler.go:394-412`) performs only trivial length/emptiness validation on `req.ID`, then calls `newActiveRequest`, which locks `h.mu`, checks `h.activeRequests[req.ID] != nil`, and errors out if occupied, otherwise claiming it (`handler.go:414-430`). The package's own comment documents this is intentional design: "the gateway stays a dumb relay: it does not otherwise interpret params" (`handler.go:80-83`). Tracing the call path upstream confirms no authorization gate exists before this: the gateway's public HTTP server (`core/services/gateway/network/httpserver.go`) forwards `auth` as an opaque string to `HTTPRequestHandler.ProcessRequest`, which in `gateway.go:267-276` dispatches straight to `h.HandleJSONRPCUserMessage` based only on method/service-name routing — no caller identity or allowlist check occurs at this layer. The `multiHandler` (`multihandler.go:62-69`) likewise only routes by method name. By contrast, the `vault` handler performs its own internal authorization (`h.requestProcessor.ProcessRequest`, backed by `AllowListBasedAuth`/JWT auth) and only registers the in-flight request under an owner-scoped key after authorization succeeds (`vault/handler.go:394-441`). The `confidentialrelay` handler has no equivalent step, so the map-key collision check operates purely on attacker-controlled input with no ownership binding.

## Impact Explanation
An attacker with no credentials can submit a decoy JSON-RPC request to the gateway's public ingress for `MethodSecretsGet` or `MethodCapabilityExec` using a request ID they predict or observe (e.g., deterministic/retried workflow execution IDs, as implied by the handler's own comment: "the request id changes per enclave retry; the execution identity does not"). This causes the legitimate caller's identical-ID request to be rejected with `"request ID already exists"`, denying that specific workflow execution's confidential-relay action. This is a low-cost, repeatable, unauthenticated denial-of-service against a targeted request, matching the "user-chosen unique ID, first writer wins" griefing pattern.

## Likelihood Explanation
Exploitability requires only: (1) network reachability to the gateway's public JSON-RPC endpoint for this handler's methods (confirmed unauthenticated at the code layers reviewed — `httpserver.go`, `gateway.go`, `multihandler.go`), and (2) knowledge or prediction of a target `req.ID` value. No operator, admin, or host access is required, and the attack is directly demonstrated by the existing `TestConfidentialRelayHandler_DuplicateRequestID` test, which shows any second caller — regardless of identity — is rejected once an ID is claimed.

## Recommendation
1. Bind in-flight request tracking to an authenticated identity, as the `vault` handler does via `owner + RequestIDSeparator + requestID`, instead of the bare client-supplied `req.ID`.
2. Add an authorization step to `HandleJSONRPCUserMessage` in `confidentialrelay/handler.go` before `newActiveRequest`, consistent with the vault handler's `requestProcessor.ProcessRequest` pattern.
3. Alternatively, derive the in-flight tracking key server-side (e.g., a hash combining authenticated sender identity and client-supplied ID) rather than trusting the raw string as a global uniqueness key.

## Proof of Concept
1. Call `h.HandleJSONRPCUserMessage(ctx, req, cb1)` with `req.ID = "target-id"` and method `MethodCapabilityExec` (attacker request, no auth required).
2. The legitimate caller then calls `h.HandleJSONRPCUserMessage(ctx, req, cb2)` with the same `ID = "target-id"`.
3. The second call returns `errors.New("request ID already exists: " + req.ID)`, denying the legitimate request — as directly demonstrated in `TestConfidentialRelayHandler_DuplicateRequestID` (`handler_test.go:863-881`), which exercises exactly this sequence with two independent callbacks and asserts the `"request ID already exists"` error.

### Citations

**File:** core/services/gateway/gateway.go (L267-276)
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
