### Title
Vault gateway skips label/MAC verification of encrypted secrets when the cached master public key is unavailable, allowing cross-owner secret impersonation - ([File: core/capabilities/vault/gateway_vault_request_processor.go])

### Summary
The zip4j advisory describes ciphertexts being accepted without a MAC/authentication-tag check under certain conditions, allowing a tampered ciphertext to be treated as valid. In this codebase, `processCreateSecretsRequest` / `processUpdateSecretsRequest` derive `skipLabelValidation := publicKey == nil` and pass that flag into `ValidateEncryptedSecretsStructure`, which, when true, skips `EnsureRightLabelOnSecret` (the check that binds a TDH2 ciphertext's authenticated label to the claimed secret owner) and instead runs only the bare `verifyEncryptedSecret`, which itself explicitly no-ops (`return nil, nil`) when `publicKey == nil`. This means whenever the internet-facing Vault gateway handler has not yet cached the vault master public key (fresh restart, cache miss, or key-refresh gap), an unprivileged client's `vault.secrets.create`/`vault.secrets.update` request bypasses the cryptographic label check that normally proves a ciphertext was actually encrypted for the claimed owner. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`EnsureRightLabelOnSecret` is the security-relevant check that verifies the TDH2 ciphertext's embedded label matches the workflow owner label before the secret is stored under that owner's namespace: [4](#0-3) 

`validateWriteRequest` only calls `EnsureRightLabelOnSecret` when `skipLabelValidation` is false; when true, it instead calls the weaker `verifyEncryptedSecret`, which itself is a no-op returning `(nil, nil)` when `publicKey == nil`: [2](#0-1) [3](#0-2) 

Both the node-side `GatewayHandler` (via `NewGatewayVaultRequestProcessor(..., stripOwnerPrefixForAuth=true, ...)`) and the gateway-facing public `handler` (`stripOwnerPrefixForAuth=false`) route unprivileged, internet-facing `vault.secrets.create`/`vault.secrets.update` JSON-RPC requests through `processCreateSecretsRequest`/`processUpdateSecretsRequest`, which set `skipLabelValidation := publicKey == nil` and pass the possibly-nil cached public key straight through: [5](#0-4) [6](#0-5) 

The public key is only obtained from a best-effort, lazily-populated cache (`getCachedPublicKey`), which can legitimately be `nil` right after a gateway restart or during a refresh gap: [7](#0-6) 

Downstream owner-scoped enforcement (`authorizeAndStamp` / `validateSecretOwnersMatchAuthorized`) checks that the `SecretIdentifier.Owner` field in the request matches the authorized workflow owner from the requester's own authorization context (allowlist digest or JWT claims) — but this only validates the *claimed* identifier owner field, not that the ciphertext itself was actually encrypted/labeled for that owner. The label check via `EnsureRightLabelOnSecret` is the only mechanism that cryptographically ties the ciphertext content to the claimed owner; skipping it (as the tests at `gw_handler_test.go:406-453` demonstrate is otherwise enforced) removes that binding whenever the public key cache is empty.

### Impact Explanation
When the label check is skipped, an authorized-but-malicious or confused caller (or a caller whose secret identifier matches their own workflow owner, which passes the separate `Owner` string check) can submit a ciphertext that was never actually encrypted/labeled for that owner, because there is no code path re-verifying the label once the public key becomes available later. Since the identifier-owner match and the ciphertext-label match are two independent controls, and one of them (`EnsureRightLabelOnSecret`) is conditionally disabled, the effective security guarantee "a stored secret's ciphertext label matches its stored owner identifier" degrades to unauthenticated in this window — analogous to zip4j accepting an unauthenticated/tampered ciphertext because the MAC check was skipped. Because this only affects Create/Update paths gated behind the same-owner identifier check, the worst-case impact is bounded to storing a secret whose ciphertext-owner binding was never cryptographically verified (data integrity/confusion of encrypted-secret provenance), not a full cross-tenant secret read.

### Likelihood Explanation
The bypass triggers automatically and deterministically any time `getCachedPublicKey()`/the node-cached key returns `nil` — a state that is documented in code comments as expected "immediately after gateway reboots" or before the periodic refresh ticker (`1 * time.Minute`) populates the cache. This is not an attacker-controlled network/timing race requiring privileged access; it is a routine operational window reachable by any client that can submit a JSON-RPC `vault.secrets.create`/`update` request during that window.

### Recommendation
Do not silently skip label verification when the public key is unavailable. Either reject write requests with a retryable error until the public key is cached, or defer label verification until the public key is available and re-validate before the secret write is finalized (rather than allowing `skipLabelValidation=true` to permanently bypass the check for that request).

### Proof of Concept
1. Restart (or simulate a fresh) Vault gateway `handler` such that `cachedPublicKeyObject` is `nil` (`core/services/gateway/handlers/vault/handler.go:680-690`).
2. As an authorized-but-arbitrary caller, submit a `vault.secrets.create` request with `EncryptedSecrets[0].Id.Owner` set to your own authorized owner, but `EncryptedValue` containing any hex-encoded ciphertext (not necessarily labeled for that owner, or even structurally arbitrary) — because `verifyEncryptedSecret` returns `(nil, nil)` immediately when `publicKey == nil` (`core/capabilities/vault/validator.go:343-358`), and `processCreateSecretsRequest` computes `skipLabelValidation := publicKey == nil` (`core/capabilities/vault/gateway_vault_request_processor.go:132`), the label/MAC-equivalent check `EnsureRightLabelOnSecret` never executes.
3. The request proceeds to `authorizeAndStamp` and is accepted/stored despite the ciphertext's label never having been cryptographically verified against the owner, in contrast to the enforced behavior once the public key is cached (as shown by the negative test case at `core/services/gateway/handlers/vault/handler_test.go:406-453`, which fails with "doesn't have owner as the label" only when a public key is present).

### Citations

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

**File:** core/capabilities/vault/validator.go (L86-95)
```go
		if skipLabelValidation {
			if _, err := verifyEncryptedSecret(publicKey, req.EncryptedValue); err != nil {
				return errors.New("Encrypted Secret at index [" + strconv.Itoa(idx) + "] is invalid. Error: " + err.Error())
			}
		} else {
			err := EnsureRightLabelOnSecret(publicKey, req.EncryptedValue, req.Id.Owner)
			if err != nil {
				return errors.New("Encrypted Secret at index [" + strconv.Itoa(idx) + "] doesn't have owner as the label. Error: " + err.Error())
			}
		}
```

**File:** core/capabilities/vault/validator.go (L317-341)
```go
// EnsureRightLabelOnSecret verifies that the TDH2 ciphertext label matches the workflow
// owner label (Ethereum address, left-padded to 32 bytes). owner must be non-empty;
// when the public key is nil, verification is skipped for the same reasons as
// verifyEncryptedSecret.
func EnsureRightLabelOnSecret(publicKey *tdh2easy.PublicKey, secret, owner string) error {
	cipherText, err := verifyEncryptedSecret(publicKey, secret)
	if err != nil {
		return err
	}
	if cipherText == nil {
		return nil
	}
	if owner == "" {
		return errors.New("owner must not be empty for secret label verification")
	}

	expected := vaultutils.WorkflowOwnerToLabel(owner)
	secretLabel := cipherText.Label()
	if secretLabel == expected {
		return nil
	}

	return fmt.Errorf("secret label [%s] does not match workflow owner label [%s]",
		hex.EncodeToString(secretLabel[:]), hex.EncodeToString(expected[:]))
}
```

**File:** core/capabilities/vault/validator.go (L343-358)
```go
func verifyEncryptedSecret(publicKey *tdh2easy.PublicKey, secret string) (*tdh2easy.Ciphertext, error) {
	cipherBytes, err := hex.DecodeString(secret)
	if err != nil {
		return nil, errors.New("failed to decode encrypted value:" + err.Error())
	}
	if publicKey == nil {
		// Public key can be nil if gateway cache isn't populated yet (immediately after gateway reboots).
		// Ok to not validate in such cases, since this validation also runs on Vault Nodes.
		return nil, nil
	}

	cipherText := &tdh2easy.Ciphertext{}
	if err := cipherText.UnmarshalVerify(cipherBytes, publicKey); err != nil {
		return nil, errors.New("failed to verify encrypted value:" + err.Error())
	}
	return cipherText, nil
```

**File:** core/services/gateway/handlers/vault/handler.go (L426-434)
```go
	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L680-690)
```go
func (h *handler) getCachedPublicKey() ([]byte, *tdh2easy.PublicKey) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if h.cachedPublicKeyGetResponse == nil {
		return nil, nil
	}
	copied := make([]byte, len(h.cachedPublicKeyGetResponse))
	copy(copied, h.cachedPublicKeyGetResponse)
	cachedPublicKeyCopy := *h.cachedPublicKeyObject
	return copied, &cachedPublicKeyCopy
}
```
