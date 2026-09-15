### Title
External Initiator job-run authentication ignores `JobPipeline.ExternalInitiatorsEnabled`, allowing runs to be triggered even when the feature is disabled - (File: `core/web/auth/auth.go`)

### Summary
The External Initiator ("EI") feature has a config gate, `JobPipeline.ExternalInitiatorsEnabled`, that is checked only at *creation* time. The authentication path used to accept EI-triggered job runs never re-checks this flag, so once an External Initiator credential exists, it remains fully functional to trigger job runs regardless of whether the feature has since been disabled by the operator. This mirrors the reported bug class: a "completed"/"active" state (successful EI authentication and run-trigger authorization) can be reached even though the prerequisite "required"/"enabled" condition is not satisfied.

### Finding Description
`ExternalInitiatorsController.Create` explicitly gates creation of new External Initiators on the config flag: [1](#0-0) 

However, the actual authentication method invoked on every incoming request tagged with EI headers, `AuthenticateExternalInitiator`, performs no equivalent check. It only validates the access key/secret pair against the stored `ExternalInitiator` record and, on success, unconditionally grants the `run` role: [2](#0-1) 

This function is one of the `authMethod`s composed by the generic `Authenticate` middleware and reused across any route wired with `AuthenticateExternalInitiator`, so the "feature enabled" check is not part of the reusable authorization path — it only exists as a one-off guard in the creation controller: [3](#0-2) 

Because the config flag is read only at record-creation time and never again, any External Initiator record created while the feature was enabled continues to authenticate successfully and receive `UserRoleRun` even after an operator later sets `ExternalInitiatorsEnabled = false`, expecting to shut off this attack surface.

### Impact Explanation
`JobPipeline.ExternalInitiatorsEnabled` is documented and used by operators as a kill switch for the External Initiator feature, which allows an external, less-trusted caller to remotely trigger job runs using only an access key/secret pair (no session, no admin role). If disabling the flag does not actually revoke this authentication/run-trigger capability, an operator who disables the feature (e.g., in response to an incident, credential leak, or as defense-in-depth) will incorrectly believe that External Initiator authenticated job-run triggering has been shut off, while any already-existing EI credentials continue to work. This is an authentication/authorization-gate bypass for job-run triggering — a legitimate "unauthorized job run" bypass reachable purely from an unprivileged/external network caller holding EI credentials, matching the acceptance criteria.

### Likelihood Explanation
This does not require exploiting a race condition or edge case — it is a straightforward, deterministic gap: the disable flag is simply never consulted outside of the create path. Any environment where the operator toggles `ExternalInitiatorsEnabled` off after initiators were already provisioned is affected, and this is a realistic and commonly expected operational action.

### Recommendation
Add an explicit check for `JobPipeline().ExternalInitiatorsEnabled()` inside `AuthenticateExternalInitiator` (or in the `Authenticate` middleware pipeline before granting the `run` role via this auth method), returning `auth.ErrorAuthFailed` when the feature is disabled, so that toggling the config flag off immediately and completely revokes External-Initiator-triggered job runs, consistent with the enforcement already done at creation time.

### Proof of Concept
1. Enable `JobPipeline.ExternalInitiatorsEnabled = true`.
2. Create an External Initiator via `POST /v2/external_initiators` — this succeeds per the check in `ExternalInitiatorsController.Create` [4](#0-3) , returning an `AccessKey`/`Secret`.
3. Operator sets `JobPipeline.ExternalInitiatorsEnabled = false` and restarts/reloads config, intending to disable the feature.
4. Using the previously issued `AccessKey`/`Secret`, send a request to an EI-authenticated route (e.g., a webhook job run trigger) with headers `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret`.
5. `AuthenticateExternalInitiator` in `core/web/auth/auth.go` (lines 119-149) does not check the `ExternalInitiatorsEnabled` config at all — it authenticates successfully and assigns `UserRoleRun`, allowing the job run to be triggered despite the feature being "disabled."

### Citations

**File:** core/web/external_initiators_controller.go (L62-90)
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

**File:** core/web/auth/auth.go (L153-173)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
}
```
