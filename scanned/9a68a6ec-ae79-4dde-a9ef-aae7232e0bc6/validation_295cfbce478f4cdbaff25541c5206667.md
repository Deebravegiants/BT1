### Title
Unauthenticated pipeline run resume endpoint allows arbitrary task completion with attacker-controlled data - (File: `core/web/pipeline_runs_controller.go`)

### Summary
The Sherlock finding centers on `ExtraRewarder.getReward(address account)` — a state-mutating function that takes an arbitrary target identifier but has no access control, letting an unprivileged caller act "on behalf of" another party and disrupt an accounting flow that depends on before/after state deltas. The closest analog in this chainlink codebase is `PipelineRunsController.Resume`, which accepts an arbitrary `runID`/task identifier from an unauthenticated caller and mutates pipeline state by finishing that run with attacker-supplied data, with no verification that the caller is the legitimate resumer of that specific task.

### Finding Description
`PipelineRunsController.Resume` is registered to handle `PATCH <application>/jobs/:ID/runs/:runID` [1](#0-0) . It parses the `runID` path parameter as a task UUID, decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest`, and immediately calls `prc.App.ResumeJobV2(ctx, taskID, result)` [2](#0-1) . There is no call to `auth.GetAuthenticatedUser` or `auth.GetAuthenticatedExternalInitiator` anywhere in this handler — unlike the sibling `Create` handler in the same file, which explicitly checks `isUser`/`isEI` before allowing a run to be triggered [3](#0-2) . The audit event emitted for this action is literally named `UnauthedRunResumed` [4](#0-3) , confirming that this endpoint is intentionally reachable without the normal session/token/external-initiator authentication that guards the rest of the `/v2/jobs` API surface (per `core/web/auth/auth.go`'s `Authenticate`/`RequiresRunRole` machinery) [5](#0-4) .

This mirrors the reported bug class exactly: a state-mutating function keyed only by a caller-supplied identifier (`account` in the Sherlock report, `runID`/taskID here) with no check that the caller is authorized to act on that specific identifier's behalf.

### Impact Explanation
If the `runID`/task UUID is discoverable or guessable (e.g., leaked through logs, other authenticated API responses that echo run IDs, or a predictable generation scheme), any unauthenticated network client can forge the resume payload and force a paused pipeline task (e.g., an async bridge/adapter callback task) to complete with attacker-chosen `result` data instead of the legitimate adapter's response. Depending on which job uses async resume (e.g., bridge-backed VRF/Keeper/OCR jobs awaiting external adapter results), this could inject falsified data into a job run that ultimately drives an on-chain transaction or feed value — a cross-user/cross-request response confusion and unauthorized state-mutation impact analogous to loss/misdirection of value in the original report.

### Likelihood Explanation
Likelihood depends on whether task run IDs are exposed to untrusted parties or are practically guessable; I could not fully verify within available iterations whether `core/web/router.go` applies any additional middleware to this specific route before dispatching to `Resume`, nor confirm the exact entropy/exposure of `runID` values at the point they'd be usable by an external, unprivileged caller. This is a caveat: the existence of the dedicated `UnauthedRunResumed` audit event strongly suggests the omission of authentication is an intentional design decision for legitimate external-adapter callbacks (secured only by the secrecy of the UUID), similar to common "webhook token in URL" patterns — so likelihood of it being an exploitable flaw (versus accepted design) hinges on whether that UUID is adequately protected end-to-end, which the current investigation could not conclusively verify.

### Recommendation
- Confirm in `core/web/router.go` whether the `Resume` route is deliberately excluded from `Authenticate` middleware; if so, ensure the `runID` (task UUID) is cryptographically random, never logged or returned in any authenticated/unauthenticated response beyond the entity that must resume it, and is single-use/invalidated after first resume.
- Consider binding the resume secret to a dedicated, high-entropy token distinct from the run ID itself (do not rely on the run ID doubling as both identifier and authorization secret), and add rate-limiting/brute-force protection on this endpoint.
- Add validation that the resumed task is still in a "pending external callback" state before accepting `Resume`, and audit-log the source IP/caller context for `UnauthedRunResumed` events for forensic traceability.

### Proof of Concept
Given a task run UUID `taskID`, an unauthenticated client can send:
```
PATCH /v2/jobs/{jobID}/runs/{taskID}
Content-Type: application/json

{"value": "<attacker-controlled result>"}
```
directly to `PipelineRunsController.Resume` [6](#0-5) , without presenting any session cookie, API token, or `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers, because no `auth.GetAuthenticatedUser`/`auth.GetAuthenticatedExternalInitiator` check gates this path — in contrast to `Create` in the same controller, which does perform such checks [3](#0-2) .

### Citations

**File:** core/web/pipeline_runs_controller.go (L109-112)
```go
	_, isUser := auth.GetAuthenticatedUser(c)
	_, isEI := auth.GetAuthenticatedExternalInitiator(c)
	// only users are allowed to run jobs using int IDs - EIs not allowed
	if isUser && !isEI {
```

**File:** core/web/pipeline_runs_controller.go (L131-157)
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
```

**File:** core/web/pipeline_runs_controller.go (L159-159)
```go
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
```

**File:** core/web/auth/auth.go (L153-173)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
}
```
