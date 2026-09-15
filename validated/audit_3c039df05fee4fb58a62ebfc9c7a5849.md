Audit Report

## Title
Cross-user response hijacking via attacker-controlled `MessageID` collision in gateway WebAPI trigger callback cache - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The gateway's legacy WebAPI capability handler (`handler.go`) stores the callback used to deliver a DON node's response to the original HTTP caller in a single shared map, `savedCallbacks`, keyed only by `msg.Body.MessageID` [1](#0-0) . Since `MessageID` is taken directly from the caller-supplied JSON-RPC request `ID` with no sender binding [2](#0-1) , any unprivileged, otherwise-legitimate caller can choose the same `MessageID` as another user's in-flight request, overwrite that user's saved callback, and receive the victim's DON response instead when `handleWebAPITriggerMessage` looks the entry up purely by `MessageID` [3](#0-2) .

## Finding Description
- `HandleLegacyUserMessage` saves the callback for the current caller into `h.savedCallbacks[msg.Body.MessageID]`, with no check for whether that key is already occupied by a different, still-pending request, and no binding to the caller's sender identity: [1](#0-0) 
- When a DON node responds, `handleWebAPITriggerMessage` fetches and deletes `h.savedCallbacks[msg.Body.MessageID]` and unconditionally forwards the node's response to whichever callback occupies that slot, without verifying that the responding node's message corresponds to the sender who created the entry: [3](#0-2) 
- `msg.Body.MessageID` is populated straight from the external JSON-RPC request's `ID` field during validation, and `Validate()` only checks length constraints, not uniqueness or ownership: [2](#0-1) [4](#0-3) 
- The `HandleNodeMessage` entry point does validate that the responding node matches the expected sender (`msg.Body.Sender != nodeAddr`) at [5](#0-4) , but this only authenticates that the message came from *a* DON node — it does nothing to verify that the specific saved callback being resolved by `MessageID` still belongs to the same HTTP caller who created it, since the key space has no sender component.
- By contrast, the general-purpose `requestCache` in `requestcache.go` explicitly scopes cache entries by `globalID{sender, id}`, demonstrating that this exact sender-binding pattern was already recognized as necessary elsewhere in the same package but was not applied to `handler.go`'s `savedCallbacks`: [6](#0-5) 
- The identical unscoped pattern also exists in the dummy/throwaway handler: [7](#0-6) 

This satisfies a genuine broken security assumption: the correlation between an HTTP caller's request and the eventual response is supposed to be 1:1 per-caller, but the shared, attacker-controlled `MessageID` keyspace allows any caller with a live connection to hijack another caller's pending response slot by simply resubmitting with a colliding ID.

## Impact Explanation
This maps to the in-scope "cross-user response corruption" impact category. An unprivileged but validly-signed caller of the gateway's legacy WebAPI trigger endpoint can, by colliding on `MessageID`, cause the DON's response intended for another user to be delivered to themselves instead, potentially leaking sensitive computed workflow output data, and simultaneously deny the victim their response (dropped/never delivered, since it's already been consumed by the attacker's callback and deleted from the map). No signature forgery or credential compromise is required — attackers use only their own valid signing key and simply control the `MessageID` field of their own request.

## Likelihood Explanation
Exploitation requires the attacker to both learn/predict a victim's chosen `MessageID` and win a race to have their own callback occupy the map slot at the moment the DON node's response for that ID arrives. This is feasible if the client SDK generates predictable/sequential/fixed IDs, or if the attacker floods likely candidate IDs, but is not trivially deterministic without such conditions. It requires no privileged access — only the ability to submit an otherwise normal request through the gateway's legacy WebAPI trigger endpoint, which is externally callable by any registered/signing user of the workflow platform.

## Recommendation
Scope `savedCallbacks` by both sender and `MessageID` (mirroring the `globalID{sender, id}` approach already used in `core/services/gateway/handlers/common/requestcache.go`), reject overwriting an existing, still-pending `(sender, MessageID)` entry, and when resolving the response in `handleWebAPITriggerMessage`, verify the message's intended recipient/sender context matches the one that created the saved callback before dispatching. Apply the same fix to the equivalent pattern in `core/services/gateway/handlers/handler.dummy.go`.

## Proof of Concept
1. Attacker submits a validly-signed `HandleLegacyUserMessage` request with `Body.MessageID = "X"`; gateway stores `savedCallbacks["X"] = attackerCallback` (`handler.go` L411-414).
2. Victim (using a client with the same or colliding ID generation scheme) submits a legitimate, validly-signed trigger request also using `Body.MessageID = "X"`; gateway overwrites `savedCallbacks["X"] = victimCallback`.
3. Before the DON responds, attacker resubmits with `MessageID = "X"` again, re-overwriting `savedCallbacks["X"] = attackerCallback`.
4. The DON node's response for `MessageID = "X"` (intended for the victim's request) arrives; `handleWebAPITriggerMessage` (`handler.go` L148-162) looks up `savedCallbacks["X"]`, finds the attacker's callback, and calls `SendResponse`, delivering the victim's response data to the attacker's HTTP connection while the victim receives nothing.
5. A Go unit test can directly instantiate `handler` (as in `handler_test.go`), call `HandleLegacyUserMessage` twice with the same `msg.Body.MessageID` but different `callback` mocks, then invoke `HandleNodeMessage`/`handleWebAPITriggerMessage` and assert that the second (overwriting) callback's `SendResponse` is invoked instead of the first's.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-255)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
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

**File:** core/services/gateway/api/message.go (L53-63)
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
```

**File:** core/services/gateway/handlers/common/requestcache.go (L34-76)
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
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
	codec := api.JSONRPCCodec{}
	timer := time.AfterFunc(c.timeout, func() {
		err := c.deleteAndSendOnce(key, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(request), ErrorCode: api.RequestTimeoutError})
		if err != nil {
			lggr.Errorw("failed to send timeout response", "error", err)
		}
	})
	c.cache[key] = &pendingRequest[T]{Callback: callback, responseData: responseData, timeoutTimer: timer}
	return nil
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
