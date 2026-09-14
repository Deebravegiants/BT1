### Title
Unauthenticated `/v2/resume/:runID` endpoint lets any unprivileged caller inject arbitrary results into any node's pipeline run - ([File: core/web/router.go])

### Summary
The `PipelineRunsController.Resume` handler, which resumes a paused pipeline task with attacker-supplied result data, is registered on an unauthenticated route group with **no session, API-token, or external-initiator authentication check whatsoever**. Any network client that can reach the node's HTTP API can invoke this endpoint for any `runID` and inject arbitrary values into the pipeline, mirroring the reported `Collateral.withdrawFrom()` bug class where a privileged, account-scoped action is reachable by an unauthenticated/unprivileged caller because no ownership/authorization check is performed on the affected resource.

### Finding Description
`v2Routes` explicitly places the resume route in the `unauthedv2` group, distinct from `authv2` (session/token-authenticated) and `userOrEI` (user-or-external-initiator-authenticated) groups used for every other mutating endpoint: [1](#0-0) 

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
``` [1](#0-0) 

The handler itself performs zero identity or ownership checks - it parses `runID`, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and immediately calls `App.ResumeJobV2` with the caller-supplied result: [2](#0-1) 

```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	rr := pipeline.ResumeRequest{}
	decoder := json.NewDecoder(c.Request.Body)
	err = errors.Wrap(decoder.Decode(&rr), "failed to unmarshal JSON body")
	...
	result, err := rr.ToResult()
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
	c.Status(http.StatusOK)
}
``` [2](#0-1) 

No check exists that the requester is the entity that started/owns the run, nor is there any secret comparison, rate limiting, or expiry enforced at this layer — the only thing gating the action is guessing/obtaining a UUID `runID`. This is structurally identical to the reported `withdrawFrom()` flaw: an action that is intended to be scoped to a specific principal (`account` in Collateral, the job/task owner here) is exposed without verifying `msg.sender`/caller identity against that principal — the endpoint even self-documents this via the `audit.UnauthedRunResumed` audit event name.

For contrast, every comparable pipeline-run mutation is authenticated: [3](#0-2) 

### Impact Explanation
Any unauthenticated client on the network path to the node's API can:
- Resume/complete arbitrary paused pipeline tasks (e.g., bridge/HTTP "async" tasks awaiting callback) with attacker-controlled result payloads, corrupting job outputs used to drive on-chain reports/transactions.
- Trigger unwanted state transitions in pipeline runs belonging to other jobs/users if the `runID` is discoverable (e.g., via logs, error messages, or brute-force over the UUID space), producing incorrect data being fed downstream (e.g., into OCR observations, VRF fulfillment, or other financially significant pipelines).
- Cause denial-of-service by repeatedly resuming/erroring runs that are still legitimately pending.

This satisfies "concrete... unauthorized job run or fund movement" or "cross-user response confusion" categories, since the endpoint allows an unprivileged actor to complete/mutate a pipeline run without ever proving they are the authorized party for that run, directly analogous to the Collateral report allowing an unprivileged caller to move another account's funds.

### Likelihood Explanation
Likelihood depends on whether `runID` values are treated purely as unguessable bearer secrets (in which case exposure via logs, telemetry, referer headers, or the Show/Index pipeline-run endpoints — which do return run and task info to any authenticated user — could leak them) versus fully random and never disclosed. Because the endpoint requires no authentication credentials at all, any leak of a `runID` (which is a standard UUID, not a high-entropy cryptographic token) is sufficient for a fully unprivileged party to exploit it. The complete absence of authentication middleware (unlike every sibling route) indicates this is at minimum a defense-in-depth gap, and the explicit `Unauthed` audit-event naming suggests the design intentionally accepted this risk without further scoping/ownership checks.

### Recommendation
- Require authentication for `/v2/resume/:runID` (e.g., via `auth.AuthenticateByToken`/`AuthenticateBySession`, or a dedicated per-run signed callback secret) rather than leaving it entirely unauthenticated.
- Additionally verify that the resuming principal is authorized for the specific `runID`/task before calling `App.ResumeJobV2`, mirroring the `onlyAccountOrMultiInvoker` style check recommended for `Collateral.withdrawFrom()`.
- If unauthenticated callback-style resumption is required by design (e.g., for external async task callbacks), use a high-entropy, single-use, time-limited signed token bound to the specific task rather than the raw pipeline run UUID.

### Proof of Concept
1. Identify or guess a valid `runID` (UUID) for a pipeline run paused on an async task (e.g., obtained from logs, an authenticated `GET /v2/jobs/:ID/runs/:runID` response leaked to a lower-privileged viewer, or brute force).
2. Without any authentication headers/cookies, send:
   ```
   PATCH /v2/resume/<runID>
   Content-Type: application/json

   {"value": "<attacker-controlled result>"}
   ```
3. The node processes the request in `PipelineRunsController.Resume` and calls `App.ResumeJobV2(ctx, taskID, result)` with no ownership verification, completing the pipeline task with the attacker-supplied value and returning `200 OK`.

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

**File:** core/web/router.go (L449-457)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
}
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
