### Title
Cross-user response hijacking via attacker-controlled `MessageID` collision in gateway WebAPI trigger callback cache - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The gateway's legacy WebAPI capability handler correlates a user's HTTP trigger request with the eventual DON node response purely by `msg.Body.MessageID` — a value fully controlled by the (unprivileged) external caller — with no binding to the caller's identity/session. Two different users can supply the same `MessageID`, and the later submission silently overwrites the earlier one's saved callback, so the response addressed to the first (victim) user gets delivered to the second (attacker) user's HTTP connection instead. This mirrors the root cause of the reported analog (a value/asset is left correlated only by a coarse identifier that the receiving side does not validate/scope to the intended party, letting an unrelated actor redirect it to themselves).

### Finding Description
- `HandleLegacyUserMessage` stores the caller's callback keyed only by the message ID taken directly from the inbound (attacker-supplied) message body: [1](#0-0) 

- When the DON node responds, `handleWebAPITriggerMessage` looks the callback up and delivers the response using that same bare `MessageID`, with no check that it belongs to the same sender who created it: [2](#0-1) 

- `msg.Body.MessageID` originates from the JSON-RPC request `ID` supplied by the external HTTP caller and is only checked for length/null-suffix, not uniqueness or ownership: [3](#0-2) [4](#0-3) 

- By contrast, the newer/general-purpose `requestCache` deliberately scopes cache entries by `globalID{sender, id}` — i.e., it *does* bind the identifier to the sender to prevent exactly this kind of collision: [5](#0-4) 

- The same unscoped-by-sender pattern is also present in the throwaway/dummy handler used elsewhere: [6](#0-5) 

Because `savedCallbacks` is a single shared `map[string]*savedCallback` per DON handler instance and the key space (message IDs) is entirely attacker-chosen, an unprivileged client can:
1. Observe or guess that another user is about to submit (or has just submitted) a trigger request with message ID `X` (message IDs are often predictable/sequential from client SDKs, or the attacker can simply race many guesses/observe network timing).
2. Submit their own trigger request using the *same* `MessageID` `X` before the victim's node response arrives.
3. Their `HandleLegacyUserMessage` call overwrites `h.savedCallbacks["X"]` with the attacker's own callback (tied to the attacker's HTTP connection).
4. When the DON node's genuine response for the victim's request arrives keyed by `"X"`, `handleWebAPITriggerMessage` delivers it to whichever callback currently occupies that map slot — the attacker's — leaking the victim's response data to the attacker and leaving the victim's request unanswered/dropped.

### Impact Explanation
This is a cross-user response confusion issue: an unprivileged external caller of the internet-facing gateway can intercept another unrelated user's DON response data by racing/colliding on a client-controlled identifier. Depending on what workflows are being triggered, the leaked data in the response payload could include sensitive computed results. It also causes denial of service for the victim (their real response is never delivered before pruning). No signature or authentication weakness needs to be defeated — the attacker only needs to control the `MessageID` field of their own otherwise-valid, properly signed request.

### Likelihood Explanation
Exploitability depends on winning a race between the victim's submission and the arrival of the DON's response for that MessageID, and on the attacker being able to predict/observe the victim's chosen MessageID (many client integrations use predictable, sequential, or fixed IDs, or the attacker may simply flood many likely IDs). This makes the likelihood moderate rather than trivial, but it requires no privileged access — any external caller of the gateway's legacy WebAPI trigger endpoint can attempt it.

### Recommendation
Scope the callback cache key by both sender and message ID (as already done in `requestcache.go`'s `globalID{sender, id}`), rather than by `MessageID` alone, in `core/services/gateway/handlers/capabilities/handler.go` (and the analogous `handler.dummy.go`). Reject/overwrite-protect duplicate `(sender, MessageID)` pairs instead of silently overwriting on bare `MessageID` collision, and verify the responding node's message correlates to the same sender/session that created the original saved callback before dispatching the response.

### Proof of Concept
1. Attacker sends `HandleLegacyUserMessage` request A with `Body.MessageID = "1234"`, signed with the attacker's key; gateway stores `savedCallbacks["1234"] = attackerCallback`.
2. Before DON nodes respond to A, victim sends a legitimate trigger request V also using `Body.MessageID = "1234"` (e.g., predictable/sequential client ID); gateway overwrites `savedCallbacks["1234"] = victimCallback`.
3. If the attacker instead sends *after* the victim (racing to overwrite last), `savedCallbacks["1234"]` becomes `attackerCallback` again.
4. A DON node responds for message ID `"1234"` (intended for the victim's request); `handleWebAPITriggerMessage` looks up `savedCallbacks["1234"]`, finds the attacker's callback, and calls `SendResponse`, delivering the victim's data to the attacker's connection while the victim never receives a response.

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

**File:** core/services/gateway/api/message.go (L42-63)
```go
type MessageBody struct {
	MessageID string `json:"message_id"`
	Method    string `json:"method"`
	DonID     string `json:"don_id"`
	Receiver  string `json:"receiver"`
	// Service-specific payload, decoded inside the Handler.
	Payload json.RawMessage `json:"payload,omitempty"`

	// Fields only used locally for convenience. Not serialized.
	Sender string `json:"-"`
}

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

**File:** core/services/gateway/handlers/common/requestcache.go (L34-57)
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
