## Analysis

This maps cleanly onto the reported bug class: a critical, state-changing operation is missing a "kill switch" check that its sibling code path enforces.

### Finding

The CRE gate `GatewayVaultManagementEnabled` is meant to act as a runtime pause switch for Vault secret write operations (`create`/`update`/`delete`). It is enforced in the standalone Gateway-side handler, `core/services/gateway/handlers/vault/handler.go`, where `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` each call `h.writeMethodsEnabled.AllowErr(ctx)` and reject the request with `UnsupportedMethodError` when the gate is disabled.

However, the node-side capability handler, `GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go`, independently re-authorizes every request via `h.requestProcessor.ProcessRequest` (defense-in-depth against a Gateway that might not enforce authorization correctly) but performs **no equivalent check** of the write-management gate before dispatching to `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`, which call straight into `secretsService.CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`.

### Title
Node-side Vault `GatewayHandler` does not enforce the `GatewayVaultManagementEnabled` write-methods kill switch - (File: core/capabilities/vault/gw_handler.go)

### Summary
The write-methods pause gate (`GatewayVaultManagementEnabled`, exposed as `writeMethodsEnabled`) that is supposed to globally disable Vault secret writes is checked only in the Gateway-service-side handler, not in the node-side `GatewayHandler`, which independently re-validates auth but silently omits this gate before performing writes.

### Finding Description
`core/services/gateway/handlers/vault/handler.go` constructs a `writeMethodsEnabled` gate limiter from `cresettings.Default.GatewayVaultManagementEnabled` and enforces it in `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`: [1](#0-0) [2](#0-1) 

The node-side capability handler `GatewayHandler` in `core/capabilities/vault/gw_handler.go` is the component that actually performs the write by calling into `secretsService`. Its `HandleGatewayMessage` re-authorizes the request via `requestProcessor.ProcessRequest` for `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete` — showing the design intent that the node should not blindly trust checks performed upstream by the Gateway — yet it never consults any write-management gate before dispatching to `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`, which unconditionally call `secretsService.CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`: [3](#0-2) [4](#0-3) 

`NewGatewayHandler`, which builds this node-side handler, accepts a `limitsFactory` but only wires it into the `requestValidator`, never into a write-methods gate: [5](#0-4) 

### Impact Explanation
The `GatewayVaultManagementEnabled` setting exists as an operational kill switch to halt Vault secret writes across the DON (e.g., during an incident, migration, or security response). Because the node-side handler never checks this setting, any code path that reaches a node's `GatewayHandler.HandleGatewayMessage` with a properly authorized (allowlisted or JWT-valid) write request — whether from a Gateway instance that has not yet propagated the disabled setting (in multi-gateway topologies, as referenced by `SuiteScenarioHTTPActionMultiGateway`/multi-gateway routing tests), a Gateway with independently misconfigured settings, or any other component invoking the node capability directly — will still perform `CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`, defeating the intended pause. This is a fund/state-integrity-relevant control bypass (secret writes proceeding during an declared "management disabled" state), not merely a UX inconsistency, since node-level enforcement is the last line of defense once a request reaches the DON.

### Likelihood Explanation
The request still requires valid authorization (allowlist or JWT), so this is not a fully unauthenticated bypass. However, any legitimately authorized client (a normal workflow owner) who can reach a node's Vault capability — via a stale/misconfigured Gateway or a Gateway not synchronized on the setting change — triggers the gap with no special conditions or timing needed, making it moderately likely to occur in any deployment using per-gateway settings distribution or the multi-gateway topology.

### Recommendation
Thread a `writeMethodsEnabled`/`GatewayVaultManagementEnabled` gate limiter (via `limitsFactory`) into `core/capabilities/vault/gw_handler.go`'s `GatewayHandler`, and check `AllowErr(ctx)` in `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` (mirroring `core/services/gateway/handlers/vault/handler.go`) before calling into `secretsService`, so the write kill switch is enforced independently at the node layer regardless of Gateway-side state.

### Proof of Concept
1. Set `GatewayVaultManagementEnabled=false` centrally, but have one Gateway instance in a multi-gateway topology (see `system-tests/tests/smoke/cre/cre_suite_test.go` `SuiteScenarioHTTPActionMultiGateway`) lag or be independently configured with the gate still enabled, or otherwise construct a request that reaches a node's `GatewayHandler.HandleGatewayMessage` directly with `MethodSecretsCreate`.
2. Send a properly authorized (allowlisted) `CreateSecrets`/`UpdateSecrets`/`DeleteSecrets` request through that path.
3. Observe that `core/capabilities/vault/gw_handler.go`'s `handleSecretsCreate` proceeds to call `secretsService.CreateSecrets` and succeeds, even though the intended DON-wide write kill switch is set to disabled — contrasted with the Gateway-side handler in `core/services/gateway/handlers/vault/handler.go`, which would have rejected the same request with `UnsupportedMethodError` had it enforced the check consistently.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L236-239)
```go
	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L613-626)
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
```

**File:** core/capabilities/vault/gw_handler.go (L84-126)
```go
func NewGatewayHandler(
	secretsService vaulttypes.SecretsService,
	connector gatewayConnector,
	workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer,
	lggr logger.Logger,
	limitsFactory limits.Factory,
	authorizer Authorizer,
	auth0 *Auth0Config,
) (*GatewayHandler, error) {
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

	requestValidator, err := NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, fmt.Errorf("failed to create request validator: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestProcessor, err := NewGatewayVaultRequestProcessor(requestValidator, authorizer, true, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L187-223)
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
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
```

**File:** core/capabilities/vault/gw_handler.go (L275-292)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}
```
