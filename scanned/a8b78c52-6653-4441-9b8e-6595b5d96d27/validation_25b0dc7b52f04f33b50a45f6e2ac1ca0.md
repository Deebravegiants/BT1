## Finding: Unauthenticated pipeline-run resume endpoint allows unauthenticated result injection

### Title
Unauthenticated `PATCH /v2/resume/:runID` allows arbitrary result injection into pipeline runs - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The Chainlink node's web router registers the pipeline-run resume endpoint outside of any authentication middleware group, unlike the analogous Sherlock finding where `safeTransferFrom` was reachable by any caller without an ownership/approval check. Here, any unauthenticated network caller who can reach the node's HTTP API can call `PATCH /v2/resume/:runID` with an arbitrary `taskID` and inject a result value/error into the corresponding suspended pipeline task run.

### Finding Description
In `core/web/router.go`, `v2Routes` creates an explicitly unauthenticated route group and registers the resume handler on it, separate from the `authv2` group that wraps all other job/run endpoints with `auth.Authenticate(...)`: [1](#0-0) 

```go
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)

authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
    auth.AuthenticateByToken,
    auth.AuthenticateBySession,
))
```

The handler itself performs no authentication or authorization check — it only parses the `runID` path parameter as a UUID and decodes the JSON body into a `pipeline.ResumeRequest`, then directly calls `ResumeJobV2`: [2](#0-1) 

`ResumeJobV2` forwards straight into the pipeline runner's `ResumeRun`, which updates the task run result and, if the run becomes unblocked, restarts pipeline execution with attacker-supplied data: [3](#0-2) [4](#0-3) 

The only "access control" for this endpoint is the unguessability of the `runID` (a v4 UUID used as the task run ID), which is sent out-of-band to external bridge adapters as part of the `ResponseURL` in outgoing bridge HTTP requests (`{bridgeResponseURL}/v2/resume/{taskID}`), as seen in the bridge task test: [5](#0-4) 

Notably, the code path is explicitly tagged as unauthenticated in the audit log call — the developers were aware this endpoint bypasses auth and rely purely on UUID secrecy as the access-control mechanism: [6](#0-5) 

### Impact Explanation
Any party who can observe or intercept a pending run's `taskID` (e.g., via the outbound bridge request/response, node logs, proxy/network taps, or other side channels) can resume the corresponding paused pipeline task with attacker-controlled result data or error, before or instead of the legitimate external adapter's response. Because pipeline runs commonly back price feeds, VRF callbacks, and other on-chain oracle reports, unauthorized result injection can corrupt oracle outputs feeding smart contracts — directly analogous to the "no access control" impact class in the reference report, where any caller could invoke a sensitive state-changing function meant to be restricted.

### Likelihood Explanation
Exploitation requires knowledge of a specific pending `taskID`, which is not exposed via any authenticated API to arbitrary users, so this is not trivially exploitable by a fully blind attacker. However, the endpoint provides zero authentication as a defense layer — it relies entirely on UUID confidentiality, which can be broken through network-level exposure of the bridge callback URL, misconfigured/compromised external adapters, verbose logging, or SSRF/leak from other node components. This is a design choice the maintainers appear aware of (given the explicit "UnauthedRunResumed" audit event name), but it still represents a complete absence of authentication on a state-mutating, potentially fund/report-impacting endpoint, matching the "unauthorized job run" and "cross-user response confusion" categories the analog should map to.

### Recommendation
Bind resume authorization to a per-run secret/HMAC token generated at run-suspension time (distinct from the run/task UUID) and require it in the resume request, or scope the resume capability to only the specific external adapter/bridge that initiated the pending call (e.g., via a signed callback token). At minimum, rotate/expire resume tokens after single use and rate-limit the endpoint to reduce exposure from guessed or leaked identifiers.

### Proof of Concept
1. Start a job whose pipeline includes an async `bridge` task; the node computes a `taskID` UUID and sends it in `ResponseURL` (`{bridgeResponseURL}/v2/resume/{taskID}`) to the external adapter, as shown in `task.bridge_test.go`.
2. An attacker who obtains this `taskID` (via network interception, adapter logs, or a malicious/compromised adapter) sends:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"error": null, "data": "<attacker-controlled-value>"}
   ```
   with no authentication headers at all.
3. `PipelineRunsController.Resume` accepts the request unauthenticated, calls `App.ResumeJobV2`, and the pipeline run resumes using the attacker-supplied value instead of the legitimate adapter response.

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

**File:** core/services/pipeline/task.bridge_test.go (L623-643)
```go
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
		assert.Equal(t, fmt.Sprintf("%s/v2/resume/%v", cfg.WebServer().BridgeResponseURL(), id.String()), reqBody.ResponseURL)
		w.Header().Set("Content-Type", "application/json")

		// w.Header().Set("X-Chainlink-Pending", "true")
		response := map[string]any{"pending": true}
		if !assert.NoError(t, json.NewEncoder(w).Encode(response)) {
			return
		}
	})
```
