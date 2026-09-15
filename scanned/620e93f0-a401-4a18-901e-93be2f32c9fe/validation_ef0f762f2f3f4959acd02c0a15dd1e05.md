## Finding

### Title
Unauthenticated `/v2/resume/:runID` Endpoint Allows Duplicate/Replay Resume of an Already-Finished Pipeline Task Run - (File: core/services/pipeline/orm.go)

### Summary
The bug class in the report is a missing "already used" guard that lets the same claim identifier be replayed to repeat a privileged state transition. The Chainlink node has an analogous, unauthenticated endpoint for resuming asynchronous pipeline task runs whose SQL guard checks only the parent run's state, not whether the specific task run has already been completed, allowing the same task-run ID to be "resumed" (its recorded output/error overwritten) more than once.

### Finding Description
The route `PATCH /v2/resume/:runID` is registered outside any authentication middleware: [1](#0-0) 

It is handled by `PipelineRunsController.Resume`, which parses an attacker-supplied `taskID` (a UUID) and a `value`/`error` result and forwards it, unauthenticated, to `ResumeJobV2` → `pipelineRunner.ResumeRun` → `orm.UpdateTaskRunResult`: [2](#0-1) [3](#0-2) 

`UpdateTaskRunResult` is the sole gate protecting against reuse. It selects the run by joining on `pipeline_task_runs.id = $1` but filters only on the **run's** state (`running`/`suspended`), never checking whether the specific **task run** identified by `$1` already has `finished_at` set: [4](#0-3) 

The subsequent `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1` is unconditional — it will overwrite a task run's result even if that same task run ID was already resumed with a legitimate answer, as long as the parent pipeline run has not yet reached a terminal state (which, for multi-task pipelines with several async/pending branches, can remain `running`/`suspended` for an extended window). This is the same root-cause pattern as the reported issue: the "claim" (task-run UUID) is not marked/checked as already consumed (`claimId[_claimId]` / `require(!claimId[_claimId])`) before the payoff-equivalent action (`finished_at`/`output` write and restart of the pipeline) is performed again.

### Impact Explanation
An unauthenticated party who learns or guesses a pending async task-run UUID (these UUIDs are embedded in the `responseURL` sent to third-party bridge/adapter endpoints, e.g. `/v2/resume/<uuid>`, and thus are exposed to any external adapter or a network observer of that call) can resubmit a different result for the same task run while the parent run is still active. Because the update is unconditional and the row is not checked for prior completion, this allows:
- Overwriting the legitimate adapter's earlier result with attacker-controlled data.
- Forcing another `start=true` restart of the pipeline's downstream computation with corrupted values, potentially propagating attacker-controlled inputs into aggregation stages (e.g., `median`) and any downstream on-chain transaction tasks, i.e. a data-integrity/replay issue analogous to "duplicate claim" causing repeated/altered privileged state transitions.

### Likelihood Explanation
Reaching this path requires only knowledge of a task-run UUID and an unauthenticated HTTP PATCH — no session, API key, or role is required (the route sits in `unauthedv2`, and the audit event is explicitly named `UnauthedRunResumed`). The main constraint is the attacker needs the UUID, which is disclosed to whichever external adapter is configured for an async bridge task and can also be seen in transit by anyone able to observe or intercept that callback. This makes exploitation feasible for a compromised/malicious external adapter or an attacker who can observe the async callback URL, which mirrors the report's "compromised/malicious ClaimManager" scenario.

### Recommendation
Add a guard so a task run can only be resumed once, mirroring the report's suggested fix (`require(!claimId[_claimId])`):
- In `UpdateTaskRunResult`'s `SELECT ... FOR UPDATE`, additionally filter on `pipeline_task_runs.finished_at IS NULL` so an already-finished task run cannot match.
- Return a distinct, explicit error (e.g., "task run already finished") when no row matches so `ResumeJobV2` can reject duplicate/replayed resume calls with an appropriate HTTP status instead of silently succeeding.

### Proof of Concept
1. Configure a webhook job with an async bridge task; the bridge's HTTP callback receives a `responseURL` of the form `http://<node>/v2/resume/<taskUUID>`.
2. Attacker (e.g., a network position between the node and the external adapter, or the adapter itself if compromised) observes `taskUUID` and sends the legitimate first `PATCH /v2/resume/<taskUUID>` with a benign value — accepted, `finished_at` set, run possibly resumes.
3. Before the parent pipeline run reaches a terminal state (still `running`/`suspended` because other branches are pending), attacker sends a second `PATCH /v2/resume/<taskUUID>` with a different `value`.
4. `UpdateTaskRunResult`'s query at [5](#0-4)  matches again (run state check only), and the unconditional `UPDATE` at [6](#0-5)  overwrites the task's output/error with the attacker's second value, despite the task already having been finished.

### Citations

**File:** core/web/router.go (L238-244)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

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

**File:** core/services/pipeline/orm.go (L271-291)
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
```
