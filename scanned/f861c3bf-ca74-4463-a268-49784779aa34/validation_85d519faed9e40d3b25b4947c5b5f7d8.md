## Title
Unauthenticated `/v2/resume/:runID` endpoint allows anyone to resume any pipeline run and inject arbitrary task results - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `sweepToken()` bug class is "a caller-facing entry point with no access control that lets an unprivileged party manipulate protocol state/funds belonging to others." The closest reachable analog in this codebase is the `PipelineRunsController.Resume` handler, which is deliberately mounted on the **unauthenticated** router group and allows any anonymous caller to resume *any* pipeline run by GUID, injecting an attacker-controlled result value.

### Finding Description
In `core/web/router.go`, the `/v2/resume/:runID` route is explicitly registered on the `unauthedv2` group, bypassing `auth.Authenticate`: [1](#0-0) 

The handler itself, `PipelineRunsController.Resume`, takes the `runID` path parameter directly as the pipeline task UUID, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and passes the caller-supplied result straight into `App.ResumeJobV2` with no ownership check tying the run to any authenticated identity: [2](#0-1) 

There is no verification that the caller is the same external initiator/bridge/adapter that originally suspended the task, nor any secret/token bound to the specific run — only the raw run UUID (task ID) is required. If that UUID can be observed or guessed/leaked (e.g., via job run logs, webhooks, error messages, or a bridge task response), any unauthenticated actor can:
- Resume the run with attacker-chosen data, effectively completing/finalizing a pipeline task on behalf of the node.
- Repeatedly hit this open endpoint to interfere with in-flight runs.

This mirrors the `sweepToken()` pattern: a public entry point performs a state-changing/fund/data-affecting action on a resource that should be scoped to a privileged actor (the resource creator), but omits any authorization check, relying only on knowledge of an identifier.

### Impact Explanation
Because the pipeline run's continuation logic (`ResumeJobV2`) can finalize task results that feed downstream on-chain transactions (e.g., ETH request-and-forward jobs, VRF fulfillment callbacks, or other suspended bridge/adapter tasks awaiting an external response), an attacker who can guess/obtain a `runID` can inject an arbitrary result into that job run. Depending on the job pipeline, this can corrupt job outputs, cause incorrect on-chain submissions, or allow spoofing of external adapter/bridge responses without needing to compromise the bridge or authenticate at all — directly analogous to "unauthorized fund movement" in the reference report, since Chainlink job pipelines are frequently the trigger point for on-chain fund-moving transactions.

### Likelihood Explanation
Likelihood is bounded by the difficulty of obtaining a valid `runID` (a UUID task ID), so this is not as trivially exploitable as the fully-parameterless `sweepToken()`. However, the endpoint is *by design* unauthenticated (it exists specifically so that external bridges/adapters without a full API token can resume paused runs), so run IDs are inherently exposed to third parties (the external adapter/bridge itself receives the task ID to call back). Any other party who obtains that ID through logging, network capture, or a leaky adapter integration can call this endpoint with no credentials at all.

### Recommendation
- Bind resumption to a per-run secret/token issued when the task is suspended (e.g., a signed callback token), rather than relying solely on the run UUID as the credential.
- Rate-limit and audit-log repeated resume attempts per run ID (partially covered today by `audit.UnauthedRunResumed`, but only logs after the action succeeds).
- Constrain which task types are resumable via this open route (e.g., only tasks explicitly marked as awaiting an external async callback), and validate that the resuming caller matches the adapter/initiator that owns the pending task.

### Proof of Concept
1. Deploy a job with a task that suspends pending an external callback (e.g., `bridge` or `http` async task), producing a `runID` (UUID).
2. As soon as the `runID` is known (e.g., leaked via the callback URL sent to the external adapter, or observed in logs/network traffic), an attacker sends:
   ```
   PATCH /v2/resume/<runID>
   Content-Type: application/json

   {"error": null, "value": "<attacker-controlled result>"}
   ```
   with **no authentication headers** at all.
3. Because this route sits in the `unauthedv2` group [1](#0-0)  and the handler performs no ownership/token check [3](#0-2) , the node accepts the attacker's payload and resumes the run with the injected value, exactly as if the legitimate external initiator had responded.

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
