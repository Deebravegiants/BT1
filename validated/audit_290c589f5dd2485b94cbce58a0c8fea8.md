The `limits` package internals (chainlink-common dependency) that implement `MakeUpperBoundLimiter` and would confirm whether it always registers a per-owner "tenant" with a background goroutine regardless of setting scope are not in this repo's index, so I cannot fully confirm the mechanism. Based on what is directly verifiable in-repo, here is my analysis.

### Title
Owner-scoped identifier limiter checks run before authorization in the vault gateway write path, letting unauthenticated callers register unbounded per-owner limiter tenants - (File: core/capabilities/vault/validator.go)

### Summary
`GatewayVaultRequestProcessor.processCreateSecretsRequest` / `processUpdateSecretsRequest` call `ValidateEncryptedSecretsStructure` before `authorizeAndStamp` runs [1](#0-0) . That pre-auth call chain reaches `ValidateSecretIdentifier`, which stamps `contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})` from the attacker-supplied `req.Id.Owner` and checks three owner-scoped `BoundLimiter`s (`MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`, `MaxIdentifierKeyLengthLimiter`) before any authentication has occurred [2](#0-1) .

### Finding Description
The codebase explicitly documents the exact bug class from the CVE analog (repeated unbounded resource creation causing host/service memory growth) and states it was deliberately fixed for the ciphertext-size limiter: checking an owner-scoped limiter "registers a per-owner tenant... [that] spawns a persistent background updater," so it "must only be called after authorization" [3](#0-2) , and the processor's own type comment reiterates: "checking them pre-auth would let unauthenticated callers create unbounded limiter tenants" [4](#0-3) .

The fix, however, was only applied to `ValidateCiphertextSizes`, which is deferred until after `authorizeAndStamp` [5](#0-4) . The identifier-length checks were not moved. `ValidateEncryptedSecretsStructure` (explicitly documented as the pre-auth structure check) calls `validateWriteRequest`, which iterates over attacker-supplied `encryptedSecrets` and calls `ValidateSecretIdentifier(ctx, req.Id.Key, req.Id.Owner, req.Id.Namespace)` for each entry [6](#0-5) . `ValidateSecretIdentifier` then wraps the context with the raw, unauthenticated `idOwner` and checks `MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`, and `MaxIdentifierKeyLengthLimiter` [7](#0-6) . This is called from `processCreateSecretsRequest`/`processUpdateSecretsRequest` before `authorizeAndStamp` runs [8](#0-7) .

There is a dedicated regression test suite (`ciphertext_limiter_tenant_test.go`) proving the ciphertext limiter is never touched pre-auth [9](#0-8) , but no equivalent test exists for the identifier-length limiters, and I found no code path that defers `ValidateSecretIdentifier`'s owner-scoped checks until after authorization.

### Impact Explanation
If the underlying scoped `BoundLimiter` implementation behaves as described in the code's own comments (registering a per-owner tenant with a persistent background goroutine on first use of a new owner string), an unauthenticated actor could repeatedly submit `vault.secretsCreate`/`vault.secretsUpdate` requests with distinct, attacker-chosen `Id.Owner`/`Id.Namespace`/`Id.Key` values, each of which fails authorization later but still causes a new limiter tenant (and background updater) to be registered before that failure. Repeated at volume this is a host memory/goroutine exhaustion vector — the same bug class as CVE-2016-10163 (repeated resource creation by an unprivileged actor before any privilege check, causing unbounded consumption).

### Likelihood Explanation
Reaching this path only requires sending a `vault.secretsCreate` or `vault.secretsUpdate` JSON-RPC request through the gateway with a valid-looking `EncryptedSecret` batch (one hex-encoded byte is sufficient to pass structure checks when `skipLabelValidation` is true, as shown in the test fixtures) and a unique `Owner`/`Namespace`/`Key` per request; no authentication token or authorization is required to reach `ValidateSecretIdentifier`, since it executes before `authorizeAndStamp`.

### Recommendation
Move the owner/namespace/key length checks in `ValidateSecretIdentifier` out of the pre-auth `ValidateEncryptedSecretsStructure`/`validateWriteRequest` path, mirroring the fix already applied to ciphertext size: split identifier structural validation (non-owner-scoped: emptiness, character set) from the owner-scoped length checks, and only invoke the owner-scoped length checks after `authorizeAndStamp` succeeds, using the authorized owner rather than the attacker-supplied one. Apply the same fix to `processDeleteSecretsRequest` and `processListSecretIdentifiersRequest`, which also call identifier validation pre-auth.

### Proof of Concept
1. Send repeated `vault.secretsCreate` requests to the gateway's vault handler, each with a distinct `Id.Owner` (e.g., `owner-0001`, `owner-0002`, ...), a minimal valid hex `EncryptedValue`, and no valid `Auth` header.
2. Each request reaches `processCreateSecretsRequest` → `ValidateEncryptedSecretsStructure` → `validateWriteRequest` → `ValidateSecretIdentifier`, which checks `MaxIdentifierOwnerLengthLimiter`/`MaxIdentifierNamespaceLengthLimiter`/`MaxIdentifierKeyLengthLimiter` under a `contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})` scoped to the attacker-supplied owner, before `AuthorizeRequest` is ever called [10](#0-9) .
3. `AuthorizeRequest` subsequently fails (no valid auth), but per the code's own documented threat model for the sibling ciphertext limiter, the owner-scoped tenant registration (and background updater) for the bogus owner has already occurred by that point.
4. Repeating with a large number of distinct owners is expected to accumulate limiter tenants/goroutines proportional to attacker-controlled requests, unbounded by authentication.

Note: I could not inspect the `chainlink-common` `limits` package internals (not indexed in this repo) to directly confirm the scoped `BoundLimiter` created by `MakeUpperBoundLimiter` for `VaultIdentifierOwnerSizeLimit`/`VaultIdentifierKeySizeLimit`/`VaultIdentifierNamespaceSizeLimit` spawns a tenant/goroutine identically to the ciphertext limiter — this is inferred from the code's own comments describing "each new owner tenant registered by a scoped limiter spawns a persistent background updater" as a general property of these limiters, plus the existence of a dedicated regression suite for the sibling ciphertext check that this identifier-length path lacks.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L32-34)
```go
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

**File:** core/capabilities/vault/validator.go (L40-80)
```go
// ValidateEncryptedSecretsStructure calls validateWriteRequest without the
// owner-scoped ciphertext-size limit, which must be checked separately after
// authorization via ValidateCiphertextSizes.
func (r *RequestValidator) ValidateEncryptedSecretsStructure(ctx context.Context, publicKey *tdh2easy.PublicKey, requestID string, encryptedSecrets []*vaultcommon.EncryptedSecret, skipLabelValidation bool) error {
	return r.validateWriteRequest(ctx, publicKey, requestID, encryptedSecrets, skipLabelValidation, false)
}

// validateWriteRequest performs common validation for CreateSecrets and UpdateSecrets requests.
// It treats publicKey as optional, since it can be nil if the gateway nodes don't have the public key cached yet.
// includeCiphertextSize controls the owner-scoped ciphertext-size check, which must be
// skipped before authorization (see ValidateEncryptedSecretsStructure).
func (r *RequestValidator) validateWriteRequest(ctx context.Context, publicKey *tdh2easy.PublicKey, id string, encryptedSecrets []*vaultcommon.EncryptedSecret, skipLabelValidation bool, includeCiphertextSize bool) error {
	if id == "" {
		return errors.New("request ID must not be empty")
	}
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, len(encryptedSecrets)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("request batch size exceeds maximum of %d: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check request batch size limit: %w", err)
	}
	if len(encryptedSecrets) == 0 {
		return errors.New("request batch must contain at least 1 item")
	}

	uniqueIDs := map[string]bool{}
	for idx, req := range encryptedSecrets {
		if req == nil {
			return errors.New("encrypted secret must not be nil at index " + strconv.Itoa(idx))
		}
		if req.Id == nil {
			return errors.New("secret ID must not be nil at index " + strconv.Itoa(idx))
		}

		if req.EncryptedValue == "" {
			return errors.New("secret must have encrypted value set at index " + strconv.Itoa(idx) + ":" + req.Id.String())
		}

		if err := r.ValidateSecretIdentifier(ctx, req.Id.Key, req.Id.Owner, req.Id.Namespace); err != nil {
			return fmt.Errorf("invalid secret identifier at index %d: %w", idx, err)
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

**File:** core/capabilities/vault/validator.go (L142-177)
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

	if err := r.MaxIdentifierNamespaceLengthLimiter.Check(ctx, pkgconfig.Size(len(idNamespace))); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[pkgconfig.Size]](err); ok {
			return fmt.Errorf("namespace exceeds maximum length of %s: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check namespace length limit: %w", err)
	}

	if err := r.MaxIdentifierKeyLengthLimiter.Check(ctx, pkgconfig.Size(len(idKey))); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[pkgconfig.Size]](err); ok {
			return fmt.Errorf("key exceeds maximum length of %s: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check key length limit: %w", err)
	}

	return nil
```

**File:** core/capabilities/vault/ciphertext_limiter_tenant_test.go (L110-138)
```go
func TestGatewayVaultRequestProcessor_ProcessRequest_UnauthorizedWriteNeverTouchesCiphertextLimiter(t *testing.T) {
	t.Parallel()

	for _, method := range []string{vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate} {
		for _, stripOwnerPrefix := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s/stripOwnerPrefix=%t", method, stripOwnerPrefix), func(t *testing.T) {
				t.Parallel()

				validator, recorder := mustNewRecordingValidator(t)

				// One-byte hex value under a fresh owner passes structure validation
				// (publicKey is nil so label validation is skipped), reaching authorization.
				secrets := []*vaultcommon.EncryptedSecret{
					{Id: &vaultcommon.SecretIdentifier{Owner: "0xnewowner", Key: "k"}, EncryptedValue: "00"},
				}
				req := mustWriteRequest(t, method, secrets)

				authorizer := vaultcapmocks.NewAuthorizer(t)
				authorizer.EXPECT().AuthorizeRequest(t.Context(), mock.Anything).Return(nil, errors.New("not authorized"))

				processor := mustNewGatewayVaultRequestProcessor(t, validator, authorizer, stripOwnerPrefix)
				_, err := processor.ProcessRequest(t.Context(), &req, nil)
				require.Error(t, err)
				require.ErrorContains(t, err, "request not authorized")
				require.Empty(t, recorder.recorded(), "owner-scoped ciphertext limiter must not be consulted before authorization")
			})
		}
	}
}
```
