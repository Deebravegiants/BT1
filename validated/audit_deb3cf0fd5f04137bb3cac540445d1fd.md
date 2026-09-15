This confirms the claim: the `ExternalInitiatorsEnabled` flag is only checked at creation time in `ExternalInitiatorsController.Create` [1](#0-0) , and `AuthenticateExternalInitiator` never re-checks it before granting `UserRoleRun` [2](#0-1) . The `Authenticate` middleware simply invokes each `authMethod` and grants access on any success, with no additional gating [3](#0-2) .

Audit Report

## Title
External Initiator job-run authentication ignores `JobPipeline.ExternalInitiatorsEnabled`, allowing runs to be triggered even when the feature is disabled - (File: `core/web/auth/auth.go`)

## Summary
The `JobPipeline.ExternalInitiatorsEnabled` config flag is enforced only inside `ExternalInitiatorsController.Create` when a new External Initiator credential is provisioned. The authentication routine invoked on every EI-tagged request, `AuthenticateExternalInitiator`, never re-checks this flag — it only validates the access key/secret against the stored `ExternalInitiator` record and unconditionally grants `UserRoleRun` on success.

## Finding Description
`ExternalInitiatorsController.Create` gates creation of new records on `eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled()` [4](#0-3) . However `AuthenticateExternalInitiator`, the `authMethod` used on every request carrying `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers, only looks up the stored initiator via `store.FindExternalInitiator` and validates the secret via `bridges.AuthenticateExternalInitiator`, then sets `SessionUserKey` to `UserRoleRun` — with no reference to the config flag anywhere in the function [2](#0-1) . The generic `Authenticate` middleware that wires this method into routes performs no additional feature-flag check either; it simply loops through `authMethod`s until one succeeds [3](#0-2) . The `ExternalInitiatorsEnabled` accessor itself is a trivial pass-through of a TOML config value with no dynamic/global disable hook elsewhere in the codebase [5](#0-4) . Thus, disabling the flag only prevents new EI provisioning; it does not revoke the authentication or run-triggering capability of previously issued EI credentials.

## Impact Explanation
This is a genuine authorization-gate bypass: an operator who disables `ExternalInitiatorsEnabled` (e.g., in response to suspected credential leakage or as defense-in-depth) reasonably expects that External-Initiator-triggered job runs are shut off. Instead, any previously created EI credential continues to authenticate and trigger job runs indefinitely, since the check is not part of the reusable `authMethod`/`Authenticate` pipeline. This falls under the "unauthorized job run" impact class, since a lower-trust EI credential holder retains the ability to trigger runs contrary to the node operator's explicit configuration intent.

## Likelihood Explanation
No race condition or unusual timing is required. The only precondition is possession of a previously-issued EI access key/secret pair (which is not privileged relative to the EI trust model — it is exactly the credential the feature is designed to use for run-triggering) and an operator subsequently toggling the config flag off. This is a deterministic, repeatable gap reachable by any holder of valid EI credentials via a normal HTTP request against an EI-authenticated route.

## Recommendation
Add an explicit `store`/config check for `JobPipeline().ExternalInitiatorsEnabled()` inside `AuthenticateExternalInitiator` (or in the `Authenticate` middleware before that method runs), returning `auth.ErrorAuthFailed` when disabled, so toggling the flag off immediately revokes all EI-authenticated job-run triggering, not just future record creation.

## Proof of Concept
1. With `JobPipeline.ExternalInitiatorsEnabled = true`, create an EI via `POST /v2/external_initiators`, obtaining `AccessKey`/`Secret`.
2. Set `JobPipeline.ExternalInitiatorsEnabled = false` and reload/restart the node.
3. Send a request to an EI-authenticated route (any route wired with `AuthenticateExternalInitiator` in `core/web/router.go`) with headers `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` set to the previously issued credential.
4. Observe the request succeeds and is granted `UserRoleRun` per `core/web/auth/auth.go` lines 119-149, despite the feature flag being disabled — confirmed by the absence of any `ExternalInitiatorsEnabled` reference in that function or in the `Authenticate` middleware.

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

**File:** core/services/chainlink/config_job_pipeline.go (L45-47)
```go
func (j *jobPipelineConfig) ExternalInitiatorsEnabled() bool {
	return *j.c.ExternalInitiatorsEnabled
}
```
