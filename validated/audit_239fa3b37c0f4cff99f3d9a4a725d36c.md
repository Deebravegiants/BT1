## Analysis

The route `PATCH /v2/resume/:runID` is registered at `unauthedv2.PATCH("/resume/:runID", prc.Resume)` with **no authentication middleware at all** — it's added to `unauthedv2 := r.Group("/v2")`, which has no `auth.Authenticate(...)` wrapper, unlike every other pipeline/job route in `v2Routes`. [1](#0-0) 

`PipelineRunsController.Resume` takes the `runID` (really a task `uuid.UUID`) directly from the URL path parameter and a `pipeline.ResumeRequest` (value/error) from the raw JSON body, with no ownership or authorization check tying the request to the run/job, and no validation that the caller is entitled to resolve that particular pending task: [2](#0-1) 

This flows into `App.ResumeJobV2` → `pipeline.Runner.ResumeRun` → `orm.UpdateTaskRunResult`, which simply looks up any pipeline run that has a *pending* task with the given `taskID` and is in `running`/`suspended` state, and unconditionally writes the attacker-supplied `Result` (value or error) into that task, then resumes the pipeline: [3](#0-2) [4](#0-3) 

Notably the code path itself even documents the risk — the audit event fired for this action is literally named `UnauthedRunResumed`: [5](#0-4) 

### Analog reasoning

This is directly analogous to the Astaria bug class: a state-transition/settlement function trusts caller-supplied parameters (`params.endTime`) instead of validating them against the authoritative, server-side record of the pending operation (the actual Seaport order). Here, `Resume` trusts a caller-supplied `runID` (task UUID) and result payload with **no authentication and no binding check** to prove the caller is the legitimate resumer of that specific task (e.g., the external adapter/bridge that the task was dispatched to). Anyone who can enumerate or guess a pending task UUID (task UUIDs are returned in job-run API responses to any run-role user, and used as callback identifiers for `AsyncTask`/bridge tasks) can inject/forge the resumption value or error for someone else's in-flight pipeline run, corrupting the run's result before it's used downstream (e.g., feeding a report, an ETH transaction task, or any consumer task with attacker-controlled data), or force premature/incorrect completion of runs belonging to other jobs.

This matches the "concrete authentication bypass / cross-user response confusion / unauthorized job run" categories the validation rules call for, and the root cause (trusting unauthenticated caller data instead of validating against the authoritative run/task ownership) is the same class of bug as the Seaport `endTime` spoofing issue.

### Title
Unauthenticated `/v2/resume/:runID` endpoint allows spoofing pipeline task run results and hijacking any pending job run - (File: `core/web/router.go`)

### Summary
The `PATCH /v2/resume/:runID` route, which resumes a suspended pipeline task with attacker-supplied result data, is registered with no authentication middleware and no ownership check binding the caller to the specific run/task, allowing any unauthenticated network client to inject or corrupt the outcome of in-flight pipeline runs.

### Finding Description
`v2Routes` registers `unauthedv2.PATCH("/resume/:runID", prc.Resume)` on a route group (`unauthedv2 := r.Group("/v2")`) that has no `auth.Authenticate` middleware, in contrast to every other job/pipeline endpoint in the same file which requires session/token or external-initiator auth (`authv2`, `userOrEI`). [1](#0-0) 

`PipelineRunsController.Resume` parses `runID` as a raw `uuid.UUID` from the path and a `pipeline.ResumeRequest` (arbitrary value or error) from the request body, then calls `App.ResumeJobV2` unconditionally: [6](#0-5) 

Downstream, `ResumeRun` calls `orm.UpdateTaskRunResult`, which locates *any* pending task run matching the given task UUID whose parent pipeline run is `running` or `suspended`, and blindly overwrites its output/error with the caller-supplied data, restarting the pipeline: [7](#0-6) [3](#0-2) 

There is no verification that the caller is the legitimate external adapter/bridge that the async task was dispatched to, no secret/token tied to the specific task invocation, and no check that the requester has any authorization over the job/run in question — the endpoint relies solely on the task UUID being unguessable, which is not an authentication mechanism.

### Impact Explanation
Any unauthenticated network client that learns or guesses a pending task UUID (exposed via other authenticated APIs, logs, or bridge/external-adapter callback URLs) can:
- Inject a fabricated success/error value into another job's in-flight pipeline run, corrupting downstream computation, reports submitted on-chain, or any consuming task.
- Prematurely resume/complete a suspended run with attacker-chosen data, potentially causing incorrect ETH transactions or writes if downstream tasks act on the falsified value.
- Cause denial-of-service by forcing arbitrary error states on jobs belonging to other users/tenants of the node.

This is high severity because it is a direct authentication bypass on a state-mutating endpoint that affects job run integrity and, transitively, on-chain transaction data.

### Likelihood Explanation
Likelihood is bounded by whether task UUIDs are treated as a de-facto secret and whether they leak (e.g., through async bridge responses, logs, or other authenticated read endpoints such as `GET /jobs/:ID/runs/:runID`, which any `run`-role user can access). Given the endpoint is completely unauthenticated by design (and the audit log literally labels the event `UnauthedRunResumed`), the barrier to exploitation is solely "knowledge of a pending task UUID," which is a much weaker bar than the intended trust model (only the specific external adapter dispatched for that async task should be able to resume it).

### Recommendation
Bind the resume operation to the specific async task invocation instead of relying on UUID secrecy alone: require the caller to present a per-task credential/secret (e.g., a signed callback token issued when the async/bridge task was dispatched) and validate it against a stored value for that `taskID` before accepting the result — analogous to the recommended fix of storing the Seaport order hash and validating submitted params against it rather than trusting caller-supplied values.

### Proof of Concept
1. Create a job with an async/bridge task (e.g., `type=bridge` or any `AsyncTask`) so a `pipeline_task_runs` row is created in `suspended` state with a task UUID.
2. Obtain the task UUID from any leak vector (e.g., through `GET /jobs/:ID/runs/:runID`, a run role token, or by observing the callback registration to an external adapter).
3. Without any authentication, send: `PATCH /v2/resume/<taskUUID>` with body `{"error": "attacker controlled"}` or `{"value": {"data": "forged"}}`.
4. Observe `UpdateTaskRunResult` accepts the write and resumes the pipeline with the forged value, with no credential check performed — confirmed by the route registration lacking any `auth.Authenticate` middleware in `core/web/router.go`.

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
