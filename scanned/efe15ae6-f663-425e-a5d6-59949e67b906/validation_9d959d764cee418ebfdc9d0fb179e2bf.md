Confirmed: `msg.Body.MessageID` is the JSON-RPC request ID (`jsonRequest.ID`) supplied by whoever calls `gateway.ProcessRequest`, and gets copied verbatim into `msg.Body.MessageID` in `handlers.dummy.go`/`handler.go` flows and used as the sole key of the `savedCallbacks` map, with no uniqueness check before insertion.

### Title
Client-controlled MessageID collision causes cross-request response hijacking in WebAPI Gateway handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handler.HandleLegacyUserMessage` stores each in-flight caller's response callback in `h.savedCallbacks` keyed only by the externally-supplied `msg.Body.MessageID`/`jsonRequest.ID`, without checking whether that key is already in use. `handler.handleWebAPITriggerMessage` later looks up and deletes exactly one entry by that same ID when a DON node responds, and returns whatever entry happens to be present under that ID to the caller. Because two different unprivileged HTTP callers can independently choose the same MessageID, one caller's saved callback silently overwrites (frees) the other's in the map, and the eventually-arriving node response is delivered to the wrong client. This is the same underlying bug class as CVE-2017-6074 (double free from insufficiently-checked object lifetime/state): a single storage slot is torn down and reused for two live "objects" (in this case in-flight request contexts) tracked only by an attacker-influenced identifier, and the resulting object confusion is externally exploitable, here as cross-user response delivery rather than kernel memory corruption.

### Finding Description
The relevant code path:
- `core/services/gateway/gateway.go` `ProcessRequest` decodes the untrusted JSON-RPC request and, for legacy requests, calls `h.HandleLegacyUserMessage(ctx, msg, callback)` where `msg.Body.MessageID = req.ID` is taken directly from client input (bounded only by the length check `len(jsonRequest.ID) > 200`). [1](#0-0) 
- `handler.HandleLegacyUserMessage` unconditionally overwrites any existing entry:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [2](#0-1) 
- `handleWebAPITriggerMessage`, invoked when a node responds, looks the entry up by the same MessageID, deletes it, and delivers the response to whoever is currently stored there:
```go
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()

if found {
    ...
    return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
}
``` [3](#0-2) 

Contrast this with the vault gateway handler's `newActiveRequest`, which explicitly rejects a duplicate ID instead of silently overwriting:
```go
if h.activeRequests[req.ID] != nil {
    h.lggr.Errorw("request id already exists", "requestID", req.ID)
    return nil, errors.New("request ID already exists: " + req.ID)
}
``` [4](#0-3) 

The `core/services/gateway/handlers/handler.dummy.go` reference handler has the identical unguarded-overwrite pattern. [5](#0-4) 

Because two concurrent, unrelated, unprivileged HTTP callers to the gateway's `/` JSON-RPC endpoint can each choose the same `ID` in their JSON-RPC request, caller A's `savedCallback` can be silently displaced by caller B's if B sends its request while A's is still pending (before A's response arrives from any DON node). When the DON node eventually responds with the message ID that A originally sent, `handleWebAPITriggerMessage` delivers that response to B's stored callback instead of A's — B receives a webhook/trigger response addressed to a request it never made, and A's request appears to time out having never received its real response. This is a cross-user response confusion vulnerability rooted in unchecked identifier reuse of a client-supplied key controlling shared state lifetime, analogous to the double-free root cause (state associated with one live handle gets torn down/reassigned to a second handle due to missing state/identity validation).

### Impact Explanation
An unprivileged remote caller of the gateway HTTP endpoint can deliberately collide MessageIDs with another in-flight, unrelated request to receive that other requester's DON response payload (which may contain another workflow/user's trigger data), and/or cause the victim's original request to silently lose its response. This is a concrete cross-user response confusion vulnerability satisfying the "Accept" criteria (cross-user response confusion via request impersonation of the response channel), reachable purely from client input over the internet-facing gateway with no privileged access required.

### Likelihood Explanation
Exploitation requires only sending an HTTP JSON-RPC request to the gateway with a `MessageID`/`ID` equal to one currently in flight from another user, and winning a race so the collision write happens before the original request's node response arrives. Message IDs are frequently predictable or attacker-choosable (e.g., sequential counters, short IDs, or values an attacker controls entirely), and the gateway enforces no per-request uniqueness or namespacing (e.g., by sender/session), so the race is straightforward for an attacker who can send many concurrent requests, though it does require some timing luck against a specific concurrent victim request. Likelihood is moderate.

### Recommendation
- Reject `HandleLegacyUserMessage`/`HandleJSONRPCUserMessage` requests whose `MessageID` collides with an existing entry in `savedCallbacks`, mirroring the vault handler's `newActiveRequest` duplicate-ID rejection, rather than silently overwriting.
- Alternatively, scope the `savedCallbacks` map key by a server-generated internal correlation ID (or by sender/session plus client ID) instead of trusting the raw client-supplied MessageID as the sole map key.
- Apply the same fix to the `dummyHandler.HandleLegacyUserMessage` code path, which has the identical unguarded overwrite.

### Proof of Concept
1. Attacker sends JSON-RPC request `R1` to the gateway's legacy WebAPI trigger endpoint with `id = "X"`, targeting DON `D`; this stores `savedCallbacks["X"] = callback_attacker` after briefly having stored the victim's callback.
2. Concurrently, victim sends their own legitimate JSON-RPC request `R2` also with `id = "X"` (predictable/collidable ID scheme, or attacker races many IDs) targeting the same DON; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with `callback_victim`, clobbering the attacker's stored callback — or vice versa depending on race order.
3. Whichever caller's DON node response for message ID `"X"` arrives first at `handleWebAPITriggerMessage` gets delivered to whatever callback currently occupies `savedCallbacks["X"]`, which may belong to the other caller, resulting in cross-delivery of one user's trigger/webhook response payload to the other's HTTP connection.
4. This can be validated in the existing test harness by calling `handler.HandleLegacyUserMessage` twice with the same `MessageID` from two different `Callback` objects and observing that only one callback remains registered, then calling `handler.HandleNodeMessage`/`handleWebAPITriggerMessage` once and confirming the response is delivered to the "wrong" `Callback` object of the two, as demonstrated in the handler_test.go test structure (`core/services/gateway/handlers/capabilities/handler_test.go`). [6](#0-5)

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
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

**File:** core/services/gateway/handlers/handler.dummy.go (L62-82)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
	params, err := json.Marshal(msg)
	if err != nil {
		return err
	}
	rawParams := json.RawMessage(params)
	req := &jsonrpc.Request[json.RawMessage]{
		Version: "2.0",
		ID:      msg.Body.MessageID,
		Method:  msg.Body.Method,
		Params:  &rawParams,
	}
	for _, member := range d.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L236-266)
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
	})

```
