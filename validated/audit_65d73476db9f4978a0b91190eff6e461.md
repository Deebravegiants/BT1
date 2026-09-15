Based on the code I examined, the underlying `limits.MakeUpperBoundLimiter`/`BoundLimiter` implementation in `chainlink-common` (external dependency) is not indexed in this repo, so I cannot directly confirm the "creates a persistent per-owner goroutine tenant" mechanism from source. However, the claim is corroborated by multiple pieces of first-party evidence that I can verify directly in this repo, and the finding is materially identical to a fix the codebase's own authors already made for the sibling `MaxCiphertextLengthLimiter` case.

Audit Report

## Title
Unauthenticated resource-exhaustion via unbounded per-owner rate-limiter tenant creation in Vault gateway request validation - ([File: core/capabilities/vault/validator.go])

## Summary
`RequestValidator.ValidateSecretIdentifier` scopes `MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`, and `MaxIdentifierKeyLengthLimiter` checks to the attacker-controlled `owner` string via `contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})` [1](#0-0) , and this function is invoked from every pre-authentication structural validator (`validateWriteRequest`, `ValidateDeleteSecretsRequest`, `ValidateListSecretIdentifiersRequest`, `ValidateGetSecretsRequest`) before `authorizeAndStamp`/`AuthorizeRequest` runs [2](#0-1) [3](#0-2) . Critically, the codebase's own comments and a dedicated regression test suite (`ciphertext_limiter_tenant_test.go`) confirm that checking an owner-scoped `BoundLimiter` "registers a per-owner tenant (with a persistent background updater goroutine)," which is exactly why the ciphertext-size check was deliberately split out of `validateWriteRequest` and deferred to after authorization — but the identical pattern for the identifier-length limiters was never fixed the same way.

## Finding Description
`ValidateCiphertextSize`/`ValidateCiphertextSizes` were explicitly redesigned so the owner-scoped `MaxCiphertextLengthLimiter.Check` call only happens after authorization, precisely because of the tenant/goroutine leak risk documented in the comment: "checking the scoped limiter registers a per-owner tenant that spawns a persistent background updater, so running it pre-auth would let unauthenticated callers create unbounded limiter tenants" [4](#0-3) . This is reinforced by a dedicated test file whose header states the same thing and which explicitly regression-tests that "owner-scoped ciphertext limiter must not be consulted before authorization" [5](#0-4) [6](#0-5) .

`ValidateSecretIdentifier`, however, still performs its three owner-scoped `BoundLimiter.Check` calls unconditionally and pre-auth [7](#0-6) , and it is called from:
- `validateWriteRequest` via `ValidateEncryptedSecretsStructure`, invoked before `authorizeAndStamp` in `processCreateOrUpdateSecrets` [8](#0-7) 
- `ValidateDeleteSecretsRequest`, invoked before `authorizeAndStamp` [9](#0-8) 
- `ValidateListSecretIdentifiersRequest`, invoked before `authorizeAndStamp` [10](#0-9) 

All of this is reachable from `GatewayHandler.HandleGatewayMessage`, the gateway's inbound message dispatcher, which routes `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList` straight into `ProcessRequest` without any prior sender authentication.

**Caveat on evidence completeness:** The actual tenant/goroutine-spawning behavior lives inside `limits.BoundLimiter`/`limits.MakeUpperBoundLimiter` in the external `chainlink-common` dependency, which is not part of this repo's index, so I could not directly inspect that implementation to confirm every owner-scoped `Check()` call unconditionally spawns a persistent goroutine regardless of the setting's configured scope (Global vs. PerOwner). I did find evidence suggesting the identifier-length settings (`VaultIdentifierKeySizeLimit`, `VaultIdentifierOwnerSizeLimit`, `VaultIdentifierNamespaceSizeLimit`) are registered as `global`-scoped settings (a test configures one via `{"global": {"VaultIdentifierKeySizeLimit": "3b"}}` [11](#0-10) ), in contrast to `VaultCiphertextSizeLimit`, which is explicitly nested under `cresettings.Default.PerOwner` [12](#0-11)  vs. [13](#0-12) . This distinction matters: if the underlying settings-scope resolution (not just the presence of an owner in `context.Context`) is what drives per-owner tenant/goroutine creation, then owner-scoped `Check()` calls against a `Global`-scoped setting may resolve to a single shared global tenant rather than one tenant per distinct owner string — which would mean the identifier-length limiters do **not** actually reproduce the unbounded-tenant-growth bug that was fixed for the (PerOwner-scoped) ciphertext limiter. I was not able to conclusively resolve this distinction from the code available in this repo's index.

## Impact Explanation
If the identifier-length limiters do behave like the ciphertext limiter (creating a new tenant/goroutine per distinct owner string regardless of the setting's own scope), the impact is memory/goroutine exhaustion (availability) on the vault-capable node/gateway process, reachable by any unauthenticated client — a legitimate CWE-20-style resource-exhaustion issue. However, because these particular settings are registered as `global`-scoped (unlike the `PerOwner`-scoped ciphertext setting that was fixed), it is plausible that no new per-owner tenant is actually created by these specific `Check()` calls, in which case the vulnerability as described would not materialize for the identifier-length limiters specifically, even though the pattern superficially resembles the fixed ciphertext-limiter issue.

## Likelihood Explanation
The pre-auth reachability of `ValidateSecretIdentifier` from an unauthenticated gateway client is clearly demonstrated and not in dispute. What remains unverified is whether the specific `Global`-scoped limiters actually allocate unbounded per-owner resources the way the `PerOwner`-scoped ciphertext limiter does — this is the crux of whether the claim's core mechanism applies here.

## Recommendation
Given the uncertainty in the underlying limiter's tenant-creation semantics for `Global`-scoped settings, I cannot conclusively validate or reject this specific claim from the available evidence. This falls into a gap that requires either (a) inspecting the `chainlink-common` `limits` package source to confirm whether `Check()` on a `Global`-scoped `BoundLimiter` allocates any additional per-owner state when passed a `contexts.CRE{Owner: ...}`-populated context, or (b) writing a test analogous to the existing `ciphertext_limiter_tenant_test.go` regression test but targeting `MaxIdentifierOwnerLengthLimiter`/`MaxIdentifierKeyLengthLimiter`/`MaxIdentifierNamespaceLengthLimiter` to empirically prove/disprove tenant creation.

## Proof of Concept
Not independently verifiable within this session; would require access to `chainlink-common/pkg/settings/limits` source or an executable test environment to confirm whether pre-auth calls to `ValidateSecretIdentifier` with varying `owner` values actually accumulate limiter tenants/goroutines, analogous to `TestGatewayVaultRequestProcessor_ProcessRequest_UnauthorizedWriteNeverTouchesCiphertextLimiter` [6](#0-5) .

### Citations

**File:** core/capabilities/vault/validator.go (L78-80)
```go
		if err := r.ValidateSecretIdentifier(ctx, req.Id.Key, req.Id.Owner, req.Id.Namespace); err != nil {
			return fmt.Errorf("invalid secret identifier at index %d: %w", idx, err)
		}
```

**File:** core/capabilities/vault/validator.go (L123-130)
```go
// ValidateCiphertextSizes checks the owner-scoped ciphertext-size limit for each
// encrypted secret in a write request that already passed structure validation
// (ValidateEncryptedSecretsStructure). It must only be called after
// authorization, with the authorized workflow owner: checking the scoped
// limiter registers a per-owner tenant that spawns a persistent background
// updater, so running it pre-auth would let unauthenticated callers create
// unbounded limiter tenants.
func (r *RequestValidator) ValidateCiphertextSizes(ctx context.Context, owner string, encryptedSecrets []*vaultcommon.EncryptedSecret) error {
```

**File:** core/capabilities/vault/validator.go (L142-178)
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
}
```

**File:** core/capabilities/vault/validator.go (L211-252)
```go
func (r *RequestValidator) ValidateListSecretIdentifiersRequest(ctx context.Context, request *vaultcommon.ListSecretIdentifiersRequest) error {
	if request.RequestId == "" || request.Owner == "" {
		return errors.New("requestID or owner must not be empty")
	}
	if err := r.ValidateSecretIdentifier(ctx, request.Owner, request.Owner, request.Namespace); err != nil {
		return fmt.Errorf("invalid secret identifier: %w", err)
	}
	return nil
}

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

**File:** core/capabilities/vault/validator.go (L297-300)
```go
	ciphertextLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.PerOwner.VaultCiphertextSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create ciphertext size limiter: %w", err)
	}
```

**File:** core/capabilities/vault/validator.go (L301-309)
```go
	idKeyLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierKeySizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create identifier key size limiter: %w", err)
	}
	idOwnerLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierOwnerSizeLimit)
	if err != nil {
		return nil, fmt.Errorf("could not create identifier owner size limiter: %w", err)
	}
	idNamespaceLengthLimiter, err := limits.MakeUpperBoundLimiter(limitsFactory, cresettings.Default.VaultIdentifierNamespaceSizeLimit)
```

**File:** core/capabilities/vault/ciphertext_limiter_tenant_test.go (L25-28)
```go
// Regression tests for the pre-auth owner-scoped ciphertext limiter issue: checking
// MaxCiphertextLengthLimiter with an owner-scoped context registers a per-owner
// tenant (with a persistent background updater goroutine) in the limiter, so it
// must never be consulted before the request is authorized.
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L133-149)
```go
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L215-223)
```go
	if err := p.validator.ValidateDeleteSecretsRequest(ctx, &deleteReq); err != nil {
		return nil, p.validationError(req, err)
	}

	return p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		deleteReq.RequestId = prefixedRequestID
		vaultutils.ApplySecretIdentifierNamespaceDefaults(deleteReq.Ids)
		return marshalVaultParams(req, &deleteReq)
	})
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L247-257)
```go
	if err := p.validator.ValidateListSecretIdentifiersRequest(ctx, &listReq); err != nil {
		return nil, p.validationError(req, err)
	}

	return p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		listReq.RequestId = prefixedRequestID
		if listReq.Namespace == "" {
			listReq.Namespace = vaulttypes.DefaultNamespace
		}
		return marshalVaultParams(req, &listReq)
	})
```

**File:** core/capabilities/vault/capability_test.go (L328-330)
```go
	t.Run("rejects key that exceeds configured max length on a later batched item", func(t *testing.T) {
		getter, err := settings.NewJSONGetter([]byte(`{"global":{"VaultIdentifierKeySizeLimit":"3b"}}`))
		require.NoError(t, err)
```
