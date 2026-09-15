This confirms `ProcessRequest` in `core/services/gateway/gateway.go` is the internet-facing HTTP entrypoint that dispatches to `h.HandleLegacyUserMessage(ctx, msg, callback)` for legacy requests identified purely by `msg.Body.DonID != ""` — reachable by any unauthenticated external client hitting the gateway's user-facing HTTP server. [1](#0-0)  The dispatch only calls `msg.Validate()`, which enforces signature format and field-length rules but never checks for `MessageID` uniqueness across senders. [2](#0-1) 

The claim is well-supported by the code:

- `HandleLegacyUserMessage` unconditionally overwrites `h.savedCallbacks[msg.Body.MessageID]` with no existence check. [3](#0-2) 
- `handleWebAPITriggerMessage` looks up and delivers the response purely by `MessageID`, with no check tying it back to the original sender/requester. [4](#0-3) 
- `HandleNodeMessage` only verifies that `msg.Body.Sender == nodeAddr` (i.e., that the DON node isn't spoofed) — it never validates that the response's `MessageID` still corresponds to the original requesting client. [5](#0-4) 
- The sibling `RequestCache.NewRequest` in the same package explicitly keys by `globalID{sender, messageID}` and rejects duplicates, proving this defense is the established, intentional pattern elsewhere in the codebase and its absence in `handler.go` is a genuine gap, not a deliberate design choice. [6](#0-5) 
- The identical unguarded pattern also exists in `handler.dummy.go`'s `HandleLegacyUserMessage`, corroborating that this is a structural gap in the legacy handling path rather than an isolated typo. [7](#0-6) 

I found one related but distinct note: a test file comment flags that sender validation/rate-limiting in this trigger path is still a known open question, which is adjacent context but not a fix or acknowledgment of the specific `MessageID` collision issue. [8](#0-7)  This does not constitute a prior disclosure/fix of the exact vulnerability described.

The root-cause analysis, exploit path, and impact are all verified against the actual code and are internally consistent. This maps to the in-scope "gateway request impersonation / cross-user response corruption" impact category and is triggerable by an unauthenticated external client without any special role, since `ProcessRequest` requires no authentication for legacy DON-ID-based requests beyond message-signature format validation.

Audit Report

## Title
Unauthenticated MessageID collision in Gateway Web API handler causes cross-user response hijacking - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` stores the caller's response callback in a shared map keyed solely by `msg.Body.MessageID`, a value fully controlled by the requesting client. The write is unconditional — it silently overwrites any existing entry for the same ID instead of rejecting duplicates. An unprivileged client can therefore pick a `MessageID` that collides with another in-flight request and hijack the eventual node response meant for that other caller.

## Finding Description
In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` stores `callback` in `h.savedCallbacks` keyed by `msg.Body.MessageID` with no check for an existing entry (lines 411-414). `MessageID` is part of the client-signed `api.MessageBody`, chosen by the requester and only constrained by length/character rules in `Message.Validate()` (message.go, lines 54-66) — there is no requirement that it be unique to the caller, unpredictable, or bound to the caller's identity/sender key. This handler is reachable directly from the internet-facing gateway HTTP server via `gateway.go`'s `ProcessRequest`, which dispatches legacy DON-ID-keyed requests to `h.HandleLegacyUserMessage` with no additional authentication beyond signature-format validation (gateway.go, lines 253-272).

When a DON node later responds, `HandleNodeMessage` verifies only that the responding node address matches the message's sender field (i.e., that the *node* isn't spoofed), not that the response's `MessageID` still belongs to the caller who originally submitted it (handler.go, lines 248-255). The response is then dispatched purely by `MessageID` lookup and delivered to whichever callback is currently stored for that ID (handler.go, lines 148-161).

Contrast this with the sibling `RequestCache.NewRequest` in the same handlers package, which explicitly guards against this exact class of bug by keying on `globalID{sender, messageID}` and rejecting duplicates (requestcache.go, lines 34-63), and `http_trigger_handler.go`'s `setupCallback`, which also rejects duplicate in-flight IDs. The legacy `handler.go` path lacks this protection, confirming it is the outlier rather than an intentional design choice.

## Impact Explanation
If User B submits a request with the same `MessageID` as User A's still-pending request, User B's callback silently replaces User A's in `savedCallbacks`. When the DON node eventually responds to that `MessageID`, `handleWebAPITriggerMessage` delivers the response to whichever callback is currently stored — now User B's — sending User A's trigger response data to User B. This is a cross-user response confusion/information-disclosure bug reachable purely from unprivileged, external client input over the internet-facing gateway. User A additionally receives no response and eventually times out, a secondary availability impact. This maps to the in-scope "gateway request impersonation / cross-user response corruption" impact category.

## Likelihood Explanation
Exploitability depends only on message-ID reuse across concurrent requests — `MessageID` values are entirely client-chosen and unauthenticated beyond signature-format checks, so any external caller of the gateway's legacy Web API trigger endpoint can trigger the collision by simply reusing/guessing another party's ID during its in-flight window (bounded by `defaultCallbackMaxAgeSec` = 120s). No special privilege beyond being a normal, unauthenticated caller is required, and the bug is a straightforward missing existence-check compared to two other handlers in the same package that already implement the fix.

## Recommendation
In `HandleLegacyUserMessage`, before storing a new callback, check whether `h.savedCallbacks[msg.Body.MessageID]` already exists and reject the new request (mirroring the pattern used in `requestcache.go`'s `NewRequest` and `http_trigger_handler.go`'s `setupCallback`). Additionally, bind the callback key to `(Sender, MessageID)` rather than `MessageID` alone, so that even accidental cross-client ID collisions cannot cause response misdelivery.

## Proof of Concept
1. User A signs and sends a legacy Web API trigger message with `MessageID = "X"` to the gateway's user-facing HTTP port; the gateway forwards it to DON nodes and stores `savedCallbacks["X"] = callbackA`.
2. Before the node responds, User B signs and sends a message reusing `MessageID = "X"`; `HandleLegacyUserMessage` overwrites the map entry: `savedCallbacks["X"] = callbackB` (handler.go:411-414, no existence check).
3. A DON node responds for `MessageID = "X"` (bound to User A's original request). `HandleNodeMessage` validates only `msg.Body.Sender == nodeAddr` (handler.go:253-255), then `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, and sends User A's node response back to User B (handler.go:148-161).
4. User B receives data intended for User A; User A's request times out with no response delivered.

Test plan: add a Go unit test in `core/services/gateway/handlers/capabilities/handler_test.go` that (a) calls `HandleLegacyUserMessage` for user A with `MessageID = "X"`, (b) calls `HandleLegacyUserMessage` for user B with the same `MessageID = "X"` before the node responds, (c) simulates a node response via `HandleNodeMessage` for `MessageID = "X"`, and (d) asserts that user B's callback (not user A's) receives the response while user A's callback times out.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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
```

**File:** core/services/gateway/api/message.go (L54-66)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-161)
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

**File:** core/services/gateway/handlers/handler.dummy.go (L62-66)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
