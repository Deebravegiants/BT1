### Title
Unauthenticated pipeline-run resume endpoint accepts arbitrary results and impersonates the external adapter callback - (File: core/web/pipeline_runs_controller.go, core/web/router.go)

### Summary
`PATCH /v2/resume/:runID` is registered on the **unauthenticated** router group and lets any network caller who knows (or discovers) a pending task's `runID` submit an arbitrary JSON body that is fed directly into the async pipeline task's result, without any check that the caller is the external adapter/bridge that the run was actually waiting on.

### Finding Description
The route is mounted with no auth middleware at all: [1](#0-0) 

The handler parses the `runID` path param, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, converts it into a `pipeline.Result`, and immediately resumes the job run with it: [2](#0-1) 

This mirrors the Sherlock finding's root cause: an operation that acts on an externally supplied "address"/target and "bytes"/payload (here, a `runID` and a caller-controlled result body) is executed without validating that the caller is the legitimate counterparty that the operation expects. In the Solidity report, `TimeLock.execute` trusted an unchecked `address`+`bytes` pair supplied by the caller; here, `Resume` trusts an unchecked `runID` + arbitrary result payload supplied by an unauthenticated HTTP caller, allowing it to "impersonate" the external adapter that the async `BridgeTask`/`HTTPTask` was actually waiting on. The `responseURL` that is normally handed only to the legitimate adapter is generated in `finalizeAndMarshalBridgeRequestData`: [3](#0-2) 

The only thing standing between an attacker and controlling a pending run's outcome is possession of the run's UUID (`t.uuid`), which is embedded in the `responseURL` sent to third-party adapters, logged, and potentially observable via network logs, proxies, or a compromised/curious adapter operator - there is no secondary secret or signature check tying the resume call back to the specific bridge/task that issued the callback.

### Impact Explanation
Any attacker capable of learning or guessing a pending run's UUID can:
- Force early completion of a pending async task with attacker-chosen data (e.g., a fake price/observation from a bridge/adapter that a job is waiting on), corrupting downstream `median`/`submit` pipeline stages.
- Trigger job-run completion that could culminate in on-chain transaction submission (`ethtx`/`submit` tasks) with attacker-influenced values, i.e., request impersonation leading to unauthorized job execution / potential fund-affecting on-chain submission.
- Because the audit log records `audit.UnauthedRunResumed`, the design already acknowledges this endpoint is intentionally unauthenticated, but that only documents the trust decision - it does not mitigate the impersonation risk if the UUID leaks.

This satisfies the "unauthorized job run or fund movement" / "request impersonation" criteria for a valid analog.

### Likelihood Explanation
Likelihood depends entirely on UUID confidentiality. Since `runID` is a UUIDv4 with no companion secret validated at resume time, exploitation requires only that some other party or channel (adapter logs, proxy/CDN logs, adapter-side bugs, network capture, or a rogue/compromised bridge adapter) exposes the value before the legitimate response arrives - the current design provides no defense-in-depth beyond the presumed unguessability of the UUID itself.

### Recommendation
- Bind the resume callback to a secret established when the async request was created (e.g., include a per-run HMAC/token in the `responseURL` and require it in the resume request body/header, verified server-side) rather than relying solely on the UUID’s unguessability.
- Alternatively, validate that the resume request originates from an allowlisted adapter/bridge (e.g., verify the request against the specific bridge's configured host, or require the `OutgoingToken`/similar credential already used elsewhere in the bridges subsystem).
- Rate-limit and audit-alert repeated resume attempts against invalid/foreign `runID`s to detect probing.

### Proof of Concept
1. Configure a job with an async `bridge`/`http` task; the pipeline computes `responseURL = <bridge_response_url>/v2/resume/<uuid>` and sends it as part of `requestData` to the external adapter (`core/services/pipeline/task.bridge.go:364-374`).
2. Obtain the `uuid` value through any leak vector (log aggregation, proxy access, network capture, or a malicious/compromised adapter).
3. Before the legitimate adapter responds, send:
   `PATCH /v2/resume/<uuid>` with body `{"value": "<attacker-controlled-data>"}` (no auth headers required, per `unauthedv2.PATCH("/resume/:runID", prc.Resume)`).
4. `PipelineRunsController.Resume` decodes the body and calls `prc.App.ResumeJobV2(ctx, taskID, result)` unconditionally, completing the pending task with attacker data instead of the legitimate adapter's response. [1](#0-0) [2](#0-1)

### Citations

**File:** core/web/router.go (L238-244)
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
