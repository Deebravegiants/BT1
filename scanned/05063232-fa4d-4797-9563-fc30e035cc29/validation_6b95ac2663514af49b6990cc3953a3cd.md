This is well-mitigated code — the codebase explicitly guards against the exact bug class the CVE describes (unauthenticated/pre-auth resource exhaustion via unbounded tenant creation), with dedicated regression tests (`TestGatewayVaultRequestProcessor_ProcessRequest_UnauthorizedWriteNeverTouchesCiphertextLimiter`) proving the fix. The `ValidateSecretIdentifier` function, however, does check `MaxIdentifierOwnerLengthLimiter` (an owner-scoped limiter) using the unauthenticated `idOwner` from the request *before* authorization occurs in `validateWriteRequest`, which itself is called from `ValidateEncryptedSecretsStructure`, i.e., pre-auth.### Title
Unbounded per-owner limiter tenant creation before authorization in Vault secret-identifier validation - ([File: core/capabilities/vault/validator.go])

### Summary
`RequestValidator.ValidateSecretIdentifier` checks the `Owner`, `Key`, and `Namespace` fields of every incoming Vault secret identifier against owner-scoped `BoundLimiter`s (`MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierKeyLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`) *before* the request has been authorized. This is the exact bug class the codebase already fixed for the ciphertext-size limiter (`MaxCiphertextLengthLimiter`) — but the fix was not applied here, leaving a pre-auth path that can register unbounded per-owner limiter tenants, analogous to the "authenticated endpoint that can render the server unresponsive" class described in CVE-2024-47217.

### Finding Description
The codebase's own comments document a known hazard: checking an owner-scoped `limits.BoundLimiter` (constructed via `limits.MakeUpperBoundLimiter`) registers a persistent per-owner tenant with a background updater goroutine, so consulting it before request authorization "would let unauthenticated callers create unbounded limiter tenants" [1](#0-0) .

To fix this for the ciphertext-size check, the code deliberately splits validation into `ValidateEncryptedSecretsStructure` (pre-auth, skips the owner-scoped size check) and `ValidateCiphertextSizes` (post-auth, only called with the *authorized* owner) [2](#0-1) [3](#0-2) .

However, `ValidateSecretIdentifier` — which is invoked from `validateWriteRequest` (called by `ValidateEncryptedSecretsStructure`, i.e. still pre-auth) for Create/Update, and directly from `ValidateDeleteSecretsRequest` / `ValidateListSecretIdentifiersRequest` for Delete/List — checks the **attacker-supplied, not-yet-authorized** `idOwner` against `MaxIdentifierOwnerLengthLimiter` using an owner-scoped context, built exactly the same way as the ciphertext limiter: `contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})` then `.Check(...)` [4](#0-3) . This limiter is constructed with the same `limits.MakeUpperBoundLimiter` factory used for the ciphertext limiter [5](#0-4) .

Since `ValidateSecretIdentifier` runs for every Create/Update/Delete/List request before `GatewayVaultRequestProcessor.authorizeAndStamp` is invoked [6](#0-5) [7](#0-6) , a caller who can reach this endpoint (before/without valid authorization succeeding) can submit an unlimited number of distinct `Owner` strings in `SecretIdentifier.Owner`, each spawning a new per-owner limiter tenant and its background updater — the very unbounded-tenant scenario the codebase's own regression tests (`ciphertext_limiter_tenant_test.go`) prove was closed for the ciphertext check, but was left open here.

### Impact Explanation
Unbounded creation of per-owner limiter tenants (each with a persistent background goroutine per the code's own documentation) leads to goroutine/memory exhaustion in the Vault gateway/node handler process. This matches the CVE's impact class: an endpoint reachable pre-authorization-completion can render the handling service unresponsive, which — for the Vault capability — would halt Vault secret operations (create/update/delete/list) for the affected DON, and potentially degrade the whole node process hosting the handler.

### Likelihood Explanation
The request path is reachable by any client able to send a JSON-RPC Vault request to the gateway (`GatewayVaultRequestProcessor.ProcessRequest`), since `ValidateSecretIdentifier` executes before `AuthorizeRequest` for all four Vault methods. No valid authorization or JWT is required to trigger tenant registration — only a syntactically valid request with a unique `Owner` value per call, which is trivial to automate.

### Recommendation
Apply the same pattern already used for `ValidateCiphertextSizes`: split `ValidateSecretIdentifier` (or its owner/key/namespace length checks) so the owner-scoped limiter checks are deferred until after `AuthorizeRequest` succeeds and are only ever invoked with the authorized owner, mirroring `ValidateEncryptedSecretsStructure`/`ValidateCiphertextSizes`. Structural/non-owner-scoped checks (non-empty, alphanumeric format) can remain pre-auth; only the calls into `MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierKeyLengthLimiter`, and `MaxIdentifierNamespaceLengthLimiter` need to move post-authorization.

### Proof of Concept
1. Send repeated `secrets_list` (or `secrets_create`/`secrets_update`/`secrets_delete`) JSON-RPC requests to the gateway's Vault handler, each with a distinct, syntactically valid but unauthorized `Owner` value (e.g., `owner-1`, `owner-2`, ... `owner-N`) in `SecretIdentifier`/`ListSecretIdentifiersRequest.Owner`.
2. Each request reaches `ValidateSecretIdentifier` before `AuthorizeRequest` is called, so `MaxIdentifierOwnerLengthLimiter.Check` is invoked with a fresh `contexts.CRE{Owner: idOwner}` for every distinct owner string, regardless of whether authorization ultimately fails.
3. Per the codebase's own documented behavior for this limiter type, each new owner value registers a persistent background-updater tenant; repeating with N unique owners accumulates N goroutines/tenants, exhausting node resources and degrading/halting the gateway's Vault request handling.

**Note on confidence:** I could not directly inspect the `chainlink-common` `limits.BoundLimiter`/`MakeUpperBoundLimiter` implementation (external dependency, not in this repo's index) to confirm that identifier-length limiters spawn background goroutines identically to the ciphertext limiter — this is inferred from the shared construction path (`limits.MakeUpperBoundLimiter`) and the codebase's own explicit comments describing that hazard for owner-scoped `BoundLimiter` checks. If the `chainlink-common` implementation differentiates behavior for simple bound checks vs. quota checks, the severity of this specific instance would need re-evaluation, though the code pattern itself (owner-scoped check before auth) is a clear regression risk that the existing regression tests were meant to prevent.

### Citations

**File:** core/capabilities/vault/validator.go (L40-45)
```go
// ValidateEncryptedSecretsStructure calls validateWriteRequest without the
// owner-scoped ciphertext-size limit, which must be checked separately after
// authorization via ValidateCiphertextSizes.
func (r *RequestValidator) ValidateEncryptedSecretsStructure(ctx context.Context, publicKey *tdh2easy.PublicKey, requestID string, encryptedSecrets []*vaultcommon.EncryptedSecret, skipLabelValidation bool) error {
	return r.validateWriteRequest(ctx, publicKey, requestID, encryptedSecrets, skipLabelValidation, false)
}
```

**File:** core/capabilities/vault/validator.go (L123-129)
```go
// ValidateCiphertextSizes checks the owner-scoped ciphertext-size limit for each
// encrypted secret in a write request that already passed structure validation
// (ValidateEncryptedSecretsStructure). It must only be called after
// authorization, with the authorized workflow owner: checking the scoped
// limiter registers a per-owner tenant that spawns a persistent background
// updater, so running it pre-auth would let unauthenticated callers create
// unbounded limiter tenants.
```

**File:** core/capabilities/vault/validator.go (L142-161)
```go
func (r *RequestValidator) ValidateSecretIdentifier(ctx context.Context, idKey, idOwner, idNamespace string) error {
	if idKey == "" {
		return errors.New("key cannot be empty")
	}
	if idOwner == "" {
		return errors.New("owner cannot be empty")
	}

	if !isValidIDComponent(idKey) || !isValidIDComponent(idOwner) || (idNamespace != "" && !isValidIDComponent(idNamespace)) {
		return errors.New("key, owner and namespace must only contain alphanumeric characters")
	}

	// TODO orgID https://smartcontract-it.atlassian.net/browse/CRE-1707
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})
	if err := r.MaxIdentifierOwnerLengthLimiter.Check(ctx, pkgconfig.Size(len(idOwner))); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[pkgconfig.Size]](err); ok {
			return fmt.Errorf("owner exceeds maximum length of %s: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check owner length limit: %w", err)
	}
```

**File:** core/capabilities/vault/validator.go (L291-312)
```go
// NewRequestValidatorFromLimitsFactory constructs a RequestValidator from CRE limits settings.
func NewRequestValidatorFromLimitsFactory(limitsFactory limits.Factory) (*RequestValidator, error) {
	limiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultRequestBatchSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create request batch size limiter: %w", err)
	}
	ciphertextLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.PerOwner.VaultCiphertextSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create ciphertext size limiter: %w", err)
	}
	idKeyLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierKeySizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create identifier key size limiter: %w", err)
	}
	idOwnerLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierOwnerSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create identifier owner size limiter: %w", err)
	}
	idNamespaceLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierNamespaceSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create identifier namespace size limiter: %w", err)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-34)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-150)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var createReq vaultcommon.CreateSecretsRequest
	if err := json.Unmarshal(*req.Params, &createReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
	if p.stripOwnerPrefixForAuth {
		createReq.RequestId = req.ID
		if err := marshalVaultParams(req, &createReq); err != nil {
			return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
		}
	} else {
		createReq.RequestId = coalesceRequestID(createReq.RequestId, req.ID)
	}

	skipLabelValidation := publicKey == nil
	if err := p.validator.ValidateEncryptedSecretsStructure(ctx, publicKey, createReq.RequestId, createReq.EncryptedSecrets, skipLabelValidation); err != nil {
		return nil, p.validationError(req, err)
	}

	authorized, err := p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		createReq.RequestId = prefixedRequestID
		vaultutils.ApplyEncryptedSecretNamespaceDefaults(createReq.EncryptedSecrets)
		return marshalVaultParams(req, &createReq)
	})
	if err != nil {
		return nil, err
	}

	if err := p.validator.ValidateCiphertextSizes(ctx, authorized.AuthResult.AuthorizedOwner(), createReq.EncryptedSecrets); err != nil {
		return nil, p.validationError(req, err)
	}
	return authorized, nil
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-292)
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
```
