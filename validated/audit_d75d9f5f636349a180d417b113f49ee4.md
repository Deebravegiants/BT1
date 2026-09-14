Confirmed: the `PATCH /v2/resume/:runID` endpoint is registered in `unauthedv2` (no session/token/EI auth middleware at all), and the audit event fired on success is literally named `audit.UnauthedRunResumed`. [1](#0-0) [2](#0-1) 

### Title
Unauthenticated pipeline-run resume endpoint allows any client to inject arbitrary results into another user's suspended job run - ([File: core/web/pipeline_runs_controller.go])

### Summary
`PipelineRunsController.Resume` handles `PATCH /v2/resume/:runID`, which is mounted on the `unauthedv2` route group with no session, token, or external-initiator authentication middleware. The only "authorization" for this endpoint is possession of the `runID` (a `uuid.UUID` task ID), which is treated as an implicit bearer capability. Anyone who can guess, intercept, or brute-force a pending task's UUID can call this endpoint and inject an arbitrary `pipeline.Result` (value or error) to resume someone else's suspended pipeline run, exactly analogous to the reported bug class: a state-mutating operation (`close`/`resume`) that omits the ownership/authorization check its sibling read-paths implicitly rely on.

### Finding Description
The route table shows `unauthedv2.PATCH("/resume/:runID", prc.Resume)` is deliberately excluded from the `auth.Authenticate(...)` middleware chain applied to every other v2 API route (`authv2`, `userOrEI`). [1](#0-0) 

Inside `Resume`, the only validation performed is that the path parameter parses as a UUID and that the JSON body deserializes into a `ResumeRequest`; there is no lookup of a caller identity, no comparison against the job/run owner, and no capability-scoping beyond the UUID itself: [3](#0-2) 

`ResumeJobV2` forwards directly to `pipelineRunner.ResumeRun`, which calls `orm.UpdateTaskRunResult(ctx, taskID, result)` and, if the run's state transitions to running, resumes execution with the attacker-supplied `Result.Value`/`Result.Error` — no ownership check is performed anywhere in this call chain. [4](#0-3) [5](#0-4) [6](#0-5) 

This design intentionally mirrors a bridge-callback pattern (the task ID is embedded in the `ResponseURL` sent to external bridge adapters, e.g. `http://localhost:6688/v2/resume/<taskID>`), so the unguessable UUID is meant to act as a capability token in place of session/API-key auth [7](#0-6) . However, unlike the vault gateway (`GatewayVaultRequestProcessor`/`allowListBasedAuth`) or the external-initiator flow (`AuthenticateExternalInitiator`), which layer an owner/allowlist check on top of any credential, `/v2/resume/:runID` has zero additional authorization beyond the UUID match, and the UUID is neither rate-limited against brute force at the per-ID level nor bound to a specific caller/session at creation time.

### Impact Explanation
Successful exploitation lets an unprivileged network client controlling only the UUID:
- Force-complete or force-fail another user's suspended async bridge/pipeline task with attacker-chosen data, potentially corrupting downstream job pipeline results (e.g., price feeds, OCR observations) that other users' jobs consume.
- Trigger unintended resumption of a pipeline run, causing side effects (further HTTP calls, on-chain transactions if `ethtx`/median tasks continue) using forged data.

The blast radius depends entirely on whether `runID`/task UUIDs can be discovered by non-owners (e.g., via logs, shared bridge adapters, timing side channels, or predictable generation), which is not established/refuted by this codebase alone.

### Likelihood Explanation
Likelihood is bounded by the entropy and secrecy of the UUID `taskID`: if `uuid.New()` (random v4) is used and never leaked to non-owners, brute force is infeasible. But architecturally the endpoint provides **no defense in depth** — there is no secondary authentication factor, no per-run owner binding, and no audit trail beyond a bare "resumed" log tagged `UnauthedRunResumed`, which is itself evidence the maintainers are aware this route is intentionally unauthenticated and rely solely on UUID secrecy. Any leak of a taskID (logging, external adapter misconfiguration, proxy logs, referer headers) is sufficient for exploitation, with no ownership check as a second line of defense — unlike the Parcl `partial_close_position` bug, where the fix was to add exactly this kind of ownership check the sibling function already had.

### Recommendation
Add resume-request authorization comparable to the sibling `POST /v2/jobs/:ID/runs` path (which does require `auth.RequiresRunRole`): bind each suspended task to the originating job/run owner or external-initiator identity at creation time, and validate that identity (or at minimum an additional shared secret/HMAC over the taskID) on `Resume` before calling `ResumeJobV2`. If UUID-only capability access is intentional, harden it by using a signed/HMAC-tagged token instead of a bare `uuid.New()` value, and ensure it is never logged or exposed to third parties.

### Proof of Concept
1. Create (or observe) any webhook/bridge job that produces an async task with a `ResponseURL` such as `http://<node>/v2/resume/<taskID>`.
2. As an unauthenticated attacker who obtains or guesses `<taskID>` (e.g., via a compromised proxy log, shared bridge server logs, or predictable UUID generation), send:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"value": "<attacker-controlled data>"}
   ```
3. No `Authorization`, session cookie, or API key is required — `unauthedv2.PATCH("/resume/:runID", prc.Resume)` accepts the request directly and resumes the pipeline run with attacker-supplied data, without ever verifying that the caller is the job's owner or the legitimate bridge adapter.

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

**File:** core/services/pipeline/orm.go (L271-308)
```go
func (o *orm) UpdateTaskRunResult(ctx context.Context, taskID uuid.UUID, result Result) (run Run, start bool, err error) {
	if result.OutputDB().Valid && result.ErrorDB().Valid {
		panic("run result must specify either output or error, not both")
	}
	err = o.transact(ctx, func(tx *orm) error {
		sql := `
		SELECT pipeline_runs.*, pipeline_specs.dot_dag_source "pipeline_spec.dot_dag_source", job_pipeline_specs.job_id "job_id"
		FROM pipeline_runs
		JOIN pipeline_task_runs ON (pipeline_task_runs.pipeline_run_id = pipeline_runs.id)
		JOIN pipeline_specs ON (pipeline_specs.id = pipeline_runs.pipeline_spec_id)
		JOIN job_pipeline_specs ON (job_pipeline_specs.pipeline_spec_id = pipeline_specs.id)
		WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended')
		FOR UPDATE`
		if err = tx.ds.GetContext(ctx, &run, sql, taskID); err != nil {
			return fmt.Errorf("failed to find pipeline run for task ID %s: %w", taskID.String(), err)
		}

		// Update the task with result
		sql = `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1`
		if _, err = tx.ds.ExecContext(ctx, sql, taskID, result.OutputDB(), result.ErrorDB(), time.Now()); err != nil {
			return fmt.Errorf("failed to update pipeline task run: %w", err)
		}

		if run.State == RunStatusSuspended {
			start = true
			run.State = RunStatusRunning

			sql = `UPDATE pipeline_runs SET state = $2 WHERE id = $1`
			if _, err = tx.ds.ExecContext(ctx, sql, run.ID, run.State); err != nil {
				return fmt.Errorf("failed to update pipeline run state: %w", err)
			}
		}

		return loadAssociations(ctx, tx.ds, []*Run{&run})
	})

	return run, start, err
}
```

**File:** core/services/pipeline/runner_test.go (L799-799)
```go
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
```
