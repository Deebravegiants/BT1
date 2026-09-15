Audit Report

## Title
Unauthenticated MessageID collision in the gateway's WebAPI capability handler overwrites another user's pending callback, causing cross-user response confusion / request-hijack denial of service - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`HandleLegacyUserMessage` stores each in-flight legacy `web_api_trigger` request's callback in `h.savedCallbacks` keyed solely by the client-supplied `msg.Body.MessageID` (which is simply the JSON-RPC `id` field set by the calling client), and unconditionally overwrites any existing entry with the same key rather than checking for an existing in-flight request first. When a DON node later responds with that `MessageID`, `handleWebAPITriggerMessage` looks it up once and routes the response to whichever callback currently occupies that slot, so a colliding second request silently steals the first caller's pending response and leaves the first caller hanging.

## Finding Description
The gateway's `ProcessRequest` in `core/services/gateway/gateway.go` decodes the incoming JSON-RPC request and, for legacy requests, uses `jsonRequest.ID` (attacker-supplied, only bounded to ≤200 chars) directly as `msg.Body.MessageID` via `ValidatedRequestFromMessage`/`ValidatedMessageFromReq`. [1](#0-0) [2](#0-1) 

`HandleLegacyUserMessage` then writes to the shared map without any existence check: [3](#0-2) 

Later, `handleWebAPITriggerMessage` matches an incoming node response back to a caller purely by `MessageID`, deletes the entry, and delivers the response to whatever callback is stored there: [4](#0-3) 

This is a genuine analog of the "insert-without-existence-check" bug pattern: the codebase's own `vault/handler.go` handles the same "unprivileged caller supplies a request ID" scenario correctly, rejecting a request whose ID already has an active entry: [5](#0-4) 

`capabilities/handler.go` has no equivalent guard, confirming its absence there is a real gap rather than intentional design.

## Impact Explanation
If two `web_api_trigger` requests reach the same handler with the same `MessageID` while the first is still in flight, the second silently overwrites the first's `savedCallback`. The first caller's HTTP request then never receives a response (hangs until the outer gateway timeout in `ProcessRequest`'s `callback.Wait(ctx)`), and the second caller instead receives the DON's response intended for the first caller's triggered execution — cross-user response corruption combined with a denial of service against the original caller's specific request. This is a real bug, reachable by any unprivileged client since `MessageID` is fully attacker-controlled and there is no per-caller/session namespacing of the key.

## Likelihood Explanation
Trivial self-collision is always possible and reproducible: any single unprivileged client can reuse the same `MessageID`/JSON-RPC `id` for two overlapping requests to demonstrate the overwrite and the resulting stuck first request. Cross-client collision additionally requires the attacker to know or guess a victim's in-flight `MessageID`; whether official SDKs generate sufficiently unpredictable IDs is not verifiable from this code alone, but the missing existence check is present regardless and produces a concrete, reproducible defect (request corruption/loss) independent of that uncertainty.

## Recommendation
Add an existence check in `HandleLegacyUserMessage` before writing to `h.savedCallbacks`, mirroring `vault/handler.go`'s `newActiveRequest` pattern — reject (or otherwise safely handle) the request when `msg.Body.MessageID` is already present, and hold the lock across the check-and-insert to avoid a TOCTOU race.

## Proof of Concept
1. Send a `web_api_trigger` JSON-RPC request to the gateway with `id = "X"`; the gateway calls `HandleLegacyUserMessage`, which stores the callback at `savedCallbacks["X"]` and forwards to DON members. [6](#0-5) 
2. Before any node responds, send a second `web_api_trigger` request reusing `id = "X"` (same or different client) — the second `HandleLegacyUserMessage` call silently overwrites `savedCallbacks["X"]`.
3. A DON node responds with `MessageID = "X"` for the first request; `handleWebAPITriggerMessage` looks up the (now second) callback, deletes the entry, and delivers the node's response to the second caller instead of the first. [7](#0-6) 
4. This can be encoded as a Go unit test extending `TestHandlerReceiveHTTPMessageFromClient` in `handler_test.go` that calls `handler.HandleLegacyUserMessage` twice with the same `MessageID` and two distinct callbacks, then asserts the first callback never resolves while the second incorrectly receives the DON's response. [8](#0-7)

### Citations

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

**File:** core/services/gateway/handlers/common/message_util.go (L34-58)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-162)
```go
func (h *handler) handleWebAPITriggerMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.mu.Lock()
	savedCb, found := h.savedCallbacks[msg.Body.MessageID]
	delete(h.savedCallbacks, msg.Body.MessageID)
	h.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		// TODO: in practice, we should wait for at least 2F+1 nodes to respond and then return an aggregated response
		// back to the user.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-419)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L236-264)
```go
func TestHandlerReceiveHTTPMessageFromClient(t *testing.T) {
	handler, _, don, nodes := setupHandler(t)
	ctx := t.Context()
	msg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "", "")
	codec := api.JSONRPCCodec{}

	t.Run("happy case", func(t *testing.T) {
		// sends to 2 dons
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()

		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, msg, cb)
		require.NoError(t, err)

		resp, err := hc.ValidatedResponseFromMessage(msg)
		require.NoError(t, err)
		err = handler.HandleNodeMessage(ctx, resp, nodes[0].Address)
		require.NoError(t, err)

		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError}, r)
```
