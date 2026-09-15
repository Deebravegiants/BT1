Confirmed: `unauthedv2.PATCH("/resume/:runID", prc.Resume)` at `core/web/router.go:243` registers this endpoint with zero authentication middleware — it sits in the plain `/v2` group, not behind `auth.Authenticate(...)`, unlike every other pipeline-run route (`authv2.GET("/jobs/:ID/runs/:runID", prc.Show)` at line 401, or the run-creation route which requires `auth.RequiresRunRole` at line 456). The audit event name itself, `audit.UnauthedRunResumed` (`core/web/pipeline_runs_controller.go:159`), documents that this was a deliberate design choice, not an oversight in this file — but it is exactly the kind of "engine accepts externally-supplied value without validating who supplied it" divergence the report describes, applied to job-run state instead of an opcode.

### Title
Unauthenticated pipeline-run resume endpoint lets any caller inject arbitrary task results into suspended job runs - ([File: core/web/router.go])

### Summary
`PATCH /v2/resume/:runID` is mounted with no authentication middleware at all, while every other pipeline-run-affecting route requires session/token or run-role auth. Anyone who can reach the node's HTTP port can supply an arbitrary `runID` (a task UUID) plus an arbitrary JSON result body and have it injected into a suspended pipeline run's task output, resuming/finishing the run with attacker-chosen data.

### Finding Description
`core/web/router.go` registers routes in three groups: `unauthedv2` (no auth), `authv2` (session/token auth, often further gated with `auth.RequiresEditRole`/`RequiresAdminRole`/`RequiresRunRole`), and `userOrEI` (external-initiator, token, or session auth). The resume route is placed in the first group: [1](#0-0) 

Contrast this with the sibling run-creation route, which is deliberately wrapped in `auth.RequiresRunRole`: [2](#0-1) 

`PipelineRunsController.Resume` takes the `runID` path param, parses it as a UUID (task run ID), decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest`, converts it into a `pipeline.Result`, and directly calls `App.ResumeJobV2`, with no ownership/ACL check tying the caller to the task or job: [3](#0-2) 

That call chain flows into `runner.ResumeRun`, which calls `orm.UpdateTaskRunResult` to write the attacker-supplied `Result{Value, Error}` into the task run, and if the run becomes ready, re-launches `r.Run` to finish the pipeline with that data baked in: [4](#0-3) 

The only thing gating this is guessing/knowing a valid pending task UUID (`runID`) for a suspended async task (e.g., a `bridge` task awaiting an external adapter's async callback, as exercised by `Test_PipelineRunner_AsyncJob_InstantRestart`, which shows the response URL pattern `http://.../v2/resume/<taskID>`): [5](#0-4) 

Because the endpoint is completely unauthenticated, this is not a role-check bug within an authenticated flow — it is a missing-auth flow, functionally equivalent to the report's "engine accepts externally supplied state that should be validated against a trusted source" pattern: the node's execution engine (pipeline runner) treats externally injected values as trusted inputs to finish a job run.

### Impact Explanation
If a job's pipeline contains an async task (bridge adapter, HTTP-with-pending flag, VRF/ETHTx-adjacent flows that resume via task result) and its task run UUID is discoverable (leaked in logs, guessable due to sequential/low-entropy generation in a misconfigured environment, or obtained via any other minor information leak), an unauthenticated network caller can forge the resumed value that feeds the rest of the pipeline — including tasks that ultimately trigger on-chain transactions (`ETHTx` task type is explicitly special-cased in `runner.go` `Run`). This can cause the node to submit or fulfill requests using attacker-controlled data instead of the intended off-chain data, i.e., unauthorized/forged job-run completion — the closest in-scope analog to "unbacked value created via a semantics bypass," since it duplicates control over "what data completes a run" without the caller ever authenticating.

### Likelihood Explanation
Exploitation requires only network access to the node's `/v2` API and knowledge of a valid, still-pending `runID` (task UUID). UUIDs are normally high-entropy and not trivially guessable, so this is not remotely exploitable "for free" — an attacker needs some way to observe or leak the task UUID (e.g., via bridge adapter callback logs, monitoring/HTTP proxies, or another disclosure). Given that constraint, likelihood is moderate rather than trivial, but the complete absence of authentication (compared to every sibling route) is a clear deviation from the codebase's own security model and is worth flagging regardless of the UUID-secrecy assumption.

### Recommendation
- Require authentication (at minimum run-role token/session, or a scoped per-run secret) on `PATCH /v2/resume/:runID`, matching the pattern used for `/v2/jobs/:ID/runs` (`auth.RequiresRunRole`).
- If external adapters must call this endpoint without session credentials, issue a single-use, cryptographically random callback token per suspended task (bound to that task ID) and require it in the resume request, rather than relying solely on UUID secrecy.
- Audit-log the caller identity/source for resume events, not just "unauthed."

### Proof of Concept
1. Create a job with an async bridge task; the bridge adapter receives a `responseURL` of the form `http://<node>:6688/v2/resume/<taskUUID>` (as shown in `runner_test.go`).
2. An attacker who observes or leaks this `taskUUID` (e.g., via adapter logs, a compromised adapter, or a proxy) sends: `PATCH /v2/resume/<taskUUID>` with body `{"value": "<attacker-controlled data>"}` — no auth header required.
3. `PipelineRunsController.Resume` decodes the body and calls `App.ResumeJobV2` unconditionally.
4. `runner.ResumeRun` writes the forged value into the task run and resumes/finishes the pipeline, potentially driving downstream tasks (e.g., an `ETHTx` task) with attacker-chosen data instead of the legitimate adapter response.

### Citations

**File:** core/web/router.go (L238-244)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

```

**File:** core/web/router.go (L449-457)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
}
```

**File:** core/web/pipeline_runs_controller.go (L131-160)
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

**File:** core/services/pipeline/runner_test.go (L798-799)
```go
		}
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
```
