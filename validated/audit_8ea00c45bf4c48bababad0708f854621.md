### Title
Unauthenticated pipeline-run resume endpoint allows unprivileged actors to inject arbitrary task results into a suspended job run - (File: core/web/pipeline_runs_controller.go)

### Summary
The reported bug class is "state saved in step 1 of a two-step async operation, completed in step 2 based on data that can be manipulated/injected by an unprivileged actor between the two steps." The closest reachable analog in this codebase is the `PATCH /v2/resume/:runID` endpoint, which is mounted in the **unauthenticated** router group and completes ("step 2") a pipeline run that was suspended in "step 1" (e.g., an async `bridge` task), accepting attacker-controlled result data keyed only by a `taskID`.

### Finding Description
Async pipeline tasks (e.g. `BridgeTask` with `async=true`, or `ETHTxTask` with pending confirmations) execute in two steps:
1. **Step 1** – The task starts, is persisted with `PipelineTaskRunID` set to a UUID, and the run is marked `RunStatusSuspended` via `StoreRun` [1](#0-0) . A callback/response URL containing this taskID is handed to an external adapter to call back later (`.../v2/resume/<taskID>`).
2. **Step 2** – Whoever calls `PATCH /v2/resume/:runID` with a JSON body supplies the result that completes the pending task and resumes the run:

```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	rr := pipeline.ResumeRequest{}
	...
	result, err := rr.ToResult()
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
	...
``` [2](#0-1) 

Crucially, this route is registered in the **unauthenticated** router group, with no session, API-token, or external-initiator authentication method attached:
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")
	prc := PipelineRunsController{app}
	...
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(), ...))
``` [3](#0-2) 

`ResumeJobV2`/`ResumeRun` then directly updates the task-run result and, if the run was suspended, restarts pipeline execution using that value:
```go
func (r *runner) ResumeRun(ctx context.Context, taskID uuid.UUID, value any, err error) error {
	run, start, err := r.orm.UpdateTaskRunResult(ctx, taskID, Result{Value: value, Error: err})
	...
	if start {
		go func() {
			...
			r.Run(ctx, &run, false, nil)
``` [4](#0-3) 

This mirrors the GMX vault bug precisely: "step 1" saves state assuming a trusted party (GMX/the bridge adapter) will supply "step 2" data, but nothing at the HTTP layer cryptographically verifies that the caller of the resume/callback endpoint is the legitimate external adapter — only the unguessability of the `taskID` UUID stands between an unprivileged actor and injecting the completion value, just as the vault relies on an implicit (and violated) assumption that only GMX can change the LP-token balance between the two steps.

### Impact Explanation
If an attacker can learn or guess a pending task's UUID (e.g., via log exposure, error messages, monitoring, or a race where the ID is observable before the legitimate adapter responds), they can:
- Inject an arbitrary `pipeline.Result` (value or error) into a suspended run, causing the pipeline to resume with attacker-controlled data instead of the genuine bridge/adapter response — directly analogous to the vault completing a deposit/withdraw with attacker-injected LP-token balance instead of the actual GMX-transferred amount.
- Cause resource confusion/DoS by resolving another run's pending task before the legitimate response arrives, or by repeatedly hitting the endpoint.
This can corrupt job outputs, task submission data sent to bridges (`submit` task pulling from injected values), or on-chain transaction parameters derived from the pipeline result.

### Likelihood Explanation
The design intentionally leaves this endpoint unauthenticated because the `runID`/taskID is treated as a bearer secret (a random UUID). This is a known, documented trust boundary in Chainlink (the audit log even calls it `audit.UnauthedRunResumed`), so exploitation likelihood depends entirely on UUID confidentiality — moderate/low likelihood absent an additional disclosure vector, but the reachable, unprivileged-actor path exists exactly as required by the bug class.

### Recommendation
- Treat the resume taskID strictly as a high-entropy secret: avoid logging it or exposing it in any user-facing/authenticated API responses, error messages, or metrics that unprivileged users can access.
- Consider binding the resume callback to additional secret material (e.g., a per-run HMAC token, similar to `OutgoingSecret`/`OutgoingToken` patterns already used for `ExternalInitiator`) rather than relying solely on UUID unguessability.
- Add idempotency/state checks in `ResumeRun`/`UpdateTaskRunResult` to reject resume calls for tasks that are not in the expected "awaiting adapter response" state from an unexpected source, and rate-limit the endpoint.

### Proof of Concept
Not executable without a live node; conceptually:
1. Create a webhook/bridge job with an `async=true` bridge task; trigger a run so the task suspends and a `PipelineTaskRunID` (UUID) is generated.
2. If the UUID is disclosed (e.g., via logs, timing, or another disclosure channel), send:
```
PATCH /v2/resume/<taskID>
{"data": {"result": "attacker-controlled-value"}}
```
to the unauthenticated endpoint before the legitimate bridge adapter responds.
3. Observe `ResumeJobV2` → `ResumeRun` accept the attacker's value and resume the pipeline run with it, as shown in `pipeline_runs_controller.go` `Resume` and `runner.go` `ResumeRun` above — no verification ties the caller to the original bridge/adapter that step 1 dispatched the request to.

### Citations

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
