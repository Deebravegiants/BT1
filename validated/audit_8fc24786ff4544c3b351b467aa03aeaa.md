### Title
Unauthenticated task-resume endpoint allows resuming/injecting results into suspended pipeline runs using only a leakable UUID - (File: core/web/router.go)

### Summary
Chainlink exposes `PATCH /v2/resume/:runID` with no authentication middleware. Anyone who obtains a task-run UUID can complete/inject a result (or an arbitrary error) into a suspended pipeline run, mirroring the CVE-2026-10560 pattern where an unauthenticated attacker uses a valid job identifier to read/cancel job state on an unauthenticated endpoint.

### Finding Description
`v2Routes` registers this route on the unauthenticated group, separate from the `authv2` group that requires session/token auth: [1](#0-0) 

The handler parses the `runID` path param as a `uuid.UUID` (the pipeline **task run** ID, not the job ID) and, without any authentication or ownership check, decodes a `pipeline.ResumeRequest` body and forwards it to resume the pipeline: [2](#0-1) 

`ResumeJobV2` → `runner.ResumeRun` directly updates the task run result and, if this was the blocking task, restarts pipeline execution using attacker-supplied `value`/`error`: [3](#0-2) [4](#0-3) 

The intended trust model is that the UUID (`t.uuid`) embedded in the `responseURL` sent to the external bridge adapter is a "bearer-token"-like secret: [5](#0-4) 

This UUID is transmitted in plaintext HTTP request bodies to third-party bridge/external-adapter endpoints (`http://.../v2/resume/<uuid>`), as shown in tests, meaning it traverses the network to external, potentially untrusted or compromised third-party services, can be captured via network logging/proxies on either side, or leaked through bridge adapter logs: [6](#0-5) [7](#0-6) 

The endpoint has no rate limiting, no signature/HMAC validation of the callback, and no binding to the original outbound request (e.g., IP allowlist, one-time signed token) — only knowledge of the UUID string. This is architecturally analogous to the reported Langflow flaw: an internet-facing endpoint that performs privileged state mutation (or state disclosure) on an identifier-only basis, with no authentication layer, explicitly flagged internally via the audit event name `audit.UnauthedRunResumed`: [8](#0-7) 

### Impact Explanation
If the run-resume UUID is disclosed (through a compromised/malicious external adapter, network capture between the node and the adapter, adapter-side logging, or a misconfigured/malicious bridge), an unauthenticated attacker can:
- Inject an arbitrary `value` into the suspended pipeline task, corrupting downstream computation (e.g., a manipulated price/data feed value flowing into subsequent tasks such as `ETHTx`), or
- Inject an arbitrary `error`, forcing early/failed completion of the run (denial-of-service against that job execution) — the CVE's "cancel jobs" analog.

Because the resumed value can flow into on-chain transaction tasks (`ETHTxTask` uses `PipelineTaskRunID` for the same resume mechanism), a successful forged resume could influence transaction data derived from the pipeline result, which is a meaningful integrity impact beyond simple information disclosure.

### Likelihood Explanation
Exploitation requires knowledge of a valid, in-flight task run UUID. This is not trivially guessable (UUIDv4 space), so likelihood is lower than the original CVE's likely more predictable identifiers, but the UUID is deliberately transmitted to external, third-party HTTP endpoints as part of normal operation (bridge adapters), putting it outside the node's trust boundary. Any adapter-side logging, proxying, browser dev tools, or a compromised/malicious bridge operator can capture it and replay it to `/v2/resume/:id` before the legitimate response arrives, since there's no additional secret, signature, or expiry enforced by the endpoint itself.

### Recommendation
- Bind the resume callback to a signed, single-use token independent of the task UUID (e.g., HMAC-signed with node secret and short expiry) rather than relying solely on UUID secrecy.
- Add replay/idempotency protection independent from DB row locking (currently only relied upon at the ORM layer) and rate-limit this route.
- Restrict/validate the resume request against the original bridge target host or require a bridge-specific pre-shared secret header, in addition to the UUID.
- Add audit/alerting on high-frequency or failed calls to this endpoint from unexpected sources.

### Proof of Concept
1. Configure a job with an async bridge task; the node sends a request to the bridge adapter containing `"responseURL": "http://<node>:6688/v2/resume/<task-uuid>"` as shown in [5](#0-4) .
2. An entity with visibility into that outbound request (the bridge server itself, a network intermediary, or adapter logs) extracts `<task-uuid>`.
3. Without any Chainlink session/API token, send:
   ```
   PATCH /v2/resume/<task-uuid>
   Content-Type: application/json

   {"value": "<attacker-controlled-json>"}
   ```
4. The node accepts the request per [9](#0-8)  and resumes the pipeline with the attacker-supplied value/error, with no authentication check performed anywhere in the call path.

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

**File:** core/services/pipeline/task.bridge_test.go (L633-636)
```go
			return
		}
		assert.Equal(t, fmt.Sprintf("%s/v2/resume/%v", cfg.WebServer().BridgeResponseURL(), id.String()), reqBody.ResponseURL)
		w.Header().Set("Content-Type", "application/json")
```

**File:** core/services/pipeline/runner_test.go (L798-799)
```go
		}
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
```
