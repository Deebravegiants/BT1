### Title
Fully unauthenticated `/v2/resume/:runID` endpoint allows any external caller to inject arbitrary results into pending pipeline (job) runs - ([File: core/web/router.go])

### Summary
The external report describes a privileged admin abusing a poorly-gated fund-movement operation (`claimProceeds`) to repeatedly extract value at no cost. The closest reachable analog in this codebase's unprivileged-actor surface is the `/v2/resume/:runID` HTTP endpoint, which is registered in the completely unauthenticated route group and lets any caller who supplies a valid task UUID complete/resume a suspended pipeline run with attacker-controlled `value`/`error` data — with no session, API token, or external-initiator authentication check at all.

### Finding Description
`v2Routes` mounts the resume handler on the unauthenticated group before any auth middleware is applied: [1](#0-0) 

```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	...
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

`prc.Resume` decodes an attacker-supplied JSON body directly into a `ResumeRequest`, converts it to a `pipeline.Result`, and calls `App.ResumeJobV2` with no role, session, or external-initiator credential checks whatsoever: [2](#0-1) 

The only "secret" gating this endpoint is the task UUID itself, which is meant to be known only by the external adapter that receives it embedded in the bridge task's async `responseURL`: [3](#0-2) 

Once `ResumeRun` is invoked, it calls into `orm.UpdateTaskRunResult` and then restarts pipeline execution with the caller-supplied value, continuing the DAG (which can include further tasks such as `ETHTx` submission or bridge submission tasks) with attacker-influenced data: [4](#0-3) 

The audit log even documents this as a known-risky, unauthenticated action via the dedicated `UnauthedRunResumed` event type: [5](#0-4) 

Unlike the external-initiator flow, which explicitly authenticates via `AccessKey`/`Secret` headers before granting the "Run" role: [6](#0-5) 

...the resume endpoint has no equivalent authentication step at all — it relies solely on the secrecy of the UUID path parameter, which can leak through logs, responses, monitoring, or a lower-privileged "view" role user who can read pending run/task details via other authenticated endpoints and then use the fully public resume endpoint to complete or tamper with a run that they were never authorized to run or edit.

### Impact Explanation
Any actor able to obtain or guess a pending task run's UUID (e.g., via log exposure, a lower-privileged "view"-role session, monitoring integrations, or interception of the adapter callback URL) can inject arbitrary result values or errors into a job run without any authentication, role check, or ownership validation. Depending on the pipeline's downstream tasks (e.g., an `ETHTx` task or a submit-to-bridge task), this can result in unauthorized job run completion with attacker-controlled data, effectively bypassing the node's role-based access control (RBAC) for run/edit operations — directly analogous to the original report's "attacker can trigger privileged, value-affecting operations at no cost, bypassing intended cost/authorization gates."

### Likelihood Explanation
Exploitation requires knowledge of a valid, still-pending task run UUID. This is not brute-forceable (UUIDv4), but the design explicitly transmits this UUID to third-party (external) HTTP adapters as a callback URL, and it may also be exposed through node logs, monitoring/observability tooling, or a lower-privileged authenticated user with read access to pipeline run details. Because the endpoint enforces zero authentication once the UUID is known, likelihood is moderate and depends entirely on operational UUID-leak vectors rather than any additional secret comparison.

### Recommendation
- Require authentication for `/v2/resume/:runID` consistent with other privileged mutating endpoints, or bind resumption to a per-run bearer secret that is rotated/invalidated after first use.
- Add ownership/ACL validation in `PipelineRunsController.Resume` (or `ResumeJobV2`) verifying the caller is authorized for the specific job/run rather than relying purely on UUID secrecy.
- Rate-limit and audit-log every unauthenticated resume attempt (success and failure) with source IP for anomaly detection, expanding on the existing `UnauthedRunResumed` audit event.
- Consider one-time-use tokens for the resume callback so a leaked UUID cannot be replayed to overwrite an already-completed task run result.

### Proof of Concept
Not independently verified beyond static code analysis in the index; the endpoint's lack of any `auth.Authenticate*` wrapper is confirmed directly in `core/web/router.go`. Conceptually:
1. Create a webhook/bridge job with an `Async=true` bridge task; the node embeds `.../v2/resume/<taskUUID>` into the outbound adapter request.
2. Obtain that UUID (e.g., via logs, network capture on the adapter side, or exposure through a lower-privileged read endpoint).
3. Send `PATCH /v2/resume/<taskUUID>` with a crafted JSON body directly to the node — no credentials required — and the pipeline resumes with attacker-supplied `value`/`error`.

Full end-to-end confirmation (e.g., whether a "view"-role authenticated user can retrieve pending task UUIDs through another endpoint) was not completed within the available search iterations; a Devin session with full repository/file access would be needed to trace `PipelineRunsController.Show`/`Index` role requirements and `presenters.PipelineRunResource` field exposure to determine the exact leak path for the UUID.

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

**File:** core/logger/audit/audit_types.go (L92-93)
```go

	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
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
