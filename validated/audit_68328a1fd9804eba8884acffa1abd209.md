Found it. This is exactly the "check for previous state, missing on first occurrence → validation skipped" bug class, applied to the vault gateway/node write-path label verification.### Title
Ciphertext label/owner-binding verification is silently skipped when the vault gateway's master public key cache is empty (e.g., immediately after gateway restart, "first request" analog) - ([File: core/capabilities/vault/validator.go])

### Summary
The M-6 root cause is a check that depends on state from a "previous" cycle: when that state doesn't exist yet (the first batch), the check is not merely skipped safely — it causes the code path to behave differently than intended. The direct analog in `chainlink` is in `verifyEncryptedSecret`/`EnsureRightLabelOnSecret` in `core/capabilities/vault/validator.go`, used by `validateWriteRequest` (called for `MethodSecretsCreate`/`MethodSecretsUpdate`). When the gateway's cached master TDH2 public key is nil — which is explicitly documented to happen "immediately after gateway reboots" — the function returns `nil, nil` and the caller treats this as "validation passed," silently skipping the owner/label binding check.

### Finding Description
`verifyEncryptedSecret` is the routine that verifies a ciphertext's TDH2 signature and extracts its `Label()` (which must match the requesting workflow owner): [1](#0-0) 

If `publicKey == nil`, the function explicitly bypasses verification and returns `nil, nil` — a "pass" result — with the comment that this is acceptable because the gateway cache might not be populated yet after a reboot, and because the check will also run on Vault Nodes.

`EnsureRightLabelOnSecret`, which enforces that the ciphertext's embedded owner label matches the claimed `SecretIdentifier.Owner`, calls this same function and treats a `nil` ciphertext as an automatic pass: [2](#0-1) 

This is invoked from `validateWriteRequest`, the shared pre-authorization validation path for `CreateSecrets`/`UpdateSecrets`: [3](#0-2) 

On the gateway side, `getMasterPublicKey` lazily fetches and caches the key on first use, and `HandleGatewayMessage` calls this exactly once, right before invoking the request processor — the public key is passed through the whole call, so if the cache is empty (fresh gateway process, or the fetch fails/returns nil transiently) the entire request is validated with `publicKey == nil`: [4](#0-3) [5](#0-4) 

This mirrors the M-6 pattern precisely: a security check (label/owner binding enforcement, analogous to "validator must be in previous tree") depends on state that may legitimately be absent on the very first invocation (analogous to "no previous batch exists yet"), and instead of failing safe, the code takes the branch that skips the check entirely.

### Impact Explanation
If this label check is bypassed, an unprivileged/unauthorized workflow owner could submit a `CreateSecrets`/`UpdateSecrets` ciphertext whose TDH2 label does not match their own claimed owner (i.e., a ciphertext actually encrypted/labeled for a different owner) and have it accepted at the gateway's pre-authorization stage without this defense-in-depth check catching the mismatch. The code comment states this is "ok" because the same validation also runs on the Vault Nodes (OCR path) — meaning this check is explicitly defense-in-depth, not the sole enforcement point. That significantly limits real-world impact: as long as the node-side validation independently and correctly re-checks the label, the gateway-side skip is a redundant-layer gap, not a full bypass of the control. I could not verify from the available index whether the Vault Node OCR-side write-path re-derives/re-checks the label with the same rigor, or whether there exists a race/window (e.g., gateway restarts and nodes' independent public-key caches are also stale simultaneously) where both checks could be skipped concurrently.

### Likelihood Explanation
The nil-publicKey condition is not a rare edge case — it explicitly occurs "immediately after gateway reboots," which is a routine operational event (deploys, crashes, restarts). During that window, any `SecretsCreate`/`SecretsUpdate` request bypasses the label-binding check at the gateway layer with no error or warning surfaced. The window duration depends on how quickly `MasterPublicKeyFromSecretsService` succeeds, which is unverified from the index.

### Recommendation
Do not treat `publicKey == nil` as an implicit pass for the owner/label-binding check in `verifyEncryptedSecret`/`EnsureRightLabelOnSecret`. Either: (a) fail closed (reject the request with a retryable error) until the master public key is available, or (b) ensure and document with certainty (with a test) that the Vault Node OCR path performs an equivalent, non-skippable label check for every accepted write, so the gateway-side skip can never result in a globally-unenforced binding. Add a metric/log warning whenever this bypass path is taken so operators can detect and bound the exposure window after gateway restarts.

### Proof of Concept
Not independently reproduced against a running system. Structurally: (1) restart the vault gateway so `cachedMasterPublicKey` is nil; (2) before the lazy fetch in `getMasterPublicKey` completes/succeeds, or if `MasterPublicKeyFromSecretsService` returns nil-with-no-error momentarily, submit a `MethodSecretsCreate` request with a TDH2 ciphertext whose label does not correspond to the claimed `SecretIdentifier.Owner`; (3) per `verifyEncryptedSecret`'s nil-publicKey branch, `validateWriteRequest` returns no error for the label mismatch at the gateway. Confirming actual exploitability requires verifying that no equivalent enforcement independently blocks the request at the Vault Node/OCR layer, which was not confirmed from the available index.

### Citations

**File:** core/capabilities/vault/validator.go (L51-95)
```go
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
		if includeCiphertextSize {
			if err := r.ValidateCiphertextSize(ctx, req.Id.Owner, req.EncryptedValue); err != nil {
				return fmt.Errorf("secret encrypted value at index %d is invalid: %w", idx, err)
			}
		}
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

**File:** core/capabilities/vault/validator.go (L317-330)
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

**File:** core/capabilities/vault/gw_handler.go (L187-199)
```go
	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```

**File:** core/capabilities/vault/gw_handler.go (L238-261)
```go
func (h *GatewayHandler) getMasterPublicKey(ctx context.Context) (*tdh2easy.PublicKey, error) {
	h.mu.RLock()
	if h.cachedMasterPublicKey != nil {
		cachedCopy := *h.cachedMasterPublicKey
		h.mu.RUnlock()
		return &cachedCopy, nil
	}
	h.mu.RUnlock()

	publicKey, err := MasterPublicKeyFromSecretsService(ctx, h.secretsService)
	if err != nil {
		return nil, err
	}

	h.mu.Lock()
	defer h.mu.Unlock()
	if h.cachedMasterPublicKey != nil {
		cachedCopy := *h.cachedMasterPublicKey
		return &cachedCopy, nil
	}
	h.cachedMasterPublicKey = publicKey
	cachedCopy := *publicKey
	return &cachedCopy, nil
}
```
