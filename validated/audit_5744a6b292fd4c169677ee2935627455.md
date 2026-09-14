## Analysis

The report describes a Broken Object Level Authorization (BOLA) issue: an unauthenticated caller can pull a full object record by supplying only its ID, because the fetching code path skips normal ACL/authorization checks and relies solely on knowledge of an identifier.

The closest reachable analog in this codebase is the `PATCH /v2/resume/:runID` route, which is deliberately registered outside of any authentication middleware and mutates a pipeline run purely based on the caller-supplied ID.

### Title
Unauthenticated pipeline run resume endpoint accepts attacker-controlled results keyed only by task UUID - (File: core/web/pipeline_runs_controller.go)

### Summary
The `/v2/resume/:runID` route is mounted on the unauthenticated router group and lets any network caller finish a suspended pipeline task and inject a result, with no session, API token, or external-initiator credential required — the task UUID is the only "authorization" factor, mirroring the report's pattern of gating sensitive object access/mutation on an object identifier instead of a real authorization check.

### Finding Description
`v2Routes` registers this handler on `unauthedv2`, a route group with no `auth.Authenticate(...)` middleware, unlike every other `PipelineRunsController` route (`Index`, `Show`, `Create`) which sit behind `authv2`/`userOrEI` groups requiring session or API-token authentication: [1](#0-0) 

The handler itself performs no authentication or ownership check — it parses the `runID` path parameter as a UUID, decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest`, and calls `App.ResumeJobV2` directly: [2](#0-1) 

The only audit signal is the log entry itself named `UnauthedRunResumed`, which confirms the endpoint is knowingly unauthenticated by design (intended for external bridge/task callbacks), but there is no additional binding proving the caller is the legitimate external system that originated the suspended task — the UUID value is the sole gating factor, structurally the same pattern as the report's root cause (an object fetch/mutation path that trusts only the object identifier and bypasses the normal authorization chain).

### Impact Explanation
If a `runID` (task UUID) is disclosed or guessable through any side channel (logs, error messages, bridge responses, or a suspended job that echoes it), an unauthenticated remote attacker can complete or corrupt in-flight pipeline runs, injecting arbitrary task results. Because this is a mutation (not just a read), it exceeds the read-only impact of the reported CVE and can affect job-run correctness and any downstream fund-moving or state-changing task encoded in the pipeline (e.g., a suspended bridge/webhook task).

### Likelihood Explanation
Exploitation requires knowledge of a valid, still-pending `runID` (UUID v4-class entropy). Since UUIDs are not intentionally exposed to unauthenticated parties in normal operation, exploitation likelihood is lower than the original CVE (which exploited a default-off flag on every document). This weakens confidence that it is directly comparable to the reported "unauthenticated, default-config, mass-read" issue, and the design is explicitly labeled as intentionally unauthenticated (`UnauthedRunResumed`), suggesting it is treated as an accepted control rather than an oversight.

### Recommendation
- Bind the resume callback to a verifiable secret/HMAC signature tied to the specific bridge/task, not just the UUID.
- Rate-limit and audit-log failed resume attempts by source IP to detect UUID-guessing attempts.
- Confirm all `runID`/task UUIDs are never leaked in logs, error responses, or job-run presenters returned to lower-privileged (`view`) users, since disclosure would let any authenticated viewer pivot into this unauthenticated mutation path.

### Proof of Concept
1. Obtain (or guess) a pending pipeline task UUID `X` for a suspended run.
2. Send `PATCH /v2/resume/X` with body `{"value": "<attacker-controlled result>"}` and no auth headers/cookies.
3. Observe `HTTP 200` and the pipeline run completing with attacker-supplied data — no session cookie, API token, or external-initiator key was required.

**Caveat:** Confidence in this being a true equivalent to the reported CVE is moderate-to-low: unlike `getDocument`, this endpoint is explicitly documented/audited as unauthenticated by design (`UnauthedRunResumed`) and depends on UUID secrecy rather than a default-off flag, so it may represent an accepted design trade-off rather than an unintended BOLA bug. I was unable to fully trace how/where task UUIDs are generated and whether they are ever exposed to lower-privileged viewers, which would be necessary to confirm real-world exploitability.

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
