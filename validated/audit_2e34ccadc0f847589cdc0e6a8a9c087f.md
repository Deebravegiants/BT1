I found a concrete analog. In `core/services/gateway/handlers/vault/handler.go`, the `writeMethodsEnabled` gate limiter (backed by `cresettings.Default.GatewayVaultManagementEnabled`) is checked in `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete`, but `handleSecretsList` performs no such check before fanning the request out to vault nodes.### Title
Missing feature-gate check on vault `SecretsList` gateway method allows metadata disclosure while vault management is disabled - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway-side Vault handler gates the mutating methods (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`) behind the `writeMethodsEnabled` gate limiter, which is backed by the `cresettings.Default.GatewayVaultManagementEnabled` feature flag. The `SecretsList` method, however, performs no such check and unconditionally fans the request out to vault nodes, so disabling the "vault management" feature does not stop callers from listing (viewing) secret identifiers/metadata for an owner.

### Finding Description
`newHandlerWithAuthorizer` constructs a single gate limiter `writeMethodsEnabled` from `cresettings.Default.GatewayVaultManagementEnabled`: [1](#0-0) 

That gate is enforced in `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete`, each of which calls `h.writeMethodsEnabled.AllowErr(ctx)` and rejects the request with `api.UnsupportedMethodError` when the feature is disabled: [2](#0-1) 

`handleSecretsList`, in contrast, performs no gate check at all and immediately proceeds to `fanOutToVaultNodes`: [3](#0-2) 

The request still passes through the shared authorizer/owner-scoping pipeline (`GatewayVaultRequestProcessor` / `authorizeAndStamp`), so this is not a full authentication bypass — it requires a legitimate allowlisted or JWT-authorized workflow owner to invoke `SecretsList`: [4](#0-3) 

However, the intent of the `GatewayVaultManagementEnabled` setting (named generically for "vault management", not "vault writes") is inconsistently enforced: three of four gateway-exposed secrets methods check it, but the list/read path does not. This mirrors the reported bug class — access controls (a feature-disable gate meant to restrict a capability) fail to cover a read/list code path, letting an otherwise-authorized-but-restricted caller still view information (existence/keys/namespaces of secrets) that the disabled feature was meant to hide.

### Impact Explanation
If an operator disables `GatewayVaultManagementEnabled` expecting vault management (including visibility into which secrets exist for an owner) to be fully suspended, an authorized workflow owner can still invoke `MethodSecretsList` and enumerate secret identifiers/namespaces for their own owner scope. This is an authorization-consistency gap rather than a full unauthenticated bypass: impact is limited to information disclosure of secret metadata (keys/namespaces), not secret values or cross-owner data, since owner-scoping in `authorizeAndStamp`/`validateSecretOwnersMatchAuthorized` still constrains the list request to the caller's own owner. Severity is therefore best characterized as low-to-medium unauthorized metadata visibility when a feature meant to disable this class of vault interaction is toggled off, not a critical breach.

### Likelihood Explanation
Likelihood is moderate: it requires (a) an operator to have disabled `GatewayVaultManagementEnabled` believing it disables Vault gateway interactions broadly, and (b) a caller who already holds valid allowlist/JWT authorization for some workflow owner (not an arbitrary unauthenticated actor) to send a `MethodSecretsList` request. No additional privilege beyond normal vault-authorized-owner status is needed, and the code path is trivially reachable through the existing gateway JSON-RPC dispatch since `handleSecretsList` skips the shared gate check by construction.

### Recommendation
Apply the same `writeMethodsEnabled.AllowErr(ctx)` (or a clearer, explicitly-scoped "management enabled" check covering both read and write vault management methods) check inside `handleSecretsList` in `core/services/gateway/handlers/vault/handler.go`, consistent with `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`. Alternatively, rename/split the setting so it is unambiguous whether `GatewayVaultManagementEnabled` is meant to gate only writes or all vault gateway methods, and audit all four handlers (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) for consistent enforcement.

### Proof of Concept
1. Operator sets `GatewayVaultManagementEnabled` (via `limits.MakeGateLimiter`) to disabled, expecting Vault gateway operations to be suspended. [5](#0-4) 
2. A workflow owner with a valid allowlist/JWT authorization (still granted by `AuthorizeRequest`) sends a `MethodSecretsList` JSON-RPC request to the gateway.
3. `handleSecretsList` is invoked and, unlike the create/update/delete handlers, does not call `writeMethodsEnabled.AllowErr(ctx)`; it proceeds straight to `fanOutToVaultNodes`, returning the list of secret identifiers/namespaces for that owner despite the feature flag being off: [3](#0-2) 

Note: I was unable to locate the definition of `cresettings.Default.GatewayVaultManagementEnabled` itself (likely defined in an external `chainlink-common` dependency not indexed here), so I cannot confirm from source comments whether the setting's documented intent explicitly includes read/list operations. This limits certainty about whether the missing check in `handleSecretsList` is a deliberate design choice (list is intentionally always available) or an oversight relative to the other three methods.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L236-253)
```go
	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}

	requestProcessor, err := vaultcap.NewGatewayVaultRequestProcessor(requestValidator, authorizer, false, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}

	return &handler{
		methodConfig:        cfg,
		donConfig:           donConfig,
		don:                 don,
		lggr:                logger.Named(lggr, "VaultHandler:"+donConfig.DonID),
		requestTimeout:      time.Duration(cfg.RequestTimeoutSec) * time.Second,
		nodeRateLimiter:     nodeRateLimiter,
		writeMethodsEnabled: writeMethodsEnabled,
```

**File:** core/services/gateway/handlers/vault/handler.go (L613-656)
```go
func (h *handler) handleSecretsCreate(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}

func (h *handler) handleSecretsUpdate(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}

func (h *handler) handleSecretsDelete(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L658-661)
```go
func (h *handler) handleSecretsList(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)
	return h.fanOutToVaultNodes(ctx, l, ar)
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
