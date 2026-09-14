Confirmed: the `/v2/resume/:runID` route is registered in the unauthenticated group at `unauthedv2.PATCH("/resume/:runID", prc.Resume)` in `core/web/router.go:243`, distinct from the authenticated `/v2/...` group requiring token/session auth. [1](#0-0) 

### Title
Unauthenticated Resume endpoint lets any caller force-complete another user's paused pipeline run with attacker-chosen data - (File: core/web/pipeline_runs_controller.go)

### Summary
`PipelineRunsController.Resume` is mounted on the deliberately unauthenticated route group and accepts a bare `runID` (task UUID) plus an attacker-controlled JSON body that is fed directly into `ResumeJobV2`, resuming/injecting a result into whatever pipeline task run matches that UUID, with no ownership or ACL check tying the caller to that run. [2](#0-1) [3](#0-2) 

### Finding Description
The route is registered without any authentication middleware, in contrast to every other pipeline-run route (`Index`, `Show`, `Create`) which sits behind `authv2` (token/session auth): [4](#0-3) 

The handler itself performs no authorization check on `runID`/task ownership — it just parses the UUID, decodes an arbitrary JSON `ResumeRequest` body, and calls into the application layer: [5](#0-4) 

The presence of the dedicated audit event `UnauthedRunResumed`, emitted right after the call, confirms this endpoint is knowingly unauthenticated by design (it is meant to serve as a webhook callback target for async task types such as bridge/external adapter responses, HTTP request results, etc.) but relies solely on the secrecy/unguessability of the task UUID as its only access control: [6](#0-5) [7](#0-6) 

This is analogous to the reported Cooler bug in structure: a state-mutating, financially/operationally consequential action (rolling a loan / resuming a pipeline run and injecting its "result") is reachable by a party who does not own or control the affected resource, with the only "protection" being the difficulty of guessing an identifier (the loan's implicit consent model vs. here the task UUID). If a `runID` (task UUID) is leaked via logs, browser history, a shared bridge configuration, or is otherwise guessable/brute-forceable, any unauthenticated party can:
- Complete a suspended pipeline task with attacker-supplied data (`ResumeRequest.Value`/`Error`), forcing the pipeline (and downstream on-chain transaction, e.g. a Flux Monitor/OCR/VRF fulfillment task) to proceed using data the attacker controls.
- Resume the same run's task with an `Error`, deliberately causing a legitimate job to fail/default at a time the attacker chooses.

### Impact Explanation
An attacker who obtains or guesses the task UUID for a pending async pipeline task run can inject an arbitrary value or force a failure into another user's/node-operator's in-flight job run. Depending on the pipeline (e.g., HTTP/bridge-fed price data feeding an ETHTx task), this can cause the node to submit an on-chain transaction with attacker-influenced data, or cause the job to fail/default at an attacker-chosen moment — mirroring the "force the borrower to overpay or default" impact from the source report, but here manifesting as forced job completion/failure with attacker-controlled payload.

### Likelihood Explanation
Likelihood depends entirely on UUID confidentiality: task run UUIDs are v4 UUIDs (128-bit), so blind brute force is infeasible, but the endpoint is deliberately unauthenticated to support legitimate external callback flows (e.g., bridge adapters), meaning any leak of a runID (via logs, network capture, misconfigured bridge, or a compromised/curious external adapter) is sufficient for exploitation — there is no secondary check (API key, HMAC, IP allowlist) binding the caller to the run owner.

### Recommendation
Bind the resume callback to a verifiable secret beyond the UUID itself — e.g., require the external-initiator/bridge outgoing token/secret (already used elsewhere, `core/bridges/external_initiator.go`) to be presented and validated for the specific job/run being resumed, or sign the resume URL with an HMAC tied to the run so a leaked UUID alone is insufficient to resume/inject data into someone else's run.

### Proof of Concept
1. Obtain (via log leakage, network sniffing on an unencrypted bridge callback, or a malicious/compromised external adapter) the `runID` (task UUID) of another user's pending async pipeline task, e.g. `abcdefab-0000-0000-0000-abcdef012345`.
2. Send `PATCH /v2/resume/abcdefab-0000-0000-0000-abcdef012345` with a body such as `{"value": "<attacker-controlled-json>"}` to the target node — no authentication headers required, since the route bypasses `authv2` entirely. [4](#0-3) 
3. The server decodes the request, calls `App.ResumeJobV2`, and resumes/completes the victim's paused task with attacker data, then logs the `UnauthedRunResumed` audit event confirming the resume succeeded without authentication. [8](#0-7)

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

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
```
