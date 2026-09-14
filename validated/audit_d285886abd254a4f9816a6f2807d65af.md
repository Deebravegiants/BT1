Found the critical analog: line 243 in `core/web/router.go` registers `unauthedv2.PATCH("/resume/:runID", prc.Resume)` with **zero authentication middleware**, unlike every other pipeline-related route which requires `auth.Authenticate(...)`.

### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Anyone to Inject Task Results and Manipulate Job Run State - ([File: core/web/router.go])

### Summary
The `/v2/resume/:runID` route is registered on the unauthenticated route group (`unauthedv2`), exposing `PipelineRunsController.Resume` to any unauthenticated network caller who can guess or observe a `runID` UUID, similar in class to the reported issue where a state-machine-triggering function lacked access control and let an unprivileged caller inject attacker-controlled parameters (there: slippage; here: task result/output value) into a privileged operation.

### Finding Description
`v2Routes` sets up `unauthedv2 := r.Group("/v2")` with no auth middleware, and registers `unauthedv2.PATCH("/resume/:runID", prc.Resume)` [1](#0-0) , in contrast to every other job/pipeline-run route which is placed under `authv2` (requiring `auth.AuthenticateByToken`/`AuthenticateBySession`) or `userOrEI` (requiring `AuthenticateExternalInitiator`/token/session) [2](#0-1) [3](#0-2) .

`PipelineRunsController.Resume` parses `runID` from the URL, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, converts it `ToResult()`, and forwards it directly to `App.ResumeJobV2(ctx, taskID, result)` — with no caller identity or ownership check tying the caller to that run [4](#0-3) . Anyone who can reach the node's HTTP interface and knows/enumerates a pending task UUID can inject an arbitrary result value that resumes a suspended pipeline task (e.g., a task awaiting an external adapter callback), analogous to how the reported `rebalanceXChain()` bug let an unauthenticated caller supply a malicious parameter (slippage) into a sensitive state-transition function.

### Impact Explanation
An attacker able to observe or brute-force a `runID` (task UUID) for a suspended pipeline run (e.g., from an async bridge/external adapter callback flow) can forge the resume payload and inject a fabricated result value into that job run, corrupting job outputs, potentially causing malicious on-chain reports/values to be computed downstream, or causing denial of service by resuming runs with invalid data. This mirrors the reported vulnerability's core issue: a caller-supplied value being trusted and forwarded into a sensitive protocol operation without access control.

### Likelihood Explanation
Exploitability depends on the attacker's ability to learn a valid `runID`; UUIDs are not trivially guessable, which reduces likelihood somewhat compared to the fully open `rebalanceXChain()` case. However, the endpoint is intentionally reachable pre-authentication by design (to support external adapter callbacks), and any leak of a `runID` (logs, network observation, a compromised/curious external adapter, or timing/enumeration) is sufficient for exploitation — there is no secondary authentication factor (unlike the external-initiator flow which uses `AccessKey`/`Secret` headers).

### Recommendation
Require that resume requests be authenticated/authorized against the specific run — e.g., bind resumption to a per-run secret/token issued when the task was created (similar to the external-initiator `AccessKey`/`Secret` pattern in `core/web/auth/auth.go`), or otherwise validate that the caller is the legitimate external adapter/bridge associated with that specific task before calling `App.ResumeJobV2`.

### Proof of Concept
1. Observe or guess a pending pipeline run's `runID` (task UUID) for a job with a suspended bridge/adapter task.
2. Send an unauthenticated request:
```
PATCH /v2/resume/<runID>
Content-Type: application/json

{ "value": "<attacker-controlled result>" }
```
3. The request hits `unauthedv2.PATCH("/resume/:runID", prc.Resume)` [5](#0-4)  with no auth check, decodes the body, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` directly [6](#0-5) , resuming the pipeline task with the attacker's injected value.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L449-456)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
```

**File:** core/web/pipeline_runs_controller.go (L131-157)
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
```
