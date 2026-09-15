### Title
Unauthenticated pipeline-run `Resume` endpoint allows any actor to inject results into another user's suspended job run - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `uniswapV3Staker` bug allowed any address to call `unstakeToken` on behalf of another depositor once a time condition (`endTime`) was reached, letting an attacker claim someone else's rewards through a side-channel (`LPStaker`). The closest reachable analog in this codebase is the `PipelineRunsController.Resume` handler, which completes a suspended pipeline task run identified only by a UUID (`runID`/`taskID`) with no verification that the caller is the entity that originated/owns that specific async task.

### Finding Description
`PipelineRunsController.Resume` accepts a `taskID` UUID from the URL, decodes an arbitrary JSON `ResumeRequest` body, and directly calls `prc.App.ResumeJobV2(ctx, taskID, result)`: [1](#0-0) 

There is no authentication check inside `Resume` (unlike `Create`, which explicitly branches on `auth.GetAuthenticatedUser`/`auth.GetAuthenticatedExternalInitiator`). The audit event fired at the end of the handler is literally named `audit.UnauthedRunResumed`, which is the codebase's own convention for marking an endpoint as intentionally unauthenticated — the same pattern used for external-adapter callback endpoints that resume async bridge tasks (`/v2/resume/<id>`), as referenced in pipeline task tests: [2](#0-1) 

The intended caller of this endpoint is the external bridge/adapter that was originally given the resume URL as part of an async bridge task (`type=bridge async=true`). The security model relies entirely on the `taskID` UUID being secret/unguessable — there is no secondary credential, HMAC, or ownership check binding the resume request to the specific pipeline run's origin, task type, or the adapter that was addressed. This mirrors the `unstakeToken` root cause: an action that should be restricted to "the party for whom this specific pending unit of work was created" is instead reachable by any caller who can present the identifier, with no cryptographic or session-based binding proving they are the legitimate resumer.

### Impact Explanation
If a `taskID` value is leaked, guessed, logged, or intercepted (e.g., via a compromised/malicious external adapter, network intermediary, or log exposure), any external party can:
- Complete/resolve a suspended pipeline run with attacker-controlled result data before the legitimate adapter responds, causing incorrect data to be fed into subsequent pipeline tasks (e.g., `ethtx`, VRF fulfillment, price adjustments) — a direct "cross-user response confusion" and potential fund-movement vector, since resumed pipeline runs commonly finish by submitting on-chain transactions (`ethtx` task) using the injected result.
- Cause a race where a legitimate resume is pre-empted by an attacker's spoofed resume, similar to how in `unstakeToken` a legitimate depositor's rewards could be intercepted/claimed by a third party.

This is analogous in class (unprivileged request impersonation completing a state transition belonging to someone else) but the severity depends heavily on how well `taskID` values are protected from disclosure in practice — this cannot be fully confirmed from index contents alone (see caveat below).

### Likelihood Explanation
Likelihood is moderate: the resume endpoint is deliberately internet/adapter-facing and unauthenticated by design (as evidenced by the `UnauthedRunResumed` naming and its use for async external-adapter callbacks), so the only barrier to a cross-user "unstake"-style impersonation is unguessability of the UUID `taskID`. UUIDs are generally hard to brute-force, which limits opportunistic exploitation, but any leak of a pending task's UUID (logging, error messages, network capture, malicious/compromised external adapter that shares URLs) would allow full impersonation with no further authentication.

### Recommendation
Bind the resume action to the calling entity: e.g., require a secret/HMAC token scoped per resume request in addition to the UUID, verify the request matches the pipeline task's expected source (bridge/adapter identity), or maintain a single-use token bound to the specific pending task/bridge invocation. At minimum, ensure `taskID` values are never exposed in logs, error responses, or client-visible surfaces, and consider rate-limiting/monitoring repeated or out-of-context resume attempts.

### Proof of Concept
1. Create a webhook/cron/etc. job containing an `async=true` bridge task; the pipeline runner suspends the run and generates a `ResponseURL` of the form `http://<node>/v2/resume/<taskID>` (as seen in `core/services/pipeline/runner_test.go:799`). [2](#0-1) 
2. If an attacker obtains this `taskID` (via network capture, log leakage, or a malicious/compromised adapter), they can send `PATCH /v2/jobs/:ID/runs/:runID` (or whatever route maps to `Resume`) with an arbitrary JSON body before the legitimate adapter responds. [3](#0-2) 
3. `ResumeJobV2` is invoked with attacker-controlled `result`, completing the run with spoofed data — with no check binding the caller to the legitimate adapter/task owner.

Note: Due to index size limits, I could not retrieve the exact route registration in `core/web/router.go` to definitively confirm whether `Resume` is mounted outside all `Authenticate` middleware groups; the `audit.UnauthedRunResumed` naming strongly implies this, but a Devin session with full repo access should verify the router wiring directly before treating this as fully confirmed.

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

**File:** core/services/pipeline/runner_test.go (L796-801)
```go
		if !assert.NoError(t, err) {
			return
		}
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Chainlink-Pending", "true")
```
