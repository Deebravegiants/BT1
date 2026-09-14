## Analysis

I found a valid analog. In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` stores a caller's callback into a shared, `MessageID`-keyed map with no uniqueness check, whereas the newer v2 trigger handler (`http_trigger_handler.go`'s `setupCallback`) explicitly rejects duplicate/in-flight request IDs. The `MessageID` is caller-supplied and reaches this map straight from the JSON-RPC request `ID` field via `gateway.go`'s `ProcessRequest` → `common.ValidatedMessageFromReq` (which copies `req.ID` into `m.Body.MessageID`). This mirrors the audit report's root cause: an unprivileged party can control a value that a shared, first-come-first-served resolution path depends on, and use it to silently swallow another legitimate request's callback delivery, forcing that request to expire via timeout — a direct analog of "receiver blacklists itself to force `exercise()` to fail until expiry."

### Title
Unprivileged Gateway callers can collide legacy `MessageID`s to overwrite and silently drop another user's in-flight callback - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` in the `WebAPIHandler` capability handler stores each request's completion callback in a map keyed only by the caller-controlled `MessageID`, without checking whether an entry already exists for that key [1](#0-0) . Because the `MessageID` originates from the untrusted JSON-RPC request `ID` field supplied by any DON-facing/unprivileged gateway client [2](#0-1) [3](#0-2) , a second attacker-submitted message using the same `MessageID` as a victim's still-pending, legitimate request overwrites the victim's saved callback in the map. The victim's original HTTP request then never receives a response and is left to expire via the gateway's own request timeout, exactly as in the referenced audit finding where an actor-controlled value (blacklisted `receiver`) is leveraged to force a pending, time-bounded operation into expiry instead of succeeding.

### Finding Description
The relevant control flow:
1. `gateway.ProcessRequest` decodes an incoming JSON-RPC request and, for legacy DON messages, calls `h.HandleLegacyUserMessage(ctx, msg, callback)`, waiting on `callback.Wait(ctx)` for the result [4](#0-3) .
2. `common.ValidatedMessageFromReq` sets `m.Body.MessageID = req.ID` directly from the untrusted request, with no server-side uniqueness enforcement at decode time [2](#0-1) .
3. `HandleLegacyUserMessage` then does:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [1](#0-0) 
There is no `if _, found := h.savedCallbacks[msg.Body.MessageID]; found { ... }` guard here, unlike the newer, hardened v2 trigger handler which explicitly rejects a duplicate/in-flight `requestID` with a `Teller`-style conflict error [5](#0-4) .
4. When a node eventually responds, `handleWebAPITriggerMessage` looks up and deletes whatever callback currently occupies that `MessageID` slot and sends the response to it — always "first response wins," per its own comment [6](#0-5) .

An attacker who can submit gateway requests (an unprivileged client of this internet-facing endpoint) can therefore:
- Observe or predict a target's `MessageID`/request `ID` (these are caller-supplied and not secret — many client libraries use simple/incrementing/deterministic IDs), or race a target's request.
- Submit their own request using the identical `MessageID` while the victim's is still in flight, overwriting `h.savedCallbacks[MessageID]` so it now points to the attacker's `callback`.
- When the DON eventually answers the victim's original request, `handleWebAPITriggerMessage` looks it up by `MessageID`, finds the attacker's callback there, and delivers the victim's response to the attacker instead (cross-user response confusion) while the victim's own callback is orphaned.
- The victim's `gateway.ProcessRequest` call then blocks until `callback.Wait(ctx)` times out, receiving `RequestTimeoutError`/handler timeout regardless of whether the underlying DON call actually succeeded [7](#0-6) .

This is the direct analog of the reported bug class: an unprivileged actor manipulates a value it controls (there: `receiver`/blacklist status; here: `MessageID`) to hijack or block a shared, time-bounded resolution path for another party, forcing that party's operation to fail/expire instead of completing normally, and in this case also potentially leaking the victim's response contents to the attacker.

### Impact Explanation
- Denial of service against a specific victim request: the legitimate caller's response is swallowed, and the request is forced to time out exactly like the "OptionToken forced to expire" analog.
- Cross-user response confusion / information exposure: the victim's DON response payload is delivered to the attacker's callback instead of the victim's, potentially leaking data intended for the victim.
- No special privilege is required — any actor able to send messages to the gateway's legacy JSON-RPC endpoint for this handler can trigger this by choosing a colliding `MessageID`.

### Likelihood Explanation
Likelihood is moderate to high in scenarios where `MessageID` space is not large/random (many client integrations use simple or predictable IDs) or where an attacker can win a race against a known request pattern. No authentication bypass is needed; only reachability to the same DON handler's legacy path is required. The comment in the code itself ("Send first response from a node back to the user, ignore any other ones") confirms the collision/overwrite behavior is not just theoretical but a documented, first-write-wins design without a duplicate check — the exact same class of gap that the newer v2 handler had to explicitly patch with a duplicate-ID rejection.

### Recommendation
- In `HandleLegacyUserMessage`, before storing into `h.savedCallbacks`, check for an existing entry keyed by `msg.Body.MessageID` (optionally scoped by `msg.Body.Sender`, similar to `requestcache.go`'s `globalID{sender, id}` key [8](#0-7) ) and reject the new request (e.g., with a conflict/duplicate error) instead of silently overwriting the prior callback, mirroring the guard already implemented in `httpTriggerHandler.setupCallback` [5](#0-4) .
- Prefer keying `savedCallbacks` by `(Sender, MessageID)` rather than `MessageID` alone, so one caller cannot collide with another caller's ID space at all.

### Proof of Concept
1. Client A sends a legacy JSON-RPC request to the gateway with `id = "req-1"` for a slow-to-respond DON method; the gateway stores `savedCallbacks["req-1"] = A's callback` and forwards the request to DON nodes [9](#0-8) .
2. Before the DON responds, attacker B sends another legacy JSON-RPC request also using `id = "req-1"` (valid per `Message.Validate`, which only checks length/format, not uniqueness [10](#0-9) ); this overwrites `savedCallbacks["req-1"]` with B's callback.
3. When the DON responds for the original message ID `"req-1"`, `handleWebAPITriggerMessage` looks up `savedCallbacks["req-1"]`, finds B's callback, deletes the entry, and delivers the DON's response to B instead of A [6](#0-5) .
4. Client A's `ProcessRequest` call, still waiting on its own (now orphaned) callback, times out and receives `RequestTimeoutError` even though the underlying operation succeeded [7](#0-6) .

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-160)
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

**File:** core/services/gateway/handlers/common/message_util.go (L46-57)
```go
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
```

**File:** core/services/gateway/gateway.go (L267-288)
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

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
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

**File:** core/services/gateway/handlers/common/requestcache.go (L34-63)
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
}

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

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```
