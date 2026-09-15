Confirmed: `unauthedv2.PATCH("/resume/:runID", prc.Resume)` is registered with **no authentication middleware at all** — it sits in the `unauthedv2` group, unlike almost every other pipeline endpoint which requires `RequiresRunRole`/`RequiresEditRole`. This is the strongest analog to the report's "anyone can act on another party's resource by supplying an identifier, causing unauthorized state change / cross-user impact." [1](#0-0) [2](#0-1) 

### Title
Unauthenticated Cross-User Pipeline Run Resumption via `/v2/resume/:runID` - (File: core/web/router.go)

### Summary
The `PipelineRunsController.Resume` endpoint, which resumes/completes a suspended pipeline task (e.g., a task blocked on `RunID`/webhook resume, such as HTTP-fetch callbacks, Mercury/VRF/CCIP off-chain callbacks, or bridge-adapter resumes), is mounted on the `unauthedv2` router group with no authentication, session, token, or ownership check whatsoever, unlike every sibling job/run endpoint which is gated by `auth.RequiresRunRole`/`auth.RequiresEditRole`.

### Finding Description
`v2Routes` registers:
```go
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)
``` [3](#0-2) 

`Resume` parses only the `runID` path parameter (a UUID identifying a suspended pipeline task, not tied to a session/user) and directly calls `App.ResumeJobV2` with attacker-supplied JSON body content used as the task result:
```go
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
	...
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
``` [4](#0-3) 

There is no verification that the caller is the entity (external initiator/bridge/adapter) that originally created or is entitled to complete that specific suspended task. The audit event name itself, `UnauthedRunResumed`, acknowledges this endpoint bypasses standard user authentication — the only "protection" is that `runID` is a UUID that must be known/guessed, which is analogous to the Merkle-proof "exposed proof" scenario in the reported bug, where knowledge of an otherwise-public/leakable identifier lets an unrelated party act on someone else's in-flight state. Any pipeline run task whose UUID is exposed (via logs, error messages, the `/v2/jobs/:ID/runs` history endpoints available to any user with `run` role, webhook payload echoes, or third-party bridge servers) can be resumed/injected with arbitrary result data by an unrelated unauthenticated caller — completing, corrupting, or replaying another user's/job's pipeline run.

### Impact Explanation
An unprivileged network client can supply attacker-controlled JSON as the task result for any known/leaked pending run, causing the pipeline to resume with falsified data. Depending on the job's task graph, this can corrupt downstream computations, prematurely complete runs, or (for jobs whose terminal task moves funds, submits on-chain transactions, or feeds price data) cause an unauthorized state change driven entirely by attacker-supplied data — a direct analog to the reported "anyone can act on another user's claim/state" bug class (request impersonation / cross-user response confusion), differing only in that the resource here is a pipeline run rather than an airdrop claim.

### Likelihood Explanation
Likelihood depends on `runID` (a v4 UUID) becoming known to an attacker. This is plausible in practice: run/task IDs are returned in pipeline run resources exposed by other endpoints (`GET /v2/jobs/:ID/runs`, `GET /v2/pipeline/runs`) to any authenticated `run`-role user or external initiator, may be echoed in bridge/adapter callback payloads sent to third-party HTTP servers, or logged. Because the endpoint requires zero authentication, exploitation requires nothing beyond obtaining that identifier.

### Recommendation
Require authentication for `/v2/resume/:runID` consistent with other pipeline endpoints (e.g., `auth.RequiresRunRole`), and additionally verify that the resuming principal is authorized for the specific run/job (e.g., match against the external initiator that owns the corresponding bridge/adapter task, or scope by job ownership) rather than relying solely on UUID secrecy.

### Proof of Concept
1. Create any job containing a task that suspends pending external resume (e.g., a bridge/adapter callback task) and start a run; observe the resulting task's `runID` via `GET /v2/jobs/:ID/runs` (accessible to any `run`-role session/EI token) or via the third-party callback URL chainlink calls out to.
2. As a completely unauthenticated client (no session cookie, no API token, no EI credentials), send:
   ```
   PATCH /v2/resume/<runID>
   Content-Type: application/json

   {"value":"<attacker-controlled-data>"}
   ```
3. Observe the pipeline run resumes with the attacker-supplied value, bypassing the job's intended external initiator/bridge as the sole legitimate resumer.

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
