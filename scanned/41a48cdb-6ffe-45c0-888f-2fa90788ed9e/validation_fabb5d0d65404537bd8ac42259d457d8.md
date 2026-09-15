Confirmed root cause: `Message.Validate()` at `core/services/gateway/api/message.go:54-88` calls `ExtractSigner()`, whose signature check (`ExtractSigner`, lines 124-134) recovers the signer from a hash that covers `MessageID | Method | DonID | Receiver | Payload` (`GetRawMessageBody`, lines 136-146). The signature therefore *is* cryptographically bound to the exact `Payload` bytes.

### Title
Signature-Payload Binding Bypass via Signature Reuse on Externally-Influenced HTTP Response - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handleWebAPIOutgoingMessage` in `core/services/gateway/handlers/capabilities/handler.go:164-236` builds a brand-new response `Message` (with a new `Payload` derived from an external HTTP call's status/headers/body) but reuses the *original request's* `Signature` field (`respMsg.Signature = msg.Signature`, line 223) instead of re-signing the new payload. This is conceptually the same bug class as the CVE: a value meant to cryptographically bind two ends of a channel (here, signature-to-payload; there, TLS-channel-binding-to-SCRAM-exchange) is copied/faked instead of freshly derived, defeating the integrity guarantee the receiver relies on.

### Finding Description
`sendHTTPMessageToClient` (`core/services/gateway/handlers/capabilities/handler.go:121-146`) constructs the outbound payload from an external HTTP response (`resp.StatusCode`, `resp.Headers`, `resp.Body`) that is not controlled by the gateway or the DON node — it is controlled by whatever server the workflow's `web_api_target`/`compute_action` request points to (an "unprivileged external initiator" in this flow: the third-party HTTP endpoint the node asked the gateway to call on its behalf).

Immediately after, `handleWebAPIOutgoingMessage` copies the *original* request's signature onto this new message:
```go
respMsg.Signature = msg.Signature
req, err := common.ValidatedRequestFromMessage(respMsg)
...
err = h.don.SendToNode(newCtx, nodeAddr, req)
```
`core/services/gateway/handlers/capabilities/handler.go:216-223`

But per `Message.Sign`/`ExtractSigner` (`core/services/gateway/api/message.go:90-134`), a valid signature is defined as one whose recovered signer matches over `MessageID | Method | DonID | Receiver | Payload`. Since `Payload` here is the new, externally-derived response body/headers/status rather than the original request payload the signature was computed over, `msg.Signature` no longer authenticates `respMsg.Body`. Any downstream code path that calls `Message.Validate()`/`ExtractSigner()` on this response to derive `Sender` (as `ValidatedMessageFromResp` does, `core/services/gateway/handlers/common/message_util.go:14-32`) will recover a *stale* signer address that has no cryptographic relationship to the actual (externally influenced) payload being delivered — the equivalent of "faking" the binding between the message and its claimed origin.

The comment in the code (lines 216-222) rationalizes this by invoking a trust model ("Gateway is trusted", "DON-side/Gateway-side allowlist + TLS secure the channel"), which is exactly analogous to the CVE's precondition ("attacker must be positioned between Dovecot and client") — the mitigation described relies on network/transport trust rather than the message-level signature actually protecting anything, while the code path still presents the signature as if it authenticates the payload.

### Impact Explanation
If any node-side or downstream consumer of this message (or any future/derived handler) trusts `ExtractSigner()`/`Validate()` on this response to establish provenance of the payload (as the codebase does elsewhere, e.g. `ValidatedMessageFromResp`), it will attribute externally-supplied HTTP response content to the original signer's identity, since the signature check will "pass" for stale-but-valid bytes yet not actually bind to the new payload. This creates cross-content confusion: a signature that was valid for request A is presented as proof-of-origin for unrelated response content B, undermining message integrity guarantees the signature scheme is meant to provide.

### Likelihood Explanation
Likelihood is bounded by the trust model comment: this is only "safe" as long as (a) the Gateway itself is trusted and (b) DON↔Gateway is allowlisted/TLS. The finding is best framed as a defense-in-depth / message-integrity design flaw rather than a directly remotely exploitable authentication bypass by an anonymous internet client, since triggering it still requires an in-scope, already-permitted node/gateway flow (`web_api_target`), and the actual attack requires influencing the external HTTP response (something the calling workflow controls anyway). This weakens confidence that it maps to a "concrete authentication or role bypass" as strictly as the Rules request.

### Recommendation
Re-sign `respMsg` with the gateway's own key (as done elsewhere via `Message.Sign`/`SignKS`) before sending to the node, rather than reusing `msg.Signature`. This ensures the signature always covers the actual `Payload` bytes being delivered, preserving the invariant that `ExtractSigner()` yields the true origin of the content.

### Proof of Concept
1. A workflow/node capability issues a `web_api_target` request through the gateway, which is validly signed by the node.
2. The gateway calls `httpClient.Send` against the target URL and receives an attacker/third-party-controlled HTTP response (status/body/headers).
3. `sendHTTPMessageToClient` builds a new `Payload` from this response.
4. `handleWebAPIOutgoingMessage` copies `msg.Signature` (valid only for the original request payload) onto the new message and forwards it to the node via `h.don.SendToNode`.
5. Any code that calls `respMsg.Validate()`/`ExtractSigner()` on this forwarded message recovers the original signer's address even though the payload bytes differ from what was actually signed — demonstrating the signature no longer authenticates content, exactly mirroring the CVE's "faked channel binding" bug class. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L121-146)
```go
func (h *handler) sendHTTPMessageToClient(ctx context.Context, req network.HTTPRequest, msg *api.Message) (*api.Message, error) {
	var payload Response
	resp, err := h.httpClient.Send(ctx, req)
	if err != nil {
		return nil, err
	}
	payload = Response{
		ExecutionError: false,
		StatusCode:     resp.StatusCode,
		Headers:        resp.Headers,
		Body:           resp.Body,
	}
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	return &api.Message{
		Body: api.MessageBody{
			MessageID: msg.Body.MessageID,
			Method:    msg.Body.Method,
			DonID:     msg.Body.DonID,
			Payload:   payloadBytes,
		},
	}, nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L216-223)
```go
		// Work around the fact that the connection manager expects all messages
		// to have a valid signature by reusing the signature that came with the message.
		// This is OK to do because:
		// - our trust model for Gateways assumes that we can trust the Gateway node. This is a central assumption since
		// the Gateway node has access to plaintext secrets sent by DON nodes.
		// - the connection between the Gateway and DON Node is already authorized via a DON-side and Gateway-side
		// allowlist, and secured via TLS.
		respMsg.Signature = msg.Signature
```

**File:** core/services/gateway/api/message.go (L90-134)
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

func (m *Message) SignKS(ctx context.Context, ks keys.MessageSigner, signer common.Address) error {
	if m == nil {
		return errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signature, err := ks.SignMessage(ctx, signer, gw_common.Flatten(rawData...))
	if err != nil {
		return err
	}
	m.Signature = utils.StringToHex(string(signature))
	m.Body.Sender = strings.ToLower(signer.Hex())
	return nil
}

func (m *Message) ExtractSigner() (signerAddress []byte, err error) {
	if m == nil {
		return nil, errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signatureBytes, err := hex.DecodeString(m.Signature)
	if err != nil {
		return nil, err
	}
	return gw_common.ExtractSigner(signatureBytes, rawData...)
}
```

**File:** core/services/gateway/handlers/common/message_util.go (L14-32)
```go
func ValidatedMessageFromResp(resp *jsonrpc.Response[json.RawMessage]) (*api.Message, error) {
	if resp.Error != nil {
		return nil, fmt.Errorf("received error, ID: %s", resp.ID)
	}
	if resp.Result == nil {
		return nil, fmt.Errorf("response result is nil, ID: %s", resp.ID)
	}
	var msg api.Message
	err := json.Unmarshal(*resp.Result, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = resp.ID
	err = msg.Validate()
	if err != nil {
		return nil, err
	}
	return &msg, nil
}
```
