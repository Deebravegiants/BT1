### Title
Gateway forwards legacy web-API-trigger messages to all DON nodes with no allowlist/authorization check - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` in the gateway's web-API capabilities handler validates only the message shape, method name, and staleness of an inbound message, then immediately fans the raw request out to every node in the DON — with an explicit TODO admitting that allowlist/rate-limit enforcement is missing at that point in the flow.

### Finding Description
`HandleLegacyUserMessage` decodes the payload, checks `payload.Timestamp` for staleness, and checks that `msg.Body.Method == MethodWebAPITrigger`, but performs no sender/topic allowlist check before converting the message to a request and sending it to every DON member: [1](#0-0) 

The code explicitly flags the gap:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [2](#0-1) 

After that check, the handler builds `req` via `common.ValidatedRequestFromMessage(msg)`, stores the callback, and forwards `req` to every DON member: [3](#0-2) 

This is structurally the same class of bug as the OpenClaw advisory: content handling/dispatch (there: cite expansion; here: cross-DON request fan-out and callback registration) happens before — and in this case entirely without — the authorization/allowlist decision that is supposed to gate it. By contrast, the vault gateway path in this same repository explicitly defers all side-effecting work (owner-scoped ciphertext-limiter tenant creation, ID stamping, param mutation) until *after* `Authorizer.AuthorizeRequest` succeeds, and even has regression tests asserting this ordering: [4](#0-3) [5](#0-4) 

`HandleLegacyUserMessage` has no equivalent authorization gate at all — the allowlist/rate-limit TODO was never implemented for this legacy code path, even though the sibling `webapiTrigger`/`processTrigger` capability trigger path (which handles the same `MethodWebAPITrigger` payload downstream) does enforce `allowedSenders` and per-sender rate limiting: [6](#0-5) 

### Impact Explanation
Any unprivileged external client able to reach the gateway's legacy user-message endpoint for this handler can cause it to broadcast attacker-controlled requests to every node in the configured DON and register a pending callback, without passing any sender/topic allowlist or rate-limit check. This is a quota/allowlist bypass and unauthorized-request-fanout vector: it lets an unauthenticated or unauthorized caller consume DON node resources and callback-table slots (`h.savedCallbacks`) that are meant to be gated by the (unimplemented) allowlist/rate-limit check, on every DON node simultaneously rather than being intercepted at the gateway edge.

### Likelihood Explanation
Likelihood is high for any deployment that still routes traffic through this legacy handler function: no cryptographic secret or bypass technique is required, only a well-formed `MethodWebAPITrigger` message with a fresh timestamp. The missing check is explicitly marked as a known gap in the code (the TODO comment), indicating it was never wired up rather than being an edge-case regression.

### Recommendation
Implement the allowlist and rate-limiting check called out by the TODO in `HandleLegacyUserMessage` before constructing/forwarding `req` to DON members — mirroring the pattern used in `core/capabilities/webapi/trigger/trigger.go`'s `processTrigger` (per-sender allowlist + rate limiter) and the vault gateway processor's "authorize before any side effect" ordering. Reject or short-circuit the message with an error response before touching `h.savedCallbacks` or calling `don.SendToNode` if the sender/topic is not allowlisted or exceeds rate limits.

### Proof of Concept
1. Send a well-formed JSON message body with `Method = "web_api_trigger"`, a valid `TriggerRequestPayload` with a fresh `Timestamp`, to the gateway endpoint that routes to `handler.HandleLegacyUserMessage` for this DON handler.
2. Observe that regardless of the sender's identity or any configured allowlist, the handler proceeds past the method/staleness checks (there is no allowlist check present) and calls `don.SendToNode` for every configured DON member, and registers the callback in `h.savedCallbacks`.
3. Repeating this with arbitrary/unauthorized sender identities demonstrates the missing allowlist/authorization gate that the code's own TODO acknowledges is absent.

### Citations

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-34)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```

**File:** core/capabilities/vault/ciphertext_limiter_tenant_test.go (L110-137)
```go
func TestGatewayVaultRequestProcessor_ProcessRequest_UnauthorizedWriteNeverTouchesCiphertextLimiter(t *testing.T) {
	t.Parallel()

	for _, method := range []string{vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate} {
		for _, stripOwnerPrefix := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s/stripOwnerPrefix=%t", method, stripOwnerPrefix), func(t *testing.T) {
				t.Parallel()

				validator, recorder := mustNewRecordingValidator(t)

				// One-byte hex value under a fresh owner passes structure validation
				// (publicKey is nil so label validation is skipped), reaching authorization.
				secrets := []*vaultcommon.EncryptedSecret{
					{Id: &vaultcommon.SecretIdentifier{Owner: "0xnewowner", Key: "k"}, EncryptedValue: "00"},
				}
				req := mustWriteRequest(t, method, secrets)

				authorizer := vaultcapmocks.NewAuthorizer(t)
				authorizer.EXPECT().AuthorizeRequest(t.Context(), mock.Anything).Return(nil, errors.New("not authorized"))

				processor := mustNewGatewayVaultRequestProcessor(t, validator, authorizer, stripOwnerPrefix)
				_, err := processor.ProcessRequest(t.Context(), &req, nil)
				require.Error(t, err)
				require.ErrorContains(t, err, "request not authorized")
				require.Empty(t, recorder.recorded(), "owner-scoped ciphertext limiter must not be consulted before authorization")
			})
		}
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
