Confirmed: `unauthedv2.PATCH("/resume/:runID", prc.Resume)` is registered on the unauthenticated route group (no `auth.Authenticate*` middleware) at [1](#0-0) , and the handler itself performs no authentication or authorization check before accepting an arbitrary caller-supplied result value and applying it to resume a suspended pipeline run [2](#0-1) .

### Title
Unauthenticated `/v2/resume/:runID` endpoint accepts arbitrary externally-supplied task results without validation - ([File: core/web/router.go])

### Summary
The `PipelineRunsController.Resume` handler is mounted on the unauthenticated route group and accepts an arbitrary JSON `pipeline.ResumeRequest` body from any network caller, using it to resume a suspended job run with attacker-controlled data, with no bounds/tolerance/sanity checking of the supplied value before it is fed back into the pipeline (and potentially on-chain via subsequent tasks).

### Finding Description
`v2Routes` registers the resume endpoint outside any authentication middleware group: `unauthedv2.PATCH("/resume/:runID", prc.Resume)` [3](#0-2) . This mirrors the audit report's core theme — accepting externally supplied data ("price") and using it to update state without any tolerance/validation check — except here the accepted value is an arbitrary pipeline task result rather than a price feed value, and the endpoint is fully unauthenticated (unlike the report's `isTrusted`-gated `updatePrice`).

`Resume` parses the `runID` and JSON body into a `pipeline.ResumeRequest`, converts it `ToResult()`, and passes it straight to `prc.App.ResumeJobV2(ctx, taskID, result)` with no caller identity check, no validation that the caller is authorized to resume that specific `taskID`, and no bounds/sanity check on the resumed value's contents [4](#0-3) . The only "protection" is a UUID-format `runID`/`taskID`, which is not a secret and can be observed/guessed depending on how it's exposed elsewhere (e.g. via job specs, logs, or other integrations that surface task IDs).

The response is explicitly logged as `UnauthedRunResumed` in the audit trail, which the code itself flags as an intentionally unauthenticated action [5](#0-4)  and [6](#0-5) .

### Impact Explanation
Any unprivileged network client that can reach the node's HTTP port and that knows or guesses a valid pending run's `taskID` can inject an arbitrary result value into a suspended pipeline task — directly analogous to the reported "price without tolerance check" issue, since there is no validation of the injected value against expected bounds/format before it flows into downstream pipeline tasks (which may include on-chain writing tasks such as `ethtx`). This could corrupt job outcomes, or in workflows where async/bridge results feed values used for downstream financial/state decisions, allow manipulation of the outcome.

### Likelihood Explanation
Exploitation requires knowledge of a currently pending/suspended task's UUID `taskID`. This is by design for legitimate async bridge/external-adapter callback flows, but the endpoint enforces no additional authentication (API key, EI credentials, etc.) to gate who can call it, so likelihood depends entirely on `taskID` confidentiality, which is not treated as a secret elsewhere in the codebase (it is a resumable, not a cryptographic secret).

### Recommendation
Require the resumer to authenticate (e.g., via bridge/EI credentials tied to the specific async task, or a per-run signed callback token) and validate/sanity-check the resumed value's shape and bounds before accepting it, rather than relying solely on the secrecy of the `taskID`.

### Proof of Concept
1. Create/observe a job with an async task and note its pending `taskID` (via job/pipeline run APIs or callback tokens issued during a legitimate async task).
2. Without any authentication headers, `PATCH /v2/resume/<taskID>` with an arbitrary JSON body, e.g. `{"error": null, "value": {"malicious": "value"}}`.
3. Observe via `GET /v2/jobs/:ID/runs/:runID` (authenticated) that the run resumed successfully with the attacker-supplied value, with no server-side validation rejecting an out-of-range or malformed value.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
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

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
```
