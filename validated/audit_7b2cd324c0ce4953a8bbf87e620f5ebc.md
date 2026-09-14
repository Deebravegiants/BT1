### Title
Legacy gateway user messages (`api.Message.Sign`) lack a deadline/expiry field, allowing indefinite signature replay - (File: core/services/gateway/api/message.go)

### Summary
The gateway's legacy signed-message envelope (`api.Message`) signs only `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` — there is no expiry/deadline field baked into the signed data or enforced generically by the gateway before dispatching the message to a handler.

### Finding Description
`Message.Sign` computes the signature over `GetRawMessageBody`, which concatenates `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` only. [1](#0-0) 
`Message.Validate`, which is invoked for every legacy request in `gateway.ProcessRequest`, only checks field lengths/format and recovers the signer — it performs no timestamp/expiry check. [2](#0-1) [3](#0-2) 

Enforcement of message freshness is left entirely to individual handlers rather than the shared envelope/validation layer. For example, `HandleLegacyUserMessage` in the WebAPI capabilities handler explicitly checks a `payload.Timestamp` field against `MaxAllowedMessageAgeSec`, but this is a handler-specific, opt-in check performed on an application-defined payload field, not something the shared `api.Message` signature or `Validate()` guarantees. [4](#0-3) 
Any other current or future legacy handler that consumes signed `api.Message`s (e.g. `OutgoingConnectorHandler.HandleGatewayMessage`, `triggerConnectorHandler.HandleGatewayMessage`) relies solely on `hc.ValidatedMessageFromReq`, which performs the same signature-only validation with no expiry. [5](#0-4) [6](#0-5) 

By contrast, newer JSON-RPC-based auth paths in the codebase (the node-to-gateway websocket handshake, and the Vault gateway allowlist/JWT authorization) do bind signed data to a timestamp/expiry and enforce it centrally: `network.AuthHeaderElems.Timestamp` is checked against tolerance during handshake, and Vault's `AllowListBasedAuth`/`RequestReplayGuard` enforce `ExpiryTimestamp` and digest-based replay prevention. [7](#0-6) [8](#0-7) [9](#0-8) 
This confirms the codebase already recognizes the deadline/replay pattern as necessary for signed requests elsewhere, but the legacy `api.Message` envelope and its generic `Validate()`/`ProcessRequest` dispatch path do not enforce it — freshness is only as good as each individual handler's opt-in logic.

### Impact Explanation
A signed legacy gateway message with no built-in expiry can, if captured (e.g. via a compromised transport hop, logging, or a malicious/compromised handler along the delivery path), be replayed indefinitely against any handler that does not itself implement a freshness check. This matches the "claim signature lacks deadline" bug class: the vulnerability is not in the ECDSA signature scheme itself, but in the missing binding of the signed payload to a validity window, enforced consistently at the framework level. The severity depends on which handler consumes the replayed message — for handlers that trigger job runs, forward triggers, or otherwise cause state changes based on `api.Message` content, replay could cause duplicate/unauthorized actions.

### Likelihood Explanation
Medium. Exploitation requires an attacker to have captured a validly-signed legacy message (this is a legacy path, distinct from the newer Vault/JWT-based request paths, which already have proper expiry+replay guards). The existing WebAPI trigger handler already mitigates this specific case via its own `Timestamp`/`MaxAllowedMessageAgeSec` check, which reduces exercised exposure but is not a systemic protection — the underlying `api.Message` primitive itself remains a footgun for any handler that doesn't replicate that check.

### Recommendation
Add a `Timestamp`/`Deadline` field to `MessageBody` that is included in the signed data in `GetRawMessageBody`, and enforce a maximum message age centrally in `Message.Validate()` (used by `gateway.ProcessRequest` for all legacy requests) rather than relying on individual handlers to implement their own freshness checks. This mirrors the pattern already used for the node-gateway handshake (`AuthHeaderElems.Timestamp` + tolerance) and Vault's `ExpiryTimestamp`/`RequestReplayGuard`.

### Proof of Concept
1. A legitimate client signs an `api.Message` via `Message.Sign` and submits it through the gateway to a handler that does not implement its own timestamp check (e.g. `OutgoingConnectorHandler.HandleGatewayMessage` or `triggerConnectorHandler.HandleGatewayMessage`), which only call `hc.ValidatedMessageFromReq`/`ValidatedMessageFromReq` (signature-only validation). [10](#0-9) 
2. An attacker who intercepts this raw signed message (`Signature` + `Body`) can resubmit the identical bytes through `gateway.ProcessRequest` at any later time. [3](#0-2) 
3. `Message.Validate()` recomputes the signer from the same unchanged raw body and succeeds regardless of elapsed time, because no expiry field exists in `GetRawMessageBody`. [2](#0-1) 
4. The handler processes the replayed message as if newly issued, since it has no independent means of detecting staleness unless it implements its own bespoke timestamp field (as the WebAPI trigger handler does).

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-383)
```go
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
```

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L301-316)
```go
// HandleGatewayMessage processes incoming messages from the Gateway,
// which are in response to a HandleSingleNodeRequest call.
func (c *OutgoingConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		c.lggr.Errorw("failed to validate request", "err", err, "gatewayID", gatewayID)
		return nil
	}
	body := &msg.Body
	l := logger.With(c.lggr, "gatewayID", gatewayID, "method", body.Method, "messageID", msg.Body.MessageID)

	ch, ok := c.responses.get(body.MessageID)
	if !ok {
		l.Warnw("no response channel found; this may indicate that the node timed out the request")
		return nil
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-184)
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
```

**File:** core/services/gateway/network/handshake.go (L44-66)
```go
// Components going into the auth header, excluding the signature.
type AuthHeaderElems struct {
	Timestamp uint32
	DonID     string
	GatewayID string
}

type ChallengeElems struct {
	Timestamp      uint32
	GatewayID      string
	ChallengeBytes []byte
}

var (
	ErrAuthHeaderParse           = errors.New("unable to parse auth header")
	ErrAuthInvalidDonID          = errors.New("invalid DON ID")
	ErrAuthInvalidNode           = errors.New("unexpected node address")
	ErrAuthInvalidGateway        = errors.New("invalid gateway ID")
	ErrAuthInvalidTimestamp      = errors.New("timestamp outside of tolerance range")
	ErrChallengeTooShort         = errors.New("challenge too short")
	ErrChallengeAttemptNotFound  = errors.New("attempt not found")
	ErrChallengeInvalidSignature = errors.New("invalid challenge signature")
)
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L63-68)
```go

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}
```

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
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
