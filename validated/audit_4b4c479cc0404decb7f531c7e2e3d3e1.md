The code matches the claim exactly: `ExternalInitiatorsEnabled()` is checked only in `ExternalInitiatorsController.Create` [1](#0-0) , while `AuthenticateExternalInitiator` performs no such check before granting the `run` role [2](#0-1) , and this method is wired directly into the run-triggering route in `router.go` [3](#0-2) .

Audit Report

## Title
`ExternalInitiatorsEnabled` kill-switch is not enforced at authentication/run time, allowing already-issued External Initiator credentials to keep triggering job runs after the feature is disabled - (File: `core/web/auth/auth.go`)

## Summary
The `JobPipeline.ExternalInitiatorsEnabled` config flag is checked only when provisioning a new External Initiator via `ExternalInitiatorsController.Create`, but is never re-checked in `AuthenticateExternalInitiator` or in the `userOrEI` route group that handles `POST /v2/jobs/:ID/runs`. As a result, an already-issued External Initiator credential continues to authenticate and trigger job runs even after an operator disables the flag, defeating its purpose as a kill switch.

## Finding Description
`ExternalInitiatorsController.Create` gates only creation of new credentials on the flag [1](#0-0) . The `AuthenticateExternalInitiator` middleware, which validates an EI's `AccessKey`/`Secret` and unconditionally assigns the `run` role, has no reference to `JobPipeline().ExternalInitiatorsEnabled()` at all [2](#0-1) . This middleware is chained directly into the `userOrEI` group that serves `POST /v2/jobs/:ID/runs` [3](#0-2) . No other code path re-validates the flag before granting run privileges to an EI-authenticated request, confirming the described gap is real and not mitigated elsewhere in the file.

## Impact Explanation
This maps to the in-scope "unauthorized job run" impact category: an operator disabling the feature flag as an incident-response measure would reasonably expect all External-Initiator-driven job execution to stop, but existing credentials remain fully functional for triggering runs via `RequiresRunRole(prc.Create)`. This is a genuine logic bug — the flag's enforcement is incomplete/asymmetric between the provisioning and usage code paths.

## Likelihood Explanation
Exploitation requires only a previously issued, valid External Initiator `AccessKey`/`Secret` pair — no privilege escalation, race condition, or additional access needed. This is deterministic and trivially repeatable by any actor who already holds legitimate EI credentials, which is exactly the population the kill switch is meant to cut off.

## Recommendation
Add an `ExternalInitiatorsEnabled()` check inside `AuthenticateExternalInitiator` (or in the `userOrEI` route-group middleware chain in `router.go`) so that disabling the config flag immediately blocks authentication/run-triggering for all External Initiators, not just new registrations.

## Proof of Concept
1. Start a node with `JobPipeline.ExternalInitiatorsEnabled = true`.
2. `POST /v2/external_initiators` to create an EI and record its `AccessKey`/`Secret`.
3. Set `JobPipeline.ExternalInitiatorsEnabled = false` and restart/reload config.
4. Confirm `POST /v2/external_initiators` now fails with "The External Initiator feature is disabled by configuration" (per `core/web/external_initiators_controller.go` lines 65-69).
5. Using the previously issued credentials, send `POST /v2/jobs/:ID/runs` with `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers. Observe the request succeeds because `AuthenticateExternalInitiator` (`core/web/auth/auth.go` lines 119-149) never checks the flag, proving the kill switch does not stop already-provisioned initiators from triggering runs.

### Citations

**File:** core/web/external_initiators_controller.go (L62-69)
```go
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}
```

**File:** core/web/auth/auth.go (L119-149)
```go
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

**File:** core/web/router.go (L449-456)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
```
