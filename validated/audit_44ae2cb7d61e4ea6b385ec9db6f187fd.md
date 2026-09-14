### Title
`ExternalInitiatorsEnabled` kill‑switch is not enforced at authentication/run time, allowing already‑issued External Initiator credentials to keep triggering job runs after the feature is disabled - (File: `core/web/auth/auth.go`, `core/web/external_initiators_controller.go`, `core/web/router.go`)

### Summary
The reported bug class is: a "pause"/kill‑switch gate is checked in some code paths but not others, so entities that already hold standing (open positions in the original report; here, already‑issued External Initiator credentials) can keep operating after the operator believes the feature has been disabled. The analog in this repo is the `JobPipeline.ExternalInitiatorsEnabled` config flag, which is only checked when *creating* a new External Initiator, not when authenticating an existing one or when it triggers a job run.

### Finding Description
`ExternalInitiatorsController.Create` gates creation of new External Initiators on the feature flag: [1](#0-0) 

However, the middleware chain used to authenticate an External Initiator and let it trigger a job run never re-checks this flag: [2](#0-1) 

This `AuthenticateExternalInitiator` method is wired directly into the router for the run-triggering endpoint, alongside `AuthenticateByToken`/`AuthenticateBySession`, with no additional feature-flag check: [3](#0-2) 

Once authenticated, `AuthenticateExternalInitiator` unconditionally grants the request the `run` role: [4](#0-3) 

So if an operator disables `JobPipeline.ExternalInitiatorsEnabled` (e.g., as an incident-response kill switch, intending to cut off all External-Initiator-driven job execution), any External Initiator credential that was issued while the feature was enabled continues to authenticate successfully and can keep calling `POST /v2/jobs/:ID/runs` — the flag only blocks the `Create` endpoint for provisioning *new* initiators, not usage of existing ones.

### Impact Explanation
This is a security-relevant "pause" bypass exactly matching the accepted category "unauthorized job run": disabling the feature is supposed to be a global stop of External-Initiator-triggered execution, but it silently fails to revoke already-issued credentials. An operator relying on this flag to shut off an untrusted or compromised External Initiator (or as part of an incident response) would falsely believe job runs from that initiator are blocked, while in fact the initiator can still authenticate (`AuthenticateExternalInitiator`) and post runs (`RequiresRunRole(prc.Create)`), causing continued unintended job execution/fund-affecting pipeline runs.

### Likelihood Explanation
Any actor already holding a valid External Initiator `AccessKey`/`Secret` pair (which is the intended trust boundary for this feature) can exploit this trivially and deterministically — no privilege escalation or race condition is required, just continuing to send requests after the flag is toggled off. The only precondition is that the External Initiator was created before the flag was disabled, which is the exact scenario the flag is meant to protect against.

### Recommendation
Enforce `JobPipeline().ExternalInitiatorsEnabled()` in `AuthenticateExternalInitiator` (or in the `userOrEI` route group in `router.go`) so that once the feature is disabled, existing External Initiator credentials immediately stop authenticating/triggering runs, not just block creation of new ones.

### Proof of Concept
1. Start a node with `JobPipeline.ExternalInitiatorsEnabled = true`.
2. Create an External Initiator via `POST /v2/external_initiators` and record its `AccessKey`/`Secret` [5](#0-4) .
3. Operator flips config to `JobPipeline.ExternalInitiatorsEnabled = false` (intending to disable all EI activity).
4. Attempt `POST /v2/external_initiators` again — this now fails with "The External Initiator feature is disabled by configuration" [6](#0-5) , confirming the flag is applied.
5. Using the previously issued credentials, call `POST /v2/jobs/:ID/runs` with headers `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` through the `userOrEI` route group [3](#0-2) . The request succeeds because `AuthenticateExternalInitiator` never checks the config flag [2](#0-1) , demonstrating the kill switch does not actually stop already-provisioned initiators from triggering runs.

### Citations

**File:** core/web/external_initiators_controller.go (L62-99)
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
