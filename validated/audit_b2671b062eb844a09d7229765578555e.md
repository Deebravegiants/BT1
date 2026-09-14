## Analog Found

### Title
Unauthenticated pipeline-run resume endpoint lets any external actor inject arbitrary task results and hijack job execution - (File: `core/web/router.go`)

### Summary
The external report shows an on-chain function (`burnRebalancer`) that performs a privileged, state-mutating action but has no access-control modifier, letting any caller invoke it. The same class of bug — a state-mutating operation reachable by a completely unauthenticated actor — exists in Chainlink's node HTTP API: the `PATCH /v2/resume/:runID` route is registered with **zero** authentication middleware, unlike every sibling route in the same router.

### Finding Description
In `v2Routes`, most `/v2/*` endpoints are grouped under `authv2`, which requires `auth.Authenticate` with `AuthenticateByToken`/`AuthenticateBySession` (and additional role gates such as `auth.RequiresEditRole`/`auth.RequiresAdminRole`/`auth.RequiresRunRole`). However, the resume endpoint is explicitly carved out into an `unauthedv2` group with no authentication method at all: [1](#0-0) 

The handler itself, `PipelineRunsController.Resume`, accepts a `runID` (task UUID) and an arbitrary JSON body that is decoded into a `pipeline.ResumeRequest`, converted to a `pipeline.Result`, and passed straight into `App.ResumeJobV2` — with no ownership, ACL, or role check whatsoever: [2](#0-1) 

This flows into `runner.ResumeRun`, which updates the task run result and, if the run was suspended waiting on this exact task, resumes and continues execution of the entire pipeline using the attacker-supplied value/error: [3](#0-2) 

The only thing standing between an unprivileged caller and forging a task's outcome is guessing/knowing the task UUID — there is no cryptographic signature, HMAC, or bearer-token check tying the caller to the bridge that legitimately owns that async callback (contrast with `AuthenticateExternalInitiator`, which does perform a `subtle.ConstantTimeCompare` on hashed secrets for other externally-triggered actions [4](#0-3) ). The code even flags the gap itself by logging this action under the audit event name `UnauthedRunResumed`: [5](#0-4) 

### Impact Explanation
If a task UUID becomes known or guessable (e.g., leaked in logs, exposed to a compromised/malicious downstream bridge server, observed via network traces, or through any other authenticated actor with lesser read access), any unauthenticated party can:
- Force-complete a suspended pipeline task with an attacker-controlled value or error, bypassing whatever external computation/bridge was actually supposed to supply that result.
- Cause downstream pipeline stages (which may include transaction submission, VRF fulfillment logic, or other consequential tasks) to execute using falsified data.
- Repeatedly hit the endpoint to disrupt/DoS in-flight runs by injecting spurious errors, functionally similar to the reported bug where an unprivileged caller could disrupt a privileged rebalancing operation by front-running/burning required state.

This matches the "unauthorized job run" category explicitly called out as an acceptable impact class.

### Likelihood Explanation
Likelihood depends on UUID exposure. It is not brute-forceable in practice (UUIDv4 space), but the architectural flaw remains: **there is no authentication layer at all** on this route — the design intentionally offloads all protection onto secrecy of the identifier, unlike other externally-initiated endpoints in this codebase that do implement constant-time secret comparisons (`AuthenticateExternalInitiator`). Any leak of the run/task ID (logging, monitoring dashboards, error messages, a compromised bridge adapter, or a lower-privileged read-only user who can view run details) is sufficient to fully exploit this with no further access control to defeat, mirroring the original finding's core defect: privileged/state-changing logic reachable by anyone who can construct the correct call.

### Recommendation
Add an authentication/authorization mechanism to the resume endpoint rather than relying purely on UUID secrecy, e.g.:
- Require the responding party to present a per-task secret/HMAC signature (generated when the async request/`responseURL` was created) that is verified before accepting the resume, in addition to the UUID.
- Alternatively, route resume callbacks through the existing external-initiator authentication mechanism (`AuthenticateExternalInitiator`) with a constant-time secret check, consistent with how other externally-triggered actions in bridges are protected.
- Rate-limit and audit-log rejected/invalid resume attempts to detect probing.

### Proof of Concept
1. Discover or leak a pending task run's UUID (e.g., via logs, monitoring, or a compromised bridge adapter that receives the `responseURL` containing `/v2/resume/<taskUUID>` per `finalizeAndMarshalBridgeRequestData`) [6](#0-5) .
2. Without any credentials, send:
   ```
   PATCH /v2/resume/<taskUUID>
   Content-Type: application/json

   {"value": "<attacker-controlled data>"}
   ```
3. The request hits `unauthedv2.PATCH("/resume/:runID", prc.Resume)` with no auth middleware, is decoded and forwarded to `App.ResumeJobV2` → `runner.ResumeRun`, which finalizes the task with the forged result and resumes pipeline execution using attacker-supplied data.

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

**File:** core/services/pipeline/runner.go (L732-755)
```go
func (r *runner) ResumeRun(ctx context.Context, taskID uuid.UUID, value any, err error) error {
	run, start, err := r.orm.UpdateTaskRunResult(ctx, taskID, Result{
		Value: value,
		Error: err,
	})
	if err != nil {
		return fmt.Errorf("failed to update task run result: %w", err)
	}

	// TODO: Should probably replace this with a listener to update events
	// which allows to pass in a transactionalised database to this function
	if start {
		// start the runner again
		go func() {
			ctx, cancel := r.chStop.NewCtx()
			defer cancel()
			if _, err := r.Run(ctx, &run, false, nil); err != nil {
				r.lggr.Errorw("Resume run failure", "err", err)
			}
			r.lggr.Debug("Resume run success")
		}()
	}
	return nil
}
```

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```

**File:** core/services/pipeline/task.bridge.go (L364-374)
```go
	if t.Async == "true" {
		responseURL := t.bridgeConfig.BridgeResponseURL()
		if responseURL != nil && *responseURL != *zeroURL {
			responseURL.Path = path.Join(responseURL.Path, "/v2/resume/", t.uuid.String())
		}
		var s string
		if responseURL != nil {
			s = responseURL.String()
		}
		merged["responseURL"] = s
	}
```
