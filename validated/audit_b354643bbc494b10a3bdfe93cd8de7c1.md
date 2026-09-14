### Title
Unauthenticated `PATCH /v2/resume/:runID` Endpoint Allows Cross-Job Pipeline Run State Manipulation - (File: core/web/router.go)

### Summary
The Chainlink node registers `PATCH /v2/resume/:runID` in the `unauthedv2` gin route group, which is created without any authentication middleware — bypassing session cookies and API-token verification entirely, in the same class of bug as the Flowise `openai-assistants-file/download` issue where an endpoint's placement outside the authenticated-route set allowed unauthenticated retrieval of resources keyed only by client-supplied identifiers.

### Finding Description
`v2Routes` explicitly creates an unauthenticated group and mounts the resume handler on it: [1](#0-0) 

Unlike every other `/v2/...` capability (jobs, keys, transfers, etc.), which are mounted under `authv2` behind `auth.Authenticate(...)` with `AuthenticateByToken`/`AuthenticateBySession`, this route has zero authentication middleware in front of it.

The handler, `PipelineRunsController.Resume`, parses only a client-supplied UUID (`runID`) from the URL and a JSON body, then calls into the application to mutate pipeline task state: [2](#0-1) 

`ResumeJobV2` forwards directly to `pipelineRunner.ResumeRun`, which finalizes/unblocks a specific pipeline task run and can inject an attacker-chosen `result.Value`/`result.Error` into the job's execution state: [3](#0-2) 

The sole "authorization" control is that `runID` must be a valid UUID matching a pending async task (used legitimately for bridge-adapter async callbacks, as shown in the test asserting the response URL is `http://localhost:6688/v2/resume/`): [4](#0-3) 

The design intent (an unguessable UUID as a bearer capability for external bridge callbacks) is acknowledged in the code itself via the `audit.UnauthedRunResumed` audit event, but this only logs the action after the fact — it performs no authorization check, no validation that the caller is the originating bridge adapter, and no rate limiting/brute-force protection beyond global request-size limits. Any unauthenticated network client that can reach the node's API can call this endpoint.

### Impact Explanation
An unauthenticated attacker who obtains or guesses a pending task's `runID` can: (1) supply an arbitrary result value/error to resolve any pending async bridge task for any job on the node, corrupting the outcome of oracle data submissions/reports, or (2) repeatedly probe the endpoint for job runs across all jobs/users on the node, since the route performs no per-run ownership check tied to any credential — matching the report's "cross-user response confusion" / unauthorized state mutation class. Since `runID` values can leak via logs, third-party bridge adapter systems, browser history, or network intermediaries (the bridge callback URL is transmitted over HTTP to external adapters), the identifier is not a strong secret comparable to a session token, unlike the fully authenticated routes.

### Likelihood Explanation
Moderate. Exploitation requires knowledge of a valid, still-pending `runID` (a v4 UUID, so it is not brute-forceable directly), but the identifier is handed to third-party external bridge adapters over plain HTTP callback URLs and stored/logged in multiple systems outside the node's authentication boundary, giving it materially weaker protection than the node's session/API-key credentials — while the endpoint itself performs literally zero authentication, unlike every sibling `/v2/*` route.

### Recommendation
Restrict `/v2/resume/:runID` to require verification bound to the specific task/run (e.g., an HMAC or per-task secret embedded in the callback URL rather than the raw pipeline task UUID alone), or move it behind a scoped, single-use signed token so that possession of the run UUID alone is insufficient to mutate state. At minimum, add rate limiting specific to this route and ensure `runID`s are single-use/invalidate immediately after consumption (verify this already happens in `ResumeRun`/`pipelineRunner`, which was not confirmed here).

### Proof of Concept
```
# Attacker obtains/observes a pending task's runID (e.g. via bridge adapter logs/network capture of a
# response_url like http://<node>:6688/v2/resume/<uuid>), then, with no session cookie or API key:

curl -X PATCH http://<chainlink-node>:6688/v2/resume/<runID> \
  -H "Content-Type: application/json" \
  -d '{"data": {"result": "999999999"}, "error": null}'

# The request succeeds (HTTP 200) with no authentication, resolving the pending pipeline task with an
# attacker-controlled value, as shown by the route being mounted in the `unauthedv2` group:
``` [5](#0-4)

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

**File:** core/services/chainlink/application.go (L1237-1243)
```go
func (app *ChainlinkApplication) ResumeJobV2(
	ctx context.Context,
	taskID uuid.UUID,
	result pipeline.Result,
) error {
	return app.pipelineRunner.ResumeRun(ctx, taskID, result.Value, result.Error)
}
```

**File:** core/services/pipeline/runner_test.go (L796-799)
```go
		if !assert.NoError(t, err) {
			return
		}
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
```
