## Analog Found

### Title
Unauthenticated pipeline-run resume endpoint allows cross-tenant task result injection - ([File: core/web/router.go])

### Summary
The external PraisonAI report describes a Jobs API where core job-control routes (submit, get, cancel, delete, result) are registered with **no authentication dependency at all**, letting any unauthenticated caller submit jobs, read other jobs' results, and cancel/delete other jobs from a shared, ownerless store. The chainlink codebase has a structurally analogous, deliberately unauthenticated route: `PATCH /v2/resume/:runID`, which resumes a suspended pipeline run and injects an attacker-supplied JSON payload as the task result — reachable by design without any session or API token.

### Finding Description
In `core/web/router.go`, `v2Routes` explicitly creates an unauthenticated route group and registers the resume endpoint on it, before the authenticated group is even constructed: [1](#0-0) 

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

The handler itself decodes an attacker-controlled JSON body into a `ResumeRequest`, converts it into a task result, and calls `App.ResumeJobV2` with only the `runID` path parameter as the authorization boundary — no `Depends`/middleware-equivalent auth check, no per-run ownership/ownership token, and no scoping to the caller: [2](#0-1) 

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
```

The audit event name itself (`audit.UnauthedRunResumed`) confirms this endpoint is intentionally unauthenticated by design — the equivalent of the PraisonAI Jobs API's missing `Depends(verify_jobs_token)`. The only "authorization" primitive is the `taskID` UUID being unguessable; there is no additional token, HMAC, or ownership check comparable to `hmac.compare_digest` recommended in the analog report. This mirrors exactly the PraisonAI root cause: a job-lifecycle route (`cancel`/`result`/`submit`-equivalent) with zero authentication dependency, relying solely on a bare identifier as an implicit secret.

### Impact Explanation
Anyone who obtains or predicts a suspended run's `taskID` (e.g., via out-of-band leakage, logs, monitoring tools, referrer headers, or a race with a legitimate async task/bridge callback) can inject arbitrary "resume" data into that pipeline run without any credentials, altering the final task result of another job's execution — a direct integrity impact on a shared job resource, analogous to the PraisonAI cross-job confidentiality/integrity primitive (unauthenticated cancel/result-injection on someone else's job). Because it's a `PATCH` (state-changing) endpoint with an `InternalServerError` response leaking Go error text on failure, it can also be used to probe run state.

### Likelihood Explanation
This differs from the PraisonAI finding in one key respect: the `taskID` is a `uuid.UUID`, not a small sequential job id, so blind guessing is infeasible. Exploitation therefore requires the ID to leak through another channel (logs, external initiator/webhook flows, monitoring, or a bridge response). This somewhat limits likelihood versus the fully enumerable PraisonAI `/api/v1/runs` (sequential-ish, listable IDs) — but the endpoint is unauthenticated **by design** and reachable from any unprivileged client on the node's HTTP interface, matching the "no token, cookie, session, or per-job ownership value" pattern flagged in the source report once the UUID is known.

### Recommendation
- Require a bound, single-use, cryptographically random resume token issued at run-suspension time (bridge/async-task credential) rather than relying on UUID secrecy alone, and verify it with constant-time comparison before calling `ResumeJobV2`.
- Bind the resume operation to the specific task/bridge that suspended the run (ownership check) rather than accepting any caller who knows the `runID`.
- Rate-limit and audit failed resume attempts distinctly from successful ones to detect probing.
- Confirm all existing suspend/resume call sites (async task, bridge external initiator flows) issue and validate such a token before merging this route into the authenticated group or adding a scoped dependency, mirroring the `PRAISONAI_JOBS_API_TOKEN` router-level dependency recommended in the source advisory.

### Proof of Concept
Given only a leaked/observed `runID` (UUID) for a suspended pipeline run on a reachable chainlink node HTTP API:
```
curl -sS -X PATCH http://TARGET:6688/v2/resume/<runID> \
  -H 'Content-Type: application/json' \
  --data-binary '{"value":"attacker-controlled-result"}'
```
No `Authorization`, cookie, or session is required — the route is registered on `unauthedv2` per `core/web/router.go:243`, and `PipelineRunsController.Resume` performs no principal/ownership check before calling `App.ResumeJobV2`, per `core/web/pipeline_runs_controller.go:134-160`.

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

**File:** core/web/pipeline_runs_controller.go (L131-160)
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
```
