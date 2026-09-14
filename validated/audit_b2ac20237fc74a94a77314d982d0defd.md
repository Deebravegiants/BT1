### Title
Unauthenticated pipeline run resumption endpoint allows arbitrary result injection into async tasks - (File: core/web/pipeline_runs_controller.go)

### Summary
The `PATCH /v2/resume/:runID` endpoint, which resumes a suspended async pipeline task (e.g. an async bridge/external-adapter task) with attacker-supplied result data, is deliberately mounted with **no authentication middleware** in the router, mirroring the report's root cause: a fund/state-changing entrypoint (`0xf6ebebbb` in the MEV Bot) that "lacks authentication" and lets any caller invoke it.

### Finding Description
`v2Routes` mounts `PipelineRunsController.Resume` on an unauthenticated group: [1](#0-0) 

Unlike every other mutating route in the same file — which is wrapped in `auth.Authenticate(...)` plus a role check (`RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`) — this route is registered on `unauthedv2` with zero auth methods: [2](#0-1) 

`Resume` parses a client-supplied `runID` (a UUID) into `taskID`, decodes an attacker-controlled JSON body into `pipeline.ResumeRequest`, converts it to a `pipeline.Result`, and directly calls `App.ResumeJobV2` with that value: [3](#0-2) 

`ResumeJobV2` forwards straight to the pipeline runner's `ResumeRun`, which persists the supplied `Value`/`Error` as the task's result and restarts pipeline execution with it: [4](#0-3) 

The code explicitly acknowledges the request is unauthenticated by logging an `UnauthedRunResumed` audit event rather than gating the request: [5](#0-4) 

This endpoint exists to let external bridge/adapter callbacks resume `async=true` bridge tasks by posting to a `responseURL` embedded in the outbound bridge request (`/v2/resume/<taskUUID>`): [6](#0-5) 

The only "secret" protecting this endpoint is the unguessability of the `taskID` UUID — there is no bearer token, HMAC signature, or shared secret validated on this path, unlike the external-initiator flow which enforces an access-key/secret pair with constant-time comparison: [7](#0-6) [8](#0-7) 

### Impact Explanation
Any unprivileged, unauthenticated actor who obtains or guesses a pending task's UUID can inject an arbitrary result/error value into a suspended pipeline task and force the pipeline to resume execution with attacker-controlled data. Because pipeline results feed downstream tasks (e.g., `jsonparse`, `multiply`, `median`, `ethtx`), this is a request-impersonation / unauthorized-job-run-continuation primitive: it lets an outsider forge the response of what should be an authenticated external-adapter/bridge callback, potentially corrupting price feed data or continuing OCR/keeper/VRF-style pipelines with fabricated values, which can influence on-chain transactions built from the pipeline. This closely parallels the MEV Bot class of bug — an unauthenticated function is used to force state transitions (there: arbitrage swaps; here: task-result injection driving pipeline continuation) — although actual fund-loss impact here depends on the downstream job's use of resumed data (e.g. whether it feeds a subsequent on-chain transaction task).

### Likelihood Explanation
Exploitability hinges entirely on discovering a valid pending `taskID` (UUID v4). Chainlink nodes commonly run bridges/external adapters, and `taskID`s are exposed in outbound bridge requests as part of `responseURL`, in job-run/task-run API responses (`GET /v2/jobs/:ID/runs/:runID`), and in logs — all of which are reachable to a user with only `view`-level authenticated access, or potentially leaked to network intermediaries handling the external-adapter callback traffic. Given the endpoint requires no credentials at all, likelihood is elevated for any actor who can observe or predict a pending run's task UUID (e.g., a malicious/compromised external adapter, a party monitoring the bridge, or someone with minimal API access to enumerate task IDs).

### Recommendation
Require the caller to authenticate this callback path — e.g., validate a per-task shared secret/HMAC embedded in the `responseURL` (analogous to the external-initiator `AccessKey`/`Secret` model), or require `AuthenticateExternalInitiator`/token auth plus `RequiresRunRole` like the sibling `POST /jobs/:ID/runs` route. At minimum, bind the resume callback to the specific external adapter/bridge that owns the task, rather than accepting any caller who supplies a task UUID.

### Proof of Concept
1. Create/observe an async bridge job whose task emits a `responseURL` of the form `http://<node>:6688/v2/resume/<taskUUID>` (as constructed in `finalizeAndMarshalBridgeRequestData`).
2. As soon as the task UUID is known (e.g., leaked via the external adapter, via `GET /v2/jobs/:ID/runs/:runID` with only view credentials, or via other observation of pending run task IDs), issue directly, with no credentials:
```
PATCH /v2/resume/<taskUUID>
Content-Type: application/json

{"error": null, "data": "<attacker-controlled value>"}
```
3. `ResumeJobV2` → `runner.ResumeRun` persists the attacker's value as the task result and restarts the pipeline, continuing downstream tasks using this forged data — without ever validating that the caller is the legitimate bridge/adapter that owns this task. [1](#0-0) [3](#0-2) [4](#0-3)

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

**File:** core/web/router.go (L450-457)
```go
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
}
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

**File:** core/web/auth/auth.go (L119-149)
```go
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
