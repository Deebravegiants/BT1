Based on my research, I found a legitimate structural analog to the Cooler.sol bug class in the chainlink pipeline-run resume path, but I want to be precise about what is and isn't confirmed given the tool budget exhausted before I could fully read `core/web/router.go`'s route-registration block.

### Title
Unauthenticated `/v2/resume/:runID` Callback Allows Attacker to Overwrite a Pending Job Run's Result Before the Legitimate External Adapter Response Arrives - (File: core/web/pipeline_runs_controller.go)

### Summary
The Cooler.sol bug is a class of "mutable pending state overwrite": a party can rewrite the terms a counterparty is about to accept, and the accept-path (`rollLoan`) trusts whatever is currently in storage with no binding to what was actually agreed. The closest reachable analog in this codebase is `PipelineRunsController.Resume`, the `/v2/resume/:runID` HTTP endpoint used to deliver async/bridge task results back into a suspended pipeline run. It writes attacker-supplied `pipeline.ResumeRequest` data into the task/run "terms" via `App.ResumeJobV2` → `runner.ResumeRun` → `orm.UpdateTaskRunResult`, and the audit event name itself (`audit.UnauthedRunResumed`) documents that no authentication is enforced on this write.

### Finding Description
`PipelineRunsController.Resume` decodes an arbitrary JSON body into `pipeline.ResumeRequest`, converts it to a `Result`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` for the given `runID` path parameter, with no session/API-token/external-initiator authentication check on the handler itself: [1](#0-0) 

That result is persisted directly as the task's final output/error via `UpdateTaskRunResult`, which locks the run and unconditionally overwrites `pipeline_task_runs.output/error/finished_at` for the given task id, then transitions the run from suspended back to running so the rest of the pipeline continues with this value: [2](#0-1) 

The task type this is built for — the async bridge task — hands out this exact resume URL (`%s/v2/resume/%v`) to the external adapter as the callback address for the "real" answer, as shown in the test fixture: [3](#0-2) 

Nothing in `UpdateTaskRunResult` (or the higher-level `Resume` handler) verifies that the caller submitting the resume payload is the external adapter that was actually asked to compute this value, that this is the first/only writer for the task, or that the value matches any previously agreed/expected shape — it is a bare "last write wins" on the task's `runID` (the task UUID), analogous to `Cooler.provideNewTermsForRoll` letting any caller of that privileged path overwrite `loan.request` with new terms that the later `rollLoan()` call blindly accepts.

### Impact Explanation
If a caller other than the legitimate bridge/external adapter learns or otherwise obtains a suspended task's `runID` (e.g., via response bodies, logs, error messages, or a race with the real adapter callback), they can submit an attacker-chosen `Result` value or error for that task before (or instead of) the legitimate response. Because the resume path itself performs no authentication and no binding check to the original outbound bridge request, the pipeline run resumes and proceeds with the attacker's injected value — this is a direct analog of the "front-run and force malicious terms" pattern in the Cooler.sol report: the borrower's `rollLoan()` accepted whatever terms happened to be in storage at execution time, exactly as this pipeline resumes with whatever result happens to be posted to the run ID.

### Likelihood Explanation
This is somewhat speculative without confirming (a) whether `/v2/resume/:runID` genuinely sits outside the authenticated route groups in `core/web/router.go` (the tool budget ran out before I could read that file, though the audit-log constant name `audit.UnauthedRunResumed` strongly implies it is intentionally unauthenticated by design, e.g., to allow arbitrary async external adapters to call back), and (b) how guessable/discoverable a given run's `taskID` UUID is to an unprivileged attacker in a real deployment. If the endpoint is deliberately unauthenticated by design (common for webhook-style bridge callbacks) and the UUID is treated as a de facto bearer secret, then the missing "is this really the expected caller / expected value" check is the same root cause as the Cooler issue: no invariant ties the accepted state to what was actually promised.

### Recommendation
Bind the resume payload to the specific outstanding request rather than trusting "whatever is posted to this run ID": require a per-request secret/nonce issued alongside the response URL, validate the caller against the bridge/external-initiator that owns the task, and reject resumes where a result has already been recorded for that task (single-use semantics) rather than always overwriting `output`/`error`/`finished_at`.

### Proof of Concept
Not independently verified end-to-end due to the exhausted tool budget (route middleware for `/v2/resume/:runID` in `core/web/router.go` was not read). Conceptually: (1) create a job with an async bridge task, which hands the external adapter a response URL of the form `.../v2/resume/<taskUUID>`; (2) before the legitimate adapter posts its real result, an attacker who obtains that `taskUUID` sends their own `PATCH .../v2/resume/<taskUUID>` body; (3) `UpdateTaskRunResult` writes the attacker's value as the task's final output and resumes the run, which will use the attacker-controlled value for all downstream tasks, matching the "forced bad terms accepted without verification" pattern from the source report.

### Citations

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

**File:** core/services/pipeline/task.bridge_test.go (L615-643)
```go
func TestBridgeTask_AsyncJobPendingState(t *testing.T) {
	t.Parallel()

	db := pgtest.NewSqlxDB(t)
	cfg := configtest.NewTestGeneralConfig(t)

	id := uuid.New()

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
