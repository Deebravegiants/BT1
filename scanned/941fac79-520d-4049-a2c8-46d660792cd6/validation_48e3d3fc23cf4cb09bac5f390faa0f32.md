### Title
Unauthenticated CPU-exhaustion via unbounded-size TDH2 ciphertext verification performed before authorization in vault gateway request pipeline - (File: core/capabilities/vault/gateway_vault_request_processor.go)

### Summary
The vault gateway request pipeline performs expensive TDH2 (pairing-based) ciphertext verification on every secret in a `SecretsCreate`/`SecretsUpdate` request *before* authorization and *before* the per-secret ciphertext-size limit is checked. An unauthenticated caller can submit a batch of secrets containing arbitrarily large hex-encoded ciphertext blobs and force the node to run this cryptographic verification before rejecting the request for lack of authorization, similar in structure to the KeyTrap class of bug (expensive cryptographic work performed on attacker-controlled input prior to establishing trust).

### Finding Description
`GatewayVaultRequestProcessor.processCreateSecretsRequest`/`processUpdateSecretsRequest` call `ValidateEncryptedSecretsStructure` before `authorizeAndStamp`: [1](#0-0) 

`ValidateEncryptedSecretsStructure` explicitly runs `validateWriteRequest` with `includeCiphertextSize=false`, deferring the owner-scoped ciphertext-size check (`ValidateCiphertextSize`) to *after* authorization, per its own documented rationale (avoiding unauthenticated callers spinning up unbounded per-owner limiter tenants): [2](#0-1) 

However, regardless of `includeCiphertextSize`, the same loop unconditionally calls `verifyEncryptedSecret` (via `EnsureRightLabelOnSecret` or directly), which performs `hex.DecodeString` followed by `tdh2easy.Ciphertext.UnmarshalVerify` — a pairing-based cryptographic verification — on every item in the batch: [3](#0-2) [4](#0-3) 

Only the *number* of items in the batch is bounded pre-auth via `MaxRequestBatchSizeLimiter.Check`: [5](#0-4) 

There is no equivalent bound on the *size* of each individual ciphertext string before it reaches `UnmarshalVerify` in this pre-auth path — the size limiter is intentionally deferred to `ValidateCiphertextSizes`, called only after `authorizeAndStamp` succeeds: [6](#0-5) 

This entire pipeline is invoked directly from `GatewayHandler.HandleGatewayMessage` for `MethodSecretsCreate`/`MethodSecretsUpdate` before any workflow-owner authorization succeeds or fails: [7](#0-6) 

### Impact Explanation
Any actor able to reach the vault gateway JSON-RPC surface (an unprivileged/unauthenticated client, since the whole point of running `ValidateEncryptedSecretsStructure` before `authorizeAndStamp` is that authorization has not yet been performed) can submit `SecretsCreate`/`SecretsUpdate` requests containing multiple large, arbitrary hex blobs as `EncryptedValue`. Each blob triggers a full `UnmarshalVerify` pairing-crypto verification attempt against the cached master public key, consuming CPU proportional to attacker-chosen input size, before the request is ever authorized. Repeated/concurrent submission of such requests can degrade or exhaust node CPU resources — a denial-of-service condition reachable without any credentials, analogous to the KeyTrap pattern of forcing expensive cryptographic validation on unauthenticated attacker-supplied data.

### Likelihood Explanation
The precondition is only that the attacker can send a JSON-RPC `SecretsCreate`/`SecretsUpdate` message to the gateway with hex-decodable garbage of large size in `EncryptedValue` — no valid signature, JWT, or workflow ownership is required to reach the vulnerable verification call, since it executes strictly before `authorizeAndStamp`. The batch-size limiter bounds the *count* of secrets but not their individual size, so the attack surface per request is effectively unbounded up to whatever outer transport/message-size limits exist (none were found within this pipeline itself).

### Recommendation
Enforce a per-item ciphertext size bound (even a conservative, unauthenticated-safe static cap, not the owner-scoped limiter) before calling `verifyEncryptedSecret`/`EnsureRightLabelOnSecret` in `validateWriteRequest`, so oversized ciphertext is rejected cheaply (e.g., by hex length) prior to any cryptographic verification. Alternatively, move a coarse, non-owner-scoped total-payload-size check ahead of the crypto-verification loop while still deferring the owner-scoped `ValidateCiphertextSizes` limiter to post-authorization as currently designed.

### Proof of Concept
1. Craft an unauthenticated `SecretsCreate` JSON-RPC request with `Params.EncryptedSecrets` containing several entries, each with `EncryptedValue` set to a very large (e.g., multi-MB) hex string and a syntactically valid (but arbitrary) `SecretIdentifier`.
2. Send it to the vault gateway handler; `HandleGatewayMessage` routes it to `ProcessRequest` → `processCreateSecretsRequest` → `ValidateEncryptedSecretsStructure`, which iterates the batch calling `verifyEncryptedSecret`/`UnmarshalVerify` on each large blob before any authorization check runs.
3. Repeat concurrently from multiple unauthenticated senders to observe sustained CPU consumption on the node prior to any request being authorized or rejected for lack of credentials. [8](#0-7)

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-149)
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
```

**File:** core/capabilities/vault/validator.go (L40-63)
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
```

**File:** core/capabilities/vault/validator.go (L81-105)
```go
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
		_, ok := uniqueIDs[vaulttypes.KeyFor(req.Id)]
		if ok {
			return errors.New("duplicate secret ID found at index " + strconv.Itoa(idx) + ": " + req.Id.String())
		}

		uniqueIDs[vaulttypes.KeyFor(req.Id)] = true
	}

	return nil
}
```

**File:** core/capabilities/vault/validator.go (L343-359)
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
}
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
