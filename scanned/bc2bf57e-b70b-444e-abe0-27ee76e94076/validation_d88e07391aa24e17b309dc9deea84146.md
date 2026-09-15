### Title
Pipeline run resumption does not verify the target task run is still pending, allowing an already-finished task result to be overwritten and the run to be re-processed - (File: core/services/pipeline/orm.go)

### Summary
The `RFPSimpleStrategy._distribute` bug class is "an action is dispatched based on high-level object state (pool/run) without validating the specific sub-item's status (milestone/task) before mutating it." The same pattern exists in chainlink's pipeline resume path: `UpdateTaskRunResult` only checks that the parent `pipeline_runs.state` is `running`/`suspended`, but never checks whether the individual `pipeline_task_runs` row identified by `taskID` is still pending (`finished_at IS NULL`) before overwriting its output/error and restarting the run.

### Finding Description
`PipelineRunsController.Resume` decodes an arbitrary caller-supplied JSON body into a `pipeline.ResumeRequest`, converts it to a `Result`, and forwards it straight to `App.ResumeJobV2` → `runner.ResumeRun`, keyed only by the `taskID` UUID from the URL: [1](#0-0) 

`ResumeRun` calls the ORM to update the task result and, if the run was suspended, restarts pipeline execution with the newly injected value: [2](#0-1) 

The ORM update itself only gates on the parent run's state, not on whether this specific task has already completed: [3](#0-2) 

Note the `WHERE ... pipeline_runs.state in ('running', 'suspended')` clause locks/validates the *run*, but the subsequent `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1` unconditionally overwrites the task row regardless of whether `finished_at` was already set from a prior legitimate completion. This mirrors the reported bug class exactly: the top-level object's coarse status is checked (`pool`/`run` not inactive) but the specific sub-item's status (`milestone`/`task`) is never validated before the state-changing action is performed.

Other parts of the same package do implement this narrower check when reconstructing state (`tr.IsPending()` is checked in `StoreRun`'s restart-detection loop), showing the codebase is aware of the distinction but does not apply it in `UpdateTaskRunResult`: [4](#0-3) 

The audit event name used by the Resume handler itself — `audit.UnauthedRunResumed` — signals that this endpoint is treated/reached without full user authentication in the intended usage (it's the callback path for asynchronous bridge/external adapters posting back results via `taskID`), which is consistent with the "unprivileged-actor" scope of this analysis: [5](#0-4) 

### Impact Explanation
If a `taskID` (UUID) is known or guessable/replayed (e.g., leaked in logs, a second callback from a slow/duplicated bridge response, or an attacker racing the resume callback), the missing per-task pending check allows:
- Overwriting an already-finished task's `output`/`error` after the fact.
- Forcing the parent run to transition back to `RunStatusRunning` and re-executing the remainder of the pipeline DAG with attacker-controlled downstream input, potentially re-triggering side-effecting tasks (e.g., ETH transactions, external adapter calls) that depend on that task's output.

This is a cross-request/state confusion issue: a stale or forged resume request is processed as if it were the authoritative, first-time completion of that task, which can lead to duplicate or manipulated job-run execution.

### Likelihood Explanation
The `/v2/resume/:runID` (Resume) path is specifically designed to be reachable by external bridge adapters posting back asynchronous results, keyed only by a UUID with no additional validation that this is the first/expected completion for that task. Any party able to reach this endpoint with a valid but already-resolved `taskID` can trigger the unwanted overwrite/restart. Exploitability depends on the ability to know or replay a `taskID`, which is plausible in async-adapter workflows (`Async: true` tasks) where the ID is transmitted to the external bridge.

### Recommendation
In `UpdateTaskRunResult` (core/services/pipeline/orm.go), add a condition ensuring the target task run has not already finished before applying the update, e.g. add `AND pipeline_task_runs.finished_at IS NULL` (or an equivalent `SELECT ... FOR UPDATE` check on the specific task row) to the query/lookup, and return a distinct "already resolved" error instead of silently overwriting.

### Proof of Concept
1. Create a job with an `Async: true` bridge task; note the generated `taskID`.
2. Let the async adapter legitimately POST back to `/v2/resume/:taskID` once, completing the task and the run.
3. Replay/POST the same `/v2/resume/:taskID` request again with different `data`/`error` payload.
4. Observe that `UpdateTaskRunResult` (core/services/pipeline/orm.go:271-308) does not reject the second update because it only checks `pipeline_runs.state in ('running','suspended')`, not the task's own `finished_at` status — the task row is overwritten and, if the run had already been marked suspended in the meantime, the pipeline is restarted with the new (attacker-controlled) value.

### Citations

**File:** core/web/pipeline_runs_controller.go (L134-157)
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
```

**File:** core/web/pipeline_runs_controller.go (L159-159)
```go
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
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

**File:** core/services/pipeline/orm.go (L197-219)
```go
			taskRuns := []TaskRun{}
			// Reload task runs, we want to check for any changes while the run was ongoing
			if err = tx.ds.SelectContext(ctx, &taskRuns, `SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1`, run.ID); err != nil {
				return fmt.Errorf("failed to select piepline task run %d: %w", run.ID, err)
			}

			// Construct a temporary run so we can use r.ByDotID
			tempRun := Run{PipelineTaskRuns: taskRuns}

			// Diff with current state, if updated, swap run.PipelineTaskRuns and early return with restart = true
			for i, tr := range run.PipelineTaskRuns {
				if !tr.IsPending() {
					continue
				}

				// Look for new data
				if taskRun := tempRun.ByDotID(tr.DotID); taskRun != nil && !taskRun.IsPending() {
					// Swap in the latest state
					run.PipelineTaskRuns[i] = *taskRun
					restart = true
				}
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
