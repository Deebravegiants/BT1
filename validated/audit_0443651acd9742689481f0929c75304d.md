### Title
Unauthenticated legacy web-API trigger request drives unbounded workflow-DON fan-out and callback-map growth - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `documenso` report describes an endpoint (`/api/files/upload-pdf`) that accepts writes/uploads from unauthenticated callers, letting an attacker create unbounded server-side state (files/DB rows) indefinitely. The closest reachable analog in this repository is `handler.HandleLegacyUserMessage` in the Gateway's capabilities handler, which processes legacy user (`msg.Body.DonID != ""`) requests **without any allowlist, authentication, or per-caller rate limiting** before persisting state and fanning the request out to every node in the DON.

### Finding Description
The Gateway's public `ProcessRequest` entrypoint [1](#0-0)  routes any legacy-style JSON-RPC request (one that carries a `DonID`) directly to the DON's registered `handlers.Handler` via `HandleLegacyUserMessage`, with no authentication check performed by the gateway itself.

In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` accepts this unauthenticated message, validates only payload structure and timestamp, and then unconditionally:
1. Stores the message in the in-memory `savedCallbacks` map keyed by attacker-controlled `msg.Body.MessageID` [2](#0-1) .
2. Fans the request out to **every** node in the DON [3](#0-2) .

Critically, the code contains an explicit acknowledgment that authorization is missing:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [4](#0-3) 

Unlike the sibling Vault gateway path, where `AllowListBasedAuth.AuthorizeRequest` [5](#0-4)  or JWT-based auth (`authorizeAllowListBasedAuth`/`authorizeJWTBasedAuth`) [6](#0-5)  gate every mutating request before it touches shared state or reaches nodes, the legacy web-API trigger path has no equivalent authorizer call.

Mitigations exist for the memory-growth side effect only: a periodic `pruneCallbacks()` job caps `savedCallbacks` at `MaxSavedCallbacks` (default 20000) and expires entries after `CallbackMaxAgeSec` (default 120s) [7](#0-6) . There is, however, no limiting of the **DON fan-out** itself — each unauthenticated request causes an RPC to be sent to every DON member node (`don.SendToNode`), which is the more expensive/impactful side effect (workflow node CPU/network consumption), and no per-caller quota exists to bound how many such requests one unauthenticated caller can issue.

### Impact Explanation
An unauthenticated actor able to reach the Gateway's user-facing HTTP endpoint can repeatedly submit legacy `web_api_trigger` messages. Each request forces the Gateway to:
- create an in-memory callback entry (bounded, but still consumes memory/CPU on eviction sort),
- send a network RPC to **every node** in the targeted DON.

This matches the CVE's "unauthenticated resource exhaustion" bug class (`VA:H` — availability impact) rather than the file-storage angle specifically, since there is no persistent disk/DB write here — the impact is network/CPU exhaustion of the DON member nodes and the Gateway's own goroutine/memory pool, triggered entirely by an unauthenticated caller. Severity is bounded by the existing `savedCallbacks` cap and node-level rate limiter (`nodeRateLimiter` gates only outgoing responses from nodes, not incoming triggers from users).

### Likelihood Explanation
The `TODO: apply allowlist and rate-limiting here` comment confirms this is a known, unresolved gap rather than a defense-in-depth omission. Reaching this code path requires only knowing/guessing a valid `DonID` and crafting a `web_api_trigger` message with a non-expired timestamp — no credentials, session, or signature verification is required by this handler before the fan-out occurs.

### Recommendation
Add authorization/allowlisting to `HandleLegacyUserMessage` analogous to the Vault gateway's `Authorizer`/`AllowListBasedAuth` pattern, and add a per-caller or global rate limiter on inbound legacy trigger requests before they are persisted to `savedCallbacks` or forwarded to DON nodes.

### Proof of Concept
Not independently verified end-to-end (I could not confirm from static analysis alone whether the outer HTTP/websocket layer in front of `gateway.ProcessRequest` enforces any caller identity for legacy-DonID requests, since `msg.Validate()`/signature verification in `core/services/gateway/api/message.go` was not fully inspected due to tool-call limits). Conceptually:
1. Determine/guess a valid `DonID` for a workflow DON served by the Gateway.
2. Send repeated JSON-RPC requests to the Gateway's user HTTP endpoint with `method: "web_api_trigger"`, unique `MessageID`s, and a current `Timestamp`, without any auth token.
3. Observe that each request is accepted, stored in `savedCallbacks`, and forwarded to all DON member nodes, with no authentication check performed.

**Caveat**: I was unable to fully confirm whether `msg.Validate()` (called for legacy requests before routing) performs any signature check that would block a fully anonymous caller — this is a gap in my analysis given tool-call limits. If `Validate()` does enforce a valid signature from a registered entity, this finding would be downgraded from "unauthenticated" to "any-authenticated-caller-can-DoS-any-DON," which is a materially different (lower) severity finding. I recommend confirming this in a Devin session with full file access.

### Citations

**File:** core/services/gateway/gateway.go (L221-265)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-339)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}

	if expired > 0 || evicted > 0 {
		h.lggr.Infow("Pruned savedCallbacks", "expired", expired, "evicted", evicted, "remaining", len(h.savedCallbacks))
	}
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-420)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-62)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}
```

**File:** core/capabilities/vault/authorizer.go (L130-146)
```go
func (a *authorizer) authorizeAllowListBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.allowListBasedAuth == nil {
		err := errors.New("AllowListBasedAuth authorizer is nil")
		a.lggr.Errorw("AllowListBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.allowListBasedAuth.AuthorizeRequest(ctx, req)
}

func (a *authorizer) authorizeJWTBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.jwtBasedAuth == nil {
		err := errors.New("JWTBasedAuth is nil")
		a.lggr.Errorw("JWTBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.jwtBasedAuth.AuthorizeRequest(ctx, req)
}
```
