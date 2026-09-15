I have enough evidence now to write the final answer.

### Title
Unauthenticated `/v2/resume/:runID` endpoint allows any unprivileged caller to inject arbitrary results into a pending pipeline run, hijacking job execution state - ([File: core/web/pipeline_runs_controller.go])

### Summary
`Cooler.rollLoan()` is exploitable because it is a state-mutating function that any caller (not just the intended counterparty) can invoke, letting an attacker impose new terms on someone else's in-flight transaction. The closest reachable analog in this codebase is the Chainlink node's `PipelineRunsController.Resume` handler, mounted on the completely unauthenticated route group and reachable by literally anyone who can reach the node's HTTP port with only a task UUID, letting them inject an attacker-chosen result/error into another party's in-flight (suspended) pipeline run and force it to resume with fabricated data.

### Finding Description
The route is registered without any authentication middleware: [1](#0-0) 

The handler parses only a `runID` (task UUID) from the URL and an arbitrary JSON body, then immediately calls `App.ResumeJobV2` with attacker-controlled `pipeline.Result` — no secret, no signature, no external-initiator/bridge credential check of any kind: [2](#0-1) 

`ResumeJobV2` forwards directly into `runner.ResumeRun`, which loads the suspended run by `taskID` and writes the attacker-supplied `value`/`err` straight into `pipeline_task_runs`, then restarts the run so downstream tasks (e.g. `multiply`, `submit` bridge task) execute using that forged value: [3](#0-2) [4](#0-3) [5](#0-4) 

The only sensitive material protecting this action is the unguessable `taskID` UUID that is normally sent only to the legitimate external adapter as part of the `responseURL` in the async bridge task's request body: [6](#0-5) 

Because there is no possession-of-secret check beyond the URL path parameter itself, any party that learns/observes/leaks a pending task's UUID (e.g., via a compromised/malicious external adapter, request logging, proxy logs, browser history, a misconfigured downstream service, or SSRF/log-disclosure elsewhere in the stack) can call this endpoint directly and force the pipeline to resume with attacker-chosen data — functionally identical in spirit to Cooler's issue where a party outside the intended relationship can unilaterally push new "terms" (here, task output) into someone else's in-progress transaction that they never agreed to. The developers were aware enough of the lack of authentication to name the audit event `UnauthedRunResumed`, but no compensating control (rate limiting, HMAC, single-use nonce validation beyond DB state, mTLS) is present in this handler. [7](#0-6) 

### Impact Explanation
An attacker who obtains a pending run's `taskID` can forcibly complete or corrupt another job's pipeline run with attacker-controlled values, potentially causing incorrect on-chain submissions from `bridge`-task pipelines, denial-of-service (repeated bogus resumes consuming the run/db), or state corruption of unrelated jobs' async task graph. This directly matches the report's "Impact: forced state change without the counterparty's true consent" bug class.

### Likelihood Explanation
Exploitation requires only knowledge of a valid pending `taskID` UUID (128-bit random, non-trivial to guess directly) plus network reachability of the node's HTTP API — no credentials, no session, no external-initiator key are checked at all, which is a strictly lower bar than any other job-run-triggering path in the codebase (all of which require a session token or EI key). Any leak of this ID (compromised/curious external adapter, proxy/log exposure, browser referrer, etc.) fully compromises the resume action.

### Recommendation
Require a per-task secret/nonce (e.g., HMAC-signed token bound to the pending task, verified server-side) in addition to the `runID`, and/or require the resume request to originate with credentials proving it is the specific bridge/adapter that was given the `responseURL` for that task, rather than only checking that a syntactically valid UUID was supplied.

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

**File:** core/services/pipeline/task.bridge.go (L360-378)
```go
			merged[string(includeInputAtKey)] = inputValues[0]
		}
	}

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
	return json.Marshal(merged)
}
```

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
```
