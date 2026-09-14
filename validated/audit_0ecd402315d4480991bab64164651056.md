### Title
External Initiator authentication does not check `ExternalInitiatorsEnabled` after being disabled - (File: core/web/auth/auth.go)

### Summary
The `ExternalInitiatorsEnabled` config flag is only enforced when an external initiator is *created*, not when it is subsequently used to authenticate and trigger job runs. This mirrors the reported bug class: a feature-enable flag exists and is checked at one control point but is never re-checked at the operations it is meant to gate, so disabling the feature after the fact does not actually stop the gated action.

### Finding Description
`ExternalInitiatorsController.Create` checks `eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled()` before allowing creation of a new `ExternalInitiator`: [1](#0-0) 

However, the actual authentication path that lets an external initiator invoke webhook job runs, `AuthenticateExternalInitiator` in `core/web/auth/auth.go`, never checks this flag. It only validates the access key/secret against the stored `ExternalInitiator` record and, on success, sets the run-role session: [2](#0-1) 

`Destroy` (deleting an external initiator) also performs no check of the flag: [3](#0-2) 

Because the flag is a config-level toggle intended to enable/disable the "External Initiator" feature (analogous to `is_staking_enabled` gating stake/unstake), an administrator flipping `JobPipeline.ExternalInitiatorsEnabled` from `true` to `false` (config reload) will block new creation of external initiators, but any external initiator credentials created previously will continue to authenticate successfully and continue to be able to trigger job/webhook runs, since `AuthenticateExternalInitiator` has no gate on the flag.

### Impact Explanation
If an administrator disables the External Initiator feature intending to shut off this attack surface (e.g., in response to a security incident or because credentials were compromised/rotated policy), existing external-initiator credentials remain fully functional for authenticating requests and triggering job runs. This defeats the administrator's expectation that disabling the feature stops all External-Initiator-authenticated actions, and preserves an unintended request-impersonation/authentication path (`SessionExternalInitiatorKey` / `UserRoleRun` context set regardless of the flag) that can be used to trigger arbitrary webhook job runs.

Note: the config doc string in `core/config/docs/core.toml` calls this field "Unused: used to enable... legacy webhook job runs," which suggests the flag may already be considered informally deprecated/unused in current deployments — this weakens (but does not eliminate) the practical severity, since the intended behavior described in code comments is ambiguous. [4](#0-3) 

### Likelihood Explanation
Likelihood is moderate: it requires (1) at least one external initiator having been created while the feature was enabled, and (2) the administrator later disabling the flag with the expectation that this revokes External Initiator access. Given the flag is documented as possibly "unused," it's unclear whether operators actively rely on toggling it at runtime for security purposes, which lowers real-world likelihood of exploitation but does not change the code-level gap.

### Recommendation
Add an explicit `ExternalInitiatorsEnabled()` check inside `AuthenticateExternalInitiator` (and consider `Destroy`) in `core/web/auth/auth.go`, returning `auth.ErrorAuthFailed` (or a clear "feature disabled" error) when the flag is false, so that disabling the feature immediately revokes authentication capability for all existing external initiators, not just blocks new creation.

### Proof of Concept
1. Administrator enables `JobPipeline.ExternalInitiatorsEnabled = true` and a user creates an external initiator via `POST /v2/external_initiators`, receiving `AccessKey`/`Secret`. [5](#0-4) 
2. Administrator disables the feature by setting `JobPipeline.ExternalInitiatorsEnabled = false` and reloads config.
3. The external initiator still sends requests with `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret` headers to endpoints protected by `Authenticate(..., AuthenticateExternalInitiator)`.
4. `AuthenticateExternalInitiator` succeeds because it never checks the `ExternalInitiatorsEnabled` flag, only the stored credential hash, setting the run-role session and permitting the job run trigger to proceed. [6](#0-5)

### Citations

**File:** core/web/external_initiators_controller.go (L62-100)
```go
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	ei, err := bridges.NewExternalInitiator(eia, eir)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := ValidateExternalInitiator(ctx, eir, eic.App.BridgeORM()); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

	resp := presenters.NewExternalInitiatorAuthentication(*ei, *eia)
	jsonAPIResponseWithStatus(c, resp, "external initiator authentication", http.StatusCreated)
}
```

**File:** core/web/external_initiators_controller.go (L102-118)
```go
// Destroy deletes an ExternalInitiator
func (eic *ExternalInitiatorsController) Destroy(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("Name")
	exi, err := eic.App.BridgeORM().FindExternalInitiatorByName(ctx, name)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("external initiator not found"))
		return
	}
	if err := eic.App.BridgeORM().DeleteExternalInitiator(ctx, exi.Name); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorDeleted, map[string]any{"name": name})
	jsonAPIResponseWithStatus(c, nil, "external initiator", http.StatusNoContent)
}
```

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```

**File:** core/config/docs/core.toml (L311-313)
```text
[JobPipeline]
# ExternalInitiatorsEnabled Unused: used to enables the External Initiator feature for legacy webhook job runs via external initiators
ExternalInitiatorsEnabled = false # Default
```
