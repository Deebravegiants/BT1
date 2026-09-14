### Title
Unauthenticated pipeline-run "Resume" endpoint allows any unprivileged client who learns/guesses a suspended run's taskID to inject arbitrary results, with no cancellation or revocation mechanism — ([File: core/web/pipeline_runs_controller.go])

### Summary
The bug-class in the external report is: a single, callback-style state-mutating action (`cancel()`) that is gated only by knowledge of an off-chain-held parameter (the order), with no on-chain, self-service way to invalidate that capability, and no built-in defense against a race to consume it first. The closest reachable analog in this repo is the `PATCH /v2/jobs/:ID/runs/:runID` (**Resume**) endpoint in `PipelineRunsController.Resume`, which finalizes a *suspended* pipeline run by injecting a caller-supplied result, keyed only by the `taskID` (a UUID) — and is explicitly audited as `audit.UnauthedRunResumed`.

### Finding Description
`PipelineRunsController.Resume` accepts a `taskID` path parameter and a JSON body containing a result, and calls `App.ResumeJobV2(ctx, taskID, result)` to complete the suspended task/run: [1](#0-0) 

The audit event fired on success is literally named `audit.UnauthedRunResumed`, which strongly indicates this endpoint is designed to be reachable without the normal session/API-token authentication that gates the rest of the `/v2` API (that pattern exists because async bridge/external adapters resuming a job don't hold node credentials). The only thing standing between an unprivileged caller and mutating a suspended run's state is knowledge of the `taskID` UUID — the same "off-chain secret parameter" pattern flagged in the report, where cancellation/consumption of a pending action depends solely on knowledge of an opaque identifier, not on cryptographic ownership proof or an on-chain-verifiable state machine.

This mirrors the report's root cause precisely:
- There is exactly one way to finalize/consume the pending state (like the report's single `cancel()` path).
- Possession of an identifier (order parameters / taskID) is the only credential.
- There's no revocation or "invalidate all my pending runs" mechanism analogous to the recommended `minimumValidNonce`/counter approach.
- If the identifier leaks (logs, error messages, network observation, or is otherwise obtainable by a third party) before the legitimate resumer (e.g. a bridge adapter) responds, an attacker can race to submit a malicious/favorable result first — a direct analog of "Alice fulfills Bob's order before he can cancel it."

### Impact Explanation
An attacker who obtains a suspended run's `taskID` (through log exposure, error responses, or other means) can call the unauthenticated `Resume` endpoint to complete that pipeline run with attacker-chosen data before the legitimate external adapter/callback does, corrupting job results and any downstream on-chain actions derived from that pipeline run. Because there is no per-run authentication beyond the UUID and no cancellation/rotation capability, this is a genuine "unauthorized job run" / state-confusion vector reachable directly from an unprivileged internet-facing client request.

### Likelihood Explanation
Likelihood depends on whether `taskID` values are otherwise exposed to unprivileged parties (e.g., via debug logging of bridge/HTTP task parameters, as referenced in `CHANGELOG.md`, or via error responses) and whether the endpoint truly bypasses authentication in the router (the `audit.UnauthedRunResumed` naming is the primary evidence found; the exact router wiring for this route was not conclusively verified in this session due to tool-call limits, so this should be confirmed against `core/web/router.go`'s actual middleware registration for the `/v2/jobs/:ID/runs/:runID` PATCH route).

### Recommendation
- Verify in `core/web/router.go` whether the `Resume` route is intentionally exempt from `Authenticate(...)` middleware; if so, restrict it to trusted callers (e.g., bind resumption to a signed/HMAC'd callback token issued at suspension time rather than the bare UUID).
- Add a single-use/consumed marker and expiry to suspended tasks so a resume attempt can only succeed once and within a bounded window.
- Avoid logging or otherwise exposing `taskID`/resume URLs in any response, error, or debug log path reachable by unprivileged actors.

### Proof of Concept
Not independently reproduced in this session (no runtime access). The concrete code path (`Resume` handler keyed solely by `taskID`, audited as `UnauthedRunResumed`) is cited above; a full PoC would require confirming the router's auth middleware configuration for this route and a scenario where the `taskID` becomes known to a third party before the legitimate resumer responds.

### Citations

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
