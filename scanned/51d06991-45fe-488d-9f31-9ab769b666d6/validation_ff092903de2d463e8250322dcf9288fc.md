## Title
Unauthenticated `PATCH /v2/resume/:runID` endpoint allows any unprivileged caller to resume/complete arbitrary pipeline task runs - (File: core/web/router.go)

### Summary
The reported Solidity issue is a state-mutating function that lacks any access-control modifier and is reachable by anyone. The direct chainlink analog is `core/web/router.go`'s `unauthedv2.PATCH("/resume/:runID", prc.Resume)` route, which is registered in the *unauthenticated* route group (`unauthedv2 := r.Group("/v2")`), bypassing all the session/token/role middleware (`auth.Authenticate`, `auth.RequiresRunRole`, etc.) that gate every other pipeline-run mutation endpoint.

### Finding Description
In `core/web/router.go`, `v2Routes` defines two groups: an unauthenticated group `unauthedv2` and authenticated groups wrapped with `auth.Authenticate(...)`. The resume-run endpoint is deliberately placed in the unauthenticated group: [1](#0-0) 

By contrast, the equivalent job-run-creation endpoint (`POST /v2/jobs/:ID/runs`) requires authentication and the `run` role: [2](#0-1) 

The handler for the unauthenticated route, `PipelineRunsController.Resume`, takes an arbitrary `runID` (task UUID) from the URL and an arbitrary JSON body (`pipeline.ResumeRequest`), then calls `prc.App.ResumeJobV2(ctx, taskID, result)` to finish/complete that pipeline task with attacker-controlled result data — with zero authentication or authorization check: [3](#0-2) 

The code even logs this via a dedicated audit event name `audit.UnauthedRunResumed`, showing the team is aware this path is intentionally unauthenticated (presumably meant only for internal/async callback use, e.g., bridge adapters resuming a suspended task by knowing the task's UUID) — but the UUID/`runID` is the only "secret," and it is not treated as a real authentication credential (not compared with constant-time comparison, not scoped/validated against any caller identity, no external-initiator-style access-key/secret check as used elsewhere in `core/web/auth/auth.go`'s `AuthenticateExternalInitiator`).

### Impact Explanation
Any unprivileged network client that can guess or observe a pending task/run UUID (e.g., leaked via logs, error messages, webhook responses, or a job spec that echoes task IDs to external systems) can:
- Inject arbitrary results into a suspended pipeline task (`ResumeRequest` → `ToResult()`), influencing job pipeline logic, potentially controlling values fed on-chain (e.g., completing a bridge/HTTP-adapter task with attacker-chosen output), or
- Trigger error paths in the pipeline that the operator did not intend.

This matches the "unauthorized job run" bug class from the rules: an unprivileged actor can complete/finish a job run without any credential check, directly analogous to the Solidity report's "critical state-mutating function has no permission control."

### Likelihood Explanation
Likelihood depends on whether task UUIDs (v4, high entropy) leak or are otherwise discoverable by an attacker. Since UUIDs are not brute-forceable, exploitation requires the attacker to already know or intercept a specific `runID`. This lowers likelihood versus a fully public setter, but the route's complete lack of any authentication layer (not even an API-key/secret pair as used for `AuthenticateExternalInitiator`) means the only protection is UUID secrecy, which is a weak, non-standard access-control mechanism, and is inconsistent with how every other mutating endpoint in this router is protected by session/token/role middleware.

### Recommendation
Require an explicit authentication mechanism for `/v2/resume/:runID`, e.g.:
- Move it into `authv2` (or `userOrEI`) and require at minimum `auth.RequiresRunRole`, or
- If it must remain usable by external non-session callers (bridge/adapter callbacks), issue and verify a per-task or per-bridge access token/secret analogous to `core/bridges/external_initiator.go`'s `AuthenticateExternalInitiator` mechanism (`crypto/subtle.ConstantTimeCompare` against a stored hashed secret) rather than relying solely on UUID secrecy.

### Proof of Concept
1. Identify or intercept a valid pending task UUID (`runID`) for a suspended pipeline task (e.g., an outstanding bridge/HTTP callback task).
2. Send, without any authentication headers/cookies:
```
PATCH /v2/resume/<runID>
Content-Type: application/json

{"error": null, "value": "<attacker-controlled result>"}
```
3. The request hits `unauthedv2.PATCH("/resume/:runID", prc.Resume)` [4](#0-3)  and `PipelineRunsController.Resume` [5](#0-4)  completes the task with the attacker-supplied value with no credential check.

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
