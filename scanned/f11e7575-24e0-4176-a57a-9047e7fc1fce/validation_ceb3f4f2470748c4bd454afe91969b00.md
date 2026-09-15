Confirmed: no dedup exists on the node→trigger path other than a coarse staleness window, so a captured valid signed legacy trigger message can be replayed to re-fire a workflow trigger.

### Title
Legacy WebAPI trigger messages lack replay protection, allowing re-execution of previously captured signed requests - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy (V1) trigger message path validates a signed `api.Message` and forwards it to DON nodes, but the only "freshness" check is a coarse timestamp window on the trigger payload (`MaxAllowedMessageAgeSec`). There is no persistent nonce, replay cache, or one-time-use enforcement of `MessageID`/signature, so any previously valid signed message can be resent verbatim within that window (or, once resubmitted, the age check itself is derived from an attacker-replayable field) to re-trigger the same workflow action — directly analogous to the reported `changeRecipientAddress` replay class, where a captured valid signature/payload pair can be reused to repeat a privileged action.

### Finding Description
`api.Message.Sign`/`ExtractSigner` (`core/services/gateway/api/message.go:96-134`) computes a signature over `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` only — there is no chain/session/nonce binding, and the same signature stays valid for as long as the signer's key is valid, exactly like the vulnerable `_signature`/`_data` pair in the report. [1](#0-0) 

For legacy (V1) requests, `handler.HandleLegacyUserMessage` accepts the message, stores a callback keyed only by `msg.Body.MessageID`, and fans the same signed message out to all DON nodes — it never checks whether this `MessageID`/signature was already processed before: [2](#0-1) 

The only mitigating check is a coarse staleness test on the trigger payload's self-reported `Timestamp` field:
```
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    ... "stale message" ...
}
``` [3](#0-2) 

Because `Timestamp` is part of the signed `Payload`, an attacker cannot forge a fresh timestamp for an old signature — but they don't need to: they can simply replay the message *within* the allowed age window (which defaults to a non-trivial duration configured by `MaxAllowedMessageAgeSec`), or replay it before that window expires, and the gateway will accept and re-forward it to the DON exactly as before, since nothing marks the `MessageID`/signature pair as already consumed once processing completes. Compare this to the sibling code paths in the same codebase that *do* implement one-time-use protection:
- The vault gateway pipeline explicitly implements a `RequestReplayGuard` with digest deduplication. [4](#0-3) 
- The V2 HTTP trigger handler rejects duplicate `requestID`s and duplicate JWT `jti`s. [5](#0-4) [6](#0-5) 
- The confidential-relay handler also rejects duplicate request IDs. [7](#0-6) 

The legacy V1 path (`handler.HandleLegacyUserMessage` / `handleWebAPITriggerMessage`) has none of these protections: the `savedCallbacks` map is keyed by `MessageID` purely for routing the DON's response back to the original HTTP caller, and the entry is deleted as soon as a response arrives, not to prevent reprocessing: [8](#0-7) 

### Impact Explanation
An unprivileged actor who has captured (e.g., via logs, network capture, a misconfigured proxy, or a legitimately-authorized caller acting maliciously later) a previously valid signed legacy trigger `Message` can resend it to the gateway's `ProcessRequest` endpoint. The gateway will re-validate the signature (which is still cryptographically correct) and forward it to all DON nodes again, causing the target workflow's `web-api-trigger` to fire a second (or Nth) time with the same `TriggerEventId`/payload. Depending on what the workflow does with that trigger event (e.g., moving funds, submitting price updates, initiating job runs), this results in duplicate/unauthorized job execution — the impact category explicitly called out as acceptable in the validation rules ("unauthorized job run"). The severity is bounded by the replay window (`MaxAllowedMessageAgeSec`) and by whatever downstream idempotency the workflow itself implements (which is outside the gateway's control), but the gateway itself provides no defense-in-depth against this class of replay on this specific code path, unlike its V2/vault counterparts.

### Likelihood Explanation
Medium. It requires the attacker to have obtained a previously valid signed message (the same precondition the external report itself accepts: "if he also got hold on one of recipient addresses"/signature history). Given that legacy trigger messages travel over the gateway's public HTTP endpoint and are logged/observable in several places (e.g., debug logs referencing `msg.Body.MessageID`), and that no additional freshness/nonce binding exists beyond the payload's self-declared timestamp, replay is straightforward once a valid message is captured, within the configured age window.

### Recommendation
Add explicit one-time-use enforcement to the legacy trigger path, mirroring the pattern already used elsewhere in the codebase (`RequestReplayGuard`, JWT `jti` cache, `requestID` dedup):
- Maintain a replay cache of `(MessageID, Signature)` or a digest of the signed body, with TTL aligned to `MaxAllowedMessageAgeSec`, and reject any request whose digest has already been seen — instead of only checking the payload's self-reported timestamp.
- Alternatively, bind the signature to a server-issued, single-use nonce/challenge (similar to `network.ChallengeElems` used in the node connection handshake) so that a captured signature cannot be reused at all.

### Proof of Concept
1. An authorized sender signs and submits a valid legacy `api.Message` trigger request (as in `triggerRequest` test helper) to the gateway's `/…` endpoint; the gateway accepts it, forwards it to the DON, and the workflow fires.
2. Within `MaxAllowedMessageAgeSec` of the original `payload.Timestamp`, an attacker who obtained the exact same signed message bytes (signature + body) resubmits it verbatim to the gateway.
3. `handler.HandleLegacyUserMessage` re-validates the signature successfully (nothing has changed), the staleness check on `payload.Timestamp` still passes (it hasn't expired), and the message is forwarded to all DON nodes again exactly as in step 1, causing the trigger/workflow to execute a second time from the identical original request. [2](#0-1)

### Citations

**File:** core/services/gateway/api/message.go (L90-108)
```go
// Message signatures are over the following data:
//  1. MessageID aligned to 128 bytes
//  2. Method aligned to 64 bytes
//  3. DonID aligned to 64 bytes
//  4. Receiver (in hex) aligned to 42 bytes
//  5. Payload (raw bytes before parsing)
func (m *Message) Sign(privateKey *ecdsa.PrivateKey) error {
	if m == nil {
		return errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signature, err := gw_common.SignData(privateKey, rawData...)
	if err != nil {
		return err
	}
	m.Signature = utils.StringToHex(string(signature))
	m.Body.Sender = strings.ToLower(crypto.PubkeyToAddress(privateKey.PublicKey).Hex())
	return nil
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
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

**File:** core/capabilities/vault/request_replay_guard.go (L9-47)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")

// RequestReplayGuard prevents replay of already-processed requests by tracking
// request digests with expiry timestamps. It is safe for concurrent use.
//
// Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow to ensure
// that a given request digest is only accepted once.
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}

// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L392-426)
```go
func newJWTReplayCache(cleanupPeriod time.Duration) *jwtReplayCache {
	return &jwtReplayCache{
		cache:         make(map[string]time.Time),
		cleanupPeriod: cleanupPeriod,
	}
}

func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}

// cleanupOldEntries removes expired entries from the cache
func (cache *jwtReplayCache) cleanupOldEntries(cutoff time.Time) int {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	var expiredCount int
	for jti, createdAt := range cache.cache {
		if createdAt.Before(cutoff) {
			delete(cache.cache, jti)
			expiredCount++
		}
	}
	return expiredCount
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
```
