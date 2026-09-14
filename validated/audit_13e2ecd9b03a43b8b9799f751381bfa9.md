### Title
Unauthenticated `/v2/resume/:runID` endpoint allows unrestricted resumption of pending pipeline runs with attacker-controlled results - (File: `core/web/router.go`)

### Summary
The `RSIManager.sol` report flags a function with no access-control restrictions on its caller, allowing arbitrary manipulation. The strongest analog in this chainlink node is the `PATCH /v2/resume/:runID` route, which is registered on the `unauthedv2` group with **no authentication middleware at all**, and its handler accepts an attacker-supplied JSON body that is written directly into the pipeline task run's result/value.

### Finding Description
In `core/web/router.go`, the route is registered without any `auth.Authenticate(...)` wrapper, unlike every other `/v2/*` route: [1](#0-0) 

This calls `PipelineRunsController.Resume`, which parses the `runID` path parameter as a UUID, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and forwards it to `App.ResumeJobV2` with zero caller identity or role check: [2](#0-1) 

`ResumeJobV2` forwards directly to the pipeline runner's `ResumeRun`, which updates the task run result in the DB and, if this was the last pending task, restarts pipeline execution with the attacker-supplied `value`/`error`: [3](#0-2) [4](#0-3) 

The only "protection" is that `runID` is a UUID (task run ID), functioning as an unguessable bearer token rather than a real authentication/authorization mechanism — there is no rate limiting, no signature verification, and no binding to the external adapter that issued the async request. This design is intentional (async bridge/external-adapter callbacks use this exact URL, as seen in `task.bridge.go`'s `responseURL` construction), but it means **any party who can guess, brute-force, or otherwise obtain a task UUID can inject arbitrary results into a pending pipeline run**, exactly matching the reported bug class of "no restriction on the calling account." [5](#0-4) 

The audit log entry name itself — `UnauthedRunResumed` — confirms this endpoint is explicitly and knowingly unauthenticated: [6](#0-5) 

### Impact Explanation
If a task UUID is disclosed (e.g., via logs, a compromised external adapter, network sniffing of the outbound bridge request, or guessing since UUIDs from some code paths may be predictable/reused), any unauthenticated network client can:
- Inject a forged/malicious response value into a pending pipeline task run, which then feeds into downstream tasks (e.g., median/answer calculations) and can corrupt job outputs used for on-chain price/data reporting.
- Force resumption of a run with an attacker-chosen error, disrupting job execution (denial-of-service on specific job runs).
This directly maps to "unauthorized job run" / "cross-user response confusion" in the validated impact classes, since no caller identity is verified.

### Likelihood Explanation
Likelihood is moderated by the requirement to know or guess a valid pending task UUID, which is not trivially guessable (UUIDv4). However, the endpoint is fully unauthenticated and internet-facing by design (it's meant to be called by external, non-Chainlink-authenticated bridge adapters), so any leak of the UUID (logging, adapter compromise, network capture over non-TLS deployments, referrer leakage) provides a direct path to exploitation with no further access control layer to stop it.

### Recommendation
Add a defense-in-depth mechanism beyond the UUID-as-secret pattern for `/v2/resume/:runID`:
- Bind the resume token to a signed/HMAC value tied to the specific bridge/task request (not just the raw DB UUID) so leaking the UUID alone is insufficient.
- Add rate limiting to this specific unauthenticated route to slow down brute-force/guessing attempts (currently there is no rate limiter configured for `unauthedv2`, unlike `sessionRoutes`, which applies `rateLimiter` to unauthenticated session creation).
- Log/alert on repeated failed resume attempts to detect probing.

### Proof of Concept
1. Identify or leak a pending task's `runID` (UUID) — e.g., via external adapter logs, network capture of the `responseURL` sent to the bridge, or a compromised adapter integration.
2. Send an unauthenticated request:
```
PATCH /v2/resume/<leaked-task-uuid>
Content-Type: application/json

{"error": null, "data": {"result": "999999"}}
```
3. No authentication headers or session cookie are required — the route is in the `unauthedv2` group at `core/web/router.go:243`.
4. `PipelineRunsController.Resume` decodes the body and calls `App.ResumeJobV2`, which resumes the pending run with the attacker-supplied value, potentially completing the job with forged data or triggering a fatal error to disrupt execution.

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

**File:** core/services/pipeline/task.bridge.go (L364-374)
```go
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
```
