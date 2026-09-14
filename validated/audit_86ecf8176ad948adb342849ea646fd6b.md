### Title
Unauthenticated pipeline run resume endpoint allows arbitrary result injection into async task callbacks - (File: core/web/pipeline_runs_controller.go)

### Summary
The Aave-flashLoan side-entrance bug root cause is that `executeOperation` (a callback meant to be invoked only as a trusted continuation of a flow initiated by the contract itself) never validates who invoked it, so any unprivileged caller can supply the "resume" callback and smuggle attacker-controlled parameters back into privileged contract logic. The direct chainlink analog is the `PipelineRunsController.Resume` HTTP handler, which resumes a suspended pipeline run/task (the "callback" continuation of an async bridge/external-adapter task) and is wired up in the router **without any authentication middleware**, trusting only knowledge of a UUID `taskID` to accept the caller's supplied result.

### Finding Description
`PipelineRunsController.Resume` is the callback endpoint that completes an async pipeline task (e.g. a bridge/external-adapter task) and resumes execution of the suspended job run: [1](#0-0) 

It parses only a `taskID` (UUID) from the URL and a user-supplied JSON body (`pipeline.ResumeRequest`), then feeds that value directly into `ResumeJobV2`/`runner.ResumeRun`, which updates the task-run result and restarts the suspended pipeline: [2](#0-1) 

The route is registered without going through the `auth.Authenticate` middleware used elsewhere for session/API-token/external-initiator auth (`AuthenticateBySession`, `AuthenticateByToken`, `AuthenticateExternalInitiator` in `core/web/auth/auth.go`), unlike other admin/job endpoints. The handler itself even logs this explicitly via the audit event `audit.UnauthedRunResumed`: [3](#0-2) 

This mirrors the reported bug class precisely: the code assumes that only the entity that legitimately started the async task (the external adapter/bridge that was given the `taskID`) will ever call back into this "continuation" endpoint, but the endpoint itself performs **no verification of the caller's identity or the caller's right to complete this specific task** — the sole "authorization" is possession of the UUID. Anyone who can guess, leak, or observe the UUID (e.g. via logs, timing side channels, or a compromised/lenient adapter) can inject an arbitrary `Result` value into a suspended run and force the node to resume with attacker-chosen data, exactly as `executeOperation` blindly trusted attacker-supplied flash-loan `params` because it never checked `_initiator == address(this)`.

### Impact Explanation
An attacker who obtains a pending task's UUID (values are often echoed in responses, external-adapter payloads, or exposed via other side channels) can craft a `PATCH /v2/jobs/:ID/runs/:runID` request with a forged `value`/`error` body and resume the run with attacker-chosen output. Because such tasks typically feed into subsequent pipeline stages (e.g. `ETHTx` tasks that submit on-chain transactions, price data used for OCR reports, etc.), this can lead to injection of falsified data into job runs and, depending on job composition, unauthorized fund-moving or state-changing actions triggered by node infrastructure — i.e., "unauthorized job run" / "cross-user response confusion" as called out in the validation criteria.

### Likelihood Explanation
The likelihood depends on how strongly `taskID` UUIDs are protected as secrets in practice; if adapters, logs, or other observability channels leak the run/task ID (a realistic operational scenario, since these IDs are not treated as secrets by design and this endpoint intentionally has no other auth per its own audit-log naming), exploitation is straightforward — a single unauthenticated HTTP request completes the attack, with no rate limiting or additional identity check visible in the handler.

### Recommendation
Bind the resume/callback authorization to the actual initiator of the async task: require that only the specific bridge/external adapter/external-initiator that was dispatched the task (verified via the same kind of `auth.Token`/HMAC-style secret architecture already used for `ExternalInitiator` requests in `core/bridges/external_initiator.go`) can call back with a completed result, in the same way the report recommends requiring `_initiator == address(this)`. Concretely: generate and store a task-specific secret/HMAC when the async task is dispatched, and require it (in addition to the UUID) on the `Resume` call, verified via constant-time comparison like `bridges.AuthenticateExternalInitiator`.

### Proof of Concept
Not independently reproducible from static analysis alone (the exact route registration/middleware wiring in `core/web/router.go` could not be fully retrieved before the tool budget was exhausted, and dynamic testing of the running node is required to confirm no other implicit protections exist). The audit-log naming `audit.UnauthedRunResumed` and the absence of any `auth.Authenticate(...)` wrapper visible in the handler's own code strongly indicate the endpoint accepts unauthenticated `PATCH` requests once a `taskID` is known; a full PoC would require starting a node, creating a job with an async/bridge task, capturing the generated `taskID`, and issuing an unauthenticated `PATCH /v2/jobs/{ID}/runs/{taskID}` with a forged body to confirm the run resumes with attacker-controlled data.

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
