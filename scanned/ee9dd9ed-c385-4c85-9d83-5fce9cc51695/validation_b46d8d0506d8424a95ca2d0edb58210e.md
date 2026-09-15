### Title
Unauthenticated `PATCH /v2/resume/:runID` Allows Cross-Run Task Result Injection - ([File: core/web/router.go])

### Summary
The `PipelineRunsController.Resume` endpoint is exposed with no authentication middleware at all, and the resume operation is performed using only the caller-supplied task/run UUID with no verification that the requester owns, is expected to complete, or is otherwise authorized to complete that specific run/task. This is directly analogous to the WeKnora bug: an ID-only lookup/action with no ownership scoping, reachable by an unprivileged (here, fully unauthenticated) actor, enabling cross-actor manipulation of another party's resource by ID.

### Finding Description
`core/web/router.go` registers the resume route in an explicitly unauthenticated group: [1](#0-0) 

```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

Unlike every other v2 route, this group has no `auth.Authenticate(...)` middleware attached. The handler itself only validates that `runID` parses as a UUID, decodes the attacker-supplied body into a `pipeline.ResumeRequest`, and immediately calls into the application layer to resume that task with the caller's data: [2](#0-1) 

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

The audit event name `audit.UnauthedRunResumed` itself acknowledges that this path is intentionally unauthenticated — the design assumes the UUID `taskID` (a per-task pending-run identifier used by bridge/async task callbacks) is the sole secret protecting the operation. This mirrors the WeKnora root cause: the service call `s.repo.GetKnowledgeBaseByID(ctx, srcKB)` trusted a caller-controlled ID as sufficient authorization for a cross-tenant action, with no ownership/ownership-scoped check enforced at the data layer. Here, `ResumeJobV2`/`ResumeRun` (interface at `core/services/pipeline/runner.go:39`) similarly performs the resume purely by `taskID` with no binding back to the requester who initiated the corresponding async bridge call or any caller identity/session, because there is no caller identity at all on this route. [3](#0-2) 

If a `taskID` (pending task UUID) is exposed to, guessed by, or leaked to an unrelated party — e.g., via logs, error messages, timing, or a compromised bridge/external adapter response channel — that party can inject arbitrary attacker-controlled `value`/`error` results into someone else's in-flight pipeline run without any authentication whatsoever, completing or corrupting that run with forged data.

### Impact Explanation
This allows an unauthenticated network attacker to complete/finalize another party's pipeline run task with attacker-chosen data, effectively impersonating the legitimate external adapter/bridge callback for that task. Depending on the pipeline (e.g., a job whose downstream tasks act on the resumed value, feed into an on-chain transaction, or trigger fund movement), this can result in falsified data being fed into a node's job pipeline — a request/response impersonation and integrity violation of async task completion, matching the "request impersonation" / "cross-user response confusion" acceptance criteria.

### Likelihood Explanation
Exploitation requires knowledge of a valid, still-pending `taskID` UUID. This is not gated by any authentication, unlike almost every other endpoint in the router; the security model relies entirely on UUID secrecy. UUIDs can leak through logs, error responses, timing side-channels, or a compromised/observed bridge webhook. The endpoint is also easy to brute force is not the concern (UUIDv4 space is large), but any leak or interception fully bypasses access control since there is zero authentication check, making this materially weaker than the equivalent tenant-scoped check WeKnora was faulted for omitting.

### Recommendation
Bind the resumable task to an authorization context: require the caller to present a per-task bearer/secret (not just the run UUID) that was minted when the async task was created, and verify it before calling `ResumeJobV2`/`ResumeRun`. At minimum, add authentication middleware to the `/v2/resume/:runID` route group and validate that the resuming caller is the same bridge/external adapter (or holds a per-task secret) that the pending task was dispatched to, rather than trusting the `runID` alone as an implicit authorization token.

### Proof of Concept
1. Trigger any job with an async bridge task, causing the node to create a pending task with a `runID` UUID (e.g., via bridge webhook flow).
2. Obtain/guess that `runID` (e.g., via log exposure, error message, or side channel).
3. As an unauthenticated third party, send:
```bash
curl -X PATCH http://localhost:6688/v2/resume/<VICTIM_RUN_UUID> \
  -H "Content-Type: application/json" \
  -d '{"value": "attacker-controlled-result"}'
```
4. Observe `200 OK` with no authentication required, and the victim's pipeline run resumes with the attacker's injected data — confirmed by the `audit.UnauthedRunResumed` audit event referencing that `runID`.

### Citations

**File:** core/web/router.go (L238-244)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

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

**File:** core/services/pipeline/runner.go (L32-39)
```go
type Runner interface {
	services.Service

	// Run is a blocking call that will execute the run until no further progress can be made.
	// If `incomplete` is true, the run is only partially complete and is suspended, awaiting to be resumed when more data comes in.
	// Note that `saveSuccessfulTaskRuns` value is ignored if the run contains async tasks.
	Run(ctx context.Context, run *Run, saveSuccessfulTaskRuns bool, fn func(tx sqlutil.DataSource) error) (incomplete bool, err error)
	ResumeRun(ctx context.Context, taskID uuid.UUID, value any, err error) error
```
