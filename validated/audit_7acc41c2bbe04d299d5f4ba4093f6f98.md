This is a genuine finding. `PATCH /v2/resume/:runID` is registered on `unauthedv2`, an **unauthenticated** router group — completely bypassing session/token authentication, unlike the OSV report's bug (which only lacked ownership checks within an authenticated context). [1](#0-0) 

### Title
Unauthenticated cross-user pipeline run resumption via `PATCH /v2/resume/:runID` - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `Resume` endpoint that finishes a pending task and resumes a pipeline run is mounted on `unauthedv2`, a router group with **no authentication middleware at all**, while every other pipeline-run and job-management endpoint requires session or token authentication (`authv2`/`userOrEI`).

### Finding Description
`v2Routes` wires `PATCH /v2/resume/:runID` directly to `prc.Resume` on the `unauthedv2` group, before any `auth.Authenticate` middleware is applied: [1](#0-0) 

`PipelineRunsController.Resume` parses the `runID` as a UUID (the pipeline task's `TaskRunID`), decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and calls `App.ResumeJobV2` with no user/session/token check and no verification that the caller is associated with the job/run in question: [2](#0-1) 

This is architecturally similar to the CVE-2025-63681 bug class (an endpoint that operates on a task/run identifier without verifying caller ownership) but is actually more severe here: it's reachable by a **completely unauthenticated** network client, not merely by a normal logged-in user acting on another user's task. Any client that can guess or observe a `runID` (UUID) can inject a `pipeline.ResumeRequest` result/error and force-complete or corrupt any pending async task (e.g., bridge/external adapter callbacks, webhook-style resumes) across the entire node, independent of who created the job or run.

The audit log entry itself documents this as intentionally unauthenticated (`audit.UnauthedRunResumed`), but this is meant for external-adapter callbacks that carry their own bridge-specific secret/token in the `ResumeRequest` body — however, `Resume` performs no validation that the caller possesses any such secret; it purely trusts a guessable UUID.

### Impact Explanation
An unauthenticated attacker who obtains or brute-forces a `runID` can complete, cancel, or inject a forged result/error into a running pipeline task for any job on the node, directly corrupting job run state and pipeline outputs (integrity impact), and can be used for denial-of-service against pending pipeline tasks awaiting external callbacks.

### Likelihood Explanation
`runID` is a UUID (`uuid.Parse(c.Param("runID"))`), so blind brute force is infeasible, but the ID can be leaked via other authenticated read endpoints (`GET /v2/jobs/:ID/runs/:runID`), logs, or third-party bridge integrations, after which exploitation requires no authentication at all.

### Recommendation
Bind the `Resume` endpoint to bridge-specific authentication (e.g., verify a per-bridge/task secret embedded in the resume request, or require the external adapter's incoming-token) rather than relying solely on the confidentiality of the UUID, and audit whether this endpoint needs to remain unauthenticated at the router level. At minimum, ensure `ResumeJobV2` validates that the resume request corresponds to a task expecting external callback and rejects results for taskless/non-pending IDs.

### Proof of Concept
1. Obtain a valid `runID` (task run UUID) for a pending pipeline run, e.g. via an authenticated `GET /v2/jobs/:ID/runs/:runID` call.
2. As an unauthenticated client, send:
```
PATCH /v2/resume/<runID>
Content-Type: application/json

{"error": "attacker forged failure"}
```
3. Observe that `prc.Resume` calls `App.ResumeJobV2` and returns `200 OK` with no authentication challenge, forcibly completing the pipeline task with attacker-controlled data. [3](#0-2)

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
