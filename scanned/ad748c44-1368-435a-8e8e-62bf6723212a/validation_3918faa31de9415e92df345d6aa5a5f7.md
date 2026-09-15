### Title
Missing owner-scoping in vault secrets delete allows cross-tenant secret deletion - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The gateway `GatewayHandler` authorizes each vault JSON-RPC request against an `AuthResult.AuthorizedOwner()` derived from the allowlist/JWT authorizer, but for `vault.secrets.delete` it never enforces that the `owner` fields inside the request payload actually belong to that authorized owner before invoking `DeleteSecrets`. This mirrors the Bullran Index root cause: an unprivileged/authenticated-but-wrong-scope actor can act on assets ("secrets") belonging to another user because a downstream state-mutating operation lacks a per-owner permission check, even though a superficial authorization step passed.

### Finding Description
`GatewayHandler.HandleGatewayMessage` routes `MethodSecretsList` and `MethodSecretsDelete` through the same `requestProcessor.ProcessRequest` pipeline and obtains an `authResult` for both: [1](#0-0) 

For `MethodSecretsList`, the handler correctly overwrites the caller-supplied owner with the authorized owner before querying, preventing a caller from listing another owner's secrets: [2](#0-1) 

For `MethodSecretsDelete`, however, `handleSecretsDelete` unmarshals the request params directly and calls `h.secretsService.DeleteSecrets(ctx, r)` with the raw, caller-controlled `Ids` (each containing an `Owner` field) — with no equivalent owner override or cross-check against `authResult.AuthorizedOwner()`: [3](#0-2) 

The upstream pipeline's `processDeleteSecretsRequest` also does not perform this check. It only structurally validates the delete request (`ValidateDeleteSecretsRequest`) and then authorizes/stamps the envelope — `AuthorizeRequest` validates the request digest/allowlist entry and expiry, but nothing there cross-checks that every `id.Owner` in `deleteReq.Ids` equals `authResult.AuthorizedOwner()`: [4](#0-3) [5](#0-4) 

By contrast, the create/update path enforces ownership indirectly by requiring the ciphertext label to match the owner (`EnsureRightLabelOnSecret`) and by scoping ciphertext-size limits to `authorized.AuthResult.AuthorizedOwner()`: [6](#0-5) [7](#0-6) 

No such owner-binding mechanism exists for delete: there's no ciphertext/label to verify ownership of a delete target, and the code path simply trusts the caller-supplied `Owner` string inside each `SecretIdentifier` in `DeleteSecretsRequest.Ids`.

### Impact Explanation
If an actor is authorized for one workflow-owner scope (e.g., via a legitimately allowlisted digest or a valid JWT for their own workflow owner) but crafts a `vault.secrets.delete` request whose `Ids[].Owner` field references a *different* owner's namespace/keys, the request passes structural validation and JSON-RPC authorization (which validates the request digest/signature, not the semantic owner field inside `Ids`), and `DeleteSecrets` is invoked with attacker-chosen owners. This is directly analogous to the Bullran Index incident, where a caller was able to trigger a privileged state-mutating action ("burn"/delete) on assets belonging to another user due to missing per-resource ownership enforcement, even though some access control existed at a coarser level. The impact is potential unauthorized destruction of another tenant's secrets (irreversible loss of vault-stored secrets), which for workflow execution purposes is a serious integrity/availability impact, though it does not directly move on-chain funds. Severity should be assessed as at least Medium given the irreversible nature of secret deletion.

### Likelihood Explanation
Likelihood depends on whether `AllowListBasedAuth.AuthorizeRequest` or `secretsService.DeleteSecrets` performs the owner cross-check server-side downstream in a layer not reachable via static search (e.g., inside `SecretsService.DeleteSecrets` implementation, which was not found in the indexed context). If such a check does not exist there, likelihood is high: any workflow owner with a valid, currently-allowlisted delete request (which only needs to match a digest for *their own* request, not per-`Id.Owner`) could substitute arbitrary owner values in the `Ids` array without failing digest verification, since the digest is computed over the full request bytes and only needs to be pre-registered for that specific payload — meaning the attacker would need a matching allowlist entry, which somewhat limits raw exploitability. This uncertainty (whether `DeleteSecrets` in `SecretsService` performs owner enforcement) could not be resolved from the available index and should be verified directly in the full repository.

### Recommendation
Enforce that every `SecretIdentifier.Owner` in `DeleteSecretsRequest.Ids` (and similarly in list/get flows) equals `authResult.AuthorizedOwner()` before calling `secretsService.DeleteSecrets`, mirroring the pattern already used in `handleSecretsList` (`r.Owner = authResult.AuthorizedOwner()`). Since delete requests can reference multiple `Ids`, add an explicit validation step in `processDeleteSecretsRequest` (post-authorization, using `authorized.AuthResult.AuthorizedOwner()`) that rejects any `Ids[].Owner` not matching the authorized owner, returning an authorization error rather than proceeding to `DeleteSecrets`.

### Proof of Concept
Conceptual PoC (pending confirmation against `SecretsService.DeleteSecrets` implementation, which is outside the indexed context):
1. Attacker obtains/derives a valid allowlisted or JWT-authorized `vault.secrets.delete` request digest for their own workflow owner `A`.
2. Attacker crafts `DeleteSecretsRequest.Ids = [{Key: "victim_secret", Owner: "B", Namespace: "main"}]` while keeping the JSON-RPC envelope (`req.ID`, `req.Method`) identical to what was allowlisted/signed for owner `A`.
3. `ValidateDeleteSecretsRequest` only checks structural validity of `id.Key/Owner/Namespace` (non-empty, alphanumeric), not that `id.Owner == authorizedOwner` — see `core/capabilities/vault/validator.go:221-252`.
4. `authorizeAndStamp` authorizes based on the request digest (which is unrelated to `Ids[].Owner` matching), then stamps the request ID with owner `A`'s prefix — see `core/capabilities/vault/gateway_vault_request_processor.go:260-293`.
5. `handleSecretsDelete` forwards the unmodified `Ids` (still referencing owner `B`) straight to `secretsService.DeleteSecrets` — see `core/capabilities/vault/gw_handler.go:313-336`.
6. If `DeleteSecrets`'s internal storage layer does not itself re-validate ownership against the JSON-RPC-level authorized owner, owner `B`'s secrets are deleted by an actor authorized only for owner `A`.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L200-206)
```go
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
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
