### Title
Missing owner-scoping enforcement on Vault `SecretsDelete` allows cross-tenant secret deletion - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault gateway/node handler enforces that a caller's authorized owner overwrites the client-supplied `Owner` field for `SecretsList` requests, but performs no equivalent enforcement for `SecretsDelete` requests. `DeleteSecretsRequest.Ids[].Owner` values supplied by the caller are passed straight through to `secretsService.DeleteSecrets` without ever being checked or overwritten against the authenticated caller's `AuthResult.AuthorizedOwner()`.

### Finding Description
`handleSecretsList` explicitly forces the owner field to the authenticated identity after authorization: [1](#0-0) 

`handleSecretsDelete`, by contrast, unmarshals `DeleteSecretsRequest` directly from client-controlled `req.Params` and calls `DeleteSecrets` with it verbatim — no line forces `deleteReq.Ids[].Owner` to equal the authorized owner: [2](#0-1) 

The pre-authorization structural validator for delete requests, `ValidateDeleteSecretsRequest`, only checks that each `Id.Owner` is syntactically well-formed (alphanumeric, within length limits) — it never compares `id.Owner` to the caller's authenticated identity: [3](#0-2) 

The shared pipeline in `GatewayVaultRequestProcessor.processDeleteSecretsRequest` / `authorizeAndStamp` only validates structure, runs `AuthorizeRequest` (a digest-based allowlist check against the caller's own registered request), and stamps the request ID — it never rewrites or cross-checks the `Owner` fields embedded inside `DeleteSecretsRequest.Ids`, unlike the write-path (`Create`/`Update`) where the encrypted-secret's TDH2 ciphertext label is cryptographically bound to `Id.Owner` via `EnsureRightLabelOnSecret`: [4](#0-3) [5](#0-4) 

The `AuthorizeRequest` implementation only checks that the digest of the entire raw request matches an entry allowlisted by the workflow registry syncer for some owner — it does not decode/validate `Ids[].Owner` inside the payload against that owner: [6](#0-5) 

Because the caller who registers/allowlists their own workflow's request digest controls the exact byte content of that request (including arbitrary `Owner` strings inside `Ids`), a caller authorized only for their own tenant identity can craft a `DeleteSecretsRequest` whose `Ids` array names a different (victim) tenant's `Owner`, register/allowlist that exact request for themselves, and have it accepted and executed by `secretsService.DeleteSecrets` — deleting another tenant's secrets. This mirrors the GFA-token root cause: a caller-reachable, unprivileged-facing function (`SecretsDelete`) lacks access-control enforcement binding the operation's target scope (`Owner`) to the caller's authenticated identity, unlike the sibling `SecretsList` path which does enforce this binding.

### Impact Explanation
If exploitable, this allows an unprivileged Vault client (one CRE workflow owner/tenant) to delete another tenant's secrets, resulting in unauthorized destruction of another user's stored assets (secrets) — a direct cross-tenant integrity/availability violation on the internet-facing gateway/node Vault path, analogous to unauthorized fund/asset manipulation.

### Likelihood Explanation
Likelihood depends on whether the digest-based `AuthorizeRequest` allowlist mechanism (workflow-registry-driven) can be satisfied by a caller for a request whose payload references another tenant's `Owner` value. The code shows no explicit check preventing this at the JSON-RPC/gateway/node handler layer for delete requests specifically (in contrast to the defensive `Owner` override present for list requests), which is a code-level asymmetry that increases likelihood, though full exploitability depends on constraints of the on-chain workflow-registry allowlist registration process that were not fully visible in the indexed code.

### Recommendation
- In `handleSecretsDelete` (and in `GatewayVaultRequestProcessor.processDeleteSecretsRequest`), enforce that every `Ids[].Owner` in the parsed `DeleteSecretsRequest` equals `authResult.AuthorizedOwner()` before calling `secretsService.DeleteSecrets`, mirroring the explicit override done in `handleSecretsList`.
- Add an equivalent check to `RequestValidator.ValidateDeleteSecretsRequest` (or a post-authorization validator) so structural validation also asserts owner-scoping consistency, not just syntactic well-formedness.

### Proof of Concept
Conceptual (not verified end-to-end against the workflow-registry allowlist internals):
1. Tenant A registers/allowlists (via the workflow registry syncer flow) a `SecretsDelete` JSON-RPC request whose `Ids` array specifies `Owner: "tenantB"` instead of Tenant A's own owner identity.
2. Tenant A sends this request through the gateway to `GatewayHandler.HandleGatewayMessage`.
3. `AuthorizeRequest` succeeds because the raw request digest matches Tenant A's own allowlisted digest entry; `AuthResult.AuthorizedOwner()` returns "tenantA" but the actual deletion targets `Ids[].Owner == "tenantB"`, since neither `handleSecretsDelete` nor the pre-auth validator enforces owner-scoping equality.
4. `secretsService.DeleteSecrets` deletes Tenant B's secrets.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L313-336)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&resultBytes),
	}
}
```

**File:** core/capabilities/vault/gw_handler.go (L338-346)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
```

**File:** core/capabilities/vault/validator.go (L221-252)
```go
func (r *RequestValidator) ValidateDeleteSecretsRequest(ctx context.Context, request *vaultcommon.DeleteSecretsRequest) error {
	if request.RequestId == "" {
		return errors.New("request ID must not be empty")
	}
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, len(request.Ids)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("request batch size exceeds maximum of %d: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check request batch size limit: %w", err)
	}
	if len(request.Ids) == 0 {
		return errors.New("request batch must contain at least 1 item")
	}

	uniqueIDs := map[string]bool{}
	for idx, id := range request.Ids {
		if id == nil {
			return errors.New("secret ID must not be nil at index " + strconv.Itoa(idx))
		}
		if err := r.ValidateSecretIdentifier(ctx, id.Key, id.Owner, id.Namespace); err != nil {
			return fmt.Errorf("invalid secret identifier at index %d: %w", idx, err)
		}

		_, ok := uniqueIDs[vaulttypes.KeyFor(id)]
		if ok {
			return errors.New("duplicate secret ID found at index " + strconv.Itoa(idx) + ": " + id.String())
		}

		uniqueIDs[vaulttypes.KeyFor(id)] = true
	}
	return nil
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-224)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var deleteReq vaultcommon.DeleteSecretsRequest
	if err := json.Unmarshal(*req.Params, &deleteReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
	if p.stripOwnerPrefixForAuth {
		deleteReq.RequestId = req.ID
		if err := marshalVaultParams(req, &deleteReq); err != nil {
			return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
		}
	} else {
		deleteReq.RequestId = coalesceRequestID(deleteReq.RequestId, req.ID)
	}

	if err := p.validator.ValidateDeleteSecretsRequest(ctx, &deleteReq); err != nil {
		return nil, p.validationError(req, err)
	}

	return p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		deleteReq.RequestId = prefixedRequestID
		vaultutils.ApplySecretIdentifierNamespaceDefaults(deleteReq.Ids)
		return marshalVaultParams(req, &deleteReq)
	})
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-293)
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

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-62)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}
```
