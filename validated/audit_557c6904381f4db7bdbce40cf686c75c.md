This confirms a genuine unprivileged-actor analog to the reported bug class.

### Title
Unauthenticated pipeline-run resumption via `PATCH /v2/resume/:runID` allows any external actor to inject arbitrary task results into another user's job run - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `partialWithdrawFromGauge()` bug is fundamentally a missing-ownership-check issue: an ID-bearing operation is exposed to any caller who can guess/observe the ID, with no verification that the caller is the entity that created/owns the underlying resource. The chainlink analog is the `Resume` endpoint of `PipelineRunsController`, registered in the **unauthenticated** route group and keyed only by a `taskID` UUID, with no check that the caller is authorized for the job/run being resumed.

### Finding Description
In `core/web/router.go`, the route is registered outside of any auth middleware group: [1](#0-0) 
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
Unlike every other pipeline-runs route (`GET /pipeline/runs`, `GET /jobs/:ID/runs`, etc.), which sit under `authv2` and require session/token auth, `unauthedv2.PATCH("/resume/:runID", ...)` requires no authentication at all.

The handler itself performs no ownership or ACL check against the `taskID`: [2](#0-1) 
```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
	c.Status(http.StatusOK)
}
```
This flows straight into `ResumeJobV2` → `runner.ResumeRun`, which updates the task's result and resumes pipeline execution using whatever `Result` value/error the caller supplied: [3](#0-2) [4](#0-3) 

The design intent (mirrored by the presence of the `audit.UnauthedRunResumed` audit event name) is that this endpoint's security boundary is meant to be the secrecy/unguessability of the `taskID` UUID (analogous to how the Depositor contract relies on `_isApprovedOrOwner`/possession of an NFT id as its only access check) — but there is no cryptographic binding, expiry, single-use enforcement, or resource-owner check tying the caller to the specific bridge/task/job that produced that ID. Any party who obtains or guesses a valid pending task UUID (e.g., via logs, error messages, monitoring tools, or bridge callbacks that echo the ID) can resume — and therefore inject a forged result into — someone else's suspended pipeline run, exactly as `partialWithdrawFromGauge()` let anyone who knew an NFT id complete a withdrawal because ownership was never re-checked.

### Impact Explanation
An unprivileged, unauthenticated caller who obtains a pending task's UUID can:
- Force premature/incorrect completion of another user's job run by supplying an attacker-controlled `Result.Value`/`Result.Error`, corrupting downstream on-chain writes/reports produced by that pipeline (e.g., bridge/external-adapter responses feeding an OCR/VRF/Keeper job).
- Cause denial of service by resuming a run early with an error, aborting legitimate execution.
- This is a cross-user response-confusion / unauthorized-run-completion primitive comparable in severity to the original "steal other people's funds" pattern, since a poisoned pipeline result can directly affect fund-moving downstream tasks (e.g. `ethtx` tasks) driven by the job pipeline.

### Likelihood Explanation
The route requires no authentication credentials whatsoever — only knowledge of a `taskID` UUID. While UUIDs are not brute-forceable, this endpoint's only defense is ID secrecy, which is a weaker security boundary than the rest of the node's role-based auth. Any leak of the run/task ID (audit logs, monitoring dashboards, external adapter/bridge responses that echo it, or accidental exposure) turns into a full authorization bypass, unlike `withdrawFromGauge`-style operations elsewhere in the codebase that pair ID lookups with authenticated session/token checks.

### Recommendation
Require authentication on `/v2/resume/:runID` (move it into the `authv2` group, at minimum requiring `auth.AuthenticateByToken`/`AuthenticateBySession`), and additionally verify in `PipelineRunsController.Resume` / `ResumeJobV2` that the authenticated caller (or the specific external-initiator/bridge integration tied to the job) is authorized to resume the specific task/run identified by `taskID`, rather than relying solely on UUID possession as the access-control mechanism.

### Proof of Concept
1. Start a job containing a suspended/async bridge task; note the run's `pipeline_task_runs.id` (UUID) that is emitted, e.g., in an external adapter's callback URL or in application logs/monitoring.
2. As an unauthenticated third party (no session cookie, no API key), send:
   ```
   PATCH /v2/resume/<observed-taskID>
   Content-Type: application/json

   {"value": "9999", "error": null}
   ```
3. The request succeeds with `200 OK` and no credentials, and `ResumeJobV2` completes the victim's pipeline run using the attacker-supplied value — confirmed by the unauthenticated route registration at [5](#0-4)  and the absence of any authorization check in the handler at [6](#0-5) .

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
