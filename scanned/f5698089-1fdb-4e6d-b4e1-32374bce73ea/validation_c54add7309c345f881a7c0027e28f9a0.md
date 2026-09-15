### Title
Unauthenticated `PATCH /v2/resume/:runID` lets anyone finalize a pending pipeline task before the real external adapter response arrives, hijacking or permanently dropping the legitimate callback - (File: core/web/router.go, core/web/pipeline_runs_controller.go, core/services/pipeline/orm.go)

### Summary
The report's bug class is: a state-mutating function reachable before the real value/allocation exists can be called by an unprivileged actor, permanently consuming a one-shot completion slot (`refunded`) and locking out the legitimate future write. The Chainlink analog is the `PATCH /v2/resume/:runID` endpoint, which is registered with **no authentication at all** and resolves directly to `pipeline.orm.UpdateTaskRunResult`, which finalizes a `pipeline_task_runs` row unconditionally (no check that the row is not already finished, and no secrecy/ownership check tying the caller to the bridge/adapter that is expected to answer).

### Finding Description
`v2Routes` mounts the resume route in the unauthenticated group, separate from every other pipeline-runs route (which requires session/token auth via `authv2`): [1](#0-0) 

`PipelineRunsController.Resume` parses only a `runID` (actually a task UUID) from the URL and a JSON body, then calls `App.ResumeJobV2` — no authentication, no check that the caller is the bridge/adapter that originally issued the request: [2](#0-1) 

This flows into `runner.ResumeRun` → `orm.UpdateTaskRunResult`, which updates the task row and, if the run was `RunStatusSuspended`, flips it back to `RunStatusRunning` and (via the caller) restarts pipeline execution with whatever `Result` was supplied in the request body: [3](#0-2) 

Critically, the update SQL has no guard against the task already being finished — it is a blind `UPDATE ... WHERE pipeline_task_runs.id = $1` gated only by the *run's* state (`running`/`suspended`), not by whether this specific task row's `finished_at` is still null: [4](#0-3) 

The only thing standing between an attacker and forging a bridge/adapter callback is guessing the task UUID (functioning as a bearer token embedded in the adapter's `ResponseURL`, e.g. `http://localhost:6688/v2/resume/<uuid>` as seen in tests): [5](#0-4) 

Just as in the `refund` bug — where calling `refund()` before `addPremium()` allocated a value permanently burns the one-shot "already refunded" flag and locks out the legitimate future refund — here an attacker (or a party who observes/derives the response URL, e.g. via logs, error messages, or a compromised external adapter/network path) can call `PATCH /v2/resume/<taskID>` **before** the real external adapter responds:
- It finalizes the pending task with attacker-supplied `value`/`error`, which resumes the pipeline with forged data and can drive downstream tasks (including tasks that submit on-chain transactions).
- When the genuine adapter later posts its real result to the same URL, the run is very likely no longer in `('running','suspended')` state (it has since completed/errored), so `UpdateTaskRunResult`'s `SELECT ... FOR UPDATE` fails to match, and the legitimate result is silently dropped/rejected — exactly the “locked forever” outcome described in the report.

### Impact Explanation
An unauthenticated party who can predict or obtain a pending task's UUID (e.g., leaked in logs/errors, sniffed on an insecure adapter callback, or via a compromised/misconfigured downstream adapter) can:
- Impersonate the external adapter response, injecting attacker-controlled data into an in-flight pipeline run (request/response impersonation).
- Drive the pipeline forward with forged values, potentially triggering unintended downstream actions such as `ETHTx` tasks.
- Permanently prevent the real adapter response from ever being applied, since the run's state has moved on, matching the report's "lock any future \[value\] forever" impact.

This is a legitimate concrete-impact analog (request impersonation / unauthorized job continuation with tainted data), reachable from an unauthenticated internet-facing endpoint.

### Likelihood Explanation
Likelihood is moderate: the task UUID is not a documented/exposed identifier by default, so exploitation typically requires the attacker to have observed the URL (log exposure, an adapter that echoes the URL, network position on the adapter callback, or timing races if the ID is otherwise recoverable). The endpoint being fully unauthenticated by design (necessary so external adapters, which have no Chainlink credentials, can call back) is what removes the normal “only privileged/authenticated actor” barrier and makes the UUID the sole line of defense, unlike the private/internal `authv2` routes.

### Recommendation
- Mirror the fix pattern from the report (fail closed if the "not yet allocated" precondition is not met) by making `UpdateTaskRunResult`'s `UPDATE pipeline_task_runs` conditional on `finished_at IS NULL`, and return an explicit "already resumed" error if zero rows are affected, so a resume call cannot silently overwrite/finalize a task that either was never actually pending or has already been resumed.
- Consider adding a per-task, single-use, high-entropy secret (independent of the task UUID) that must be presented alongside the task ID to authorize a resume call, so knowledge/leakage of the UUID alone is insufficient to impersonate the adapter callback.
- Rate-limit and audit-log resume attempts against unknown/already-finished task IDs to detect scanning/guessing attempts (the `UnauthedRunResumed` audit event already exists and should be enhanced to flag failed/duplicate attempts).

### Proof of Concept
1. Create a job with an async `bridge` task; the bridge task's adapter is given a `ResponseURL` of the form `http://<node>/v2/resume/<taskUUID>` as shown in the runner test flow. [6](#0-5) 
2. Obtain/derive the pending task's UUID (e.g., via log exposure or observing the adapter's incoming request before it replies).
3. Before the real adapter responds, send: `PATCH /v2/resume/<taskUUID>` with an attacker-chosen JSON body (`{"error": ...}` or `{"value": ...}`) — no authentication headers required, since the route is registered in the unauthenticated group. [7](#0-6) 
4. The pipeline run resumes using the forged value; when the genuine adapter later calls the same URL with the real result, `UpdateTaskRunResult`'s state-gated `SELECT ... FOR UPDATE` no longer finds the run in `running`/`suspended` state (it has already completed with the forged data), so the legitimate response is rejected/lost. [8](#0-7)

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

**File:** core/services/pipeline/runner.go (L732-754)
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
```

**File:** core/services/pipeline/orm.go (L271-302)
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
```

**File:** core/services/pipeline/runner_test.go (L783-806)
```go
func Test_PipelineRunner_AsyncJob_InstantRestart(t *testing.T) {
	db := pgtest.NewSqlxDB(t)

	btcUSDPairing := utils.MustUnmarshalToMap(`{"data":{"coin":"BTC","market":"USD"}}`)

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
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Chainlink-Pending", "true")
		response := map[string]any{}
		if !assert.NoError(t, json.NewEncoder(w).Encode(response)) {
			return
		}
	})
```

**File:** core/services/pipeline/runner_test.go (L837-857)
```go
	s := fmt.Sprintf(`
ds1 [type=bridge async=true name="%s" timeout=0 requestData=<{"data": {"coin": "BTC", "market": "USD"}}>]
ds1_parse [type=jsonparse lax=false  path="data,result"]
ds1_multiply [type=multiply times=1000000000000000000]

ds2 [type=http method="GET" url="%s" requestData=<{"data": {"coin": "BTC", "market": "USD"}}>]
ds2_parse [type=jsonparse lax=false  path="data,result"]
ds2_multiply [type=multiply times=1000000000000000000]

ds3 [type=http method="GET" url="blah://test.invalid" requestData=<{"data": {"coin": "BTC", "market": "USD"}}>]
ds3_parse [type=jsonparse lax=false  path="data,result"]
ds3_multiply [type=multiply times=1000000000000000000]

ds1->ds1_parse->ds1_multiply->median;
ds2->ds2_parse->ds2_multiply->median;
ds3->ds3_parse->ds3_multiply->median;

median [type=median index=0]
ds4 [type=http method="GET" url="%s" index=1]
ds5 [type=http method="GET" url="%s" index=2]
`, bt.Name.String(), s2.URL, s4.URL, s5.URL)
```
