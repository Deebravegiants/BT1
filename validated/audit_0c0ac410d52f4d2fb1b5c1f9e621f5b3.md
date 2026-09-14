### Title
Unauthenticated `/v2/resume/:runID` endpoint allows arbitrary pipeline task-run result injection into suspended jobs - ([File: core/web/pipeline_runs_controller.go])

### Summary
The multisig report's root issue is that a state-transition entry point lacks proper authorization scoping, letting an unprivileged actor drive privileged execution logic (mutating wallet parameters, then re-entering to execute with elevated rights) with only a design comment ("no security issue") rather than an enforced check. The closest reachable analog in chainlink is the `PATCH /v2/resume/:runID` route, which is deliberately placed in the *unauthenticated* route group and lets any network caller who supplies a valid task UUID inject an arbitrary `pipeline.Result` (value or error) into a suspended pipeline run, resuming its execution with attacker-controlled data.

### Finding Description
The `v2Routes` function mounts the resume endpoint outside of any authentication middleware: [1](#0-0) 

`PipelineRunsController.Resume` performs no session/API-token/external-initiator check at all — it parses the `runID` path param as a UUID (the async task ID), decodes an arbitrary JSON body into `pipeline.ResumeRequest`, and forwards the caller-supplied result directly into `Application.ResumeJobV2`, which calls `pipelineRunner.ResumeRun`: [2](#0-1) 

`ResumeJobV2` passes the caller's value/error straight through to the ORM's `UpdateTaskRunResult`, which looks up the run by task ID and, if the run is `suspended`, flips it back to `running` and restarts pipeline execution with the caller-supplied output: [3](#0-2) [4](#0-3) 

The only mitigation is that a UUID task ID must be known/guessed — the endpoint's design assumes the async task UUID functions as an unguessable bearer credential (analogous to a webhook callback secret). However, unlike the multisig report's flow which is contained within its own trust boundary, this endpoint has **no additional authorization layer, no binding to which caller/bridge is allowed to resolve which task, and no scoping check that the result matches the expected task type** (e.g., only `TaskTypeETHTx`/async bridge tasks should be resumable). The code even logs this deliberately as `audit.UnauthedRunResumed`, an audit event name that itself documents the unauthenticated nature of the action: [5](#0-4) 

This matches the report's bug class: a privileged state-mutating operation (resuming/continuing a job's execution pipeline, potentially driving on-chain transactions or oracle-fed data) is reachable by an unauthenticated/unprivileged actor whose only "authorization" is possessing an identifier that flows through the same trust chain as the object it targets — with no independent authorization check comparable to the recommended "prevent contract from acting on itself/being added as trusted party" fix in the report.

### Impact Explanation
If an attacker discovers or brute-forces/leaks a pending task's UUID (e.g., via logs, error messages, monitoring dashboards, or a compromised low-privilege bridge adapter), they can inject arbitrary result values or errors into a suspended pipeline run for any job on the node — including jobs that ultimately submit data on-chain or trigger further downstream tasks. This can corrupt job outputs, force premature/incorrect completion of a run, or resume execution with attacker-chosen data that flows into subsequent tasks (e.g., median/multiply/ETH-tx tasks), directly affecting fund-moving or oracle-reporting behavior.

### Likelihood Explanation
Likelihood depends entirely on UUID confidentiality. Chainlink task UUIDs are v4 random values, which is a reasonable secret-based authorization pattern if properly protected end-to-end, but this endpoint has zero defense-in-depth: no rate limiting scoped to this route beyond the global unauthenticated group, no per-caller/task binding, and the ID is exposed in the async bridge integration's outgoing `responseURL` (`http://.../v2/resume/<uuid>`), increasing exposure surface across logs, request/response captures, and potentially compromised or misbehaving external bridge adapters.

### Recommendation
- Add authorization scoping equivalent to the external-initiator model used elsewhere in the auth stack (`AuthenticateExternalInitiator`, `RequiresRunRole`) so that resuming a run requires proof tied to the specific bridge/task, not just knowledge of a bare path parameter.
- Validate that the resumed task is actually of the expected async/bridge type before applying the caller-supplied result, rather than trusting any task ID blindly.
- Consider rotating/short-lived signed tokens embedded in the resume URL instead of a raw persisted UUID, and rate-limit per-task-ID resume attempts.
- Document this endpoint's trust model explicitly (similar to the report's "long term: document privileged roles/responsibilities" recommendation), since the existing `UnauthedRunResumed` audit event name suggests awareness of the risk without an enforced compensating control.

### Proof of Concept
1. Create (or observe) an async pipeline job that suspends awaiting an external adapter's callback (e.g., a `bridge async=true` task), which produces a `responseURL` of the form `http://<node>/v2/resume/<taskUUID>`.
2. An attacker who obtains this `taskUUID` (via log exposure, network capture, or a compromised bridge) sends: `PATCH /v2/resume/<taskUUID>` with body `{"data": {"result": "<attacker-controlled value>"}}` — no authentication headers required, confirmed by the route registration at [6](#0-5)  and the lack of any auth check in [7](#0-6) .
3. The suspended run resumes immediately with the attacker-supplied value via `ResumeRun`, as shown at [8](#0-7) , propagating the injected data through the remainder of the pipeline DAG.

Note: I could not verify from the index alone how tightly the `taskUUID` is scoped/exposed in production deployments (e.g., whether it ever appears in externally-reachable logs or third-party bridge configs) — that would require checking actual bridge adapter configurations and deployment logging practices, which are outside indexed file contents.

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

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
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
