Found a concrete, unauthenticated-endpoint issue that maps to the requested categories (unauthorized job run / cross-user resume of a pipeline task). This is intentional-by-design in the code (it's named `UnauthedRunResumed`), but it is registered with **no authentication at all** and no ownership check binding the `runID` (task UUID) to any caller identity, which is the closest reachable analog to the "no protection window around a state transition that lets an unprivileged actor act on someone else's position" bug class from the report.

### Title
Unauthenticated `PATCH /v2/resume/:runID` allows any external caller to resume/complete arbitrary pipeline task runs - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `Resume` endpoint used to complete/report results back into a paused pipeline task run (e.g. a webhook/bridge external-adapter callback) is mounted in an explicitly unauthenticated route group and performs no authorization or ownership check tying the caller to the `runID` (task UUID) being resumed.

### Finding Description
The route is registered under `unauthedv2 := r.Group("/v2")` with `unauthedv2.PATCH("/resume/:runID", prc.Resume)` [1](#0-0) , in contrast to every other `/v2` route which sits behind `auth.Authenticate(...)` with token/session/role checks. The handler `PipelineRunsController.Resume` simply parses the `runID` UUID from the URL, decodes the request body into a `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` directly, with the only "acknowledgement" of the lack of auth being that it logs an `audit.UnauthedRunResumed` audit event afterward [2](#0-1) . `ResumeJobV2` forwards straight into `pipelineRunner.ResumeRun`, which updates the task run result in the DB and, if the result completes the run's dependencies, restarts pipeline execution from that point [3](#0-2) [4](#0-3) . There is no verification that the caller is the legitimate external adapter/bridge that owns this specific task-run UUID — any unprivileged network client that can guess or observe a `runID` can inject an arbitrary result/error value and force-resume that pipeline run.

### Impact Explanation
An unprivileged, unauthenticated actor can inject a forged `Result`/`Error` value into someone else's paused pipeline task run and trigger continuation of that job's execution with attacker-controlled data. Depending on the job's downstream tasks (e.g., an ETH transaction task keyed off the injected value), this can lead to unauthorized/incorrect job execution or cross-user response confusion, matching the "unauthorized job run" and "cross-user response confusion" categories called out in scope.

### Likelihood Explanation
Exploitability depends on the attacker being able to guess or otherwise obtain a valid `runID` (a UUID), since the route requires no credentials whatsoever — this is a meaningfully lower bar than any authenticated endpoint in the same router file, all of which require a token/session and role check [5](#0-4) . UUIDs are not inherently secret and may leak via job-run listings, logs, or webhook responses, making this a realistic low-privilege network path rather than a purely theoretical one.

### Recommendation
Bind resume authorization to the specific pending task/run rather than trusting an unauthenticated caller with only the UUID — e.g., require a per-run bearer secret (already generated for webhook/bridge callbacks) to be validated inside `Resume` before calling `ResumeJobV2`, or move this route behind the same `auth.Authenticate` + role-check middleware used for the rest of `/v2`, falling back to a scoped, single-use callback token model if external, credential-less systems must be able to call it.

### Proof of Concept
1. Create any job with a task that pauses pending an external callback (e.g., a bridge/external-adapter task), and note or observe the run's `runID` (UUID).
2. As an unauthenticated client, send `PATCH /v2/resume/<runID>` with a crafted JSON body matching `pipeline.ResumeRequest` (e.g., `{"value": "<attacker-controlled>"}`).
3. Observe that `PipelineRunsController.Resume` accepts the request without any credentials, calls `prc.App.ResumeJobV2`, and the pipeline run resumes/completes using the attacker-supplied value — confirmed by the code path at [2](#0-1)  being reachable purely through the unauthenticated group registered at [6](#0-5) .

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

**File:** core/web/pipeline_runs_controller.go (L134-160)
```go
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
```

**File:** core/services/chainlink/application.go (L1237-1243)
```go
func (app *ChainlinkApplication) ResumeJobV2(
	ctx context.Context,
	taskID uuid.UUID,
	result pipeline.Result,
) error {
	return app.pipelineRunner.ResumeRun(ctx, taskID, result.Value, result.Error)
}
```

**File:** core/services/pipeline/runner.go (L732-755)
```go
func (r *runner) ResumeRun(ctx context.Context, taskID uuid.UUID, value any, err error) error {
	run, start, err := r.orm.UpdateTaskRunResult(ctx, taskID, Result{
		Value: value,
		Error: err,
	})
	if err != nil {
		return fmt.Errorf("failed to update task run result: %w", err)
	}

	// TODO: Should probably replace this with a listener to update events
	// which allows to pass in a transactionalised database to this function
	if start {
		// start the runner again
		go func() {
			ctx, cancel := r.chStop.NewCtx()
			defer cancel()
			if _, err := r.Run(ctx, &run, false, nil); err != nil {
				r.lggr.Errorw("Resume run failure", "err", err)
			}
			r.lggr.Debug("Resume run success")
		}()
	}
	return nil
}
```
