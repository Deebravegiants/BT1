### Title
Unauthenticated pipeline run resume endpoint allows any external party to inject task results and control job execution - (File: core/web/router.go)

### Summary
The `/v2/resume/:runID` endpoint is registered without any authentication middleware, unlike virtually every other mutating endpoint in the node's API (`/v2/jobs/*`, `/v2/transfers/*`, `/v2/replay_from_block/*`, etc., all of which require `auth.Authenticate(...)`). This mirrors the MCPHub bug class: an endpoint that performs a privileged, state-mutating action on behalf of the node but is not wrapped by the authentication middleware, allowing an unauthenticated actor to invoke it directly.

### Finding Description
`v2Routes` in `core/web/router.go` creates an explicitly unauthenticated router group `unauthedv2` and registers the resume route on it: [1](#0-0) 

```go
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)

authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
    auth.AuthenticateByToken,
    auth.AuthenticateBySession,
))
```

Every other route mutating node state (`/v2/jobs`, `/v2/keys/*`, `/v2/transfers/*`, `/v2/bridge_types`, `/v2/external_initiators`, `/v2/replay_from_block/:number`, etc.) lives under `authv2`, requiring token or session authentication (`core/web/router.go:245-457`). `/v2/resume/:runID` is the one exception that is reachable with zero authentication.

The handler for this route, `PipelineRunsController.Resume`, only validates that `runID` parses as a UUID and that the request body is well-formed JSON — there is no secret, HMAC, or bearer token check tying the caller to the specific pending task: [2](#0-1) 

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

The audit event is even explicitly named `UnauthedRunResumed`, confirming the design intentionally leaves this route open to unauthenticated callers — but the only "secret" protecting it is the unguessability of the `taskID` UUID assigned to a pending async task, which is generated when a bridge task (`type=bridge async=true`) suspends the pipeline waiting for an external adapter callback.

`ResumeJobV2` forwards straight into the pipeline runner: [3](#0-2) 

```go
func (app *ChainlinkApplication) ResumeJobV2(
	ctx context.Context,
	taskID uuid.UUID,
	result pipeline.Result,
) error {
	return app.pipelineRunner.ResumeRun(ctx, taskID, result.Value, result.Error)
}
```

which updates the task's result and, if the run is suspended awaiting exactly that task, restarts the whole pipeline with the attacker-supplied value/error: [4](#0-3) 

### Impact Explanation
Anyone who can guess or obtain a pending task's `runID` UUID (e.g., via log leakage, network observation, or brute force against a low-entropy/predictable generator) can:
- Inject an arbitrary value or error into a suspended pipeline task without any authentication, directly influencing downstream computations (e.g., price feeds, OCR job pipelines) that depend on `median`/`multiply` tasks fed by that async bridge task, as shown in the runner tests: [5](#0-4) 
- Prematurely resume/complete a run before the legitimate external adapter responds, causing incorrect or attacker-controlled data to flow into a job.
This is a genuine unauthenticated-actor impact on data integrity of running pipeline jobs, consistent with "request impersonation" / "authentication bypass" in the report's rules.

### Likelihood Explanation
Exploitation requires knowledge of a specific `runID` (task UUID) for a currently suspended async bridge task. UUIDv4 space makes blind guessing infeasible, so the practical likelihood depends on whether task IDs leak (e.g., via logs, monitoring dashboards, error messages, or a compromised/malicious bridge adapter relaying the callback URL to a third party). Given the endpoint is intentionally unauthenticated by design (confirmed by the explicit `unauthedv2` grouping and `UnauthedRunResumed` audit event name), the security model here relies entirely on UUID secrecy rather than a token/HMAC — a weaker control than the authenticated-and-role-checked pattern used everywhere else in the API. This is a plausible-but-not-trivial exploitation path, lower likelihood than a fully open endpoint but still a deliberate authorization gap for a state-mutating action.

### Recommendation
Bind the resume callback to a verifiable secret rather than relying solely on UUID secrecy: e.g., include an HMAC/signed token (scoped to the specific task) issued at suspension time and validated in `Resume`, or require the external initiator/bridge access key used to create the original bridge request. At minimum, ensure task IDs are never logged or exposed anywhere reachable by unauthenticated actors, and consider rate-limiting/monitoring repeated invalid resume attempts to detect brute-force guessing.

### Proof of Concept
1. Configure a job with an async bridge task (`type=bridge async=true`), which suspends the pipeline run waiting for an external callback to `PATCH /v2/resume/:runID` where `runID` is the task's UUID, as exercised in `core/services/pipeline/runner_test.go` (`Test_PipelineRunner_AsyncJob_InstantRestart`) which asserts the callback URL is `http://localhost:6688/v2/resume/<taskID>` [6](#0-5) .
2. Without any authentication header/cookie, send:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"error": null, "value": "<attacker-controlled-data>"}
   ```
3. The request hits `unauthedv2.PATCH("/resume/:runID", prc.Resume)` and is processed with zero auth check, per `core/web/router.go:243`, injecting the attacker's value into the suspended run and resuming the pipeline with it, as confirmed by `PipelineRunsController.Resume` (`core/web/pipeline_runs_controller.go:134-161`).

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
