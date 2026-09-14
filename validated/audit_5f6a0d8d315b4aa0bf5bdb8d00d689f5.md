This is confirmed by design, not a bypassable vulnerability by itself — `PATCH /v2/resume/:runID` is intentionally registered in the `unauthedv2` group without any authentication middleware, unlike almost every other mutation endpoint in `core/web/router.go`, which requires `auth.Authenticate` and role checks (`RequiresEditRole`, `RequiresRunRole`, `RequiresAdminRole`). [1](#0-0) 

### Title
Unauthenticated `PipelineRunsController.Resume` allows any caller to complete/resume arbitrary suspended pipeline task runs by GUID - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
`PATCH /v2/resume/:runID` is registered on the unauthenticated route group (`unauthedv2`) with no auth middleware at all, while it invokes `prc.Resume`, which calls `App.ResumeJobV2` to inject an arbitrary result/error payload into a suspended pipeline task run identified only by a UUID (`runID`).

### Finding Description
In `core/web/router.go`, the route table wires:
```go
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)
``` [2](#0-1) 

This contrasts with virtually every other job/pipeline mutation endpoint in the same file, all wrapped by `auth.Authenticate(...)` plus a role check, e.g. `authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))`, `userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))`. [3](#0-2) [4](#0-3) 

The handler itself performs no additional caller authorization — it only parses `runID` (a UUID) from the path, decodes a JSON body into `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)`:
```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
	c.Status(http.StatusOK)
}
``` [5](#0-4) 

Note the audit event name itself is literally `UnauthedRunResumed` — the code explicitly acknowledges this endpoint is intentionally unauthenticated (likely by design, for external "resume/callback" async task use cases such as bridge/HTTP-request callbacks that must complete an in-flight run without holding node session credentials). This is analogous to the report's root cause: a state-changing operation reachable without any privileged caller check, similar to `executeBatchDeposit()` lacking `onlyKeeper`.

### Impact Explanation
Because `runID` is the only credential-equivalent value and it's a UUID generated per suspended task (not secret by construction, and often observable/leaked through logs, webhooks, or job configuration), any unauthenticated network client that can guess or obtain a pending task's UUID can force-resume/complete that pipeline run with attacker-controlled data or errors, potentially finalizing a pipeline/job run prematurely, injecting bogus values into task results, or repeatedly completing/duplicating async webhook-style callbacks. This resembles the report's "unpause bypassed by anyone" pattern — a supposedly gated lifecycle transition triggerable by any unprivileged caller.

### Likelihood Explanation
This appears to be a long-standing, intentional design choice (the explicit `Unauthed` audit event name and the pattern of "resume" callback URLs used by async bridge adapters that can't hold node credentials) rather than an accidental omission. Exploitability depends entirely on whether `runID` values are treated as secret bearer tokens by operators/integrations. I could not verify from this code alone whether `runID` values are unpredictable enough or are exposed elsewhere (e.g., returned in job run presenters to unauthenticated external initiators, or leaked in logs) to make brute-force/guessing practical.

### Recommendation
If unauthenticated resume truly requires no secret-token style protection beyond the run UUID, ensure `runID` values are cryptographically unguessable, never logged in this line context, and consider requiring per-run one-time secrets or bridge-issued signed tokens (similar to `ExternalInitiator`'s access-key/secret pair) rather than relying solely on UUID obscurity. Since this pattern is intentional per the codebase's own naming (`UnauthedRunResumed`), a background engineer should confirm with the security team whether this is an accepted design tradeoff before treating it as a defect.

### Proof of Concept
Not independently verifiable from static review alone — I could not confirm in the index whether `runID` GUIDs are exposed to unauthenticated parties elsewhere in the codebase (e.g., returned via bridge task callback URLs is expected/by-design) or whether they leak via any other channel that would make this practically exploitable beyond the documented, apparently intentional, unauthenticated design.

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

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
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
