Based on my investigation, I found a genuine analog to the RLP length-vs-decoding inconsistency bug in the vault gateway's owner-prefixed request ID handling.

### Title
Inconsistent parsing of owner-prefixed request IDs (`strings.Cut` vs `strings.Index`+hardcoded offset) enables request ID / owner confusion - ([File: core/capabilities/vault/gateway_vault_request_processor.go])

### Summary
`RequestIDSeparator = "::"` is used to build a composite ID `authorizedOwner + "::" + userRequestID` after authorization [1](#0-0) . This composite ID is later parsed back apart in at least three different places using two different algorithms: one uses `strings.Cut` (first-occurrence split, keeping everything after the first separator as the "original ID") and the others use `strings.Index` plus a hardcoded `+2` offset to strip the prefix before sending the response to the user.

### Finding Description
The gateway builds the prefixed ID in `authorizeAndStamp` as `authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID`, where `originalRequestID` is the user-supplied JSON-RPC request `ID` — an attacker-controlled string that is not validated to exclude the `"::"` sequence before this point [2](#0-1) .

On the node side (`stripOwnerPrefixForAuth` mode), the reverse operation `stripPrefixedVaultRequestID` uses `strings.Cut`, which splits at the **first** occurrence of `"::"`: [3](#0-2) 

Meanwhile, the gateway-side response-encoding paths (`sendSuccessResponse` and `errorResponse` in the vault handler) strip the prefix using `strings.Index` plus a **hardcoded `+2`** offset — implicitly assuming the separator is exactly 2 characters and that only the first `"::"` is meaningful: [4](#0-3) [5](#0-4) 

Both of these implementations agree on where the *first* `"::"` is, but if the user-supplied `originalRequestID` itself contains additional `"::"` sequences, the two ends of the pipeline can disagree on what constitutes the "user ID" portion vs. the "owner" portion in different contexts. For example, `incomingOwner` extraction for logging in `authorizeAndStamp` also uses `strings.Index` (first occurrence) purely for diagnostics [6](#0-5) , but is never used to reject or canonicalize an ID that already embeds a separator before the owner prefix is added. Because the check for "does this ID already contain the separator" is absent prior to stamping, a malicious client can submit a request ID such as `attacker-owner::victim-id`. After authorization, the gateway will produce `authorizedOwner::attacker-owner::victim-id`. Depending on which stripping routine downstream code uses (`Cut`-based first-split vs. `Index`+`+2`-based first-split), the "user-visible" ID recovered can diverge from what the authorizing owner actually intended, and it is also echoed into `vaultcommon.*Request.RequestId` fields that get compared/logged/matched by callers (e.g., `req.RequestId == "0xabc"+vaulttypes.RequestIDSeparator+"1"` assertions throughout the tests) [7](#0-6) .

This mirrors the RLP bug class precisely: one code path (`RLPInput`, full decode) and another code path (`RlpUtils`, length-only decode) implement the *same* logical operation (parsing length/offsets of untrusted input) with different algorithms that silently diverge on malformed/adversarial input, instead of using one canonical implementation or rejecting non-canonical input up front.

### Impact Explanation
If the two ID-parsing algorithms disagree on adversarial input (an ID that embeds extra `"::"` sequences), this can result in:
- Response ID / request ID mismatch returned to callers, breaking the JSON-RPC 2.0 "response ID must match request ID" invariant that the code explicitly tries to preserve (see comments at `handler.go:586-587` and `handler.go:785-786`).
- Potential confusion of which `RequestId` an operation stores/matches against, since the same string is echoed into `vaultcommon.CreateSecretsRequest.RequestId` / `ListSecretIdentifiersRequest.RequestId`, etc., which are compared elsewhere by exact string equality.
- Because these IDs are also part of the OCR-signed payload (`vaultutils.SignedPayloadRequestID`) that downstream code strips using the same `"::"`-suffix convention [8](#0-7) , any place that assumes a single well-defined owner-prefix boundary could mis-attribute a response to the wrong logical request if an attacker engineers a colliding ID.

### Likelihood Explanation
Low-to-moderate. The user-controlled `req.ID` field is never validated to reject embedded `"::"` sequences before the owner prefix is appended, so an unprivileged client can trivially construct a colliding request ID. However, actual exploitation depends on how strictly other components validate the round-tripped `RequestId`/response `ID` (e.g., some tests do exact-match assertions like `req.ID == "0xDef"+vaulttypes.RequestIDSeparator+"1"`, which would break/behave unexpectedly under a crafted `"::"`-laden ID), and I could not fully confirm a concrete, demonstrable request/response impersonation or fund-movement scenario within the code available to the index — only a structural, provable data-validation inconsistency between two ID-parsing implementations.

### Recommendation
- Reject any user-supplied request ID that already contains `vaulttypes.RequestIDSeparator` before stamping the owner prefix (fail closed rather than allow ambiguous IDs).
- Replace the hardcoded `+2` offset in `handler.go` (`sendSuccessResponse`, `errorResponse`) with a call to the same canonical helper (`stripPrefixedVaultRequestID`, or equivalently use `len(vaulttypes.RequestIDSeparator)` instead of the literal `2`) so there is a single implementation of the strip/prefix logic used everywhere.
- Add unit tests asserting behavior when the user-supplied ID contains the separator string, matching the reported bug's recommendation to add explicit tests for edge/adversarial length-parsing cases.

### Proof of Concept
1. Send a vault JSON-RPC request (e.g., `vault.secrets.list`) with `ID = "evil::victim-id"` and valid auth for owner `0xabc`.
2. The gateway's `authorizeAndStamp` computes `prefixedRequestID = "0xabc::evil::victim-id"` and stamps this into `ListSecretIdentifiersRequest.RequestId` and `req.ID` [9](#0-8) .
3. On the response path, `sendSuccessResponse`/`errorResponse` strip using `strings.Index` (first `"::"`) + `+2`, yielding `"evil::victim-id"` as the "user" response ID — not `"victim-id"` — while other logic using `strings.Cut`-based `stripPrefixedVaultRequestID` (used in `stripOwnerPrefixForAuth` node mode) would instead yield `prefixedOwner = "0xabc"`, `originalRequestID = "evil::victim-id"` too (since `Cut` also finds only the first occurrence) — demonstrating that neither implementation canonicalizes multi-separator IDs, and no code path currently rejects them as invalid, leaving the "true" user-supplied ID ambiguous across the codebase's several ID-recovery implementations.

### Citations

**File:** core/capabilities/vault/vaulttypes/types.go (L34-35)
```go
	// RequestIDSeparator is used to separate parts(owner, user-provided-requestId) of the request ID.
	RequestIDSeparator = "::"
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L265-268)
```go
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-286)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L305-311)
```go
func stripPrefixedVaultRequestID(requestID string) (originalRequestID, prefixedOwner string) {
	prefixedOwner, originalRequestID, ok := strings.Cut(requestID, vaulttypes.RequestIDSeparator)
	if !ok {
		return requestID, ""
	}
	return originalRequestID, prefixedOwner
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L585-591)
```go
func (h *handler) sendSuccessResponse(ctx context.Context, l logger.Logger, ar *activeRequest, resp *jsonrpc.Response[json.RawMessage]) error {
	// Strip the owner prefix from the response ID before sending it back to the user
	// This ensures compliance with JSONRPC 2.0 spec, which requires response id to match request id
	index := strings.Index(resp.ID, vaulttypes.RequestIDSeparator)
	if index != -1 {
		resp.ID = resp.ID[index+2:]
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L785-790)
```go
	// Strip the owner prefix from the json response ID before sending it back to the user
	// This ensures compliance with JSONRPC 2.0 spec, which requires response id to match request id
	index := strings.Index(req.ID, vaulttypes.RequestIDSeparator)
	if index != -1 {
		req.ID = req.ID[index+2:]
	}
```

**File:** core/capabilities/vault/gw_handler_test.go (L480-482)
```go
				ss.EXPECT().CreateSecrets(mock.Anything, mock.MatchedBy(func(req *vaultcommon.CreateSecretsRequest) bool {
					return req.RequestId == "0xabc"+vaulttypes.RequestIDSeparator+"1"
				})).Return(&vaulttypes.Response{ID: "test_secret"}, nil)
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L519-536)
```go
// requireSignedPayloadRequestID asserts the vault OCR signed payload carries the gateway
// request ID inside the signed bytes. The gateway prefixes authorizedOwner to the user
// request ID (owner::requestID) before forwarding to the vault DON; OCR signs that value.
// JSON-RPC response ID is stripped back to the user request ID and is not signature-covered.
func requireSignedPayloadRequestID(t *testing.T, method, userRequestID, authorizedOwner string, payload json.RawMessage) {
	t.Helper()

	require.NotEmpty(t, userRequestID)
	require.NotEmpty(t, payload)

	signedRequestID, err := vaultutils.SignedPayloadRequestID(method, payload)
	require.NoError(t, err)
	require.NotEmpty(t, signedRequestID, "signed payload requestId should not be empty")

	expectedSuffix := vaulttypes.RequestIDSeparator + userRequestID
	require.True(t, strings.HasSuffix(signedRequestID, expectedSuffix),
		"signed payload requestId %q should end with gateway user request ID suffix %q", signedRequestID, expectedSuffix)

```
