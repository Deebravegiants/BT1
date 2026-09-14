## Analog Vulnerability Found

### Title
Griefing via unauthenticated, globally-shared user-supplied `req.ID` in confidential relay gateway handler - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The `gateway` package routes any inbound HTTP request from an unprivileged caller straight to a handler's `HandleJSONRPCUserMessage` without a generic gateway-level authentication step [1](#0-0) . The confidential relay handler's `HandleJSONRPCUserMessage` performs *no* authorization/attestation check of its own before registering the caller-supplied `req.ID` in a single, DON-wide `activeRequests` map keyed only by that string [2](#0-1) [3](#0-2) . This is structurally identical to the Folks Finance bug: a caller-chosen identifier ("loanId" there, `req.ID` here) is checked for uniqueness in a shared table with no ownership/session binding, so any party who can reach the gateway can "claim" an ID before its legitimate owner does.

### Finding Description
`newActiveRequest` only checks `h.activeRequests[req.ID] != nil` and returns `"request ID already exists"` if so [4](#0-3) . This check:
- is not scoped by caller/owner/workflow — it is a single global map shared by every requester hitting this DON's confidential-relay handler,
- runs before any authentication of the request (there is no `ProcessRequest`/attestation/authorizer call in this handler's `HandleJSONRPCUserMessage`, unlike the sibling `vault` handler which does call `h.requestProcessor.ProcessRequest` before creating the active request [5](#0-4) ).

The companion node-side handler (`core/capabilities/confidentialrelay/handler.go`) does have an attestation/authorization step, but that happens *after* the gateway has already accepted/rejected the request based on the ID collision — the griefing takes effect at the gateway layer, before any legitimacy check.

Consequently, an attacker who can reach the gateway's public HTTP endpoint can:
1. Predict or replay a `req.ID` that a legitimate confidential-relay client is expected to use (test code confirms IDs are simple client-chosen strings, e.g. `"req-1"`/`"req-dup"` [6](#0-5) ), or brute-force submit many IDs.
2. Submit a request with that ID first. `newActiveRequest` inserts it into the shared map.
3. When the legitimate caller's real request with the same ID arrives, `HandleJSONRPCUserMessage` returns `"request ID already exists"` and the legitimate request is rejected outright [7](#0-6) .

This mirrors the Folks Finance `LoanManager::createUserLoan` bug exactly: a user-controlled identifier is checked for prior existence in a shared table (`_userLoans[loanId]` there, `activeRequests[req.ID]` here) with no per-user namespace, enabling front-running/griefing of another party's operation.

### Impact Explanation
This is a griefing / availability impact only (matching the "Griefing" impact category used in the source report): an unprivileged attacker can deny legitimate confidential-relay requests from succeeding for the duration of the collided ID's TTL (`requestTimeout`, default configurable, cleaned up by `removeExpiredRequests` [8](#0-7) ). Since there is no authentication gate before the ID check, this requires no privileges or valid credentials — only the ability to reach the gateway's public endpoint and guess/replay an ID.

### Likelihood Explanation
Likelihood depends on whether `req.ID` values used by legitimate confidential-relay clients (enclave retries) are predictable or replayable by an outside caller. The test suite shows IDs are plain caller-chosen strings without any embedded secret/nonce that would prevent guessing [9](#0-8) . I could not fully confirm, within the indexed portion of the codebase, how the enclave/relay-DON client actually generates production `req.ID` values (e.g., whether they include a high-entropy random component that would make blind guessing infeasible) — this is a gap in what I could verify from the available index. If IDs are low-entropy or derivable from `workflowID`/`executionID` (which are themselves visible in request params [10](#0-9) ), likelihood is high; if they are cryptographically random and unpredictable, exploitation requires an attacker who can observe or race the ID (e.g., via network timing) rather than guess it outright.

### Recommendation
- Require gateway-level authentication/authorization (attestation or signed JWT) in `confidentialrelay` handler's `HandleJSONRPCUserMessage` *before* `newActiveRequest` touches the shared map, consistent with what the `vault` handler already does.
- Scope the `activeRequests` map key by an authenticated identity (e.g., `owner`/`workflowID`) combined with `req.ID`, rather than by the raw caller-supplied `req.ID` alone, so that collisions can only occur within a single authenticated caller's own namespace (analogous to recommending a server-side, incrementing/namespaced `loanId` instead of an arbitrary user-supplied one).
- Alternatively, generate/derive the request-cache key server-side (e.g., hash of authenticated owner + execution identity) instead of trusting the client-controlled `ID` field directly for uniqueness enforcement.

### Proof of Concept
The existing unit test already demonstrates the collision mechanics (absent any authentication) at the handler level: [6](#0-5) 
This test shows that two different, unauthenticated callers using the same `req.ID` ("req-dup") result in the second submission being rejected with `"request ID already exists"` — the second caller here stands in for the "victim" whose legitimate request is blocked once an attacker has claimed the same ID first, exactly paralleling the Folks Finance PoC where the bad actor front-runs the victim's `loanId`.

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L84-108)
```go
type requestLabels struct {
	WorkflowID  string `json:"workflow_id"`
	ExecutionID string `json:"execution_id"`
}

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-369)
```go
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		l := h.requestLogger(er.req, er.labels)
		l.Debugw("request expired, evaluating collected relay responses",
			"collected", len(responses),
			"nodes", len(h.donConfig.Members),
			"unanswered", len(h.donConfig.Members)-len(responses),
		)
		summary, err := h.bundler.Bundle(er.req, responses, l)
		if err != nil {
			l.Errorw("failed to build relay response bundle", "error", err)
			if sendErr := h.sendResponseAndClearRequest(ctx, er, h.constructErrorResponse(er.req, api.FatalError, err)); sendErr != nil {
				l.Errorw("error returning bundle failure on expiry", "error", sendErr)
			}
			continue
		}
		// Expiry makes further responses unavailable to this request. The common
		// readiness path forwards a viable partial bundle or returns a timeout.
		if err := h.forwardBundleOrTerminateIfReady(ctx, l, er, summary, 0, true); err != nil {
			l.Errorw("error forwarding bundle on expiry", "error", err)
		}
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

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L1207-1220)
```go
		ID:     "req-blocked-node",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	done := make(chan error, 1)
	start := time.Now()
	go func() {
		done <- h.HandleJSONRPCUserMessage(t.Context(), req, common.NewCallback())
	}()

	select {
	case fanOutErr := <-done:
		// Three of four nodes still received the request, so quorum remains possible and the
```
