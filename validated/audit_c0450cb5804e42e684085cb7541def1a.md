Confirmed: `/v2/resume/:runID` is registered completely unauthenticated (`unauthedv2.PATCH("/resume/:runID", prc.Resume)`), while the "pull funds then push back" reentrancy pattern in the report maps to Chainlink's async bridge task flow: the bridge task makes an external call (POST to the bridge/adapter URL) while a `pipeline_run` is suspended awaiting external input, and the callback mechanism that finalizes/resumes the run (`Resume`) is exposed without any authentication or ownership check on the caller.

### Title
Unauthenticated `/v2/resume/:runID` endpoint allows any external party to inject or race pending pipeline run results - ([File: core/web/router.go])

### Summary
The `PipelineRunsController.Resume` handler, which finalizes/resumes a suspended (async) pipeline run started by a `BridgeTask`, is mounted on an explicitly unauthenticated route group and accepts an arbitrary `taskID` (a UUID) with no secret/token verification tying the caller to the bridge that was originally invoked.

### Finding Description
The external report describes a reentrancy-class bug where an `Exchange` contract pulls funds, performs external calls, and later pushes funds back based on stale state, because the external call in the middle of the operation is not guarded — allowing manipulation of in-flight state via an unauthenticated callback path. The closest structural analog in this codebase is the async bridge/webhook resume flow.

`BridgeTask.Run` embeds a `responseURL` pointing to `/v2/resume/<taskUUID>` into the outbound HTTP request sent to a bridge/external adapter (`core/services/pipeline/task.bridge.go:364-374`), and the run is suspended (`pendingRunInfo()`) until that URL is called back. That callback route is registered as fully unauthenticated: [1](#0-0) 

`PipelineRunsController.Resume` parses only the `runID` (task UUID) from the path and the JSON body, with no signature, secret header, or bridge-identity check, then immediately calls `ResumeJobV2` → `pipelineRunner.ResumeRun`, mutating and restarting the pipeline run: [2](#0-1) [3](#0-2) 

The task UUID (`t.uuid`) that forms the callback URL/`runID` is a v4 UUID generated when the task run is created, and is only ever transmitted to the external bridge server as part of the outbound `responseURL` field — but nothing after that point verifies the caller of `/v2/resume/:runID` is the same bridge that received it, nor is the UUID treated as a secret with rotation/expiry semantics; it's a bearer-token-like value sitting in a URL path, sent over plain HTTP to third-party bridge adapters (potentially logged, cached, or proxied) and then trusted for resuming and finalizing the run. [4](#0-3) 

### Impact Explanation
An unprivileged network actor who learns/guesses/intercepts a pending task UUID (e.g. from bridge server logs, a compromised/malicious bridge, network intermediary, or replay of a captured request) can call `PATCH /v2/resume/:runID` directly, without any node credentials, to inject an arbitrary result value/error into that pipeline run and force it to resume with attacker-controlled data. Since job pipelines can drive on-chain transactions (e.g., a webhook/bridge task feeding into subsequent tasks that submit transactions), this is a viable path to unauthorized manipulation of a job run's outcome — the same "external call happens mid-operation, and the party controlling that external channel can reach back in and finalize state before the original caller intended" pattern flagged in the report, translated to Chainlink's async-run resume mechanism rather than a Solidity reentrancy guard.

### Likelihood Explanation
The route's lack of authentication is confirmed directly in the router configuration (`unauthedv2.PATCH("/resume/:runID", prc.Resume)`), and the handler performs no secondary validation beyond UUID parsing. Exploitability depends on obtaining a valid, still-pending `runID`, which is only disclosed to the configured bridge endpoint — so likelihood is moderate and contingent on bridge-side compromise, logging leakage, or interception, rather than being directly reachable from a fully anonymous internet client with no prior knowledge.

### Recommendation
Bind the resume token to the specific external bridge invocation cryptographically (e.g., HMAC-signed callback token bound to task ID + expiry, verified in `Resume`), rather than relying solely on UUID secrecy in a URL path. Additionally, invalidate/consume the token on first successful resume to prevent replay, and consider rate-limiting/auditing this endpoint given it is intentionally unauthenticated for legitimate external-bridge callbacks. This maps to the report's recommendation of guarding state-mutating paths that are reached via external calls made mid-operation.

### Proof of Concept
1. Configure a webhook/bridge-backed job with an `async=true` `BridgeTask`. When invoked, Chainlink suspends the run and sends the bridge adapter a request containing `responseURL: http://<node>/v2/resume/<taskUUID>` (`core/services/pipeline/task.bridge.go:364-374`).
2. An attacker who obtains this `taskUUID` (via bridge log exposure, network capture, or a compromised/malicious bridge server) sends `PATCH /v2/resume/<taskUUID>` directly to the node with a crafted JSON body (`pipeline.ResumeRequest`).
3. Because the route is registered under `unauthedv2` with no auth middleware (`core/web/router.go:239-243`), the request is accepted without any credential check, and `ResumeJobV2` immediately updates the task result and resumes the pipeline run with attacker-supplied data (`core/services/pipeline/runner.go:732-755`), potentially before or instead of the legitimate bridge response.

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

**File:** core/services/pipeline/task.bridge.go (L364-378)
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

	*requestData = merged
	return json.Marshal(merged)
}
```
