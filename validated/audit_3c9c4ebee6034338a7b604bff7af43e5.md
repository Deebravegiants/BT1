Audit Report

## Title
Cross-user response hijacking via attacker-controlled `MessageID` collision in Gateway WebAPI trigger callback cache - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The Gateway's legacy WebAPI-trigger request path stores each caller's response callback in a DON-scoped, in-memory map (`h.savedCallbacks`) keyed solely by the client-supplied JSON-RPC `ID` (propagated unchanged into `Message.Body.MessageID`), with no uniqueness check, identity binding, or collision rejection. Because the DON's later trigger response is matched and delivered purely by this same attacker-controlled key, a second caller who submits a request with a colliding `MessageID` on the same DON can overwrite the first caller's callback slot and receive the victim's node response instead, while the victim's own request either hangs until timeout or is answered by the attacker's stale entry.

## Finding Description
`gateway.ProcessRequest` decodes the raw JSON-RPC request and only bounds `jsonRequest.ID` in length (`> 200` chars) before treating it as trusted input: [1](#0-0) . For legacy DON-routed requests it calls `msg.Validate()` (which does not enforce ID uniqueness) and dispatches to `h.HandleLegacyUserMessage`: [2](#0-1) .

`ValidatedMessageFromReq` copies the fully attacker-controlled `req.ID` directly into `Message.Body.MessageID` with no server-side randomization: [3](#0-2) .

`handler.HandleLegacyUserMessage` then unconditionally writes the caller's callback into the shared map keyed only by `msg.Body.MessageID`, silently overwriting any existing entry with the same key: [4](#0-3) . There is no check for an existing/in-flight entry before this overwrite.

When a DON node later returns a `MethodWebAPITrigger` response, `handleWebAPITriggerMessage` looks up and deletes the map entry purely by `msg.Body.MessageID` and forwards the node's response to whichever callback currently occupies that slot: [5](#0-4) . The only identity check performed on the node side is that `msg.Body.Sender == nodeAddr` (verifying the *node*, not the original user) in `HandleNodeMessage`: [6](#0-5) . Nothing binds the `savedCallback` entry to the original caller's session, signature, or address — it is a bare `map[string]*savedCallback` keyed by client-chosen string: [7](#0-6) [8](#0-7) .

This confirms the claim's root cause exactly as described: any two unprivileged callers routed to the same DON handler (`h.handlers[donID]` keyed by `msg.Body.DonID` in `ProcessRequest`) share one `savedCallbacks` map with no per-caller isolation, and a colliding `MessageID` lets a later caller's insertion silently clobber an earlier one.

## Impact Explanation
This is a genuine cross-user response-hijacking / corruption bug in the Gateway's request/response matching for `MethodWebAPITrigger`: an unprivileged internet client can, by choosing a `MessageID` identical to another in-flight caller's ID on the same DON, either receive that other caller's trigger response (potential data leak if the response contains sensitive workflow output) or cause the victim's request to silently fail to be answered (denial of response). This maps to the "gateway request impersonation / cross-user response corruption" impact class referenced in the scope rules.

## Likelihood Explanation
Exploitation requires only that an unprivileged attacker (1) know or guess another caller's `MessageID` on the same DON, and (2) send a colliding request within the `~120s` window (`defaultCallbackMaxAgeSec`) before the legitimate node response arrives. No node/operator/host privilege is needed — this is fully triggerable via ordinary HTTP requests to the Gateway's public user-facing port, exactly matching the "reachable by unprivileged client" requirement. Real-world likelihood depends on how the client generates `MessageID`s (sequential/predictable IDs make this trivial; cryptographically random IDs make blind collision infeasible, but a malicious co-tenant knowing/observing a victim's ID could still deliberately collide).

## Recommendation
- Bind `savedCallbacks` entries to caller-specific context (e.g., a server-generated nonce or hash including a per-connection/session identifier), not solely the client-chosen `MessageID`.
- Reject insertion into `savedCallbacks` (return an explicit "duplicate/in-flight request ID" error) rather than silently overwriting an active entry.
- Consider adopting the identity-bound request-cache pattern in `handlers/common/requestcache.go` uniformly for `MethodWebAPITrigger` instead of the ad hoc map in `capabilities/handler.go`.

## Proof of Concept
1. Configure a Gateway with a DON handling `web_api_trigger` requests.
2. Client A sends a valid `web_api_trigger` request with `id = "shared-id"`; `HandleLegacyUserMessage` stores Client A's callback at `savedCallbacks["shared-id"]` (`core/services/gateway/handlers/capabilities/handler.go:411-414`).
3. Before the DON responds to Client A, Client B sends its own valid `web_api_trigger` request also using `id = "shared-id"`, overwriting `savedCallbacks["shared-id"]` with Client B's callback.
4. When a DON node emits the `web_api_trigger` response for `MessageID = "shared-id"` (intended for Client A), `handleWebAPITriggerMessage` (`handler.go:148-162`) forwards it to Client B's callback instead; Client A's HTTP request times out with `RequestTimeoutError` in `gateway.ProcessRequest` (`gateway.go:281-288`).
   - This can be implemented as a Go unit test in `core/services/gateway/handlers/capabilities/handler_test.go` that calls `HandleLegacyUserMessage` twice with colliding `MessageID`s from two distinct mock callbacks, then invokes `HandleNodeMessage`/`handleWebAPITriggerMessage` once and asserts which callback received `SendResponse`.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L72-76)
```go
type savedCallback struct {
	id        string
	createdAt time.Time
	handlers.Callback
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-256)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
	start := time.Now()
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
