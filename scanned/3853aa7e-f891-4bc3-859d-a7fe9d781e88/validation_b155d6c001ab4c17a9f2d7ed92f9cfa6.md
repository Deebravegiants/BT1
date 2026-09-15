### Title
Unauthenticated resume of arbitrary async pipeline task runs via `PATCH /v2/resume/:runID` - (File: core/web/router.go / core/web/pipeline_runs_controller.go)

### Summary
`PATCH /v2/resume/:runID` is registered on the fully unauthenticated route group in `v2Routes`, and its handler, `PipelineRunsController.Resume`, accepts an attacker-supplied task UUID and result body and forwards it straight to `App.ResumeJobV2` without any authentication or ownership/ACL check. This mirrors the `reclaimContract` bug class: the endpoint trusts caller-supplied identifiers ("does a pending task with this ID exist and is it still suspended?") as the sole gate for performing a state-mutating, potentially fund/job-flow-affecting action, rather than verifying the caller is the legitimate initiator of that task (e.g., the specific external adapter bridge that owns it).

### Finding Description
In `core/web/router.go`:

```go
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)
``` [1](#0-0) 

Unlike every other pipeline-run route, which sits behind `authv2` (session/token auth) or `userOrEI` (session/token/external-initiator auth), this `resume` route has **no** authentication middleware attached at all.

The handler itself performs no additional authorization:

```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	rr := pipeline.ResumeRequest{}
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
``` [2](#0-1) 

The naming of the audit event `audit.UnauthedRunResumed` confirms this endpoint is intentionally unauthenticated (it's designed so external adapters, which hold no node credentials, can post back async results). Downstream, `runner.ResumeRun` → `orm.UpdateTaskRunResult` matches purely on the task UUID:

```go
sql := `
SELECT pipeline_runs.*, ...
FROM pipeline_runs
JOIN pipeline_task_runs ON (pipeline_task_runs.pipeline_run_id = pipeline_runs.id)
...
WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended')
FOR UPDATE`
``` [3](#0-2) 

There is no check that the caller is the specific bridge/external adapter that was actually sent the async request, nor any secret/token tied to that particular task run (analogous to the `reclaimContract` case, which only checked `expiry`/`settled`/`reclaimed` flags on attacker-supplied `Order` data instead of validating the order actually originated from the system). Here the only "proof" required is guessing/knowing a task UUID that happens to be `suspended`.

### Impact Explanation
Any unauthenticated party who obtains or brute-forces/guesses a pending task UUID for an async bridge task (UUIDs can leak via logs, previous API responses, or a race where a run is created but the adapter response hasn't arrived yet) can inject an arbitrary `value`/`error` into that specific pipeline task run and force the pipeline to resume/complete with attacker-controlled data. Since pipeline runs can feed on-chain transactions (e.g., driving OCR reports, VRF proofs, Keeper actions, or ETH transactions further down the pipeline DAG), this can lead to job runs completing with falsified data, corrupted outputs, or premature/duplicate resumption of a run — a direct analog to the reported "fake order" bug where unauthenticated/unverified input is trusted to trigger state-changing, downstream-consequential behavior in the protocol.

### Likelihood Explanation
Exploitability depends on how hard it is to obtain a valid, currently-suspended task UUID. UUIDs are not secrets by design (v4 UUIDs are not meant to double as bearer tokens), and the endpoint is deliberately internet/adapter-facing and unauthenticated, so the primary barrier is guessing or leaking a valid ID during the (typically short) suspension window for an async bridge task. This is a real, reachable path from an unauthenticated HTTP client hitting the node's gateway, matching the required "unprivileged actor" analog criteria.

### Recommendation
- Bind each async/resumable task to a per-task secret (e.g., an HMAC token or one-time credential returned only to the adapter that was actually contacted), and require that token in the `Resume` request instead of relying solely on the UUID as an implicit bearer credential.
- Alternatively, scope resume authorization to the specific bridge/external adapter identity (similar to the existing `AuthenticateExternalInitiator` pattern) rather than leaving the route fully unauthenticated.
- Add rate limiting / narrow response information (avoid distinguishing "not found" vs "wrong state" in error responses) to reduce ID-guessing feasibility.

### Proof of Concept
1. An async bridge task is created for job X; its task UUID (e.g., `abc-123`) becomes queryable/observable through the node's own APIs (`GET /jobs/:ID/runs/:runID`) or otherwise leaks/becomes guessable while `pipeline_runs.state = 'suspended'`.
2. Without any authentication, send:
   ```
   PATCH /v2/resume/abc-123
   Content-Type: application/json

   {"error": null, "value": "<attacker-controlled data>"}
   ```
3. `PipelineRunsController.Resume` parses the body via `pipeline.ResumeRequest.ToResult()` [4](#0-3)  and calls `App.ResumeJobV2(ctx, taskID, result)` with zero authentication checks.
4. `orm.UpdateTaskRunResult` locates the run purely by `pipeline_task_runs.id = $1` and current run state, writes the attacker-supplied output/error, and — if the run was `suspended` — flips state to `running` and triggers `runner.Run` to resume execution with the injected data. [5](#0-4) 

Note: I could not fully trace `App.ResumeJobV2`'s implementation body (only found references in mocks/interfaces) or definitively confirm end-to-end that no other guard exists between the controller and the ORM call; this should be verified directly in `core/services/chainlink/application.go` before treating this as fully confirmed.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
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

**File:** core/services/pipeline/orm.go (L276-284)
```go
		sql := `
		SELECT pipeline_runs.*, pipeline_specs.dot_dag_source "pipeline_spec.dot_dag_source", job_pipeline_specs.job_id "job_id"
		FROM pipeline_runs
		JOIN pipeline_task_runs ON (pipeline_task_runs.pipeline_run_id = pipeline_runs.id)
		JOIN pipeline_specs ON (pipeline_specs.id = pipeline_runs.pipeline_spec_id)
		JOIN job_pipeline_specs ON (job_pipeline_specs.pipeline_spec_id = pipeline_specs.id)
		WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended')
		FOR UPDATE`
		if err = tx.ds.GetContext(ctx, &run, sql, taskID); err != nil {
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
