Confirmed: `Config.Validate()` in `core/services/ocr2/plugins/vault/config.go:20-32` validates `IssuerURL` and `Audience` when `Auth0` is configured, but never validates `TenantID`, allowing it to remain `0` in the job spec. That zero value flows unchanged through `NewGatewayHandler` into `JWTBasedAuthConfig.TenantID` and then into `NewJWTBasedAuth`, where it is silently replaced with the hardcoded default `1`.

### Title
JWT tenant-ID validation silently defaults to tenant `1` when Auth0 config omits `TenantID`, enabling cross-tenant JWT auth bypass - ([File: core/capabilities/vault/jwt_based_auth.go])

### Summary
`Config.Validate()` for the OCR2 Vault plugin validates that `IssuerURL` and `Audience` are set when `Auth0` config is present, but does not require `TenantID` to be set. When `TenantID` is left at its zero value, `NewJWTBasedAuth` silently substitutes the hardcoded constant `defaultJWTAuthJobSpecTenantID = 1` instead of rejecting the misconfiguration, exactly mirroring the reported bug class of defaulting an unset security-relevant parameter instead of failing closed.

### Finding Description
`Config.Validate()` only checks `IssuerURL` and `Audience`: [1](#0-0) . The `Auth0Config.TenantID` field has no non-zero validation anywhere else, so a job spec that omits `tenantID` (or sets it to `0`) passes validation and is passed straight through [2](#0-1) .

`NewJWTBasedAuth` then treats zero as "unset" and defaults `expectedTenantID` to `defaultJWTAuthJobSpecTenantID = 1`: [3](#0-2) [4](#0-3) .

This `expectedTenantID` is the authoritative value checked against every incoming JWT's `tenant_id`/`urn:chainlink:tenant_id` claim in `AuthorizeRequest`, and a match derives the caller's authorized workflow owner address for secret operations: [5](#0-4) [6](#0-5) . Tenant ID `1` is a low, predictable/likely-first-tenant value (comment even calls it `defaultJWTAuthJobSpecTenantID`), and `DeriveJWTAuthorizedVaultWorkflowOwner` derives the owner address deterministically from `(tenantID, orgID)` [7](#0-6) . If a node/job operator misconfigures Auth0 (omitting `tenantID`) expecting strict tenant isolation, any org holding a validly signed JWT with `tenant_id=1` (a plausible/guessable tenant ID) from the same Auth0 issuer/audience will be authorized for that job's Vault secrets endpoint, instead of the deployment failing to authenticate any request.

### Impact Explanation
This is reachable from an unprivileged external caller through the internet-facing Gateway → node JWT-based auth path used for Vault secret create/update/delete/list operations (`vaulttypes.MethodSecretsCreate/Update/Delete/List`) handled in `GatewayHandler.HandleGatewayMessage` [8](#0-7) . Successful cross-tenant matching against the defaulted tenant ID results in incorrect workflow-owner derivation and authorization, i.e., unauthorized access to another tenant's secret operations — a concrete authentication/role bypass and cross-tenant confusion, matching the required impact categories.

### Likelihood Explanation
Requires (a) the operator to misconfigure/omit `TenantID` in `Auth0Config` for a job spec — plausible since `Config.Validate()` does not enforce it — and (b) an attacker to possess a validly signed JWT from the same Auth0 tenant/issuer/audience with `tenant_id=1` (or any org whose real tenant happens to be `1`). Likelihood is moderate: it depends on operator misconfiguration rather than pure attacker-side exploitation, but the silent default with no logged warning or startup error makes the misconfiguration easy to miss and persist in production.

### Recommendation
In `Config.Validate()` (`core/services/ocr2/plugins/vault/config.go`), require `Auth0.TenantID != 0` when `Auth0` is configured, returning a validation error otherwise. In `NewJWTBasedAuth` (`core/capabilities/vault/jwt_based_auth.go`), remove the silent default-to-`1` behavior and instead return an error (`errors.New("tenantID is required and must be non-zero")`) when `cfg.TenantID == 0`, so misconfiguration fails closed at startup rather than silently authorizing against a guessable default tenant.

### Proof of Concept
1. Deploy a Vault-capable job spec with `Auth0.IssuerURL` and `Auth0.Audience` set but `Auth0.TenantID` omitted (zero value). `Config.Validate()` passes.
2. `NewGatewayHandler` constructs `JWTBasedAuthConfig{TenantID: 0, ...}` and `NewJWTBasedAuth` sets `expectedTenantID = 1` (`core/capabilities/vault/jwt_based_auth.go:137-140`).
3. An external caller obtains a valid Auth0-issued JWT for the correct issuer/audience with `tenant_id` (or `urn:chainlink:tenant_id`) claim equal to `1` (e.g., their own org happens to be the first-provisioned tenant, or the value is otherwise obtainable/guessable) and a matching `workflow_owner`/`request_digest`.
4. Submit a `secrets/create`, `secrets/update`, `secrets/delete`, or `secrets/list` gateway request with this JWT in `req.Auth`.
5. `AuthorizeRequest` accepts the request because `claims.TenantID (1) == v.expectedTenantID (1)`, even though the job spec operator never intended tenant `1` to be authorized, granting access to the node's Vault secret operations for the derived workflow owner.

### Citations

**File:** core/services/ocr2/plugins/vault/config.go (L20-32)
```go
func (c *Config) Validate() error {
	if c.RequestExpiryDuration.Duration() <= 0 {
		return errors.New("request expiry duration cannot be 0")
	}
	if c.Auth0 != nil {
		if c.Auth0.IssuerURL == "" {
			return errors.New("auth0 issuerURL is required when auth0 is configured")
		}
		if c.Auth0.Audience == "" {
			return errors.New("auth0 audience is required when auth0 is configured")
		}
	}
	return nil
```

**File:** core/capabilities/vault/gw_handler.go (L97-101)
```go
		jwtAuthService, err = NewJWTBasedAuth(JWTBasedAuthConfig{
			IssuerURL: auth0.IssuerURL,
			Audience:  auth0.Audience,
			TenantID:  auth0.TenantID,
		}, limitsFactory, lggr)
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

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
```

**File:** core/capabilities/vault/jwt_based_auth.go (L46-47)
```go
const (
	defaultJWTAuthJobSpecTenantID uint64 = 1
```

**File:** core/capabilities/vault/jwt_based_auth.go (L137-140)
```go
	expectedTenantID := cfg.TenantID
	if expectedTenantID == 0 {
		expectedTenantID = defaultJWTAuthJobSpecTenantID
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L200-206)
```go
	if claims.TenantID == 0 {
		return nil, ErrMissingTenantID
	}
	if claims.TenantID != v.expectedTenantID {
		v.lggr.Debugw("JWT tenant id does not match job spec auth0 tenantID", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "claimsTenantID", claims.TenantID, "expectedTenantID", v.expectedTenantID)
		return nil, fmt.Errorf("%w: jwt tenant id %d expected tenant id %d", ErrJWTTenantIDJobSpecMismatch, claims.TenantID, v.expectedTenantID)
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L219-223)
```go
	derivedWorkflowOwner, err := DeriveJWTAuthorizedVaultWorkflowOwner(claims.OrgID, claims.TenantID, claims.WorkflowOwner)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to derive authorized workflow owner", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}
```

**File:** core/capabilities/vault/workflow_owner_derivation.go (L14-36)
```go
// DeriveJWTAuthorizedVaultWorkflowOwner derives the JWT-authorized Vault workflow-owner address using
// the same inputs as cre-platform-graphql/internal/service/account_service.go GetCreOrganizationInfo:
//
//	workflows.GenerateWorkflowOwnerAddress(strconv.FormatUint(tenantID, 10), orgID)
//
// tenantID must be non-zero (equivalent to GraphQL rejecting a missing tenant context).
func DeriveJWTAuthorizedVaultWorkflowOwner(orgID string, tenantID uint64, claimedWorkflowOwnerFromJWT string) (string, error) {
	if orgID == "" {
		return "", errors.New("org_id is required for JWT-derived vault workflow owner")
	}
	if tenantID == 0 {
		return "", ErrMissingTenantID
	}
	prefix := strconv.FormatUint(tenantID, 10)
	addr, err := workflows.GenerateWorkflowOwnerAddress(prefix, orgID)
	if err != nil {
		return "", fmt.Errorf("could not derive vault workflow owner address: %w", err)
	}
	derived := common.BytesToAddress(addr).Hex()
	if claimedWorkflowOwnerFromJWT != "" && !strings.EqualFold(strings.TrimSpace(claimedWorkflowOwnerFromJWT), derived) {
		return "", fmt.Errorf("JWT workflow_owner claim %q does not match derived workflow owner %q", claimedWorkflowOwnerFromJWT, derived)
	}
	return derived, nil
```
