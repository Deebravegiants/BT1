## Title
Unbounded per-sender rate-limiter map growth allows memory exhaustion (OOM) of the WebAPI trigger connector - (File: `core/services/workflows/ratelimiter/ratelimiter.go`)

### Summary
The Nethermind report describes a peer able to force unbounded resource allocation on the victim, leading to an out-of-memory crash. The closest analog reachable from an *unprivileged, internet-facing* request path in this codebase is the `RateLimiter.Allow` implementation used by the WebAPI trigger connector: it allocates a new per-sender `rate.Limiter` entry for every distinct sender string it observes, and never evicts old entries.

### Finding Description
`RateLimiter.Allow` lazily creates and permanently stores a `*rate.Limiter` keyed by the caller-supplied `sender` string, with no size cap, TTL, or eviction: [1](#0-0) 

This limiter is used by the WebAPI trigger connector (`triggerConnectorHandler.processTrigger`) to rate-limit incoming trigger requests per `body.Sender`: [2](#0-1) 

`body.Sender` originates from the gateway message body and is converted to an `ethCommon.Address` in `HandleGatewayMessage`, but the `rateLimiter.Allow` call is invoked with the raw string `body.Sender`, not a value that is validated to be a registered/allow-listed sender before the limiter map entry is created: [3](#0-2) 

Notably, the allow-list check (`trigger.allowedSenders[sender.String()]`) happens *after* the topic match but the rate limiter is consulted on the same iteration for every matched topic regardless of whether the sender check passed — and more importantly, nothing in `RateLimiter` bounds the number of distinct sender keys that can accumulate over the life of the process. Contrast this with the sibling `savedCallbacks` map in `core/services/gateway/handlers/capabilities/handler.go`, which is explicitly bounded and reaped (`MaxSavedCallbacks`, `pruneCallbacks`): [4](#0-3) 

No equivalent pruning/eviction exists for `ratelimiter.RateLimiter.perSender`.

### Impact Explanation
Any unprivileged client able to reach the gateway's user-facing endpoint and route a message to a node's WebAPI trigger handler with an attacker-chosen `Sender` value on each request causes a new map entry (a `*rate.Limiter` struct) to be permanently retained in process memory. Because the map is never pruned, sustained requests with varying sender values cause monotonic, unbounded heap growth, eventually leading to an out-of-memory crash of the node process — the same DoS class described in the Nethermind report, but reachable via the HTTP/gateway boundary rather than the devp2p layer.

### Likelihood Explanation
Likelihood is moderate: it requires an attacker who can submit many gateway-routed trigger requests with distinct sender values fast enough to outpace the process's available memory, and depends on whether upstream authentication/allow-listing (gateway-level JWT/allowlist checks, per-message signature verification) is enforced before `processTrigger`/`Allow` is reached. I was not able to fully trace whether `body.Sender` is cryptographically verified elsewhere in the message-validation pipeline (`hc.ValidatedMessageFromReq`) before this point — this is a gap in my analysis and should be confirmed by a background agent with full repo access.

### Recommendation
Bound the `perSender` map in `ratelimiter.RateLimiter` with either a maximum entry count plus LRU/oldest eviction, or a TTL-based reaper (mirroring the `pruneCallbacks`/`MaxSavedCallbacks` pattern already used elsewhere in the gateway code), and ensure the sender key used to index the limiter is validated against `allowedSenders` (or otherwise authenticated) before an entry is created.

### Proof of Concept
1. Register a WebAPI trigger with `allowedTopics` containing a topic the attacker knows.
2. Send repeated `MethodWebAPITrigger` gateway messages through the connector with the same matching topic but a freshly randomized `Sender` header value on every request.
3. Each request causes `triggerConnectorHandler.processTrigger` to call `trigger.rateLimiter.Allow(body.Sender)` with a novel sender string, permanently growing `RateLimiter.perSender`.
4. Repeat at high volume; process RSS grows unbounded until OOM kill, without ever needing a valid/allow-listed sender to pass authorization.

### Citations

**File:** core/services/workflows/ratelimiter/ratelimiter.go (L40-52)
```go
func (rl *RateLimiter) Allow(sender string) (senderAllow bool, globalAllow bool) {
	rl.mu.Lock()
	senderLimiter, ok := rl.perSender[sender]
	if !ok {
		senderLimiter = rate.NewLimiter(rate.Limit(rl.config.PerSenderRPS), rl.config.PerSenderBurst)
		rl.perSender[sender] = senderLimiter
	}
	rl.mu.Unlock()

	senderAllow = senderLimiter.Allow()
	globalAllow = rl.global.Allow()
	return senderAllow, globalAllow
}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-118)
```go
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-188)
```go
func (h *triggerConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		h.lggr.Errorw("error validating message from request", "err", err, "request", req)
		return nil
	}
	body := &msg.Body
	sender := ethCommon.HexToAddress(body.Sender)
	var payload webapicap.TriggerRequestPayload
	err = json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw("error decoding payload", "err", err)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("error %s decoding payload", err.Error()).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
		return nil
	}

	switch body.Method {
	case ghcapabilities.MethodWebAPITrigger:
		resp := h.processTrigger(ctx, gatewayID, body, sender, payload)
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-334)
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
```
