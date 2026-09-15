This confirms the strongest analog: the `/v2/resume/:runID` endpoint is registered on the **unauthenticated** router group, so `PipelineRunsController.Resume` requires no session, token, or role — this is a direct architectural analog to `applyToRound()` lacking access control, where an unprivileged caller can act on state (a pipeline run) they don't own, given only a resource ID.

### Title
Unauthenticated pipeline run resumption via `/v2/resume/:runID` allows arbitrary users to complete/inject task results for job runs they don't own - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
`v2Routes` registers `PATCH /v2/resume/:runID` on `unauthedv2` — a route group with no `auth.Authenticate` middleware at all — while every other pipeline/job endpoint is behind `authv2` requiring session/token auth plus role checks (`auth.RequiresRunRole`, `auth.RequiresEditRole`, etc.). [1](#0-0)  `Resume` accepts only a `runID` path parameter and a JSON body containing a `pipeline.ResumeRequest`, with zero checks that the caller is authorized to resume that specific run, and then calls `App.ResumeJobV2` to feed the result into the pipeline. [2](#0-1) 

### Finding Description
This is architecturally the same bug class as `applyToRound()`: a state-mutating entrypoint takes a caller-supplied resource identifier (`projectId` in the Solidity report, `runID` here) and performs an action tied to that identifier without verifying the caller is authorized for that specific resource. In Chainlink's case, the route sits entirely outside any authentication middleware — `unauthedv2 := r.Group("/v2")` followed directly by `unauthedv2.PATCH("/resume/:runID", prc.Resume)`, with no session, token, or external-initiator auth applied before the handler runs. [3](#0-2)  Inside `Resume`, the handler parses `runID` as a UUID (the pipeline task ID), decodes an attacker-controlled JSON body into `pipeline.ResumeRequest`, converts it to a `pipeline.Result`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` — completing/injecting a value into whatever async task that UUID corresponds to. [4](#0-3)  The audit log entry is even explicitly named `audit.UnauthedRunResumed`, indicating this was a deliberate design choice (likely intended only for bridge/external-adapter callback resumption, where the "secret" is meant to be the unguessable UUID) — but it means any party who obtains or guesses a `runID` can resume that pipeline run regardless of who owns it. [5](#0-4) 

### Impact Explanation
An unprivileged, unauthenticated actor who learns or brute-forces a pending run's UUID can inject arbitrary task-completion data into that pipeline run, potentially corrupting the run's data flow, causing incorrect oracle/report outputs, or completing runs prematurely with attacker-chosen results — directly analogous to the audit report's concern about false information entering downstream on/off-chain decision-making, but here with a more severe outcome since it can affect actual oracle data pipelines rather than just triggering an event.

### Likelihood Explanation
Exploitation requires knowledge of a valid, pending `runID` (UUID), which is not guessable at scale, so likelihood is bounded by how these UUIDs are exposed/leaked (e.g., logs, responses, bridge callbacks). This mirrors design intent for external-adapter async resumption but the complete absence of any authentication (not even a shared adapter secret check within the handler itself) is the structural gap.

### Recommendation
Require verification that the resumption request originates from an authorized source: bind the run's task to a per-request adapter/bridge secret or nonce validated inside `Resume` (rather than relying purely on `runID` unguessability), or scope this endpoint to only accept resumptions matching an external-initiator/bridge auth context, consistent with how `AuthenticateExternalInitiator` is used elsewhere. [6](#0-5) 

### Proof of Concept
1. Trigger any job/pipeline run that produces a pending async task with a bridge/HTTP callback, exposing (or leaking via logging/monitoring) its `runID` UUID.
2. As an unauthenticated attacker, send `PATCH /v2/resume/<leaked-runID>` with a crafted JSON body matching `pipeline.ResumeRequest`. [7](#0-6) 
3. The server decodes the body and calls `ResumeJobV2` with attacker-supplied result data, with no check that the caller owns or is authorized for that run. [8](#0-7)

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
