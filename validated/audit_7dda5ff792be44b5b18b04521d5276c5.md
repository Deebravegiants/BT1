## Title
Unauthenticated `/v2/resume/:runID` endpoint permits unlimited replays that overwrite already-finished task results without re-validation - (File: `core/services/pipeline/orm.go`, `core/web/router.go`, `core/web/pipeline_runs_controller.go`)

### Summary
The reported Vaultka bug is a state-machine flaw: `request_withdraw` never checks `position_info.is_in_withdraw_request` before acting, so the same withdrawal state can be re-triggered repeatedly, letting an attacker collect funds more than once. The chainlink analog is the pipeline "resume" callback: it is deliberately unauthenticated (secured only by an unguessable UUID acting as a bearer token), and the underlying `UpdateTaskRunResult` query/update never checks whether the target task run has already been finalized before overwriting its result. This allows unlimited replays of a resume call for the same `taskID`, silently mutating a task's stored output/error after the pipeline has already consumed or acted on it.

### Finding Description
`v2Routes` registers the resume route with no authentication middleware at all: [1](#0-0) 

The handler decodes an arbitrary `ResumeRequest` body and applies it directly to `ResumeJobV2`/`ResumeRun`: [2](#0-1) 

`ResumeRun` forwards the caller-supplied value/error straight to the ORM without checking whether this `taskID` was already resolved: [3](#0-2) 

The ORM's `UpdateTaskRunResult` only checks that the *pipeline run* is in `running`/`suspended` state (`FOR UPDATE`), but the `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1` statement has **no guard against the specific task row already having a non-null `finished_at`**. As long as the overall run is still `running` or `suspended` (e.g., because it has other pending async tasks or because the caller is racing the "instant restart" window), the same completed task's result can be overwritten again and again: [4](#0-3) 

On the read side, `scheduler.reconstructResults` only skips a task if it `IsPending()`; once finished it trusts whatever is stored in `pipeline_task_runs`, meaning a later-overwritten value is picked up verbatim on the next resumption pass: [5](#0-4) 

This mirrors exactly the audited bug class: a state-transition function (`request_withdraw` / `Resume`) that is reachable by an untrusted caller repeatedly, with no idempotency/"already handled" check, letting stale or attacker-controlled state feed back into downstream logic (fund movement in Vaultka; task/job outcome data — including ETHTx task results — in chainlink).

### Impact Explanation
`taskID` values are UUIDs embedded in bridge "responseURL" callbacks (`/v2/resume/<uuid>`), so the endpoint's security model assumes the UUID is secret/unguessable. But because the route has zero authentication and the update path has no "already completed" check, anyone who obtains a `taskID` (e.g., via logs, network capture, a leaky bridge adapter, or brute force against a low-entropy/older ID) can repeatedly PATCH arbitrary `value`/`error` payloads into that task's row. If the task feeds an `ETHTxTask` or otherwise influences fund-moving branches of a pipeline (Keeper/VRF/OCR-adjacent jobs, price data used for on-chain writes), replayed or forged callbacks can corrupt job execution results feeding on-chain actions — a direct analog to the reported "receiving more tokens than intended" impact via unconstrained repeated state-transition calls.

### Likelihood Explanation
The route is reachable by any unauthenticated network client (it is explicitly outside the `authv2`/`userOrEI` auth groups) and requires nothing but knowledge of a `taskID` UUID, which is generated per-task and transmitted to bridge adapters over the network — a weaker secret than a signed token or HMAC. Any pipeline using async bridge/webhook resume semantics is potentially exposed while its run is still `running`/`suspended`.

### Recommendation
- Require the resume callback to include a per-run secret/HMAC (not just the taskID) that only the true async job initiator possesses, similar to the outgoing-secret model already used for `ExternalInitiator` (`core/bridges/external_initiator.go`).
- In `UpdateTaskRunResult`, explicitly reject updates to a `pipeline_task_runs` row whose `finished_at` is already non-null, returning an error instead of silently overwriting.
- Rate-limit and audit-log all resume attempts, especially repeated calls for the same `taskID`.

### Proof of Concept
1. Create/observe a job with an async task (e.g., `BridgeTask{Async: "true"}`), capturing the `responseURL` it emits, e.g. `http://node/v2/resume/<taskID>`.
2. Send `PATCH /v2/resume/<taskID>` with a body `{"value": "9700"}` — completes the task normally.
3. Immediately send a second `PATCH /v2/resume/<taskID>` with a different body `{"value": "1"}` while the overall run is still `running`/`suspended` (e.g. other async tasks still pending in the same pipeline). Because `UpdateTaskRunResult` re-`UPDATE`s the row unconditionally and `scheduler.reconstructResults` trusts stored (non-pending) results on the next scheduling pass, the second overwrite propagates into the final pipeline outcome, demonstrating unauthenticated replay/overwrite of a finalized task result.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

**File:** core/web/pipeline_runs_controller.go (L131-160)
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

**File:** core/services/pipeline/scheduler.go (L114-161)
```go
func (s *scheduler) reconstructResults() {
	// if there's results already present on Run, then this is a resumption. Loop over them and fill results table
	for _, r := range s.run.PipelineTaskRuns {
		task := s.pipeline.ByDotID(r.DotID)

		if task == nil {
			panic("can't find task by dot id")
		}

		if r.IsPending() {
			continue
		}

		result := Result{}

		if r.Error.Valid {
			result.Error = errors.New(r.Error.String)
		}

		if r.Output.Valid {
			result.Value = r.Output.Val
		}

		s.results[task.ID()] = TaskRunResult{
			Task:       task,
			Result:     result,
			CreatedAt:  r.CreatedAt,
			FinishedAt: r.FinishedAt,
		}

		// store the result in vars
		var err error
		if result.Error != nil {
			err = s.vars.Set(task.DotID(), result.Error)
		} else {
			err = s.vars.Set(task.DotID(), result.Value)
		}
		if err != nil {
			s.logger.Panicf("Vars.Set error: %v", err)
		}

		// mark all outputs as complete
		for _, output := range task.Outputs() {
			id := output.ID()
			s.dependencies[id]--
		}
	}
}
```
