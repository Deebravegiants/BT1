## Analysis

The reported CVE describes an unauthenticated attacker triggering uncontrolled resource consumption via a public upload endpoint that lacks proper request validation, leading to a DoS. I found an analogous unprivileged-actor resource-consumption weakness in Chainlink's internet-facing Gateway service.

### Title
Unauthenticated/self-signed legacy Gateway messages bypass allowlisting and rate-limiting, enabling resource-exhaustion DoS via unbounded callback map growth and DON-wide fan-out - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Gateway's public HTTP endpoint accepts "legacy" user messages (`api.Message`) that are routed to `handler.HandleLegacyUserMessage`. The only gate before this handler runs is `msg.Validate()`, which merely checks that the message is self-consistently signed by *some* ECDSA key — it does not check that the signer is an authorized/allowlisted party. Any internet client can generate its own keypair, sign an arbitrary `web_api_trigger` message, and reach the handler. The handler contains an explicit `// TODO: apply allowlist and rate-limiting here` comment confirming no authorization or throttling is applied at this stage.

### Finding Description
`core/services/gateway/gateway.go`'s `ProcessRequest` decodes the raw HTTP body and, for legacy requests (`msg.Body.DonID != ""`), only calls `msg.Validate()` before dispatching to the handler: [1](#0-0) 

`msg.Validate()` in `core/services/gateway/api/message.go` verifies field lengths and that the signature is well-formed / recoverable — it does not check the recovered signer against any allowlist: [2](#0-1) 

`handler.HandleLegacyUserMessage` then unconditionally accepts the message (subject only to a stale-timestamp check), explicitly notes that allowlisting/rate-limiting is not yet applied, stores an entry in the in-memory `savedCallbacks` map, and fans the request out to **every** DON member node: [3](#0-2) 

The `savedCallbacks` map is only pruned periodically (every `CallbackPruneIntervalSec`, default 30s) and capped at `MaxSavedCallbacks` (default 20000), with the config comment itself acknowledging it "could briefly exceed under heavy load": [4](#0-3) [5](#0-4) 

### Impact Explanation
Because signature validity does not imply authorization, any unprivileged network client can flood the public Gateway HTTP endpoint with self-signed `web_api_trigger` messages. Each request causes: (1) a heap allocation in the shared `savedCallbacks` map guarded only by periodic (30s) pruning, and (2) an amplified fan-out — one attacker HTTP request produces `N` outbound `SendToNode` calls to every member of the target DON. Sustained flooding can exhaust Gateway memory/goroutines and impose amplified load on DON nodes, a availability/DoS impact analogous to the reported CVE's uncontrolled resource consumption from an unprivileged upload request.

### Likelihood Explanation
Exploitation requires no credentials — an attacker only needs to generate an ECDSA keypair locally (trivial, unprivileged) to produce a validly-signed message that passes `msg.Validate()`. The endpoint is internet-facing by design (Gateway public HTTP server). The likelihood is High for reaching the vulnerable code path; the severity depends on operational size limits (`MaxSavedCallbacks`, prune interval, request-body/ID length caps already present in `httpserver.go` and `gateway.go`) which bound but do not eliminate the amplification and transient memory growth.

### Recommendation
Enforce allowlist/authorization and rate-limiting for legacy `HandleLegacyUserMessage` requests *before* accepting the message into `savedCallbacks` or fanning out to DON nodes — i.e., implement the outstanding `// TODO: apply allowlist and rate-limiting here` in `core/services/gateway/handlers/capabilities/handler.go`. Additionally, tighten pruning (shorter interval or size-based backpressure) so a burst cannot transiently exceed `MaxSavedCallbacks` before eviction, and consider per-sender rate limiting keyed off the recovered signer address (mirroring the `nodeRateLimiter` already used for `handleWebAPIOutgoingMessage`).

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration/allowlisting required).
2. Construct an `api.Message` with `Method: "web_api_trigger"`, a valid current `Timestamp`, and any `DonID` matching a live DON; sign it with the generated key using `msg.Sign(privateKey)`.
3. Wrap it as a JSON-RPC 2.0 request (`ID` = message ID, `Method` = message method, `Params` = the signed message) and POST it repeatedly to the Gateway's public HTTP endpoint.
4. Each request passes `msg.Validate()` (signature is internally consistent) and reaches `HandleLegacyUserMessage`, which stores a callback entry and calls `don.SendToNode` for every DON member — repeat at high volume to grow `savedCallbacks` and multiply outbound load faster than the 30-second prune cycle reclaims it. [6](#0-5)

### Citations

**File:** core/services/gateway/gateway.go (L253-265)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
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
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```
