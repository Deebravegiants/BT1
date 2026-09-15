The `WebAPICapabilitiesType` handler (`capabilities.NewHandler`) is actively registered and reachable — this confirms the legacy handler path is still wired into production configurations, not deprecated.

The evidence fully confirms the claim as presented. `Message.Validate()` in `core/services/gateway/api/message.go` only checks field lengths and signature format, extracting a signer via `ExtractSigner` without any allowlist check [1](#0-0) . In `gateway.ProcessRequest`, any request carrying a `don_id` is routed to `HandleLegacyUserMessage` after only calling `msg.Validate()` [2](#0-1) . `HandleLegacyUserMessage` explicitly has `// TODO: apply allowlist and rate-limiting here` immediately before broadcasting the request to every DON member via `don.SendToNode` [3](#0-2) . This handler type (`WebAPICapabilitiesType`) is actively registered in `handler_factory.go`, confirming reachability rather than dead/deprecated code [4](#0-3) .

Audit Report

## Title
Missing Allowlist/Authorization Check on Legacy WebAPI Trigger Gateway Path - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
The legacy gateway user-message path for the WebAPI capability (`web_api_trigger` method) forwards attacker-controlled requests to all DON nodes without any allowlist, per-user authorization, or user-identity check, despite the code explicitly acknowledging this gap with a `TODO` comment.

## Finding Description
`gateway.ProcessRequest` routes any request carrying a `don_id` to the legacy handler path after only calling `msg.Validate()`. `Message.Validate()` checks field lengths/signature format and extracts a signer address from the signature via `ExtractSigner`, but never verifies that signer against any allowlist, node registry, or user permission table — it accepts whatever key signed the payload. That message is then handed to `HandleLegacyUserMessage`, which decodes the `TriggerRequestPayload`, checks timestamp freshness, and checks the method name, but the code explicitly states `// TODO: apply allowlist and rate-limiting here` right before broadcasting the request to every DON member via `don.SendToNode`. This contrasts with the parallel vault handler (`AllowListBasedAuth`/JWT via `requestProcessor.ProcessRequest`) and the v2 HTTP trigger handler (JWT-based authentication), both of which enforce authorization before dispatch. The `WebAPICapabilitiesType` handler that contains this vulnerable code path is actively instantiated in `handler_factory.go`, confirming this is live, reachable code rather than dead/deprecated legacy code.

## Impact Explanation
Any unprivileged client capable of reaching the gateway's public HTTP endpoint and producing a validly-formatted (not validly-authorized) signed message can trigger a `web_api_trigger` job run broadcast to all nodes of a DON configured with the `web-api-capabilities` handler type, since there is no allowlist gate comparable to the vault/v2 http trigger handlers. This maps to the "unauthorized action via unauthenticated/unauthorized endpoint" bug class — request impersonation / unauthorized job trigger on an internet-facing gateway component.

## Likelihood Explanation
The gateway HTTP endpoint (`ProcessRequest`) is explicitly internet-facing and designed to accept external client requests; reaching this legacy code path only requires supplying a `don_id` in the request body and any valid-format ECDSA signature (the signer need not be a known/authorized identity). This is directly reachable without insider access, limited only to DONs configured to use the `web-api-capabilities` handler type rather than the newer v2/vault path — but that handler type remains a supported, wired-up option in the current codebase, not something that has been removed.

## Recommendation
Add an authorization/allowlist check (mirroring `AllowListBasedAuth`/`Authorizer` used in the vault and v2 HTTP trigger handlers) inside `HandleLegacyUserMessage` before forwarding requests to DON nodes, replacing the outstanding `TODO` at `core/services/gateway/handlers/capabilities/handler.go` line 384 with actual allowlist and rate-limiting enforcement tied to the message's extracted signer (`msg.Body.Sender`).

## Proof of Concept
1. Craft a `MessageBody` with `Method: "web_api_trigger"`, a `don_id` matching a DON configured with the `web-api-capabilities` handler type, and a `TriggerRequestPayload` with `Timestamp` set to current time.
2. Sign the message with any arbitrary ECDSA private key (not registered/authorized anywhere) using `Message.Sign`.
3. POST the raw JSON to the gateway's public HTTP endpoint (`ProcessRequest`).
4. `msg.Validate()` succeeds (only checks format/signature well-formedness) → `HandleLegacyUserMessage` executes and calls `don.SendToNode` for every DON member, without ever checking whether the signer is allowlisted — confirming the missing authorization gate at the `TODO` comment.

### Citations

**File:** core/services/gateway/api/message.go (L80-87)
```go
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-419)
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
```

**File:** core/services/gateway/handler_factory.go (L84-85)
```go
	case WebAPICapabilitiesType:
		return capabilities.NewHandler(handlerConfig, donConfig, don, hf.httpClient, hf.lggr)
```
