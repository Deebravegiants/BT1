Audit Report

## Title
Pipeline run resumption does not verify the target task run is still pending, allowing an already-finished task result to be overwritten and the run to be re-processed - (File: core/services/pipeline/orm.go)

## Summary
`UpdateTaskRunResult` in `core/services/pipeline/orm.go` gates the update solely on the parent `pipeline_runs.state` being `running` or `suspended`, without checking whether the specific `pipeline_task_runs` row (identified by `taskID`) has already finished (`finished_at IS NOT NULL`). In a multi-async-task pipeline where the overall run remains `suspended` waiting on one outstanding task, an attacker who knows/replays the `taskID` UUID of a *different, already-completed* task in the same run can re-POST to `/v2/resume/:taskID` and overwrite that task's output/error and flip the run back to `RunStatusRunning`, forcing re-processing with attacker-controlled data.

## Finding Description
`PipelineRunsController.Resume` accepts an arbitrary caller-supplied JSON body and forwards it, keyed only by the `taskID` UUID in the URL, to `App.ResumeJobV2` → `runner.ResumeRun`: [1](#0-0) 

`ResumeRun` calls the ORM directly and restarts the pipeline if the run was suspended: [2](#0-1) 

The ORM query only validates the *run's* coarse state, not the *targeted task's* completion status:
```
WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended')
```
followed by an unconditional `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1`. [3](#0-2) 

Reviewing `StoreRun`, `pipeline_runs.state` is only set to `RunStatusCompleted`/`RunStatusErrored` when the *entire* run finishes; while any task is still outstanding, the run stays `suspended`: [4](#0-3) . This means that for a DAG with multiple async tasks, once task A completes but task B is still pending, the run remains `suspended`. An attacker who has (or replays) task A's `taskID` can call `/v2/resume/:taskIDofA` again — the `WHERE` clause still matches because the run is `suspended` (waiting on B), even though task A's own row already has `finished_at` set. The task-level `IsPending()` check that exists elsewhere in the same file (used in `StoreRun`'s diff loop) is conspicuously absent here: [5](#0-4) [6](#0-5) 

The handler logs this action under `audit.UnauthedRunResumed`, confirming this endpoint is intentionally reachable without full user authentication as the async-bridge callback path: [7](#0-6) 

## Impact Explanation
This allows overwriting an already-finished task's `output`/`error` and forcing the parent run from `suspended` back to `RunStatusRunning`, re-triggering `runner.Run` with attacker-controlled data injected into a completed task's result, which can propagate to downstream tasks (potentially including side-effecting tasks such as ETH transactions or bridge calls) that consume that task's output. This maps to an in-scope "unauthorized job run manipulation" impact category, since it lets an external, unauthenticated party corrupt an already-resolved task result and force re-execution of pipeline logic.

## Likelihood Explanation
Exploitability requires knowledge of a specific task's UUID `taskID`, which is inherently transmitted to external async bridge adapters as part of the normal `Async: true` task callback workflow — the attack model matches the endpoint's own documented purpose (`audit.UnauthedRunResumed`). The scenario is realistic specifically for pipelines with two or more outstanding async tasks in the same run (one already resolved, one still pending), which is a legitimate, reachable pipeline configuration, not a contrived edge case.

## Recommendation
Add an explicit guard in `UpdateTaskRunResult` ensuring the specific `pipeline_task_runs` row targeted by `taskID` has not already finished, e.g., add `AND pipeline_task_runs.finished_at IS NULL` to the `SELECT ... FOR UPDATE` query (or perform a `SELECT` on `pipeline_task_runs` alone with a `FOR UPDATE` lock and check `IsPending()` before proceeding), returning a distinct "task already resolved" error instead of silently overwriting the row and toggling the run back to running.

## Proof of Concept
1. Configure a job whose pipeline DAG contains two independent `Async: true` bridge tasks, A and B, feeding into a downstream task.
2. Let task A's async adapter legitimately POST to `/v2/resume/:taskIDofA`, completing task A; because B is still outstanding, the run persists as `RunStatusSuspended` (per `StoreRun`).
3. Replay `/v2/resume/:taskIDofA` a second time with a different `value`/`error` payload before B completes.
4. Observe (per `core/services/pipeline/orm.go:271-308`) that the query's `WHERE pipeline_runs.state in ('running','suspended')` still matches (run is suspended waiting on B), so the second call is accepted: task A's row is overwritten, `run.State` is flipped to `RunStatusRunning`, and `ResumeRun` triggers a re-execution of the pipeline (`core/services/pipeline/runner.go:732-755`) using the attacker-supplied value for task A — with no rejection based on task A's own already-set `finished_at`.

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

**File:** core/services/pipeline/orm.go (L185-262)
```go
// StoreRun will persist a partially executed run before suspending, or finish a run.
// If `restart` is true, then new task run data is available and the run should be resumed immediately.
func (o *orm) StoreRun(ctx context.Context, run *Run) (restart bool, err error) {
	err = o.transact(ctx, func(tx *orm) error {
		finished := run.FinishedAt.Valid
		if !finished {
			// Lock the current run. This prevents races with /v2/resume
			sql := `SELECT id FROM pipeline_runs WHERE id = $1 FOR UPDATE;`
			if _, err = tx.ds.ExecContext(ctx, sql, run.ID); err != nil {
				return fmt.Errorf("failed to select pipeline run %d: %w", run.ID, err)
			}

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

			if restart {
				return nil
			}

			// Suspend the run
			run.State = RunStatusSuspended
			if _, err = tx.ds.NamedExecContext(ctx, `UPDATE pipeline_runs SET state = :state WHERE id = :id`, run); err != nil {
				return fmt.Errorf("failed to update pipeline run %d to %s: %w", run.ID, run.State, err)
			}
		} else {
			defer o.prune(ctx, tx.ds, run.PruningKey)
			// Simply finish the run, no need to do any sort of locking
			if run.Outputs.Val == nil || len(run.FatalErrors)+len(run.AllErrors) == 0 {
				return fmt.Errorf("run must have both Outputs and Errors, got Outputs: %#v, FatalErrors: %#v, AllErrors: %#v", run.Outputs.Val, run.FatalErrors, run.AllErrors)
			}
			sql := `UPDATE pipeline_runs SET state = :state, finished_at = :finished_at, all_errors= :all_errors, fatal_errors= :fatal_errors, outputs = :outputs WHERE id = :id`
			if _, err = tx.ds.NamedExecContext(ctx, sql, run); err != nil {
				return fmt.Errorf("failed to update pipeline run %d: %w", run.ID, err)
			}
		}

		sql := `
		INSERT INTO pipeline_task_runs (pipeline_run_id, id, type, index, output, error, dot_id, created_at, finished_at)
		VALUES (:pipeline_run_id, :id, :type, :index, :output, :error, :dot_id, :created_at, :finished_at)
		ON CONFLICT (pipeline_run_id, dot_id) DO UPDATE SET
		output = EXCLUDED.output, error = EXCLUDED.error, finished_at = EXCLUDED.finished_at
		RETURNING *;
		`

		taskRuns := []TaskRun{}
		query, args, bindErr := tx.ds.BindNamed(sql, run.PipelineTaskRuns)
		if bindErr != nil {
			return fmt.Errorf("failed to prepare named query: %w", bindErr)
		}
		err = tx.ds.SelectContext(ctx, &taskRuns, query, args...)
		if err != nil {
			return fmt.Errorf("failed to insert pipeline task runs: %w", err)
		}
		run.PipelineTaskRuns = taskRuns
		return nil
	})
	return restart, err
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

**File:** core/services/pipeline/models.go (L314-316)
```go
func (tr *TaskRun) IsPending() bool {
	return !tr.FinishedAt.Valid && tr.Output.Empty() && tr.Error.IsZero()
}
```
