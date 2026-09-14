### Title
Missing owner-authorization binding on `DeleteSecrets` requests allows deletion of another workflow owner's vault secrets - (File: core/capabilities/vault/gw_handler.go)

### Summary
The Vault gateway/node pipeline validates and stamps the *authorized* owner onto `ListSecretIdentifiersRequest` before executing it, but the equivalent stamp is missing for `DeleteSecretsRequest`. As a result, a caller who is only authorized (via the on-chain allowlist digest mechanism) to submit *some* request can specify an arbitrary `Owner` value inside the `Ids[]` array of a delete request, and that unvalidated, attacker-supplied owner is forwarded straight to `secretsService.DeleteSecrets`. This mirrors the reported analog: a caller-controlled identity field (`recipient` in the NFT case, `Owner` here) is trusted without being cross-checked against the actual authenticated identity, letting the caller act on behalf of / against a victim identity that never approved the operation.

### Finding Description
The shared gateway vault pipeline is documented as:
`ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits` [1](#0-0) 

For `DeleteSecrets`, `processDeleteSecretsRequest` only validates the *structure* of the identifiers (format, batch size, duplicates) via `ValidateDeleteSecretsRequest` — it never checks or rewrites the `Owner` field on each `Id` to match the authorized caller: [2](#0-1) 

`ValidateDeleteSecretsRequest` itself performs only structural checks (non-empty, batch size, alphanumeric identifier format) and never compares `id.Owner` to any authenticated identity: [3](#0-2) 

By contrast, the `List` path explicitly overwrites the client-supplied `Owner` with the value derived from the authorization result before it reaches the secrets service, preventing exactly this class of bug: [4](#0-3) 

The delete handler has no such override — it unmarshals the raw, attacker-supplied request and passes it directly to the backing service: [5](#0-4) 

Authorization itself (`AllowListBasedAuth.AuthorizeRequest`) only proves that the *exact request bytes* were pre-registered on-chain (as a digest) by some workflow owner using their own signer; nothing in that on-chain registration step constrains the *contents* of the request (i.e., which `Owner` values appear inside `Ids[]`) to be the registrant's own address: [6](#0-5) 

So a caller can legitimately register (under their own on-chain identity) an allowlisted digest for a `DeleteSecretsRequest` whose `Ids` array names a victim owner's secret identifiers, get `AuthorizeRequest` to succeed with `AuthorizedOwner()` equal to the attacker's own address, and have the unvalidated victim-owned `Ids` forwarded unchanged to `DeleteSecrets`.

This is structurally the same defect as the reported `transfer_nft` bug: a party-identifying field supplied by the caller (`recipient` there, `Owner` here) is not cross-validated against the entity that was actually authorized/paid/approved, allowing the caller to act against a third party who never consented.

### Impact Explanation
If `DeleteSecrets` does not perform any additional server-side ownership check beyond what's shown here, this allows an unprivileged workflow owner to delete another owner's Vault secrets (a destructive, hard-to-reverse action) purely by crafting request content — a cross-user authorization bypass on a security-sensitive secret-management surface. This is graded high because it breaks tenant isolation of the Vault subsystem, one of the internet/gateway-facing capabilities explicitly in scope.

### Likelihood Explanation
Exploitability requires only that the attacker be a legitimate (but otherwise unprivileged) workflow owner able to register an allowlist entry through the standard `WorkflowRegistry` flow — no elevated privilege is needed, and the missing check is a straightforward code-path gap (asymmetry between `List` and `Delete` handling), making this readily reachable. Confidence is not absolute because I could not verify (within the indexed/available code) whether `secretsService.DeleteSecrets`'s underlying implementation performs its own independent owner-authorization check that would neutralize this gap; the gateway/validator layer clearly does not.

### Recommendation
Mirror the `List` path: after authorization, overwrite/validate every `Id.Owner` in `DeleteSecretsRequest.Ids` (and, if applicable, `Create`/`Update` identifiers not already bound by the ciphertext label check) against `authResult.AuthorizedOwner()` before invoking `secretsService.DeleteSecrets`, rejecting the request if any identifier's owner does not match the authorized caller.

### Proof of Concept
Not independently executed; derived from static code-path analysis:
1. Attacker (owner `A`) crafts a `DeleteSecretsRequest` with `RequestId=X`, `Ids=[{Key:"k", Owner:"B", Namespace:"main"}]` (owner `B` is a victim).
2. Attacker registers this exact request's digest as allowlisted on-chain under their own signer/address `A` via the `WorkflowRegistry` (per `allow_list_based_auth.go` logic, nothing ties `Ids[].Owner` to the registrant).
3. Attacker sends the request to the gateway; `AuthorizeRequest` succeeds and returns `AuthorizedOwner()=A` [7](#0-6) .
4. `processDeleteSecretsRequest`/`handleSecretsDelete` forward the request untouched — including `Owner: "B"` — to `secretsService.DeleteSecrets` [5](#0-4) , deleting victim `B`'s secret.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-34)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
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

**File:** core/capabilities/vault/gw_handler.go (L338-349)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to list secret identifiers: %w", err))
	}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-76)
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

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```
