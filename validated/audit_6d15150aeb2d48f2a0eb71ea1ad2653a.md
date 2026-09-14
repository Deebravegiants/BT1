## Analog Vulnerability Found

### Title
`ExternalInitiatorsEnabled` config flag is not enforced during authentication, allowing existing External Initiator credentials to keep triggering job runs after the feature is disabled - (File: `core/web/auth/auth.go`)

### Summary
The Mattermost CVE-2023-3586 bug class is: disabling a feature flag ("Enable Publicly-Shared Boards") does not retroactively revoke access to resources that were exposed while the flag was enabled. Chainlink has the same pattern with the `JobPipeline.ExternalInitiatorsEnabled` config flag and External Initiator (EI) credentials.

### Finding Description
The EI feature flag is checked **only** at creation time, in `ExternalInitiatorsController.Create`: [1](#0-0) 

No other code path re-checks `ExternalInitiatorsEnabled`. In particular, the authentication middleware `AuthenticateExternalInitiator` validates the EI's access key/secret against the `external_initiators` DB table and grants a `run`-role session with no reference to the config flag at all: [2](#0-1) 

This middleware is wired directly into the job-run trigger route in the router: [3](#0-2) 

So once an EI credential exists in the database (created while the feature was enabled), it remains fully functional for `POST /v2/jobs/:ID/runs` indefinitely, even after an operator flips `ExternalInitiatorsEnabled = false` in config to shut the feature off. The `Destroy` endpoint (`DELETE /v2/external_initiators/:Name`) also performs no enabled-flag check, but deletion is an explicit admin action — the bug is that *disabling the feature config* alone does nothing to existing credentials, exactly mirroring "disabling publicly-shared boards" not disabling already-shared boards.

### Impact Explanation
An operator who disables `ExternalInitiatorsEnabled` (e.g., to shut down the legacy webhook/EI feature for security reasons) reasonably expects that all EI-based access is cut off. Instead, any previously issued EI access key/secret pair continues to authenticate as `UserRoleRun` and can trigger arbitrary job runs via `/v2/jobs/:ID/runs`. If the intent of disabling the flag was to close off an unwanted/legacy external attack surface, that surface stays open, and an external actor holding old EI credentials retains unauthorized "Run"-role job-triggering ability against operator expectation of the config.

### Likelihood Explanation
Requires possession of an EI's `AccessKey`/`Secret` (issued previously), which is the same requirement as in the intended-enabled state — so no new secret is needed. The only precondition is that the config flag was toggled off after EI records existed, which is a realistic operational scenario (feature deprecation/security hardening) and matches the CVE's precondition exactly.

### Recommendation
Enforce `ExternalInitiatorsEnabled` at authentication time in `AuthenticateExternalInitiator` (and/or at the route-group level in `v2Routes`), rejecting EI auth attempts with `auth.ErrorAuthFailed` when the flag is disabled, regardless of whether matching DB records exist. Optionally, also enforce the check in `Destroy`/`Index` for full consistency, and consider purging or invalidating existing EI records when the feature is disabled.

### Proof of Concept
1. Start a node with `JobPipeline.ExternalInitiatorsEnabled = true`.
2. Create an EI via `POST /v2/external_initiators` (admin/edit-role) and record `AccessKey`/`Secret`.
3. Set `JobPipeline.ExternalInitiatorsEnabled = false` and restart/reload the node config (no DB cleanup of the EI record).
4. Send `POST /v2/jobs/:ID/runs` with headers `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret` set to the values from step 2.
5. Observe the request succeeds (HTTP 200/201) and a job run is triggered, despite the feature being disabled — as `AuthenticateExternalInitiator` never checks `App.GetConfig().JobPipeline().ExternalInitiatorsEnabled()`.

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
