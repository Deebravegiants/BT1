### Title
Unauthenticated owner-scoped identifier limiters register unbounded per-owner tenants before request authorization, causing resource-exhaustion DoS in the Vault gateway pipeline - ([File: core/capabilities/vault/validator.go])

### Summary
`RequestValidator.ValidateSecretIdentifier` checks the client-supplied `SecretIdentifier.Owner`/`Namespace`/`Key` against owner-scoped limiters (`MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`, `MaxIdentifierKeyLengthLimiter`) *before* the request has been authorized. Checking a scoped limiter with an attacker-controlled owner registers a brand-new per-owner "tenant" (with a persistent background updater goroutine) in the limiter — the exact same resource-exhaustion pattern the codebase already identified and fixed for `MaxCiphertextLengthLimiter`, but never applied to the identifier-length limiters.

### Finding Description
The gateway vault pipeline runs structure validation before authorization for `CreateSecrets`/`UpdateSecrets` requests: [1](#0-0) 

`ValidateEncryptedSecretsStructure` explicitly documents that it is the pre-auth-safe variant of `validateWriteRequest` because it *skips* the ciphertext-size check: [2](#0-1) 

`validateWriteRequest` (invoked pre-auth) still calls `ValidateSecretIdentifier` for every item in the batch: [3](#0-2) 

`ValidateSecretIdentifier` scopes three limiter checks by the **unauthenticated, attacker-controlled** `idOwner` value using `contexts.WithCRE(ctx, contexts.CRE{Owner: idOwner})`: [4](#0-3) 

This is the *identical* scoping pattern used by `ValidateCiphertextSize`, which the codebase's own comments and regression tests confirm registers a persistent per-owner tenant/goroutine in the limiter and therefore must never run before authorization: [5](#0-4) [6](#0-5) 

The comment on `GatewayVaultRequestProcessor` reiterates the invariant that was applied to fix the ciphertext limiter, but the fix was scoped only to that one limiter, not the sibling `MaxIdentifierOwnerLengthLimiter` / `MaxIdentifierNamespaceLengthLimiter` / `MaxIdentifierKeyLengthLimiter`: [7](#0-6) 

This mirrors the external report's bug class: an unvalidated, attacker-supplied field (`operator` in the vault contract vs. `SecretIdentifier.Owner` here) is used directly to inflate internal per-key/per-tenant accounting state before any ownership/authorization check is performed, and the accumulation of that unvalidated state degrades or breaks a shared subsystem (the vault's `sharePrice()` calculation vs. Chainlink's scoped rate-limiter goroutine pool).

### Impact Explanation
Any caller able to reach the gateway-routed vault `CreateSecrets`/`UpdateSecrets` path (even without a valid allowlist digest or JWT) can submit distinct, arbitrary `owner` strings in `SecretIdentifier.Owner`. Each distinct owner triggers creation of a new limiter tenant with its own persistent background goroutine before authorization rejects the request. Repeated requests with unique fake owners cause unbounded goroutine/resource growth on the node, degrading or crashing the vault capability/gateway handler process — a denial of service against a component that gates critical vault operations (secret create/update/list/delete).

### Likelihood Explanation
High: no authentication or allowlisting is required to reach `ValidateEncryptedSecretsStructure` — it runs strictly *before* `authorizeAndStamp` in `processCreateSecretsRequest`/`processUpdateSecretsRequest`. Only structural validity (non-empty batch, valid alphanumeric identifier components, batch size limit) is required, which is trivial for any client to satisfy while varying the `owner` field on each request.

### Recommendation
Apply the same deferral pattern already used for `MaxCiphertextLengthLimiter`: move the `MaxIdentifierOwnerLengthLimiter`, `MaxIdentifierNamespaceLengthLimiter`, and `MaxIdentifierKeyLengthLimiter` checks (or at minimum the owner-scoping of them) out of the pre-auth `ValidateSecretIdentifier`/`ValidateEncryptedSecretsStructure` path, and only consult them (scoped to the authorized owner) after `AuthorizeRequest` succeeds — analogous to `ValidateCiphertextSizes`. Alternatively, perform the raw length checks pre-auth using a non-owner-scoped/static limiter (no tenant registration) and defer only the owner-tenant-registering check until post-authorization.

### Proof of Concept
1. Send repeated `vault.secrets.create` (or `vault.secrets.update`) JSON-RPC requests to the gateway/handler with no valid `Auth` and no valid allowlist digest.
2. In each request's `EncryptedSecrets[i].Id.Owner`, use a new random alphanumeric string (satisfying `isValidIDComponent`) not tied to any real allowlisted workflow owner.
3. Each request passes `MaxRequestBatchSizeLimiter` and reaches `ValidateSecretIdentifier`, which calls `MaxIdentifierOwnerLengthLimiter.Check` (and the namespace/key limiters) with `contexts.CRE{Owner: idOwner}` set to the attacker-chosen owner — registering a new tenant/goroutine per unique owner value, per the documented behavior in `ciphertext_limiter_tenant_test.go`.
4. The request is ultimately rejected at `AuthorizeRequest` (not allowlisted / invalid JWT), but the limiter tenant has already been created.
5. Repeating with a large number of unique owner strings causes unbounded goroutine/tenant growth in the node process, exhausting resources.

Note: I was unable to directly confirm the concrete limiter implementation wired into `RequestValidator.MaxIdentifierOwnerLengthLimiter` in production (`capability.go`) within the available indexed context — the conclusion that it is a tenant/goroutine-spawning `BoundLimiter` implementation is based on: (a) it shares the exact same interface type (`limits.BoundLimiter[pkgconfig.Size]`) and owner-scoping call pattern (`contexts.WithCRE(ctx, contexts.CRE{Owner: ...})`) as `MaxCiphertextLengthLimiter`, and (b) the codebase's own comments/tests describe this general risk for "a scoped limiter." If `capability.go`'s wiring uses a different, non-tenant-spawning limiter implementation for these three fields specifically, the resource-exhaustion severity would be reduced to log/metric noise rather than goroutine leakage — a Devin session with full file access should verify the concrete limiter construction in `core/capabilities/vault/capability.go` to confirm impact severity.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-34)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-136)
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

```

**File:** core/capabilities/vault/validator.go (L40-45)
```go
// ValidateEncryptedSecretsStructure calls validateWriteRequest without the
// owner-scoped ciphertext-size limit, which must be checked separately after
// authorization via ValidateCiphertextSizes.
func (r *RequestValidator) ValidateEncryptedSecretsStructure(ctx context.Context, publicKey *tdh2easy.PublicKey, requestID string, encryptedSecrets []*vaultcommon.EncryptedSecret, skipLabelValidation bool) error {
	return r.validateWriteRequest(ctx, publicKey, requestID, encryptedSecrets, skipLabelValidation, false)
}
```

**File:** core/capabilities/vault/validator.go (L65-80)
```go
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

**File:** core/capabilities/vault/validator.go (L107-130)
```go
func (r *RequestValidator) ValidateCiphertextSize(ctx context.Context, owner, encryptedValue string) error {
	rawCiphertext, err := hex.DecodeString(encryptedValue)
	if err != nil {
		return fmt.Errorf("failed to decode encrypted value: %w", err)
	}
	// TODO orgID https://smartcontract-it.atlassian.net/browse/CRE-1707
	innerCtx := contexts.WithCRE(ctx, contexts.CRE{Owner: owner})
	if err := r.MaxCiphertextLengthLimiter.Check(innerCtx, pkgconfig.Size(len(rawCiphertext))*pkgconfig.Byte); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[pkgconfig.Size]](err); ok {
			return fmt.Errorf("ciphertext size exceeds maximum allowed size: %s: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check ciphertext size limit: %w", err)
	}
	return nil
}

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

**File:** core/capabilities/vault/ciphertext_limiter_tenant_test.go (L25-34)
```go
// Regression tests for the pre-auth owner-scoped ciphertext limiter issue: checking
// MaxCiphertextLengthLimiter with an owner-scoped context registers a per-owner
// tenant (with a persistent background updater goroutine) in the limiter, so it
// must never be consulted before the request is authorized.

type recordedCiphertextCheck struct {
	owner  string
	amount pkgconfig.Size
}

```
