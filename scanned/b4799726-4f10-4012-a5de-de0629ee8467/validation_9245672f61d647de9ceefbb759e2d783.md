### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Unauthorized Manipulation of Any Async Task Result - ([File: core/web/router.go])

### Summary
The `/v2/resume/:runID` endpoint is registered on the unauthenticated router group and dispatches directly to `PipelineRunsController.Resume`, with the only "access control" being knowledge of a task-run UUID. Unlike the `BlueBerryBank.takeCollateral` bug (any caller could withdraw any position's collateral because the function never checked `msg.sender` against the position owner), this endpoint never checks that the caller is the external adapter/bridge that actually owns the corresponding pending task — it just trusts whoever presents the runID.

### Finding Description
In `core/web/router.go`, the resume route is deliberately placed outside the authenticated router group: [1](#0-0) 

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

The handler itself performs no ownership/ACL check at all — it only parses the UUID from the URL and forwards the attacker-supplied JSON body directly into the pipeline as the task's resolved value/error: [2](#0-1) 

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

The audit event is literally named `UnauthedRunResumed`, confirming this path bypasses the node's `Authenticator`/session/token auth layer entirely — the same class of bug as the report (a state-mutating operation reachable without verifying the caller is authorized for the specific resource it is mutating). The task UUID (`TaskRun.ID`) is the *only* factor gating this call; there is no secondary secret, HMAC, or bridge-credential check comparable to `AuthenticateExternalInitiator`'s access-key/secret pair used elsewhere in the same package: [3](#0-2) 

### Impact Explanation
Any actor who can obtain or guess a pending task-run UUID (e.g., via response bodies logged/cached, proxy logs, error messages, browser history, or a leaky bridge/EA integration) can inject an arbitrary result or error into that pipeline run without any authentication. Since resumed tasks feed into downstream pipeline stages that can trigger on-chain transactions (e.g., Keeper/VRF/OCR bridge-callback flows, FM), an attacker-controlled `value`/`error` can corrupt job outcomes, force premature/incorrect on-chain submissions, or cause denial of service for pending runs — a direct authorization-bypass analog to the reported "unauthorized withdrawal from any position" bug, since the mutating operation identifies the target resource purely by an externally-supplied identifier with no ownership check.

### Likelihood Explanation
Exploitability is gated by the requirement to know a specific run's task UUID; it is not a passively public value under normal operation. This lowers likelihood relative to the original report's fully unauthenticated function, but the design intentionally forgoes any node-level authentication (`unauthedv2` group), meaning any leak of the UUID (through logs, external adapter misconfiguration, network proxies, or race-prediction of UUID generation in specific deployments) grants full write access to that pipeline run with no further checks — a legitimate reduction in defense-in-depth compared to admin/edit/run role-gated endpoints elsewhere in the same router.

### Recommendation
Bind the resume capability to a verifiable secret rather than relying solely on the run UUID as a bearer token: e.g., require the external adapter/bridge outgoing token/secret established at task dispatch time to be presented and validated (mirroring `AuthenticateExternalInitiator`'s access-key/secret verification), or require the resume request to be signed/HMAC'd with a per-task secret generated when the task was created and never exposed to unrelated parties. At minimum, ensure UUIDs used as resume identifiers are treated as high-entropy secrets and never logged, echoed in error responses, or exposed to third parties, and add audit-log alerting/rate-limiting on this endpoint given its currently unauthenticated nature.

### Proof of Concept
1. Identify (or leak) a pending task's UUID, e.g. from an external adapter response, node logs, or reverse-engineering task creation timing.
2. Send an unauthenticated request:
```
PATCH /v2/resume/<taskID> HTTP/1.1
Content-Type: application/json

{"value": "<attacker-controlled-json>"}
```
3. `PipelineRunsController.Resume` (`core/web/pipeline_runs_controller.go:134-161`) accepts this without any session/token/ownership validation and calls `App.ResumeJobV2(ctx, taskID, result)`, injecting the attacker's value into the corresponding pipeline run.

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

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```
