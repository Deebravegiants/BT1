## Summary

The Gondi report is about callback data (`LoanRepaymentData.callbackData` / `LoanExecutionData.callbackData`) that is not signed by the borrower, letting an unprivileged third party replace it and inject arbitrary "result" data into a privileged flow (loan repayment/BNPL) that moves funds. The chainlink analog is the node's unauthenticated `Resume` endpoint for pipeline runs, which lets an unprivileged caller inject arbitrary result data into a suspended job run.

### Title
Unauthenticated pipeline-run resume endpoint accepts unsigned/unverified result data - (File: core/web/pipeline_runs_controller.go)

### Summary
`PipelineRunsController.Resume` is exposed without session or API-key authentication (the code explicitly logs it via `audit.UnauthedRunResumed`), and accepts an arbitrary, unsigned `pipeline.ResumeRequest` body from any caller who can reach the endpoint with a task's UUID.

### Finding Description
`Resume` parses the `runID` path param as a `taskID` UUID and decodes the request body directly into a `pipeline.ResumeRequest`, converting it to a `pipeline.Result` and forwarding it unchecked to `ResumeJobV2` → `ResumeRun`: [1](#0-0) . `ResumeRun` writes this attacker-supplied `Result{Value, Error}` directly into the task run and, if the run was suspended, restarts pipeline execution with that value/error injected into the DAG: [2](#0-1) . The underlying ORM call `UpdateTaskRunResult` persists whatever `Value`/`Error` is supplied for the given `taskID` and flips the run back to `running`, with no signature, ownership, or origin check tying the resumer to the original external call: [3](#0-2) . The mechanism exists to let external async bridge adapters call back into the node (see the response URL constructed for bridge tasks, `/v2/resume/<taskID>`) [4](#0-3) , but the only "authentication" is possession of the `taskID` UUID — there is no signed digest, HMAC, or bridge-specific secret binding the resumption payload to the original request, unlike the borrower-signed `LoanExecutionData`/`LoanRepaymentData` model the report recommends.

### Impact Explanation
Any unprivileged actor who learns or brute-forces a pending task's UUID (e.g., via log leakage, a slow/predictable generator, or a chatty external adapter) can inject arbitrary `value`/`error` into that specific suspended pipeline run, exactly as the report's front-runner replaces unsigned `callbackData` to redirect fund-relevant execution to an attacker-favorable outcome. Because the resumed value flows straight into downstream DAG tasks — potentially including tasks that construct and submit on-chain transactions — the injected data can corrupt oracle answers, force a job into a false success/failure branch, or otherwise subvert the job's business logic, with no cryptographic binding to the legitimate external initiator or bridge adapter that was supposed to supply the result.

### Likelihood Explanation
Likelihood depends on secrecy of the UUID `taskID`, which is the sole access control. Since the endpoint is intentionally unauthenticated (as flagged by the `UnauthedRunResumed` audit label) and is reachable by any HTTP client that knows/derives a `taskID`, this is a real, reachable unprivileged-actor code path rather than a theoretical one, though exploitation requires task-ID disclosure or prediction, which I could not fully verify (e.g., how UUIDs are generated/exposed, or whether the router applies any additional non-auth protections). I could not confirm the exact router registration/middleware chain for this route within available context—only that `Resume` itself performs no auth check and explicitly logs the action as "unauthed."

### Recommendation
Bind the resume payload to the original request the same way the report recommends for callback data: require the resumer to present a signed/HMAC token issued when the task was suspended (e.g., signing `taskID` + expected result schema/bridge identity), verified before `UpdateTaskRunResult` is applied, so an attacker who merely knows or guesses the `taskID` cannot inject unauthenticated result data into the run.

### Proof of Concept
1. Create/observe a job with an async bridge task; capture its suspended task's UUID from `pipeline_task_runs` (e.g., via response URL leaked to the external adapter, logs, or timing/enumeration).
2. Send `PATCH /v2/resume/<taskID>` with an attacker-chosen JSON body (`pipeline.ResumeRequest`) and no authentication headers.
3. Observe `PipelineRunsController.Resume` [1](#0-0)  accepts the request, and `ResumeRun` [2](#0-1)  resumes the run with attacker-controlled data, with no verification that the caller is the original bridge/external initiator that the suspended task was awaiting a response from.

### Citations

**File:** core/web/pipeline_runs_controller.go (L134-161)
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

**File:** core/services/pipeline/task.bridge_test.go (L623-643)
```go
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var reqBody adapterRequest
		payload, err := io.ReadAll(r.Body)
		if !assert.NoError(t, err) {
			return
		}
		defer r.Body.Close()

		err = json.Unmarshal(payload, &reqBody)
		if !assert.NoError(t, err) {
			return
		}
		assert.Equal(t, fmt.Sprintf("%s/v2/resume/%v", cfg.WebServer().BridgeResponseURL(), id.String()), reqBody.ResponseURL)
		w.Header().Set("Content-Type", "application/json")

		// w.Header().Set("X-Chainlink-Pending", "true")
		response := map[string]any{"pending": true}
		if !assert.NoError(t, json.NewEncoder(w).Encode(response)) {
			return
		}
	})
```
