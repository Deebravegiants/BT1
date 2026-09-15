### Title
Unauthenticated pipeline run resume endpoint accepts arbitrary `runID`/result without ownership validation - (File: core/web/pipeline_runs_controller.go / core/web/router.go)

### Summary
The `deposit`-style bug class in the report ("missing input validation on a caller-supplied identifier leading to funds/state being applied to the wrong destination") maps to the `PATCH /v2/resume/:runID` endpoint, which is mounted with no authentication and accepts an attacker-controlled `runID` and arbitrary `result` payload that is applied directly to whatever pipeline task matches that UUID.

### Finding Description
The route is registered on the *unauthenticated* router group, separate from the `authv2` group that requires token/session auth: [1](#0-0) 

The handler itself performs no check that the caller is authorized to resume that specific run/task — it only validates that `runID` parses as a UUID and that the JSON body decodes, then hands the caller-supplied `result` straight to `ResumeJobV2`: [2](#0-1) 

There is no validation that:
- the `runID` actually belongs to a task that is in a "pending external resume" state expecting this caller,
- the caller has any relationship to the job/task owner,
- the `result` payload is scoped/sanitized to the expected shape for that specific task.

This is functionally analogous to the reported `deposit(to, ...)` bug: a caller-supplied identifier (`to` address / `runID`) is used to route an operation (fund deposit / pipeline result injection) without validating that the identifier is legitimate for the caller's intended target. If the `runID` (a task UUID) is guessable, logged, or otherwise obtained by an unrelated party, that party can complete/resume someone else's pending pipeline task with attacker-chosen `result` data — this is the "invalid/uncontrolled destination" analog to the zero-address deposit issue, occurring in an unauthenticated, internet-facing part of the node's API surface.

### Impact Explanation
Pipeline runs frequently drive on-chain writes downstream (e.g., VRF fulfillment, Keeper/upkeep execution, external-adapter-driven data that becomes a report value). Injecting an attacker-controlled `result` into a pending task via a guessed/leaked `runID` can corrupt or redirect the outcome of that pipeline run, potentially leading to incorrect on-chain submissions or unauthorized completion of a job run that was not meant to be finished by that caller. Because the endpoint requires no authentication at all, any unprivileged network client that can reach the node's HTTP API can attempt this.

### Likelihood Explanation
Likelihood depends entirely on whether `runID` (a UUID) is treated as an unguessable bearer secret throughout its lifecycle (i.e., never logged, never exposed to third parties, never included in URLs passed through untrusted channels). UUIDv4 space makes blind guessing impractical, but the code makes no attempt to independently validate authorization beyond UUID parsing — there is no secondary check (e.g., signature, secret token binding, requester identity) tying the resume request to the original task issuer. This is a design reliance on secrecy of an identifier rather than positive authorization/input validation, which is the same missing-validation pattern flagged in the source report.

### Recommendation
- Do not rely solely on UUID unguessability as an authorization control for `/v2/resume/:runID`.
- Bind resume tokens to the specific pending task via a dedicated per-task secret/nonce (separate from the run/task ID used for lookups), verified on resume.
- Validate that the task referenced by `runID` is actually in an "awaiting external resume" state before accepting a result, and reject/no-op otherwise.
- Consider rate-limiting and audit-logging failed resume attempts to detect enumeration attempts (partially covered by `audit.UnauthedRunResumed`, but only logged on success).

### Proof of Concept
1. An external, unauthenticated client sends `PATCH /v2/resume/<runID>` with a JSON body containing an arbitrary `result` value, where `<runID>` is a task UUID obtained by any means other than being the legitimate task initiator (e.g., leaked via logs, callback URL exposure, or a race/guess).
2. `PipelineRunsController.Resume` parses the UUID, decodes the body into `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` with no ownership or state check [3](#0-2) .
3. If the task with that ID is currently pending, the attacker's `result` is applied to complete it, regardless of whether the attacker is the legitimate resumer for that task.

Note: full confirmation that no additional secret-binding exists elsewhere in `ResumeJobV2`/pipeline task-run bookkeeping could not be completed due to index/tool-call limits; a Devin session with full repo access should verify whether task resume tokens are bound to a separate secret before treating this as conclusively exploitable in production.

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
