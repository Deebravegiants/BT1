### Title
Unauthenticated `Resume` endpoint allows forging async bridge/external-adapter callbacks to hijack pipeline run results - (File: core/web/pipeline_runs_controller.go)

### Summary
The `PipelineRunsController.Resume` handler, which is used to complete async `bridge` tasks (external adapter callbacks), performs **no authentication or authorization check** on the caller. Any actor who obtains the task's `runID` (UUID) can POST an arbitrary `pipeline.ResumeRequest` and resume/finish a suspended pipeline run with attacker-chosen `value`/`error`, impersonating the legitimate external adapter that was supposed to deliver that result.

### Finding Description
When a `BridgeTask` runs asynchronously, it embeds a callback URL of the form `/v2/resume/<taskID>` in the outgoing request to the external adapter [1](#0-0) . The external adapter is expected to later POST its result back to that URL to resume the paused pipeline run.

The corresponding controller method, `Resume`, only validates that `runID` parses as a UUID and that the JSON body decodes into a `ResumeRequest` — it never verifies the caller's identity, an EI/API token, HMAC signature, or any secret tied to the specific bridge/task: [2](#0-1) 

The handler directly calls `App.ResumeJobV2` → `runner.ResumeRun` → `orm.UpdateTaskRunResult(ctx, taskID, Result{Value, Error})`, which updates the task run purely based on the supplied `taskID` and blindly trusts the caller-provided `Value`/`Error`, with no check that the request actually originates from the external adapter/bridge server associated with that specific pending task: [3](#0-2) 

Notably, the audit log event fired at the end of this handler is literally named `UnauthedRunResumed`, corroborating that this route is deliberately treated as an unauthenticated endpoint: [4](#0-3) 

This is structurally the same bug class as the OpenQ `claimBounty` issue: the system accepts an unauthenticated, attacker-suppliable "who completed this work / here is the result" claim (`_closer` in OpenQ, `taskID` + `Result` in Chainlink) and acts on it (fund transfer in OpenQ, pipeline result / on-chain tx trigger in Chainlink) without cryptographically or session-verifying that the caller is the legitimate party (the victim/`U1` in OpenQ, the correct external adapter/bridge in Chainlink).

### Impact Explanation
If a `taskID` (a UUID minted per pending async task) is disclosed by any means — logging, error messages, network capture on an unencrypted/misconfigured bridge, a malicious or compromised bridge/EA server, browser history via Explorer/Operator UI, etc. — any unauthenticated third party can:
- Forge the result of a pending job run (e.g., inject a fabricated price, VRF output, or other oracle response) causing the associated pipeline to complete with attacker-controlled data.
- Trigger unintended downstream actions (e.g., `ETHTx` submission) driven by attacker-controlled `Result.Value`.
- Cause denial-of-service by resuming runs with `Result.Error`, preventing the legitimate adapter's real result from ever landing (the run is already marked resumed).

This is a request-impersonation / unauthorized-action class vulnerability directly reachable from an unprivileged, unauthenticated HTTP client (no session, no API key, no EI credentials required).

### Likelihood Explanation
Exploitability depends on the attacker learning a specific pending `taskID`. This is not a guessable sequential ID (it's a UUID), so it is not trivially bruteforceable, but the endpoint provides zero defense-in-depth: unlike every other write-capable route registered through `Authenticate(...)` in `core/web/router.go`, `Resume` requires no secret at all. Any leak of the UUID (logs, proxy/monitoring, malicious/compromised external adapter operator, SSRF, or misconfigured logging of the `responseURL`) is sufficient for full exploitation, and there is no secondary authentication factor to fall back on.

### Recommendation
Bind the resume callback to a verifiable secret tied to the specific bridge task rather than relying solely on knowledge of the UUID:
- Require the external adapter to present a per-task shared secret/HMAC signature (e.g., derived similarly to `auth.HashedSecret`) that is verified in `Resume` before calling `ResumeJobV2`.
- Alternatively, require authentication via a token scoped to the specific bridge, and verify that the `taskID` belongs to a task associated with that bridge before accepting the result.
- At minimum, apply constant-time secret comparison and rotate/expire the resume token so leaked URLs cannot be replayed indefinitely.

### Proof of Concept
1. Configure a webhook/bridge job with an `async=true` `BridgeTask`; the node generates a `responseURL` such as `http://node/v2/resume/<taskID>` and sends it to the external adapter as part of the request body [1](#0-0) .
2. Obtain/leak that `taskID` (e.g., via a compromised/malicious adapter, network capture, or log exposure).
3. As an unauthenticated attacker, send: `PATCH /v2/jobs/:ID/runs/<taskID>` with body `{"error": null, "data": {"result": "9999999"}}` — no `X-API-KEY`, `X-API-SECRET`, or EI headers required.
4. `Resume` accepts the request purely based on the UUID matching a pending task and resumes the pipeline run with the attacker-supplied value [2](#0-1) , completing the run with forged data instead of the legitimate external adapter's response.

### Citations

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

**File:** core/web/pipeline_runs_controller.go (L134-161)
```go
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
