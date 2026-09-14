This confirms the finding. `gateway.ProcessRequest` in `core/services/gateway/gateway.go` accepts a raw JSON-RPC request from any unauthenticated HTTP client, decodes it, and for legacy DON-ID requests calls `h.HandleLegacyUserMessage(ctx, msg, callback)` where `msg.Body.MessageID` is fully attacker-controlled (it comes straight from `jsonRequest.ID` via `ValidatedMessageFromReq`, only bounded to 200 chars). The capabilities `handler.HandleLegacyUserMessage` then stores the callback keyed **only** by that attacker-chosen string: [1](#0-0) 

with no binding to sender/requester identity, unlike the properly-scoped `RequestCache` used elsewhere in the same package tree, which keys pending requests by `globalID{sender, id}`: [2](#0-1) 

When a DON node later responds, `handleWebAPITriggerMessage` looks the callback back up purely by `msg.Body.MessageID` and delivers the response to whichever caller currently owns that slot in the map: [3](#0-2) 

The same unscoped-map pattern also exists in `dummyHandler.HandleLegacyUserMessage`/`HandleNodeMessage`: [4](#0-3) 

### Title
Unprivileged client can hijack another user's gateway trigger response via MessageID collision in `savedCallbacks` map - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The legacy web-API-trigger gateway path stores each pending user request's response callback in a single process-wide map keyed only by the client-supplied `MessageID`, with no binding to the caller's identity/session. Any unauthenticated HTTP client hitting the public gateway can choose an arbitrary `MessageID` (JSON-RPC `id`), so this is directly analogous to the reported bug class: a shared piece of state that identifies "who receives the response/funds/callback" can be overwritten by an unrelated, unprivileged actor, leading to cross-user response confusion.

### Finding Description
`gateway.ProcessRequest` accepts unauthenticated requests and, for legacy requests, forwards `msg` (built from the client-controlled JSON-RPC `id`) straight into `handler.HandleLegacyUserMessage`: [5](#0-4) 
`ValidatedRequestFromMessage`/`ValidatedMessageFromReq` copy the request `id` directly into `msg.Body.MessageID` without any per-sender namespacing: [6](#0-5) 
`HandleLegacyUserMessage` then inserts the callback into `h.savedCallbacks` keyed solely by this attacker-chosen `MessageID`: [1](#0-0) 
If a second, unrelated request arrives (from any other unauthenticated client) using the same `MessageID` while the first is still pending, the map entry silently overwrites the first entry — no uniqueness/ownership check is performed here, unlike the newer `httpTriggerHandler.setupCallback`, which explicitly rejects a duplicate/in-flight request ID (`jsonrpc.ErrConflict`): [7](#0-6) 
or `RequestCache.NewRequest`, which scopes the key by `{sender, id}` and rejects duplicates: [8](#0-7) 
When a DON node eventually responds with that `MessageID`, `handleWebAPITriggerMessage` looks up and deletes whatever callback is currently registered under that key and delivers the DON's response to it — which may now belong to the second (attacker) request, not the original requester: [3](#0-2) 

### Impact Explanation
An unprivileged, unauthenticated client can cause the gateway to deliver a legitimate user's trigger response (which may contain workflow trigger data) to the attacker's own HTTP connection instead of the intended requester, and/or cause the legitimate requester to hang/timeout because their callback slot was silently overwritten. This is a cross-user response confusion / hijack analogous to the "reset the receiver" bug class, though the impact here is data/response redirection and denial-of-service rather than direct fund loss. The severity is bounded by the difficulty of winning the timing race and by whatever data the trigger response actually contains.

### Likelihood Explanation
Exploitability requires the attacker to guess or observe another pending request's `MessageID` and race a colliding request into the window before the original DON response arrives. `MessageID` is not visible to third parties in the base protocol, so blind guessing is impractical, but it becomes practical whenever `MessageID`s are predictable/sequential/reused by legitimate client tooling, or when an attacker can also observe or influence another client's chosen ID (e.g., shared front-end, replay, logging). This is explicitly called out as unresolved in the code's own test suite (`// TODO: Validate Senders and rate limit check ...`): [9](#0-8) 

### Recommendation
Scope `savedCallbacks` (and the equivalent map in `handler.dummy.go`) by a composite key that includes the authenticated/verified sender identity in addition to `MessageID`, mirroring the pattern already used in `RequestCache` (`globalID{sender, id}`) and in `httpTriggerHandler.setupCallback` (explicit duplicate/in-flight rejection). Reject new registrations when the same key is already in-flight instead of silently overwriting, and validate/bind `MessageID` to the connection or authenticated caller before storing the callback.

### Proof of Concept
1. Client A sends a legacy `web-api-trigger` request to the public gateway HTTP endpoint with JSON-RPC `id = "X"`, which is stored in `h.savedCallbacks["X"]` bound to A's HTTP connection/callback.
2. Before any DON node responds, Client B (unauthenticated, unprivileged) sends its own legacy request to the same gateway/DON with the same `id = "X"`. This overwrites `h.savedCallbacks["X"]` with B's callback (`core/services/gateway/handlers/capabilities/handler.go:411-414`), with no conflict/ownership check.
3. A DON node responds to A's original request with `MessageID = "X"`. `handleWebAPITriggerMessage` looks up `h.savedCallbacks["X"]`, finds B's callback, deletes the entry, and delivers A's response to B (`core/services/gateway/handlers/capabilities/handler.go:148-162`).
4. Client A's HTTP request either hangs until the gateway-level timeout or (if B's own response also races back) never gets a matching callback at all.

### Citations

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

**File:** core/services/gateway/handlers/common/requestcache.go (L34-47)
```go
type globalID struct {
	sender string
	id     string
}

type pendingRequest[T any] struct {
	handlers.Callback
	responseData *T
	timeoutTimer *time.Timer
	mu           sync.Mutex
}

func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L50-63)
```go
func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
```

**File:** core/services/gateway/handlers/handler.dummy.go (L62-109)
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

func (d *dummyHandler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	var msg api.Message
	err := json.Unmarshal(*resp.Result, &msg)
	if err != nil {
		return err
	}
	msg.Body.MessageID = resp.ID
	err = msg.Validate()
	if err != nil {
		return err
	}
	if nodeAddr != msg.Body.Sender {
		return fmt.Errorf("node address %s does not match message sender %s", nodeAddr, msg.Body.Sender)
	}
	d.mu.Lock()
	savedCb, found := d.savedCallbacks[msg.Body.MessageID]
	delete(d.savedCallbacks, msg.Body.MessageID)
	d.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(&msg), ErrorCode: api.NoError})
	}
	return nil
}
```

**File:** core/services/gateway/gateway.go (L253-279)
```go
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
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```
