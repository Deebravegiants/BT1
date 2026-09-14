### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Unprivileged Actors to Complete/Modify Pending Job Runs - ([File: core/web/router.go])

### Summary
The Sherlock report describes `CollateralManager.withdraw()` lacking access control, letting any unprivileged caller trigger a state transition (collateral claim to lender) that the affected party did not consent to. The closest reachable analog in this codebase is the `PATCH /v2/resume/:runID` route, which is deliberately mounted on the **unauthenticated** router group and lets any caller resume/complete a pending pipeline (job) run by supplying arbitrary task results.

### Finding Description
In `core/web/router.go`, the route table explicitly separates authenticated and unauthenticated route groups: [1](#0-0) [1](#0-0) 

`unauthedv2.PATCH("/resume/:runID", prc.Resume)` is registered on `unauthedv2`, which has no `auth.Authenticate(...)` middleware attached, unlike the sibling `authv2` group that requires `AuthenticateByToken` or `AuthenticateBySession`.

`PipelineRunsController.Resume` in `core/web/pipeline_runs_controller.go` accepts a `runID` (a UUID identifying a pending pipeline task) and an arbitrary JSON body (`pipeline.ResumeRequest`) that is converted into a task `Result` and fed directly into `App.ResumeJobV2`: [2](#0-1) 

There is no check that the caller is the entity that originally suspended the run (e.g., an external adapter awaiting a callback) — any unauthenticated actor who can guess or observe a `runID` (task UUID) can supply an arbitrary result and force-resume that pipeline run, similarly to how the "anyone" caller in the reported bug could force `withdraw()` to transition loan/collateral state that only the lender should control.

### Impact Explanation
`ResumeJobV2` is the mechanism used by asynchronous/bridge tasks to inject a completion result into an in-flight job pipeline. Because this endpoint is unauthenticated by design (the log message name is even literally `audit.UnauthedRunResumed`), an attacker who learns or brute-forces a pending run's UUID can:
- Inject a forged/malicious result into a pipeline run before the legitimate external adapter responds, corrupting downstream computation results (e.g., price feeds, VRF-adjacent pipeline stages, or any job using bridge/external-adapter tasks).
- Complete a run prematurely with attacker-chosen values, potentially causing bad data to be written on-chain by whatever pipeline consumes the result, or causing double-completion/race conditions with the legitimate resumption.

This matches the report's "unprivileged actor forces an unwanted state transition" bug class, but the root cause here is by-design lack of authentication on a state-mutating endpoint rather than accidental omission, which slightly weakens the case that it's an actionable bug versus documented design (task UUIDs are treated as bearer capability tokens).

### Likelihood Explanation
Exploitability depends entirely on the secrecy/unguessability of the `runID` UUID, which is not exposed to unauthenticated users through any endpoint I could find in the available index; it is only obtainable by parties that already have access to task/run details (e.g., through authenticated `/v2/jobs/:ID/runs` endpoints, or logs). Absent a documented leak path for `runID` to unauthenticated third parties, exploitability is low/uncertain, and the design intent (`Unauthed` naming in the audit event) suggests this was a conscious tradeoff for callback-style external adapter completions rather than an unnoticed access-control gap.

### Recommendation
- If the intent of `/v2/resume/:runID` is to allow only the specific external adapter/bridge that suspended the given task to complete it, consider binding an unguessable, single-use secret to the resume operation (distinct from the run/task UUID which may be logged or otherwise exposed) or validating a shared secret/HMAC per task.
- Rate-limit and audit-log resume attempts with source IP to detect brute-force guessing of `runID`s.
- Confirm that `runID` values are never exposed through any authenticated-but-lower-privilege endpoint, webhook payload, or log line accessible to less-trusted parties.

### Proof of Concept
Not fully demonstrable from static analysis alone — exploitation requires knowledge of a valid pending `runID` (task UUID). Conceptually:
```
PATCH /v2/resume/<known-or-guessed-runID>
Content-Type: application/json

{"error": null, "value": "<attacker-controlled-result>"}
```
sent without any authentication header/cookie will be accepted by `unauthedv2.PATCH("/resume/:runID", prc.Resume)` and passed to `App.ResumeJobV2`, as shown in [3](#0-2)  and the unauthenticated route registration at [4](#0-3) .

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
