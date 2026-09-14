### Title
Unauthenticated `PATCH /v2/resume/:runID` allows any caller to inject arbitrary task results into a pipeline run - ([File: core/web/router.go])

### Summary
The `mintRebalancer()` finding is a case where a state‑mutating function that should only be callable by a trusted, privileged actor (the rebalancer) is instead reachable by anyone, letting them corrupt a value (`collateralFactor()`) that other logic relies on to make security‑relevant decisions. The closest analog in this Chainlink codebase is the `Resume` endpoint of `PipelineRunsController`, which is deliberately mounted on the **unauthenticated** router group and lets any network caller supply the `Value`/`Error` result for a suspended pipeline task, which then resumes and continues execution of that job run.

### Finding Description
In `core/web/router.go`, the `v2Routes` function registers: [1](#0-0) 

`unauthedv2.PATCH("/resume/:runID", prc.Resume)` is registered on the `unauthedv2` group, which has **no** `auth.Authenticate(...)` middleware attached — unlike every other `/v2/...` route, which requires either session or API-token authentication (`authv2 := r.Group("/v2", auth.Authenticate(...))`).

The handler itself, `PipelineRunsController.Resume` in `core/web/pipeline_runs_controller.go`: [2](#0-1) 

accepts a `runID` (a task UUID) from the URL and a JSON body containing a `pipeline.ResumeRequest` (`Value`/`Error`), decodes it into a `pipeline.Result`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` with **no caller identity, role, or ownership check whatsoever**. `ResumeJobV2` forwards directly into the pipeline runner: [3](#0-2) 

which calls `ResumeRun`, updates the task's result in the DB, and if the run is marked to restart, kicks off execution of the rest of the pipeline: [4](#0-3) 

The only implicit "access control" mechanism is that `runID` is a randomly-generated UUID (essentially acting as a bearer secret) — there is no authentication header, no session, no role check, and no verification that the caller is the bridge/adapter that legitimately owns that pending task. The route is explicitly audited with `audit.UnauthedRunResumed`, confirming the code authors are aware this endpoint bypasses the RBAC system used everywhere else in the node's web API (`RequiresRunRole`, `RequiresEditRole`, `RequiresAdminRole`, seen throughout `core/web/router.go`).

### Impact Explanation
Any unprivileged network caller who can guess, intercept, or otherwise obtain a pending task UUID (e.g., via response leakage, logs, or brute force against a low-entropy/short-lived task) can:
- Inject an attacker-controlled `Value`/`Error` result into a suspended pipeline task, exactly analogous to how `mintRebalancer()` let an unprivileged caller inject an attacker-controlled value (`totalSupply`) that fed into downstream security-relevant computation (`collateralFactor()`).
- Cause the resumed pipeline run to execute downstream tasks (e.g., further HTTP requests, on-chain transactions such as VRF fulfillment or OCR reporting flows that route through bridge/async tasks) using falsified data, potentially corrupting job outputs or triggering unintended transactions/state changes, without any authentication.
- Because there is zero role/ownership verification, this constitutes unauthorized manipulation of node-controlled job execution state by an unprivileged actor — the same "any caller can corrupt a value relied upon elsewhere" root cause as the reported bug.

### Likelihood Explanation
Exploitability depends on task-UUID secrecy (UUIDv4 has high entropy, so blind brute force is impractical), but the design still violates the principle applied to every other admin/edit/run-role route in the file — there is no defense-in-depth (rate limiting is only applied to `/sessions`, not `/resume/:runID`), and any leak of a `runID` (logging, error message, bridge response, proxy log) fully compromises that task's integrity with no secondary authentication check.

### Recommendation
Add authentication/authorization consistent with the rest of the `/v2` API (e.g., a bridge/external-initiator-scoped token check, or restrict resumption to a caller that can prove it corresponds to the specific pending bridge callback), and add rate limiting to the unauthenticated `/resume/:runID` group similar to `sessionRoutes`'s use of `rateLimiter(...)` in `core/web/router.go`, since brute-force/guessing risk is not currently mitigated for this route the way it is for `/sessions`.

### Proof of Concept
1. Attacker obtains (or brute forces, if entropy/lifetime allow) a pending task's UUID `runID` for an in-flight async pipeline task (e.g., via a leaked bridge response, application log, or shared proxy log).
2. Attacker sends `PATCH /v2/resume/<runID>` with body `{"value": "<attacker-controlled-value>"}` — no `X-API-KEY`/`X-API-SECRET` or session cookie required, since the route is under `unauthedv2` with no `auth.Authenticate` middleware: [5](#0-4) 
3. `PipelineRunsController.Resume` decodes the body and calls `App.ResumeJobV2`: [6](#0-5) 
4. The pipeline runner writes the attacker-supplied result and resumes/continues executing the rest of the job's DAG with that falsified value, with no verification that the caller was the legitimate bridge/adapter that owns the task: [4](#0-3)

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
