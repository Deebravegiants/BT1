### Title
Delete-secrets path trusts client-supplied `Owner` instead of enforcing the authenticated caller's authorized owner - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault gateway handler's `MethodSecretsList` path rewrites the client-supplied `Owner` field with the value derived from the authorization result before querying the secrets service, but the `MethodSecretsDelete` path does not perform the equivalent enforcement, so the identifiers actually deleted are taken verbatim from client-controlled request params rather than being pinned to the authenticated/authorized owner.

### Finding Description
In `handleSecretsList`, after authorization succeeds, the handler explicitly overwrites the owner scope with the value derived from `AuthResult` before calling the secrets service: [1](#0-0) 

By contrast, `handleSecretsDelete` unmarshals the client-supplied `DeleteSecretsRequest` (which contains a list of `SecretIdentifier{Key, Namespace, Owner}` entries) and passes it straight to `secretsService.DeleteSecrets` with no rewrite or cross-check of the per-identifier `Owner` field against the authorized owner: [2](#0-1) 

The same asymmetry exists one layer up, in the shared pipeline (`GatewayVaultRequestProcessor`). `processListSecretIdentifiersRequest` at least validates the request via `ValidateListSecretIdentifiersRequest`, which requires `request.Owner` to be non-empty and well-formed, but nothing in `processDeleteSecretsRequest` ties `deleteReq.Ids[*].Owner` to `authResult.AuthorizedOwner()`: [3](#0-2) 

`RequestValidator.ValidateDeleteSecretsRequest` only checks structural/length constraints on each identifier's `Key`/`Owner`/`Namespace` via `ValidateSecretIdentifier` — it never compares the identifier's `Owner` to the caller's authorized identity: [4](#0-3) 

The on-chain allowlist path (`allowListBasedAuth.AuthorizeRequest`) binds authorization to a digest of the *entire* request bytes, so for that specific authorizer a tampered `Owner` field would produce a different digest and fail allowlist lookup: [5](#0-4) 

However, `NewGatewayHandler` also wires in an optional JWT-based authorizer (`Auth0Config`/`jwtBasedAuth`) that is combined with the allowlist authorizer via `NewAuthorizer`: [6](#0-5) 

I was not able to fully inspect the JWT-based authorizer's `AuthorizeRequest` implementation (its source file was not retrieved before the iteration budget ran out), so I cannot confirm from code whether that path also binds authorization to the full request digest (as the allowlist path does) or whether it authorizes based only on JWT claims (e.g., the caller's own owner/org) independent of the specific `Ids[*].Owner` values requested for deletion. If the JWT path authorizes by identity/claims alone (which is the more typical design for bearer-token auth, and is consistent with why `handleSecretsList` needs to explicitly override `Owner` with `authResult.AuthorizedOwner()` — precisely because the authorizer for that path does not itself constrain the payload's owner field), then the missing analogous override in the delete path would let an authenticated-but-unprivileged caller (valid JWT for owner A) submit a `DeleteSecretsRequest` naming another owner `B` in `Ids[*].Owner` and have owner B's secrets deleted.

### Impact Explanation
If the JWT authorization path does not itself bind the authorized identity to the specific target `Owner` in the payload (as strongly suggested by the fact that `handleSecretsList` needs an explicit override to prevent exactly this), any authenticated Vault client could delete another workflow owner's secrets (e.g., API keys, private keys used by other workflows) by supplying an arbitrary `Owner` in `DeleteSecretsRequest.Ids`. This is a direct analog to the Roll incident's root cause — insufficiently scoped authority over sensitive assets held on behalf of multiple parties — manifesting here as a potential cross-tenant secret-deletion / denial-of-service and integrity issue rather than a hot-wallet key leak.

### Likelihood Explanation
Likelihood is **uncertain** and depends entirely on the internal behavior of the JWT-based authorizer, which I could not verify with the available context/tools (file not retrieved). If the JWT authorizer only validates token validity/rate limits and derives `AuthorizedOwner()` from claims without cross-checking it against `deleteReq.Ids[*].Owner`, the bug is directly and trivially reachable by any authenticated (non-privileged) client. If the JWT authorizer independently enforces per-identifier ownership (mirroring what `ValidateDeleteSecretsRequest` conspicuously does not do), the issue would not be exploitable via this specific path.

### Recommendation
Regardless of the JWT authorizer's internal behavior, defense-in-depth argues for making `processDeleteSecretsRequest` (or `handleSecretsDelete`) explicitly enforce that every `Ids[*].Owner` in a `DeleteSecretsRequest` equals `authResult.AuthorizedOwner()` before calling `secretsService.DeleteSecrets`, exactly as `handleSecretsList` already does for `ListSecretIdentifiersRequest.Owner`. This removes any authorizer-implementation-dependent trust in client-supplied ownership data for a destructive operation.

### Proof of Concept
Conceptual PoC (cannot be fully confirmed without the JWT authorizer's source):
1. Obtain a valid JWT/API credential scoped to owner `A` for the Vault gateway.
2. Submit a `MethodSecretsDelete` JSON-RPC request through the gateway with `Ids: [{Key: "victim-secret", Namespace: "default", Owner: "B"}]`.
3. If the configured authorizer (JWT path) authorizes based on caller identity/claims without validating that the payload's target `Owner` matches the caller, `GatewayVaultRequestProcessor.processDeleteSecretsRequest` → `RequestValidator.ValidateDeleteSecretsRequest` will accept the request (only format/length checks), and `GatewayHandler.handleSecretsDelete` will forward it unmodified to `secretsService.DeleteSecrets`, deleting owner `B`'s secret despite the caller only being authorized as owner `A`.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L93-111)
```go
	var jwtAuthService services.Service
	var jwtBasedAuth Authorizer
	if auth0 != nil {
		var err error
		jwtAuthService, err = NewJWTBasedAuth(JWTBasedAuthConfig{
			IssuerURL: auth0.IssuerURL,
			Audience:  auth0.Audience,
			TenantID:  auth0.TenantID,
		}, limitsFactory, lggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create JWTBasedAuth: %w", err)
		}
		jwtBasedAuth = jwtAuthService.(Authorizer)
	}

	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
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

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-68)
```go
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
```
