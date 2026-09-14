### Title
Unauthenticated pipeline run resumption allows arbitrary task result injection via guessable/leaked run UUID - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `cancelOrder`-class bug (an action that mutates state without verifying the caller's identity/authorization) has an analog in `PipelineRunsController.Resume`, the `PATCH /v2/jobs/:ID/runs/:runID` handler. Unlike other job-run and job-proposal mutation endpoints in the codebase, this handler is not gated by any of the `web/auth` authentication methods (session, API token, or external-initiator token), and the audit event name itself, `audit.UnauthedRunResumed`, confirms this is a deliberately unauthenticated action.

### Finding Description
`PipelineRunsController.Resume` parses a `runID` (task UUID) from the URL and a JSON body, converts it to a `pipeline.Result`, and directly calls `prc.App.ResumeJobV2(ctx, taskID, result)` with no caller identity check: [1](#0-0) 

`ResumeJobV2` forwards straight into the pipeline runner: [2](#0-1) 

`ResumeRun` then updates the task run result in the DB and, if the run is ready, restarts pipeline execution with the attacker-supplied `value`/`err`: [3](#0-2) 

By contrast, other comparable state-changing endpoints in the web layer (job proposal cancel/revoke, external-initiator create/delete, run creation via `PipelineRunsController.Create`) either require a session/role check (`authenticateUserCanEdit`, `RequiresRunRole`) or, for external initiators, verify a shared secret via `bridges.AuthenticateExternalInitiator` (constant-time HMAC-style secret compare) before honoring the request: [4](#0-3) [5](#0-4) [6](#0-5) 

`Resume`, however, has no such gate — like `cancelOrder` in the reported bug, which stores a cancellation without validating the signer, this endpoint accepts and applies a mutation (task result / resume trigger) based solely on knowledge of a resource identifier (`runID`), with no cryptographic or session-based proof that the caller is entitled to resume that specific run. The `router.go` route wiring shows generic auth-required grouping for most `v2Routes`, but the Resume route's controller code path performs no per-request `auth.GetAuthenticatedUser`/`GetAuthenticatedExternalInitiator` check at all, unlike `Create` in the same controller which explicitly checks both: [7](#0-6) 

### Impact Explanation
If an unprivileged actor can obtain or guess a `runID` (e.g., via information leakage, response bodies, logs, or a predictable/short-lived async task UUID), they can inject arbitrary task output/error values into a suspended pipeline run and force it to resume — analogous to the "cancel with no signature check" issue, where a state-changing action is accepted without verifying the requester is authorized to perform it on that specific resource. This could corrupt pipeline results (e.g., a paused bridge/webhook task waiting on an external system callback), leading to incorrect on-chain reports or job outputs, or allow DoS by prematurely/falsely resuming runs.

### Likelihood Explanation
Exploitability depends on whether `runID` values are exposed to unprivileged callers or are practically guessable; this could not be fully confirmed from the indexed code — the task ID is a randomly generated UUID (`uuid.New()`), which mitigates brute-force guessing, but the endpoint's design (no authentication check for a request that mutates pipeline state and is explicitly logged as "Unauthed") indicates the intended threat model is that the UUID itself is the only barrier, i.e., a capability-URL design. Given the report's rule to focus on unprivileged-actor-reachable endpoints, this is a valid analog to flag, though full exploitability confirmation (e.g., whether UUIDs ever leak to less-trusted parties, such as external initiators/webhooks) would need further investigation of how `runID`s are distributed to consumers.

### Recommendation
Require the caller to prove ownership/authorization of the specific run before allowing `Resume` to mutate it — for example, bind resumption to the external initiator or bridge that owns the pending task (mirroring `AuthenticateExternalInitiator`), or require a per-run bearer token issued at task-creation time and validated via constant-time comparison, similar to how `bridges.AuthenticateExternalInitiator` validates external initiator secrets. At minimum, rate-limit and audit-log failed/successful resumes distinctly, and consider requiring session/API-token auth in addition to UUID knowledge for callers who are not the async task's designated resolver.

### Proof of Concept
Not independently verifiable from the indexed codebase alone (no runtime/network access in this mode). Conceptually: an actor who obtains a valid `runID` for a suspended pipeline task (e.g., from a bridge webhook payload, logs, or another exposed channel) can issue `PATCH /v2/jobs/{jobID}/runs/{runID}` with an arbitrary JSON body without any `X-API-KEY`, session cookie, or `X-Chainlink-EA-*` headers, since `PipelineRunsController.Resume` at [8](#0-7)  performs no authentication/authorization check before calling `ResumeJobV2`.

### Citations

**File:** core/web/pipeline_runs_controller.go (L86-129)
```go
// Create triggers a pipeline run for a job.
// Example:
// "POST <application>/jobs/:ID/runs"
func (prc *PipelineRunsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	respondWithPipelineRun := func(jobRunID int64) {
		pipelineRun, err := prc.App.PipelineORM().FindRun(ctx, jobRunID)
		if err != nil {
			jsonAPIError(c, http.StatusInternalServerError, err)
			return
		}
		res := presenters.NewPipelineRunResource(pipelineRun, prc.App.GetLogger())
		jsonAPIResponse(c, res, "pipelineRun")
	}

	idStr := c.Param("ID")

	// Webhook runs used external job UUIDs; that job type has been removed.
	if _, err := uuid.Parse(idStr); err == nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, fmt.Errorf("cannot run job of type %q: %w", job.Webhook, job.ErrJobTypeRemoved))
		return
	}

	_, isUser := auth.GetAuthenticatedUser(c)
	_, isEI := auth.GetAuthenticatedExternalInitiator(c)
	// only users are allowed to run jobs using int IDs - EIs not allowed
	if isUser && !isEI {
		// Is it an int32? Then process it regardless of type
		var jobID int32
		jobID64, err := strconv.ParseInt(idStr, 10, 32)
		if err == nil {
			jobID = int32(jobID64)
			jobRunID, err := prc.App.RunJobV2(ctx, jobID, nil)
			if err != nil {
				jsonAPIError(c, http.StatusInternalServerError, err)
				return
			}
			respondWithPipelineRun(jobRunID)
			return
		}
	}

	jsonAPIError(c, http.StatusUnprocessableEntity, errors.New("bad job ID"))
}
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

**File:** core/services/chainlink/application.go (L1237-1243)
```go
func (app *ChainlinkApplication) ResumeJobV2(
	ctx context.Context,
	taskID uuid.UUID,
	result pipeline.Result,
) error {
	return app.pipelineRunner.ResumeRun(ctx, taskID, result.Value, result.Error)
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

**File:** core/web/resolver/mutation.go (L826-846)
```go
// CancelJobProposalSpec cancels the job proposal spec.
func (r *Resolver) CancelJobProposalSpec(ctx context.Context, args struct {
	ID graphql.ID
}) (*CancelJobProposalSpecPayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}

	id, err := stringutils.ToInt64(string(args.ID))
	if err != nil {
		return nil, err
	}

	feedsSvc := r.App.GetFeedsService()
	if err = feedsSvc.CancelSpec(ctx, id); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return NewCancelJobProposalSpecPayload(nil, err), nil
		}

		return nil, err
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
