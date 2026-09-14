### Title
Unauthenticated `PATCH /v2/resume/:runID` Endpoint Accepts Attacker-Controlled Payload to Resume/Complete Pipeline Runs - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `Resume` endpoint that finalizes a suspended pipeline task is mounted with **no authentication middleware** at all, unlike every other privileged mutation route in the router. Any unauthenticated network caller who can guess or intercept a `runID` (task UUID) can submit an arbitrary JSON payload that is decoded and fed directly into the node's pipeline runner as the resumed task's result/error, controlling downstream execution of that job run.

### Finding Description
In `core/web/router.go`, the route is registered on the unauthenticated group, before any `auth.Authenticate` middleware is applied: [1](#0-0) 

Compare this to every other mutating pipeline/job route, which is registered under `authv2` (session or API-token authenticated) or `userOrEI` (external-initiator/token/session authenticated with `RequiresRunRole`): [2](#0-1) [3](#0-2) 

The handler itself performs zero identity or ownership checks — it only parses the `runID` path param, JSON-decodes the request body into a `pipeline.ResumeRequest`, and calls `App.ResumeJobV2` directly: [4](#0-3) 

This means the "authenticity" of the resume request is verified solely by knowledge of the run's UUID — there is no signature, token, or session check comparable to `AuthenticateExternalInitiator`/`AuthenticateByToken` used elsewhere: [5](#0-4) 

This is structurally the same bug class as the reported RustDesk issue: a state-changing "command" (here, resuming/completing a suspended job run with attacker-supplied result data) is accepted from an unauthenticated/unprivileged network path purely based on possessing an opaque identifier in the payload, with no verification of the sender's authenticity or authorization to control that specific pipeline run.

### Impact Explanation
An attacker who obtains or brute-forces a `runID` (e.g., via logs, error messages, or a leaked link used by an async task) can inject arbitrary resume data or error values into a live pipeline run. Depending on the job's downstream tasks (e.g., ETH transactions, bridge calls), this can influence job outcomes, cause resource exhaustion by repeatedly hitting the endpoint (self-acknowledged by the dedicated audit event `UnauthedRunResumed`), or corrupt pipeline state — all without any credential.

### Likelihood Explanation
The route requires only knowledge of a run UUID, no credentials. While UUIDs provide some obscurity, this is the only barrier; the design intentionally treats this endpoint as unauthenticated (confirmed by the explicit `audit.UnauthedRunResumed` log entry name), so likelihood of exploitation depends entirely on UUID exposure/predictability rather than any cryptographic or session-based control.

### Recommendation
- Tie resumption to a per-run secret/token issued at suspension time (not just the run UUID) and verify it in `Resume`, or require the same `AuthenticateExternalInitiator`/API-token flow used by other job-run endpoints.
- Rate-limit and audit-log all resume attempts (partially done already) and reject resumes for runs not in an awaiting/suspended state to reduce blast radius even if the UUID leaks.

### Proof of Concept
1. Discover or guess a suspended run's UUID (`runID`), e.g., from logs/telemetry.
2. Send `PATCH /v2/resume/<runID>` with a crafted JSON body matching `pipeline.ResumeRequest` (no auth headers needed):
```
curl -X PATCH https://node/v2/resume/<runID> -d '{"error":null,"value":"<attacker-controlled>"}'
```
3. The request is accepted and processed by `PipelineRunsController.Resume` → `App.ResumeJobV2`, with no authentication check performed, as shown at [6](#0-5)  and [7](#0-6) .

### Citations

**File:** core/web/router.go (L238-248)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L391-401)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))

		// PipelineRunsController
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)
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

**File:** core/web/pipeline_runs_controller.go (L131-161)
```go
// Resume finishes a task and resumes the pipeline run.
// Example:
// "PATCH <application>/jobs/:ID/runs/:runID"
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	rr := pipeline.ResumeRequest{}
	decoder := json.NewDecoder(c.Request.Body)
	err = errors.Wrap(decoder.Decode(&rr), "failed to unmarshal JSON body")
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	result, err := rr.ToResult()
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
	c.Status(http.StatusOK)
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
