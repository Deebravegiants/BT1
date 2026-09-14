Confirmed: `PATCH /v2/resume/:runID` is explicitly registered in the unauthenticated route group in `core/web/router.go`, with no session/token/EI authentication middleware applied. [1](#0-0) 

### Title
Unauthenticated pipeline run resumption allows any external caller to resume/complete another user's paused job run - ([File: core/web/router.go], [File: core/web/pipeline_runs_controller.go])

### Summary
The `Resume` endpoint used to finish a paused pipeline task (e.g., a webhook/bridge task suspended awaiting external callback) is mounted on the unauthenticated route group and has no ownership/ACL check tying the caller to the run being resumed, analogous to the Cooler `roll()` issue where any third party can act on a resource without the owning user's/lender's consent.

### Finding Description
The route is registered as `unauthedv2.PATCH("/resume/:runID", prc.Resume)`, bypassing all of the `auth.Authenticate(...)` middleware (`AuthenticateByToken`, `AuthenticateBySession`, `AuthenticateExternalInitiator`) that protect every other job/run mutation route in the same file. [1](#0-0) 

The handler itself performs no additional authorization check beyond parsing the `runID` (a UUID) from the URL and the JSON body, then directly calling `App.ResumeJobV2`: [2](#0-1) 

There is no verification that the requester is the job's creator, the external initiator tied to that run, or any authenticated identity at all — the audit log entry is even explicitly named `audit.UnauthedRunResumed`, acknowledging the lack of authentication by design for legitimate async callback use cases (e.g., bridge adapters completing a task). However, this means **any unprivileged network client** who can guess or observe a `runID` can supply an arbitrary `pipeline.ResumeRequest` result/error payload to force-complete or fail a pending pipeline run belonging to any job/user on the node, without any relationship to that job's owner, external initiator credentials, or bridge that originally suspended it.

### Impact Explanation
An attacker who obtains or guesses a pending run's UUID can inject arbitrary result data (or force an error) into someone else's in-flight job run, similar to how the Cooler `roll()` bug let an unrelated party force state changes (loan extension) affecting another party without consent. Depending on what tasks consume the resumed value downstream (e.g., price feeds, bridge responses feeding on-chain transactions), this could allow poisoning of pipeline results or denial of service for async job completions across the whole node, not just the caller's own resources.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain a valid `runID` (a random UUID), which is not trivial to brute-force, but `runID`s may leak through logs, webhook URLs echoed to third parties, or bridge integrations that expose the callback URL to less-trusted external adapters. Given the endpoint is intentionally unauthenticated to support external bridge callbacks, the actual likelihood is elevated in setups where the resume URL is shared with any external system that isn't fully trusted, since there is no secondary secret/token binding the resume request to the specific pending task beyond the UUID itself.

### Recommendation
Bind the resume capability to a per-run secret (e.g., HMAC token issued when the task was suspended) rather than relying solely on the run UUID as an implicit bearer credential, and validate that secret in `PipelineRunsController.Resume` before calling `ResumeJobV2`. Alternatively, require external-initiator authentication scoped to the specific job/bridge that created the pending task, so only the initiator that owns that specific run can resume it — mirroring the recommendation from the source report to check the caller against the resource's rightful owner before allowing a state-mutating action.

### Proof of Concept
1. Node A creates a job with a task that suspends pending an external callback, producing pipeline run UUID `X` (as done in `TestRunner_WebhookJobRemoved`/general async-task flows using `cltest.CreateJobRunViaUserByID` etc.). [3](#0-2) 
2. Any unauthenticated third party sends `PATCH /v2/resume/X` with a crafted `pipeline.ResumeRequest` body directly, without any credentials, exactly as allowed by the router configuration: [4](#0-3) 
3. `PipelineRunsController.Resume` accepts the request, decodes the body, and calls `App.ResumeJobV2(ctx, taskID, result)` with no ownership check, completing/failing the run on behalf of the legitimate job owner. [5](#0-4)

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

**File:** core/services/job/runner_integration_test.go (L844-858)
```go
	job, _ := cltest.MustInsertWebhookSpec(t, app.GetDB(), jobUUID)

	runBody := cltest.MustJSONMarshal(t, eiRequest)
	headers := map[string]string{
		static.ExternalInitiatorAccessKeyHeader: eia.AccessKey,
		static.ExternalInitiatorSecretHeader:    eia.Secret,
	}
	url := app.Server.URL + "/v2/jobs/" + jobUUID.String() + "/runs"
	resp, cleanup := cltest.UnauthenticatedPost(t, url, bytes.NewBufferString(runBody), headers) //nolint:bodyclose // closed via cleanup
	defer cleanup()
	cltest.AssertServerResponse(t, resp, http.StatusUnprocessableEntity)
	cltest.AssertCountStays(t, app.GetDB(), "pipeline_runs", 0)

	cltest.DeleteJobViaWeb(t, app, job.ID)
}
```
