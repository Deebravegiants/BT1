### Title
Missing validation of user-supplied JSON-RPC request ID allows injection of the internal owner/request-ID separator (`::`) in the Vault gateway pipeline - ([File: core/capabilities/vault/gateway_vault_request_processor.go])

### Summary
The Vault gateway request pipeline concatenates an internally-derived, trusted `authorizedOwner` with an attacker-controlled `req.ID` (or `RequestId` param) using a fixed separator string `"::"` to build a "prefixed request ID" that is used as a map key, forwarded to DON nodes, and echoed back in JSON-RPC responses. Like the `header_field_name`/colon issue in the external report, this code never validates that the untrusted, attacker-supplied component does not itself contain the separator, so the two logically distinct fields (owner, request id) are not reliably delimited.

### Finding Description
`RequestIDSeparator = "::"` is defined as the delimiter between an owner and a user-supplied request ID [1](#0-0) .

In `authorizeAndStamp`, the code builds `prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID`, where `originalRequestID` is `req.ID`, i.e., attacker-controlled input that is never checked for embedded `"::"` sequences before concatenation [2](#0-1) . The only bound placed on `req.ID` upstream is a length check (`<= 200` chars) in `HandleJSONRPCUserMessage`; there is no character-set or separator validation [3](#0-2) .

Downstream, the composite ID is later split back apart using only the *first* occurrence of the separator:
- `stripPrefixedVaultRequestID` uses `strings.Cut` on the first `"::"` [4](#0-3) .
- `sendSuccessResponse` and `errorResponse` in the gateway-side vault handler strip everything up to the first `"::"` via `strings.Index` before returning the ID to the user [5](#0-4) [6](#0-5) .

Because splitting always happens on the *first* separator instance, and the untrusted user-supplied ID portion is never rejected for containing `"::"`, a user can submit a request ID such as `"someOwner::realID"`. This does not simply get treated as an opaque string end-to-end: it changes the shape of the value that is later parsed with "split on first occurrence" logic in multiple independent code paths (gateway response stripping, node-side envelope re-authorization stripping). This is exactly the pattern flagged in the external report — trusting an untrusted field to not contain the delimiter that a downstream parser uses to reconstruct structured meaning from a flat string.

The report also notes it is "sufficient" to assert the untrusted component doesn't contain the delimiter, but recommends validating the full allowed character set defensively rather than relying on"if the signer/producer is well-behaved" assumptions — here, there is no defensive validation of `req.ID` (or `RequestId` param) content at all, only a length cap.

### Impact Explanation
The blast radius of this specific instance is currently constrained by the fact that `authorizedOwner` (the first component in the concatenation) is always the trusted/derived value, not attacker controlled, and the "strip first occurrence" operations are all performed on the composite string where the trusted owner is guaranteed to be the leftmost segment. I could not find a concrete path in the code reachable in this session where a low-privilege user can leverage the missing separator validation to forge another owner's prefix, desynchronize the `activeRequests` map keyed by full prefixed ID, or read another user's secrets — the request authorization itself (`AuthorizeRequest`) is independent of the ID content. The main confirmed effect is that the request ID string returned to the client, or logged (`incomingOwner` extracted for logging only) can contain misleading embedded `"::"` sequences that don't correspond to real owner boundaries, and JSON-RPC ID echoing/stripping logic operates on attacker-shaped strings rather than a validated opaque token.

### Likelihood Explanation
Any unprivileged, already-authenticated Vault gateway client can trivially set `Request.ID` or the `request_id` field in a create/update/delete/list payload to include `"::"`, since there is no rejection of this pattern anywhere in `HandleJSONRPCUserMessage` or the various `process*Request` functions in `gateway_vault_request_processor.go`. This makes the precondition to trigger the anomalous string handling trivially reachable.

### Recommendation
Explicitly validate that user-supplied request IDs (`jsonrpc.Request.ID` and the `RequestId` field inside Vault method params) do not contain the `vaulttypes.RequestIDSeparator` string (`"::"`) before it is used in `authorizeAndStamp`, `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest` in `core/capabilities/vault/gateway_vault_request_processor.go`. Reject such requests with an `InvalidVaultParamsError` rather than silently concatenating and later relying on "split on first occurrence" logic to recover structure.

### Proof of Concept
Not applicable as a demonstrated exploit in this session — I was unable to trace a concrete, reachable authorization/secret-disclosure bypass from this missing validation within the code available, only the structural analog to the reported bug class (trusting an untrusted, delimiter-containing field). A conclusive proof-of-concept (e.g., showing map-key collision in `activeRequests`, or cross-owner response leakage) would require running the gateway/node pipeline end-to-end, which is beyond what could be verified via static code review alone.

### Citations

**File:** core/capabilities/vault/vaulttypes/types.go (L34-35)
```go
	// RequestIDSeparator is used to separate parts(owner, user-provided-requestId) of the request ID.
	RequestIDSeparator = "::"
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-286)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

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

**File:** core/services/gateway/handlers/vault/handler.go (L394-401)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
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
