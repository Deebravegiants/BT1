## Analysis

The Sherlock finding is a reentrancy pattern: a malicious external call during `repayLoan`'s `safeTransferFrom` lets the caller re-enter and mutate loan state mid-transaction, so stale/half-updated data gets used later. The closest reachable analog in `chainlink--019` is the **unauthenticated pipeline-run resume endpoint**, which lets an external (bridge adapter) actor overwrite a task-run's persisted result while the same pipeline run is still mid-execution, corrupting state that other in-flight logic (restart detection) later trusts.

### Key code

The resume route is deliberately unauthenticated (it's called by external bridge adapters using a callback URL, not by a logged-in user): [1](#0-0) 

It goes straight into `ResumeJobV2` → `ResumeRun` → `UpdateTaskRunResult`: [2](#0-1) [3](#0-2) 

`UpdateTaskRunResult` unconditionally overwrites the task run's `output`/`error`/`finished_at` regardless of whether that task run was already finished, only gating the "restart the run" side-effect on `run.State == RunStatusSuspended`: [4](#0-3) 

`StoreRun` documents that it relies on locking + a state comparison specifically "to prevent races with /v2/resume", but only re-checks whether a *pending* task became non-pending — it does not protect an already-finished task run from being silently rewritten by a second, out-of-order resume call while the run is `RunStatusRunning`: [5](#0-4) 

### Finding

The resume callback URL (`/v2/resume/:runID`, keyed by the async task's UUID) is handed out to an external, unprivileged bridge adapter as part of `BridgeTask`'s async request body: [6](#0-5) 

Because `UpdateTaskRunResult`'s `UPDATE pipeline_task_runs ... WHERE id = $1` has no `finished_at IS NULL` guard, and the "is this run still suspended" check only controls whether the run is *restarted*, a second (or replayed/malicious) resume call for the same `taskID` — sent by the same untrusted adapter that received the callback URL — can still overwrite the row's `output`/`error` after the first legitimate value was already read into memory and used to continue the pipeline (`r.Run` in the spawned goroutine operates on the in-memory `run` struct returned by the *first* call, not by re-querying). This persists attacker-controlled data into `pipeline_task_runs` after the value has already been consumed by the running pipeline, corrupting the durable record of what the pipeline actually computed and, if the run later suspends again for another task, letting `StoreRun`'s DB-reload-and-diff logic (`tempRun.ByDotID`) pick up this rewritten (not re-validated) value on the next suspend/restart cycle. This is the same class of bug as the report: state that should be immutable once "consumed" (loan terms / task result) can be mutated out-of-band by the same external party mid-flow, because there is no guard preventing a second, adversarial post-hoc update to already-processed data.

### Impact

- An external adapter (the only party with knowledge of the resume URL, i.e. the unprivileged actor in this trust boundary) can send multiple resume calls for one async task.
- The first value is consumed by the live pipeline goroutine; a subsequent call still successfully overwrites the corresponding `pipeline_task_runs.output/error` row in the database with arbitrary attacker data, with no `finished_at`/idempotency check.
- If the overall run has other pending async legs and suspends again, the corrupted row can be re-read via `StoreRun`'s restart-diff path and folded back into pipeline state, meaning a value computed and already used by the engine differs from what is later trusted/audited — a direct analog of "new loan terms rolled over" via an external callback race, but here achieved via an intentionally-unauthenticated resume endpoint rather than an ERC20 callback re-entrancy.

### Recommendation

In `UpdateTaskRunResult`, add a `pipeline_task_runs.finished_at IS NULL` condition (or an equivalent “first-write-wins”/idempotency check) to the `SELECT ... FOR UPDATE` / `UPDATE` so a task run cannot be overwritten once it has already been resumed and consumed, and consider single-use invalidation of the resume URL/taskID after first successful resume. [7](#0-6)

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
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

**File:** core/services/pipeline/orm.go (L185-228)
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

**File:** core/services/pipeline/task.bridge.go (L364-376)
```go
	if t.Async == "true" {
		responseURL := t.bridgeConfig.BridgeResponseURL()
		if responseURL != nil && *responseURL != *zeroURL {
			responseURL.Path = path.Join(responseURL.Path, "/v2/resume/", t.uuid.String())
		}
		var s string
		if responseURL != nil {
			s = responseURL.String()
		}
		merged["responseURL"] = s
	}

	*requestData = merged
```
