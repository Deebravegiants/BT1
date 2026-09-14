Based on my research, I found a genuinely unauthenticated endpoint (`audit.UnauthedRunResumed` even names it explicitly), which is a strong analog to the RFP bait-and-switch: an unprivileged caller can mutate pipeline state that was previously "accepted" (task suspended awaiting a specific external result) with attacker-controlled data, and this can drive fund-moving pipeline stages (ETH transactions) with no verification that the resumer is the party who was supposed to supply that result.

### Title
Unauthenticated `Resume` endpoint lets any caller inject results into suspended pipeline runs, enabling bait-and-switch tampering of in-flight jobs before fund-moving stages execute - (File: core/web/pipeline_runs_controller.go)

### Summary
`PipelineRunsController.Resume` (registered as `PATCH /v2/jobs/:ID/runs/:runID` and reachable also via `/v2/resume/:runID`) accepts a task run ID and arbitrary JSON result body and calls `App.ResumeJobV2` with no authentication or authorization check at all. The audit log call is explicitly named `audit.UnauthedRunResumed`, confirming this endpoint is intentionally left open.

### Finding Description
`Resume` parses `runID` from the URL and a `ResumeRequest` from the request body, then immediately calls: [1](#0-0) 

Unlike other controller actions in this file, `Resume` performs no call to `auth.GetAuthenticatedUser`, no role check (`RequiresEditRole`/`RequiresRunRole`), and no verification that the caller is the legitimate external system that the suspended task (e.g. a bridge/webhook task) was waiting on. The router wires this route without additional per-route auth middleware distinguishing it from session/token-authenticated routes, and the code explicitly labels the resulting audit event `audit.UnauthedRunResumed`.

This mirrors the RFP bait-and-switch class directly: a task is "accepted" into a suspended/pending state (analogous to the winning bid being accepted), but the actual value/result used to drive later fund-moving stages of the pipeline (e.g., ETH tx tasks that pay out based on the resumed value) can be supplied — or overwritten/raced — by any unauthenticated caller who guesses or observes the task run UUID, without the job's true completion criteria (a signed bridge callback, a legitimate EI, etc.) being verified at resume time.

### Impact Explanation
If a job pipeline suspends a task pending an external callback (a common pattern for bridge/EI-driven jobs) and a later pipeline stage uses the resumed value to determine a payout, fee, or on-chain transaction (fund movement), an unprivileged actor who can enumerate or predict `runID` can substitute their own result for the legitimate one — directly analogous to Bob rewriting his bid after Alice already committed to a distribution decision. This can corrupt job outputs feeding transmission/tx tasks, or be used for griefing/DoS by resuming runs with malformed/malicious data before the legitimate responder does.

### Likelihood Explanation
Likelihood depends on `runID` (a UUID for the task run) not being guessable/enumerable externally and on the network exposure of the node's HTTP API. If the node API is reachable by less-trusted parties (e.g., through a shared network segment or if run IDs leak via logs/errors/other endpoints), exploitation only requires an HTTP PATCH with the correct runID and no credentials — the code path has literally no auth gate, which is a stronger precondition than the original Solidity bug (which at least required knowing pool/job semantics).

### Recommendation
Add an authentication/authorization check to `Resume` consistent with other mutating endpoints (e.g., require the caller to be either a legitimate external initiator bound to the specific suspended task, or an authenticated user with at least `run` role), and/or bind resume tokens to a per-suspension secret (already partially present via `pipeline.ResumeRequest`/task metadata) so that only the party the task is actually waiting on can supply the result. At minimum, do not leave this endpoint reachable with zero authentication given it can influence downstream fund-moving pipeline stages.

### Proof of Concept
1. Create a job whose pipeline includes a task that suspends pending an external result (task run gets a `runID`), followed by a stage that uses the resumed value to drive a transaction/payout.
2. As an unauthenticated actor, discover or guess the `runID` (e.g., via a leaking log, timing, or shared infra).
3. Send `PATCH /v2/jobs/:ID/runs/:runID` with attacker-chosen JSON body to `PipelineRunsController.Resume`: [2](#0-1) 
4. The pipeline resumes using the attacker's value instead of the legitimate external system's value, corrupting the downstream fund-moving stage — the "bait-and-switch" analog: the pipeline had effectively "accepted" a pending completion, and the attacker substitutes the final payload before the true responder does, with no access control preventing it.

### Citations

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
