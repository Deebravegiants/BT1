### Title
Global JSON-RPC request-ID collision in gateway user-message handlers enables cross-user request-ID front-running / denial of service - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`, `core/services/gateway/handlers/vault/handler.go`)

### Summary
Several of the internet-facing gateway handlers key their in-flight-request bookkeeping (`activeRequests` / `callbacks` maps) purely on the client-supplied JSON-RPC `req.ID`, with no per-sender or per-owner namespacing at registration time. An unprivileged client can pick or predict another user's request ID and race them, occupying the slot first so the legitimate request is rejected outright — the same "observe and front-run a matching slot to deny another user" pattern described in the `Trader` finding, transplanted to the gateway's request dispatch layer.

### Finding Description
The `confidentialrelay` gateway handler registers every incoming user JSON-RPC request in a process-wide map keyed only by `req.ID`: [1](#0-0) 

If an entry already exists for that ID, the second caller's request is rejected with `"request ID already exists: " + req.ID` instead of being processed. The same pattern exists in the Vault gateway handler: [2](#0-1) 

and in the HTTP-trigger handler, which stores in-flight callbacks in a map also keyed by the raw `requestID` taken from the incoming request: [3](#0-2) 

The `req.ID` is fully client-controlled (it comes straight from the JSON-RPC envelope decoded in `gateway.ProcessRequest`, with only a length check applied — no uniqueness/ownership binding): [4](#0-3) 

Because the map is global across all senders (not scoped by sender/owner/org), any unprivileged client can submit a request whose ID collides with an ID a victim is expected to use (many clients use simple, predictable IDs like `"1"`, sequential counters, or workflow-derived identifiers visible from other UI/logging channels). Whoever's request reaches the handler first "claims" the slot; the other request is bounced with a hard error and never processed. This mirrors the `Trader` griefing pattern: an attacker "front-runs" a resource that is supposed to be exclusively consumed by one party, denying the intended party service, at essentially no cost to the attacker (a single JSON-RPC call).

It's worth noting that on the node-side handler (`core/capabilities/vault/gw_handler.go`), the request ID is re-prefixed with the authorized owner *after* authorization (`authorizedOwner + RequestIDSeparator + originalRequestID`), which would prevent cross-owner collisions at that later stage: [5](#0-4) 

However, the gateway-side `activeRequests`/`callbacks` maps shown above register the request keyed by the **raw, pre-authorization** `req.ID` before any such per-owner namespacing occurs, so the collision window exists at the gateway ingress layer regardless of what happens downstream.

### Impact Explanation
An unprivileged actor can deny another unprivileged actor's gateway request (Vault secrets operations, confidential-relay capability execution, or HTTP-trigger workflow execution) from being registered/processed by racing them with the same JSON-RPC request ID. This is a denial-of-service/griefing vector on user-facing gateway operations — the victim's legitimate request fails immediately with an "already exists" error rather than being handled, and must be retried with a different ID (if the client even surfaces this to the end user). Depending on the caller (e.g., a time-sensitive vault secret read/write or workflow trigger), this could cause missed or delayed actions similar in spirit to the original `Trader` griefing (denying a user's action by claiming the shared slot first).

### Likelihood Explanation
Exploitability depends on request-ID predictability and the attack window: the attacker must guess or observe the ID before or as the victim's request is submitted, and must reach the handler first. Many client implementations use simple/sequential/deterministic IDs (as seen throughout the test suite, e.g. IDs like `"1"`, `"req-1"`, `"test-request-id-rate-limit"`), making some collisions plausible without insider knowledge. This is a moderate-likelihood griefing vector rather than a full compromise, and its severity is bounded by how predictable production client IDs actually are — this could not be fully confirmed from the indexed code since client-side ID-generation logic is outside the reviewed files.

### Recommendation
Scope the in-flight request map key by both the sender identity (authenticated org/owner/session, not solely the client-supplied `req.ID`) and the request ID, e.g. `key = senderID + ":" + req.ID`, before performing the "already exists" check in `newActiveRequest` (confidentialrelay and vault gateway handlers) and in the HTTP-trigger handler's `callbacks` map. This ensures ID collisions are only possible within a single authenticated sender's own request stream, eliminating the cross-user front-running/denial vector.

### Proof of Concept
1. Attacker (unprivileged) observes or predicts that a victim's client will submit a JSON-RPC request to the gateway with `id = "victim-req-1"` for `vault.secrets.create` (or any handler using the pattern above).
2. Attacker submits their own request with the identical `id = "victim-req-1"` slightly before the victim's request arrives.
3. `newActiveRequest` in `core/services/gateway/handlers/vault/handler.go` (or `confidentialrelay/handler.go`) succeeds for the attacker's request and populates `h.activeRequests["victim-req-1"]`.
4. When the victim's real request with the same ID arrives, `newActiveRequest` finds `h.activeRequests[req.ID] != nil` and returns `"request ID already exists: victim-req-1"`, so the victim's request is rejected outright instead of being processed — reproducing the griefing/denial pattern described in the source finding.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L185-195)
```go
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback, time.Now())
		require.NoError(t, err)

		handler.callbacksMu.Lock()
		saved, exists := handler.callbacks[requestID]
		handler.callbacksMu.Unlock()

		require.True(t, exists)
		require.Equal(t, callback, saved.Callback)
		require.NotNil(t, saved.responseAggregators)
	})
```

**File:** core/services/gateway/gateway.go (L221-234)
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-281)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID
```
