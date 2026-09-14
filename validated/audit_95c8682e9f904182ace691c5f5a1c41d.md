### Title
Unauthenticated task resume endpoint allows anyone to complete/manipulate any pipeline run by guessing or leaking a task ID - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `PATCH /v2/resume/:runID` route is mounted on the `unauthedv2` route group with no session, API-token, or ownership check, and its handler `PipelineRunsController.Resume` accepts any UUID and directly injects an arbitrary result value into that pipeline task run, exactly mirroring the reported bug class: an unprivileged caller supplies only a value/ID (there, an NFT id; here, a task UUID) and the backend performs a privileged, state-changing operation without verifying the caller is authorized to act on that resource.

### Finding Description
The router registers this endpoint outside of any authentication middleware: [1](#0-0) 

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

All other v2 controllers (keys, transfers, bridge types, external initiators, etc.) are behind `auth.Authenticate(...)` with role checks (`RequiresAdminRole`, `RequiresEditRole`, `RequiresRunRole`) as seen further in the same file, e.g. `authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))` [2](#0-1) . The resume endpoint is a deliberate exception — but the handler itself performs no additional authorization at all: [3](#0-2) 

```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	rr := pipeline.ResumeRequest{}
	decoder := json.NewDecoder(c.Request.Body)
	err = errors.Wrap(decoder.Decode(&rr), "failed to unmarshal JSON body")
	...
	result, err := rr.ToResult()
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
	c.Status(http.StatusOK)
}
```

This ultimately calls into `runner.ResumeRun`, which looks the task run up purely by `taskID` and writes the caller-supplied output/error directly into the suspended pipeline run, then resumes execution of the pipeline (potentially continuing on-chain transaction/fund-moving tasks with attacker-controlled data): [4](#0-3) 

The database lookup that resolves a `taskID` to a run has no notion of ownership/tenant — it just matches `pipeline_task_runs.id = $1`: [5](#0-4) 

The presence of the audit event name `audit.UnauthedRunResumed` confirms this is a known, intentionally unauthenticated path (the taskID/UUID is meant to act as an unguessable bearer credential handed only to the async bridge/adapter that is supposed to call back). However, unlike the reported gauge bug where an NFT id is a well-defined ownership token checked against a registry, here **no code path re-validates that the caller is the legitimate external system that received the taskID**, and the audit trail records the action as "unauthenticated" rather than blocking it.

### Impact Explanation
If a task UUID is disclosed (e.g., via logs, a compromised or malicious downstream bridge/adapter, browser history, proxy logs, or brute-force of an insufficiently random ID in a misconfigured environment), any unauthenticated third party can complete or corrupt an in-flight pipeline run belonging to any job — including runs that drive on-chain transactions (e.g., resuming an `ethtx`/VRF fulfillment task with attacker-chosen data) — without holding any Chainlink session, API key, or role. This is a direct analog of the reported "anyone can call with a value/ID and take away/manipulate funds" pattern: the authorization boundary is absent, and the resource identifier is the only "credential" checked.

### Likelihood Explanation
Exploitability depends entirely on task-ID secrecy since the endpoint performs zero authentication. This is a lower-likelihood variant than the original NFT case (where token IDs are public by design), because task UUIDs are intended to be unguessable, single-use secrets normally known only to the external system chosen to fulfil the async task. Still, any leak of a task ID (logging, error messages, network intermediaries, malicious/compromised external adapter) results in unauthenticated fund/logic-affecting completion of that specific run, with no additional check possible to prevent it.

### Recommendation
Bind resumption to possession of a scoped, single-use signed token (not just the raw UUID) or require the resuming caller to also present the original request's authentication context (e.g., a per-task shared secret issued only to the invoked external task/bridge, validated server-side), and ensure task IDs are never logged or echoed in any response accessible to unauthenticated parties. Additionally, apply stricter server-side validation that a run is only resumable via the exact external endpoint/adapter it was dispatched to, rather than relying purely on knowledge of the UUID.

### Proof of Concept
1. Obtain (via log exposure, network capture, or a malicious bridge adapter) the `taskID` UUID associated with a suspended pipeline task for a victim's job run.
2. Send `PATCH /v2/resume/<taskID>` with a crafted JSON body (`pipeline.ResumeRequest`) with no authentication headers/cookies at all — the request succeeds because the route is registered on `unauthedv2` [6](#0-5) .
3. The handler writes the attacker-supplied result into `pipeline_task_runs` and resumes the run [7](#0-6) , potentially causing the pipeline to proceed with attacker-controlled data on subsequent tasks (e.g., transaction submission) without the requester ever needing to be an authenticated Chainlink node user.

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

**File:** core/web/router.go (L275-277)
```go
		ets := EVMTransfersController{app}
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
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

**File:** core/services/pipeline/orm.go (L271-293)
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
