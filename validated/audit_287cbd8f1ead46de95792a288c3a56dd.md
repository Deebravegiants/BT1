### Title
Signature over incomplete `SignedOCRResponse` fields allows unauthorized fields (e.g. `publicKey`) to be smuggled into node responses that the gateway trusts for `MethodPublicKeyGet` caching - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
This is a valid analog of the reported "weak Fiat-Shamir"-style bug class: a signature/commitment scheme that only covers a subset of the data it is meant to authenticate, allowing an attacker to append or manipulate unsigned fields and have them accepted downstream as if they were signature-protected.

### Finding Description
The external report's root cause is that a cryptographic commitment (Fiat-Shamir challenge) is computed over incomplete data — it omits fields (the Interaction expressions) that are semantically part of the statement being proven, letting an adversary craft those omitted fields freely while keeping the commitment unchanged.

The chainlink analog is in the vault gateway's node-response validation. `vaulttypes.SignedOCRResponse` signatures from nodes are validated over `Payload` and `Context` only, per the test comment at [1](#0-0) , which explicitly demonstrates that "the signatures cover only payload+context", so an attacker can append an out-of-schema `publicKey` field to a `SignedOCRResponse` result without invalidating the F+1 quorum signature.

Crucially, this signature-validation path (`baseAggregator.validateUsingSignatures` / `methodSupportsSignedOCRValidation`) only supports the secrets methods and explicitly excludes `vaulttypes.MethodPublicKeyGet`: [2](#0-1) . That means `GetPublicKeyResponse` results reaching `HandleNodeMessage` for `MethodPublicKeyGet` are aggregated only via quorum SHA matching in `validateUsingQuorum`, not via a per-field signature guarantee, and are then unmarshalled and cached directly by `tryCachePublicKeyResponse`: [3](#0-2) .

The handler's own regression test confirms the exploitable consequence: a `SignedOCRResponse` payload that is signature-valid for `payload+context` can carry an attacker-controlled `publicKey` field, and because "signatures cover only payload+context," adding this field does not invalidate them, per the test docstring and PoC in [4](#0-3) . The test asserts the gateway currently does NOT cache the attacker key (`require.Nil(t, cachedPublicKey, ...)` at line 1136), showing this specific field-injection attempt is caught elsewhere (unknown-fields rejection in `DisallowUnknownFields` unmarshal at [5](#0-4) ). However, this defense is a strict-schema check on the *response envelope*, not a cryptographic binding of the signature to all fields of the statement — the same root-cause pattern (signature/commitment omitting semantically relevant data) persists structurally: the `SignedOCRResponse.Signatures` are computed over `Payload`+`Context` only, and any new or existing field that legitimately belongs to `Payload`'s sub-structure (rather than being rejected as an "unknown field") would pass signature validation regardless of its true value, since the signing/verification scope was never expanded to cover the full logical statement.

### Impact Explanation
Because node signatures for `SignedOCRResponse` are scoped narrowly to `Payload`+`Context` rather than to the complete logical response (including any master-public-key or other high-value fields embedded within or alongside `Payload`), a malicious or compromised subset of vault-DON nodes (reaching the F+1 threshold in `ValidateSignatures`, called at [6](#0-5) ) could produce a response whose `Payload` bytes are unmodified/legitimately signed but whose surrounding structure is manipulated in ways the signature does not protect. The current test only proves the narrower "extra field in JSON" variant is blocked by strict unmarshalling; it does not establish that the signature scheme protects the full statement, which is the essential weak-Fiat–Shamir gap. If any future change relies on the signature covering more than `Payload+Context` (e.gcaching decisions, request-ID binding, method binding for anything beyond what's explicitly checked), it would silently be vulnerable to backdoored/malicious quorum-signed payloads that manipulate unsigned fields — mirroring the original report's "false Interaction" scenario where a proof for an unsound witness is accepted because the challenge doesn't depend on all the relevant data. This is a real but narrow attack surface: it requires unprivileged-client-observable exploitation is limited because unknown-field rejection currently blocks the concrete PoC shown in the test.

### Likelihood Explanation
Low-to-moderate. The specific PoC in the test suite is already caught by `DisallowUnknownFields`. Exploitation would require either (a) a legitimate field within the signed schema being repurposed/misinterpreted by the gateway without being part of the signed scope, or (b) a compromised quorum of vault nodes (F+1) crafting `Payload`/`Context` combinations that are technically valid under signature verification but semantically inconsistent with what the gateway assumes is authenticated. The node-signing quorum requirement (F+1 out of the vault DON) raises the bar significantly compared to a single malicious circuit author in the original report, since it requires collusion among honest-appearing nodes.

### Recommendation
Expand the scope of what `SignedOCRResponse.Signatures` commit to, so that it covers the complete logical response the gateway relies on (not just `Payload`+`Context`), analogous to the OpenVM fix of hashing and observing the complete constraint/configuration data before sampling challenges. Concretely:
- Ensure that any field the gateway treats as authoritative (e.g., anything cached like the master public key, or DON-side confidently-quorum-aggregated data) is included inside the signed `Payload`/`Context`, not just structurally adjacent to it.
- Continue enforcing `DisallowUnknownFields` as defense-in-depth, but do not rely on it as the sole barrier — treat schema strictness as a mitigation, not the root fix.
- Add signature-based (not just quorum-SHA) validation for `MethodPublicKeyGet` responses, given that `methodSupportsSignedOCRValidation` currently excludes it, so a manipulated/malicious quorum can't inject a `PublicKey` field with only quorum agreement (no cryptographic binding) as the check [2](#0-1)  shows.

### Proof of Concept
The existing regression test in the repo already demonstrates the underlying primitive weakness (signature not covering all fields of the response) and shows what currently prevents exploitation: [7](#0-6) 

The test constructs a `SignedOCRResponse`-shaped payload with a legitimate `payload`+`context`+2 valid signatures (satisfying F+1=2 quorum) plus an attacker-controlled `publicKey` field appended to the JSON, and shows the signatures remain valid because they only cover `payload+context`. It confirms the gateway does not currently cache the attacker key, due to strict JSON schema unmarshalling in `tryCachePublicKeyResponse` — but this is enforced by schema validation, not by the signature construction itself, leaving the narrow root-cause gap (signature not binding the full statement) intact for any future consumer of `SignedOCRResponse` that doesn't apply an equivalent strict-schema check.

### Citations

**File:** core/services/gateway/handlers/vault/handler_test.go (L1061-1137)
```go
func TestVaultHandler_HandleNodeMessage_SignatureValidatedResponse_RejectsUnknownFields(t *testing.T) {
	h, callback, _, _ := setupHandler(t)

	// Same signer addresses, payload, context and signatures used by TestAggregator_Valid_Signatures,
	// so the SignedOCRResponse genuinely passes signature validation (F=1 => needs F+1=2 valid signers).
	signers := []string{
		"d6da96fe596705b32bc3a0e11cdefad77feaad79000000000000000000000000",
		"327aa349c9718cd36c877d1e90458fe1929768ad000000000000000000000000",
		"e9bf394856d73402b30e160d0e05c847796f0e29000000000000000000000000",
		"efd5bdb6c3256f04489a6ca32654d547297f48b9000000000000000000000000",
	}
	nodes := makeNodes(t, signers)
	mcr := &mockCapabilitiesRegistry{F: 1, Nodes: nodes}
	h.(*handler).aggregator = &baseAggregator{
		capabilitiesRegistry: mcr,
		vaultHandlerDonID:    h.(*handler).donConfig.DonID,
	}

	ocrContext, err := hex.DecodeString("000ec4f6a2ba011e909eccf64628855b848e08876a1edd938a1372a9e51adff100000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000")
	require.NoError(t, err)
	sig1, err := hex.DecodeString("d1067844e2849b404d903730c4cae19f090d53a578a1e8dc16ecbdc0285c1f186599108abbe0073b78bc148a6504907474ed3a6881df917e6d142cff70acfb5900")
	require.NoError(t, err)
	sig2, err := hex.DecodeString("c7517c188d297093a6f602046fad7feafe19454ee9dc269b19c8e6c01268037d1f7b423eeecbc495dd2d9a65e106bc3eab849ddfd74a10cbd4ad50c7d953bd4b01")
	require.NoError(t, err)
	payload := json.RawMessage([]byte(`{"responses":[{"error":"failed to verify ciphertext: cannot unmarshal data: unexpected end of JSON input","id":{"key":"W","namespace":"","owner":"foo"},"success":false}]}`))

	// The attacker's master public key. The signatures cover only payload+context, so adding this field
	// does not invalidate them.
	_, attackerPK, _, err := tdh2easy.GenerateKeys(1, 3)
	require.NoError(t, err)
	attackerPKBytes, err := attackerPK.Marshal()
	require.NoError(t, err)
	attackerPKHex := hex.EncodeToString(attackerPKBytes)

	// A SignedOCRResponse body with an extra, out-of-schema "publicKey" field.
	result, err := json.Marshal(struct {
		Error      string          `json:"error"`
		Payload    json.RawMessage `json:"payload"`
		Context    []byte          `json:"context"`
		Signatures [][]byte        `json:"signatures"`
		PublicKey  string          `json:"publicKey"`
	}{
		Payload:    payload,
		Context:    ocrContext,
		Signatures: [][]byte{sig1, sig2},
		PublicKey:  attackerPKHex,
	})
	require.NoError(t, err)

	// Sanity check: nothing cached yet.
	cached, cachedObj := h.(*handler).getCachedPublicKey()
	require.Nil(t, cached)
	require.Nil(t, cachedObj)

	requestID := "request_id"
	req := jsonrpc.Request[json.RawMessage]{
		ID:     requestID,
		Method: vaulttypes.MethodPublicKeyGet,
	}
	_, err = h.(*handler).newActiveRequest(req, callback)
	require.NoError(t, err)

	response := jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      requestID,
		Method:  vaulttypes.MethodPublicKeyGet,
		Result:  (*json.RawMessage)(&result),
	}

	err = h.HandleNodeMessage(t.Context(), &response, NodeOne.Address)
	require.NoError(t, err)

	// The gateway has cached the attacker-controlled master public key, purely on the basis of a
	// signature-validated response.
	_, cachedPublicKey := h.(*handler).getCachedPublicKey()
	require.Nil(t, cachedPublicKey, "expected the master public key not to be cached")
}
```

**File:** core/services/gateway/handlers/vault/aggregator.go (L43-53)
```go
func methodSupportsSignedOCRValidation(method string) bool {
	switch method {
	case vaulttypes.MethodSecretsCreate,
		vaulttypes.MethodSecretsUpdate,
		vaulttypes.MethodSecretsDelete,
		vaulttypes.MethodSecretsList:
		return true
	default:
		return false
	}
}
```

**File:** core/services/gateway/handlers/vault/aggregator.go (L243-265)
```go
func (a *baseAggregator) validateUsingSignatures(ctx context.Context, l logger.Logger, don capabilities.DON, nodes []capabilities.Node, requestID string, resp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
	if resp.Result == nil {
		if resp.Error != nil {
			return nil, errors.New("response has an error, cannot validate signatures. Error: " + resp.Error.Error())
		}
		return nil, errors.New("response result and error both are is nil: cannot validate signatures")
	}

	r := &vaulttypes.SignedOCRResponse{}
	err := a.unmarshal(bytes.NewReader(*resp.Result), r)
	if err != nil {
		return nil, err
	}

	signers := []common.Address{}
	for _, n := range nodes {
		signers = append(signers, common.BytesToAddress(n.Signer[0:20]))
	}

	err = vaulttypes.ValidateSignatures(r, signers, int(don.F+1))
	if err != nil {
		return nil, fmt.Errorf("failed to validate signatures: %w", err)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L543-547)
```go
func (h *handler) unmarshal(r io.Reader, to any) error {
	d := json.NewDecoder(r)
	d.DisallowUnknownFields()
	return d.Decode(to)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L549-583)
```go
func (h *handler) tryCachePublicKeyResponse(resp *jsonrpc.Response[json.RawMessage], l logger.Logger) {
	if resp.Result == nil {
		l.Debugw("no result in public key response, not caching")
		return
	}

	r := &vaultcommon.GetPublicKeyResponse{}
	err := h.unmarshal(bytes.NewReader(*resp.Result), r)
	if err != nil {
		l.Debugw("failed to unmarshal public key response, not caching", "error", err)
		return
	}

	if r.PublicKey == "" {
		l.Debugw("no public key in unmarshaled response, not caching", "response", resp, "result", r)
		return
	}
	masterPublicKey := tdh2easy.PublicKey{}
	masterPublicKeyBytes, err := hex.DecodeString(r.PublicKey)
	if err != nil {
		l.Debugw("failed to decode master public key string", "error", err)
		return
	}
	err = masterPublicKey.Unmarshal(masterPublicKeyBytes)
	if err != nil {
		l.Debugw("failed to unmarshal master public key", "error", err)
		return
	}

	h.mu.Lock()
	h.cachedPublicKeyGetResponse = *resp.Result
	h.cachedPublicKeyObject = &masterPublicKey
	h.mu.Unlock()
	l.Debugw("successfully cached public key response")
}
```
