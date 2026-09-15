### Title
Cross-user response confusion via sender-unscoped `savedCallbacks` map keyed only by client-supplied `MessageID` - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The OliveTin advisory describes a broadcast/subscription path that fails to bind delivered data to the authorized recipient — any authenticated subscriber can receive output belonging to another user's action. The closest reachable analog in chainlink is the gateway's legacy WebAPI trigger handler, `handler.HandleLegacyUserMessage`, which caches a per-request callback keyed *solely* by the client-controlled `MessageID`, with no binding to the sender/requester identity. Because delivery of a node's response back to the caller is resolved purely by this map lookup, one caller's chosen `MessageID` can collide with (and clobber/redirect) another caller's in-flight request/response mapping.

### Finding Description
`HandleLegacyUserMessage` stores the caller's callback keyed only by `msg.Body.MessageID`, a value fully controlled by the requester's signed message body: [1](#0-0) 

There is no per-sender namespacing of this key — contrast this with `MessageBody.MessageId` in the peer-to-peer capability protocol, which is explicitly documented as "scoped to sender": [2](#0-1) 
and with the gateway's `common.RequestCache`, which deliberately keys pending requests by `globalID{sender, id}` to prevent exactly this kind of collision: [3](#0-2) 

The legacy WebAPI-trigger handler's `savedCallbacks` map does not follow this same-sender-scoping pattern: [4](#0-3) 

When a node later responds, delivery is resolved purely by map lookup on `msg.Body.MessageID`, deleting and returning whatever callback is currently stored under that key: [5](#0-4) 

If two different low-privileged, authenticated callers happen to choose (or a malicious caller deliberately chooses) the same `MessageID` while a first request is still pending, the second caller's `SendResponse` callback overwrites the first caller's entry in `savedCallbacks`. When the DON node subsequently returns the response correlated to the *original* `MessageID`, the handler looks the callback up only by that ID and delivers it to whichever callback is currently registered — potentially the second (unrelated) caller. This is a cross-user response-confusion primitive of the same class flagged in the OliveTin report (data delivered to the wrong, unauthorized recipient) because there is no check that the responding message's originating requester matches the callback owner.

The test suite's own inline TODO acknowledges this gap explicitly: [6](#0-5) 

### Impact Explanation
If exploitable, this allows a low-privileged authenticated (or even loosely-authenticated, since this legacy path predates the newer per-workflow JWT/allowlist auth layer used elsewhere in the gateway) client to receive another user's WebAPI trigger response — an information-disclosure / cross-user response-confusion issue analogous to CVE-2026-32102's unauthorized action-output disclosure. Depending on payload contents (e.g., HTTP action outputs, target execution results), this could expose sensitive workflow output data to a party not authorized to see it.

### Likelihood Explanation
This code path (`MethodWebAPITrigger` / legacy user message handling in `core/services/gateway/handlers/capabilities`) is explicitly called out in comments as a "legacy" mechanism with a pending TODO for allowlist/rate-limiting and sender validation, suggesting it is a known-weaker, still-reachable surface. Exploitation requires the attacker to guess or control a `MessageID` matching a victim's concurrently in-flight request — the collision window is bounded by `CallbackMaxAgeSec` (default 120s) and requires the requester to be authenticated to the gateway/DON. This lowers but does not eliminate likelihood; it is a timing/ID-collision-dependent bug rather than a trivially always-exploitable one, and I was unable to fully verify within the available context whether an upstream layer (not visible in the retrieved code) additionally binds `MessageID` to sender before reaching this map.

### Recommendation
Scope `savedCallbacks` (and the analogous `dummyHandler.savedCallbacks`) by `(sender, MessageID)` rather than `MessageID` alone, mirroring the `globalID{sender, id}` pattern already used in `common.RequestCache`. Additionally, validate on node-response delivery that the responding message's sender/session corresponds to the same requester that originated the cached callback, rejecting mismatches instead of silently delivering to whatever callback currently occupies that key.

### Proof of Concept
Not independently executed against a live gateway; the code-level trace above establishes the vulnerable map key and the delivery lookup. A concrete PoC would require: (1) authenticating as user A, sending a `web_api_trigger` request with `MessageID = "X"`; (2) before the DON responds, authenticating as user B and sending a colliding `web_api_trigger` request with the same `MessageID = "X"`, overwriting `savedCallbacks["X"]`; (3) observing that when the DON's response for A's original request arrives, it is delivered to B's callback via `handleWebAPITriggerMessage`'s lookup at `handler.go:150`.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/capabilities/remote/types/messages.pb.go (L140-140)
```go
	MessageId    []byte                 `protobuf:"bytes,5,opt,name=message_id,json=messageId,proto3" json:"message_id,omitempty"` // scoped to sender
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```
