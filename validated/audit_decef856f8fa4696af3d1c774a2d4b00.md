Audit Report

## Title
Unauthenticated `/v2/resume/:runID` Endpoint Allows Duplicate/Replay Resume of an Already-Finished Pipeline Task Run - (File: core/services/pipeline/orm.go)

## Summary
The `PATCH /v2/resume/:runID` route is registered in the unauthenticated route group and forwards attacker-supplied `taskID`/result data directly to `ORM.UpdateTaskRunResult` without checking whether that specific task run has already been completed. This allows a party who knows (or observes) a pending task-run UUID to resubmit a different result for the same task run, overwriting a previously recorded output/error while the parent pipeline run remains `running`/`suspended`.

## Finding Description
The route is registered outside of any auth middleware group: [1](#0-0) 

It is handled by `PipelineRunsController.Resume`, which parses the UUID `taskID` from the URL and the caller-supplied result body, then calls `App.ResumeJobV2` unauthenticated, and logs the action as `audit.UnauthedRunResumed`: [2](#0-1) 

This flows to `runner.ResumeRun` → `orm.UpdateTaskRunResult`: [3](#0-2) 

The gating `SELECT ... FOR UPDATE` filters only on the parent run's state (`running`/`suspended`), not on whether the individual task row (identified by `pipeline_task_runs.id = $1`) already has `finished_at` set. The subsequent `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1` is unconditional and will overwrite a task run that was already finished, as long as the parent run has not reached a terminal state: [4](#0-3) 

The only "authentication" for this endpoint is possession of the unguessable task-run UUID, which by design is handed to external bridge/adapter callbacks as part of the `responseURL`. The code does not verify that the UUID has not already been consumed before applying the write, which is the exact "already used" guard omission described in the claim.

## Impact Explanation
Because the row lookup and the write are not scoped by `finished_at IS NULL`, a second (or later) `PATCH /v2/resume/<uuid>` call for the same task run can silently overwrite the previously recorded legitimate result with attacker-controlled `value`/`error`, and can force a second `start=true` restart of the downstream pipeline if the run was suspended again in the interim. This maps to the in-scope "unauthorized job run" / cross-response corruption category: an external party without any node credential can corrupt or replay a bridge/adapter response into an active pipeline run, potentially propagating attacker-controlled values into aggregation and on-chain transaction tasks.

## Likelihood Explanation
Exploitation requires only knowledge of a pending task-run UUID and an unauthenticated HTTP PATCH request — no API key, session, or role is required, since the route sits in the `unauthedv2` group with no `auth.Authenticate*` middleware attached. The realistic attacker is a compromised/malicious external adapter (which legitimately receives the `responseURL` containing the UUID) or a party able to observe that callback in transit; both scenarios are plausible for jobs using async bridge tasks, and repeatability is only bounded by the parent pipeline run remaining non-terminal.

## Recommendation
Add a guard in `UpdateTaskRunResult`'s `SELECT ... FOR UPDATE` to also require `pipeline_task_runs.finished_at IS NULL`, so an already-finished task run cannot match and be overwritten. Return a distinct error when no row matches (already finished vs. not found) so `ResumeJobV2`/`Resume` can reject replayed resume calls with an appropriate HTTP status (e.g., 409 Conflict) instead of silently succeeding a second time.

## Proof of Concept
1. Configure a webhook job with an async bridge task; the external adapter receives a callback URL of the form `http://<node>/v2/resume/<taskUUID>`.
2. Send `PATCH /v2/resume/<taskUUID>` with a legitimate `{"value": "100"}` — accepted, `finished_at` set on the task run, and (if the run was suspended) it resumes/restarts execution.
3. While the parent pipeline run is still `running`/`suspended` (e.g., due to other pending branches), send a second `PATCH /v2/resume/<taskUUID>` with `{"value": "999999"}`.
4. Observe that `UpdateTaskRunResult`'s query at `core/services/pipeline/orm.go:271-292` matches again (only the run's state is checked) and the unconditional `UPDATE` overwrites `output`/`finished_at` for the same task run, demonstrating the replay/overwrite. A Go unit test can call `orm.UpdateTaskRunResult` twice with the same `taskID` against a run left in `suspended` state and assert the second call unexpectedly succeeds and overwrites the first result.

### Citations

**File:** core/web/router.go (L238-244)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

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

**File:** core/services/pipeline/runner.go (L732-742)
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
```

**File:** core/services/pipeline/orm.go (L271-292)
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
```
