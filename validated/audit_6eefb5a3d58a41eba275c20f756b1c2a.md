This confirms it — I found the key finding. The `PATCH /v2/resume/:runID` route is registered on `unauthedv2` (unauthenticated) group at [1](#0-0) , which maps to `PipelineRunsController.Resume` [2](#0-1) . This is analogous to the report's core theme (a component being able to perform a privileged, value-affecting action — completing/injecting results into a pipeline run — without proper authorization), reachable directly by an unprivileged/unauthenticated client.

### Title
Unauthenticated pipeline run resumption allows arbitrary injection of task results - (File: core/web/pipeline_runs_controller.go)

### Summary
The `/v2/resume/:runID` HTTP endpoint, which resumes a suspended pipeline run (e.g., a task awaiting an external callback/webhook) with an attacker-controlled JSON body, is registered in the `unauthedv2` route group and requires no authentication whatsoever — no session, no API token, and no external-initiator credentials.

### Finding Description
`v2Routes` registers the resume endpoint before any authentication middleware is applied: [1](#0-0) 

This routes `PATCH /v2/resume/:runID` directly to `PipelineRunsController.Resume`, which parses the `runID` from the URL, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` without validating the caller's identity, role, or a shared secret tied to the run: [2](#0-1) 

Notably, the code even logs this as `audit.UnauthedRunResumed`, acknowledging the endpoint operates without authentication: [3](#0-2) [4](#0-3) 

This mirrors the report's root-cause pattern: a privileged mutation path (here, feeding arbitrary "result" data back into an in-flight pipeline run, potentially controlling values fed to bridge/HTTP tasks, VRF callbacks, or other pending task outputs) is reachable without any authorization check that ties the caller to legitimate ownership of that run/task.

### Impact Explanation
Any unauthenticated network client that can reach the node's web server can call this endpoint. If an attacker can guess or enumerate a `runID`/task UUID (used as `resume/:runID`), they can inject arbitrary task results into any pending pipeline run across the node — potentially manipulating oracle report data, resuming stuck jobs prematurely, or corrupting job outputs, without needing any credentials, contrary to the intended authenticated/role-gated design used for nearly every other job/run-related endpoint (e.g., `POST /v2/jobs/:ID/runs` requires `RequiresRunRole`).

### Likelihood Explanation
The endpoint is unconditionally mounted and reachable on any deployment exposing the node's HTTP API without additional network-layer restrictions. The primary mitigating factor is that the `runID`/task UUID must be known or guessed by the attacker; if these identifiers are unpredictable (UUIDv4) and not otherwise leaked, exploitation likelihood is lower but not eliminated (e.g., if IDs leak via logs, other API responses, or webhook callback URLs shared with external systems).

### Recommendation
Require the resume request to be authenticated by a secret specific to the pending task/run (e.g., a per-task callback token embedded in the resume URL and validated server-side), or move this endpoint behind the standard `auth.Authenticate` middleware with an appropriate role check, consistent with the rest of the run-related endpoints in `v2Routes`.

### Proof of Concept
1. Create any job containing a task that suspends pipeline execution awaiting external resumption (e.g., a bridge/webhook task), and note the resulting `runID` (task UUID) either from the pipeline run's task metadata or logs.
2. Without any authentication headers or session cookie, send:
```
PATCH /v2/resume/<runID>
Content-Type: application/json

{"error": null, "value": "<attacker-controlled result>"}
```
3. Observe that `PipelineRunsController.Resume` accepts the request (HTTP 200) and the pipeline run resumes with the attacker-supplied `value`, as it is on the `unauthedv2` group and performs no authorization check [5](#0-4) [6](#0-5) .

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

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
```
