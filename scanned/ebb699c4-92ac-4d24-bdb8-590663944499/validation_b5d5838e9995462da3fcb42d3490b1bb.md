### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Arbitrary Job Run Manipulation - ([File: core/web/router.go])

### Summary
The `PATCH /v2/resume/:runID` route is registered in the `unauthedv2` route group with no authentication or authorization middleware applied, allowing any unauthenticated client to resume/complete arbitrary pipeline task runs by supplying only a run/task UUID.

### Finding Description
In `v2Routes`, the route table is split into an unauthenticated group (`unauthedv2`) and an authenticated group (`authv2`) that requires session or token auth via `auth.Authenticate`. The resume endpoint is deliberately placed in the unauthenticated group: [1](#0-0) 

This routes to `PipelineRunsController.Resume`, which parses the `runID` path parameter as a UUID, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(...)` to complete the corresponding pipeline task — with no check that the caller is authorized to act on that job/task: [2](#0-1) 

The only "access control" the code relies on is the fact that `taskID` is a UUID and thus presumably hard to guess, and the code even logs the action under an audit event named `UnauthedRunResumed`, indicating awareness that this endpoint bypasses normal auth. Unlike the external-initiator (`AuthenticateExternalInitiator`) or session/token (`AuthenticateBySession`/`AuthenticateByToken`) paths defined in `core/web/auth/auth.go`, which validate a caller's identity and role before allowing job/run mutation, this route performs zero authentication and zero binding of the caller to the job owner, bridge, or external initiator that originally created the pending task: [3](#0-2) 

This is a direct structural analog to the reported `CoreOracle.setRoutes` issue: a state-mutating operation (resuming/completing a job run, which can inject arbitrary result data into a pipeline, e.g. bridge/HTTP task callbacks) is exposed without any access-control check, relying only on obscurity of an identifier rather than an explicit authorization mechanism.

### Impact Explanation
An unauthenticated attacker who obtains or guesses/brute-forces a pending task's UUID can inject arbitrary result payloads into a running pipeline (e.g., completing bridge/HTTP callback tasks with attacker-controlled data), potentially corrupting oracle report data, causing incorrect job outcomes, or triggering unintended downstream fund-moving transactions if the resumed pipeline feeds into a transmission/reporting flow. This matches the "unauthorized job run" impact category.

### Likelihood Explanation
Exploitation likelihood depends on the entropy and lifecycle handling of the UUID `runID`/task identifier and whether it is otherwise exposed (e.g., leaked via logs, error messages, or third-party callback URLs sent to external bridges). Since UUIDs are the sole guard and this endpoint is intentionally unauthenticated (per the `UnauthedRunResumed` audit label), any leakage of the identifier — which is expected to be shared with external bridge/adapter services as part of normal operation — is sufficient for exploitation, making this a realistic risk rather than a purely theoretical one.

### Recommendation
Add an explicit authorization check to the resume path: at minimum, bind the resumable task to the external initiator or bridge context that created it (similar to how `AuthenticateExternalInitiator` scopes external callers to the `run` role in `core/web/auth/auth.go`), and validate that the caller presenting the resume request is the same entity the pending task was issued to (e.g., via a signed/keyed callback token in addition to the UUID), rather than relying solely on the unauthenticated `unauthedv2` route group.

### Proof of Concept
1. Identify or obtain a valid pending task UUID (e.g., via a bridge/adapter callback URL, logs, or brute force of the UUID keyspace).
2. Send `PATCH /v2/resume/<taskID>` with an attacker-crafted JSON body matching `pipeline.ResumeRequest` — no authentication headers or session cookies required, since the route sits in the `unauthedv2` group.
3. `PipelineRunsController.Resume` decodes the body and calls `App.ResumeJobV2`, completing the task with attacker-supplied data, as shown in `core/web/pipeline_runs_controller.go` lines 134-160.

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

**File:** core/web/auth/auth.go (L153-173)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
}
```
