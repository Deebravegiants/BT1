### Title
Unauthenticated resume of pipeline task runs allows arbitrary run manipulation - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `PATCH /v2/resume/:runID` endpoint is registered in the unauthenticated route group and its handler performs no authentication or authorization check before resuming a pipeline task run with attacker-supplied data, mirroring the "anybody can mint" class of bug where a state-mutating entry point is missing the authorization check present on its sibling endpoint.

### Finding Description
`NewRouter` registers `v2Routes`, which places `prc.Resume` on the completely unauthenticated router group: [1](#0-0) 

This contrasts directly with the sibling "run" mutation endpoint, `POST /v2/jobs/:ID/runs`, which is placed behind `auth.Authenticate(...)` and `auth.RequiresRunRole`: [2](#0-1) 

The `Resume` handler itself contains no user, session, external-initiator, or role check — it simply parses the `runID` from the path, decodes an attacker-controlled JSON body into a `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2` directly: [3](#0-2) 

This is analogous to the `DebtToken`/`MintableNonFungibleToken` bug: `create` (the "authorized" path, analogous to `POST /jobs/:ID/runs`) enforces authorization, while `mint`/`Resume` (an alternate path that mutates the same underlying state — token IDs / pipeline task runs) does not, letting any unauthenticated caller directly manipulate state that should only be reachable through the authorized flow.

The code even acknowledges this via the audit log event name `audit.UnauthedRunResumed`, indicating the lack of authentication is a known, accepted design decision rather than an oversight — the endpoint is intended to be reachable by adapters via `runID` as a bearer-token-like secret. However, this still means: if an attacker learns or guesses a pending task run's UUID (e.g. via logs, error messages, or brute force of the UUID v4 space), they can resume/complete/fail an in-flight pipeline run with arbitrary attacker-controlled result data, with zero authentication check at the HTTP layer.

### Impact Explanation
An unprivileged, unauthenticated actor who obtains or guesses a `runID` can:
- Force completion or failure of a pending bridge/task run with arbitrary result data, corrupting job execution logic (e.g. injecting a fake price, fake VRF proof stage, or arbitrary bridge adapter callback data).
- Repeatedly attempt to resume runs to interfere with node operation, potentially disrupting OCR/keeper/VRF job pipelines that depend on external adapter callbacks.

This matches the report's core theme: an unprivileged actor can invoke a state-mutating operation that should require the same authorization as its "authorized" counterpart, and use it to disrupt normal system operation (analogous to blocking debt-order fills by front-running the `mint` call).

### Likelihood Explanation
Reaching this path requires knowledge of a valid, currently-pending `runID` (a UUID). This is a real but non-trivial precondition — it is by design intended only for external adapters that receive the run ID as part of a callback URL. The security relies entirely on `runID` unguessability/secrecy rather than any authentication check, which is weaker than the token/role-based auth used elsewhere in the same controller (`Create`). If a `runID` leaks (e.g., via bridge logs, external adapter logs, referrer headers, or a compromised adapter), it becomes fully exploitable by an unrelated unprivileged party.

### Recommendation
- At minimum, ensure `runID` values are cryptographically unguessable and never logged or exposed to any party other than the specific adapter/bridge that should resume them.
- Consider adding a scoped credential requirement (e.g. an HMAC or the external initiator's outgoing token used only for that resume callback) rather than relying purely on the run UUID as an implicit bearer token.
- Ensure rate limiting is applied to this unauthenticated route to reduce guessing/brute-force risk.

### Proof of Concept
1. Obtain (e.g. from leaked adapter logs or the bridge's outgoing request) a pending pipeline run's `runID`.
2. Send `PATCH /v2/resume/<runID>` with an attacker-chosen JSON body matching `pipeline.ResumeRequest`, with no authentication headers/cookies at all.
3. The request is routed by `unauthedv2.PATCH("/resume/:runID", prc.Resume)` (core/web/router.go:243) directly into `prc.Resume` (core/web/pipeline_runs_controller.go:134-161), which decodes the body and calls `App.ResumeJobV2`, completing/failing the run with attacker-supplied data — with no check equivalent to the `RequiresRunRole`/authentication check enforced on `POST /jobs/:ID/runs`.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
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
