### Title
Missing allowlist/authorization check on legacy WebAPI trigger messages allows any signer to inject trigger requests to all DON nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The CVE describes Tinc's meta-protocol accepting attacker-controlled meta-packets without message authentication, letting an unprivileged network actor manipulate protocol state. The closest in-scope analog is the gateway's legacy WebAPI trigger path: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` cryptographically verifies that a message is *signed by someone*, but never checks that the signer is an authorized/allowlisted party before fanning the message out to every node in the DON. Any external, unprivileged caller who can produce a valid ECDSA keypair (trivial, unauthenticated) can therefore have arbitrary trigger requests delivered to every DON member.

### Finding Description
`api.Message.Validate()` (core/services/gateway/api/message.go:54-88) only proves that the message was signed by *some* ECDSA key — `ExtractSigner()` recovers whatever address corresponds to the signature and stores it in `m.Body.Sender`. It performs no comparison against a known/allowlisted set of senders. [1](#0-0) 

`HandleLegacyUserMessage` uses exactly this weak guarantee: it decodes the payload, checks the method name and a staleness timestamp, then immediately forwards the request to every DON member — with an explicit acknowledgement that sender allowlisting is not implemented: [2](#0-1) [3](#0-2) 

The corresponding test file confirms this is a known, unresolved gap rather than a deliberate design choice elsewhere in the code: [4](#0-3) 

This mirrors the CVE's root cause conceptually: a protocol message is accepted and acted upon as long as it is well-formed, without verifying that the *originator* is entitled to send it. In Tinc, the missing check was a MAC on meta-protocol packets; here it is a missing allowlist/authorization check on the message's cryptographically-recovered sender before the gateway routes the message to nodes.

### Impact Explanation
Any unauthenticated network client that can reach the gateway's legacy HTTP/WS entrypoint can sign a trigger message with a throwaway key and have it delivered to every node in the target DON as a `MethodWebAPITrigger` request. Since the nodes' own capability layer trusts requests routed through the gateway, this allows an unprivileged actor to invoke workflow triggers they are not authorized to invoke, which can result in unauthorized workflow/job execution across the entire DON.

### Likelihood Explanation
The check is entirely missing (not merely misconfigured), and the code path is reachable directly from an unprivileged HTTP client through the gateway's public-facing legacy message handler with no additional preconditions beyond generating a valid signature, which requires no special privilege.

### Recommendation
Before calling `don.SendToNode` in `HandleLegacyUserMessage`, verify `msg.Body.Sender` (or equivalently the workflow/owner identity it maps to) against an authorization allowlist analogous to the one already used elsewhere in the codebase (e.g., `allowListBasedAuth` in `core/capabilities/vault/allow_list_based_auth.go`), and add rate limiting per sender, closing the TODO explicitly left in the handler.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration or privilege required).
2. Construct an `api.Message` with `Method = MethodWebAPITrigger`, a valid `Timestamp`, and any `TriggerRequestPayload`, then call `msg.Sign(privateKey)` (as done in the test helper `triggerRequest` in `core/services/gateway/handlers/capabilities/handler_test.go:193-234`).
3. Submit the message to the gateway's legacy message endpoint.
4. Observe that `HandleLegacyUserMessage` forwards the request to every member of `h.donConfig.Members` without ever checking whether the recovered `msg.Body.Sender` is permitted to issue trigger requests.

### Citations

**File:** core/services/gateway/api/message.go (L82-88)
```go
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```
