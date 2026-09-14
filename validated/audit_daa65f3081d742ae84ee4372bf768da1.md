## Analog Vulnerability Found

The Surge Protocol bug pattern (a state-changing function—`liquidate()`—reachable by any caller with no check that the caller is authorized to act on the specific resource, only that they hold the right "currency") maps to `chainlink`'s unauthenticated pipeline-run resume endpoint.

### Title
Unauthenticated `/v2/resume/:runID` endpoint lets any unprivileged client inject task results into arbitrary pipeline runs - (File: core/web/router.go)

### Summary
The route `PATCH /v2/resume/:runID` is registered in the `unauthedv2` group, bypassing all of Chainlink's session/token/external-initiator authentication middleware. Any caller who can send the request — not just the bridge adapter that originated the async task — can invoke `PipelineRunsController.Resume`, which forwards the raw body's value/error directly into `Application.ResumeJobV2` → `pipeline.Runner.ResumeRun` → `ORM.UpdateTaskRunResult`, mutating the state of that specific pipeline run. [1](#0-0) 

### Finding Description
`v2Routes` explicitly carves this single endpoint out of the authenticated router group: [1](#0-0) 

`Resume` takes the `runID` path parameter as a bare `uuid.UUID` (the task ID), decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest`, and passes the result straight through to `ResumeJobV2` with no ownership, ACL, or resource-binding check whatsoever: [2](#0-1) 

`ResumeJobV2` and the underlying `ResumeRun`/`UpdateTaskRunResult` accept any caller-supplied task UUID and result payload without verifying the caller is the entity (e.g., the external bridge/adapter) that the pending async task was actually delegated to: [3](#0-2) [4](#0-3) 

The only thing standing between "any unprivileged network client" and "resume this specific in-flight pipeline task with arbitrary attacker-controlled output/error" is knowledge of the task UUID — there is no cryptographic binding, per-caller allowlist, or session check comparable to the `AuthenticateBySession`/`AuthenticateByToken`/`AuthenticateExternalInitiator` middleware used on every other `/v2/*` mutation route. This is structurally identical to the reported `liquidate()` issue: a state-mutating action with real economic/operational impact is exposed to any caller who satisfies a single, weak precondition (there: possessing loan tokens; here: possessing/guessing a task UUID), instead of being restricted to the specific authorized party (there: a permissioned liquidator role; here: the specific external adapter that was delegated that exact task).

### Impact Explanation
An attacker who obtains or brute-forces a pending task's UUID (e.g., via log/monitoring leakage, a compromised bridge partner, or race-condition observation) can:
- Prematurely resolve another job's suspended pipeline run with attacker-chosen data or an injected error, corrupting downstream on-chain reporting/aggregation that depends on that pipeline's output.
- Force a run into a finished state before the legitimate external adapter responds, causing duplicate/garbage submissions or silently poisoning oracle data — directly comparable to "premature liquidation" in the referenced report, where an unauthorized party forces a state transition on someone else's resource ahead of the legitimate conditions being met.

### Likelihood Explanation
Task UUIDs (`google/uuid`, presumably v4) are not trivially guessable, which raises the bar versus the original report's zero-precondition exploit. However, the endpoint is intentionally unauthenticated by design (to support bridge adapter callbacks) and grants full write access to pipeline run state to anyone possessing that single value, with no secondary authentication, signature, or caller-identity check — the audit log even tags the action `UnauthedRunResumed`, acknowledging the lack of authentication at this call site: [5](#0-4) 

### Recommendation
Bind the resume capability to the specific task/adapter that was delegated the async work, e.g., by requiring a per-task bearer secret (distinct from the guessable/loggable UUID) issued when the task was suspended, or by authenticating the caller via the same external-initiator credential mechanism used elsewhere in the API, and validating that credential against the specific pending task before allowing `UpdateTaskRunResult` to proceed.

### Proof of Concept
1. Observe or intercept a pending bridge task's `runID` (UUID) for a job belonging to another user/job spec (e.g., via shared infrastructure logs, a malicious/compromised external adapter, or timing side channels).
2. Send `PATCH /v2/resume/<runID>` with an arbitrary JSON body (`{"error": "...", "value": ...}` per `pipeline.ResumeRequest`) without any session cookie, API token, or external-initiator header.
3. Observe that `core/web/router.go`'s `unauthedv2` group routes this straight to `PipelineRunsController.Resume` → `App.ResumeJobV2`, which finalizes/mutates the targeted pipeline run's task result — despite the caller never having authenticated as the job owner or the delegated external adapter.

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
