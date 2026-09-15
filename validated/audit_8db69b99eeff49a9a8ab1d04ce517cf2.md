Audit Report

## Title
Unprivileged client can hijack another user's pending Gateway callback via colliding `MessageID` (cross-user response confusion) - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`handler.HandleLegacyUserMessage` stores a `*savedCallback` into the shared `h.savedCallbacks` map keyed solely by the attacker-controlled `msg.Body.MessageID`, with no check for an existing entry and no binding to the caller's identity [1](#0-0) . Because `handleWebAPITriggerMessage` looks up and delivers the DON's response using only `msg.Body.MessageID` [2](#0-1) , a second unprivileged client that submits a request with the same `MessageID` as a victim's in-flight request overwrites the victim's callback entry, causing the DON's eventual response to be delivered to the attacker's connection instead of the victim's.

## Finding Description
The gateway's legacy HTTP endpoint accepts unauthenticated JSON-RPC requests — the `Authorization` header is optional and only used as an opaque `auth` string passed to `jsonrpc2.DecodeRequest` [3](#0-2) ; for the `capabilities` handler's legacy path there is no JWT/allowlist enforcement (the code even contains a `// TODO: apply allowlist and rate-limiting here` comment) [4](#0-3) .

`gateway.ProcessRequest` only checks `len(jsonRequest.ID) <= 200` and calls `msg.Validate()`, which requires a syntactically valid signature but derives `Sender` from whatever key the caller chooses to sign with — any attacker can generate a fresh keypair and self-sign an arbitrary `MessageID` [5](#0-4) [6](#0-5) . `msg.Body.MessageID` is fully attacker-controlled and not required to be unique per sender at this layer.

`HandleLegacyUserMessage` then unconditionally overwrites `h.savedCallbacks[msg.Body.MessageID]` [1](#0-0) . When a DON node later responds with the same `MessageID`, `handleWebAPITriggerMessage` looks the entry up and deletes it purely by `MessageID`, without checking any Sender/Receiver correlation to the original HTTP caller, then delivers the payload via `savedCb.SendResponse(...)` [2](#0-1) . This confirms the claim's core mechanism: the map has no collision protection, unlike `RequestCache.NewRequest`, which explicitly keys by `(Sender, MessageID)` and rejects duplicates with `"request already exists"` [7](#0-6) , and unlike the v2 HTTP trigger handler, which rejects duplicate request IDs bound to a JWT ("token has already been used") [8](#0-7) .

The `savedCallback` struct does track `createdAt` for pruning (`defaultCallbackMaxAgeSec = 120`) but this only bounds staleness, not the overwrite/collision issue itself [9](#0-8) .

## Impact Explanation
This is a concrete cross-user response confusion bug reachable by two fully unprivileged HTTP clients hitting the gateway's legacy user-message endpoint with colliding `id`/`MessageID` values. It can leak one user's web-API-trigger response to an unrelated attacker's connection and silently orphan the legitimate requester's call (denial of the original response until timeout). This matches the in-scope "gateway request impersonation / cross-user response corruption" impact category.

## Likelihood Explanation
No authentication, allowlist, or per-caller namespacing gates the `MessageID` on this legacy path — an attacker only needs to guess or predict a victim's client-chosen ID (which may have low entropy, e.g., sequential counters or common defaults) and send a competing request within the ~120s callback window (`defaultCallbackMaxAgeSec`) while the victim's request is pending. This makes exploitation realistic for an attacker who can observe or guess ID patterns, though it does still require winning a race against the real DON response and either predicting or somehow learning the victim's exact `MessageID`.

## Recommendation
Namespace `h.savedCallbacks` by `(Sender, MessageID)` or another value tied to caller identity/connection instead of `MessageID` alone, and reject `HandleLegacyUserMessage` calls that collide with an existing pending entry (mirroring `RequestCache.NewRequest`'s `"request already exists"` behavior). Longer-term, migrate this legacy handler to the same `RequestCache` abstraction used elsewhere in the gateway, and implement the still-pending allowlist/rate-limiting TODO.

## Proof of Concept
1. Client A sends a legacy `web_api_trigger` JSON-RPC request to the gateway's user HTTP endpoint with `id = "X"`, self-signed with A's own ephemeral key; gateway stores `savedCallbacks["X"] = callbackA` and forwards to DON nodes (`core/services/gateway/handlers/capabilities/handler.go:411-419`).
2. Before any DON node replies, client B sends its own self-signed request with `id = "X"`; gateway overwrites `savedCallbacks["X"] = callbackB` with no duplicate check.
3. A DON node responds with `MessageID = "X"`; `handleWebAPITriggerMessage` pops `savedCallbacks["X"]` (now `callbackB`) and sends the response intended for A's request to B's HTTP connection.
4. Client A's request never resolves and times out (`RequestTimeoutError` after `callback.Wait(ctx)` expires).

A Go unit/integration test extending `core/services/gateway/handlers/capabilities/handler_test.go` can drive this deterministically: call `HandleLegacyUserMessage` twice with distinct `handlers.Callback` instances but identical `msg.Body.MessageID`, then invoke `HandleNodeMessage`/`handleWebAPITriggerMessage` once and assert which callback receives the response.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
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

**File:** core/services/gateway/gateway.go (L221-264)
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
```

**File:** core/services/gateway/handlers/common/requestcache.go (L57-63)
```go
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L389-392)
```go
		// Second request with same ID should fail
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "token has already been used")
```
