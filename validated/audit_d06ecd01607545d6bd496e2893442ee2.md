### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Any Caller to Repeatedly Manipulate/Disrupt Pending Async Job Runs - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `PipelineRunsController.Resume` handler, exposed as `PATCH /v2/jobs/:ID/runs/:runID`, resumes a suspended pipeline task by `taskID` (a UUID) with attacker-supplied JSON body content, and is explicitly documented as unauthenticated (the audit event is literally named `UnauthedRunResumed`). This mirrors the Switchboard `RandomnessCommit` bug: an instruction/endpoint callable by anyone, any number of times, which can disrupt a genuine in-flight async operation or be raced to inject an attacker-chosen result before the legitimate response arrives.

### Finding Description
`Resume` parses `runID` as a `uuid.UUID` task ID, decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, and calls `App.ResumeJobV2(ctx, taskID, result)` with no caller authentication or authorization check: [1](#0-0) 

`ResumeJobV2` forwards directly to `pipelineRunner.ResumeRun`: [2](#0-1) 

`ResumeRun` updates the task run's `Result` (value/error) unconditionally by `taskID`, and if the run was `Suspended`, flips it to `Running` and restarts the pipeline: [3](#0-2) [4](#0-3) 

The only "protection" is that `taskID` is a random UUID that must be known/guessed by the attacker (analogous to needing the oracle/seed values in the Switchboard case), but there is no mechanism that restricts calls once a genuine responder is expected, nor any check that the caller is the external adapter/bridge that originated the async request. This is the same class of bug as `RandomnessCommit`: a state-transition instruction reachable by any unprivileged caller, with no restriction against being invoked again before/instead of the legitimate response, and no binding of the caller's identity to the original request.

The audit log entry name itself acknowledges the unauthenticated nature of the action: [5](#0-4) [6](#0-5) 

By contrast, the newer Vault gateway/CRE authorization stack demonstrates the correct pattern that Switchboard's remediation calls for — binding a request to an authorized owner and rejecting repeat/duplicate submissions via a replay guard: [7](#0-6) [8](#0-7) 

The legacy `/v2/resume` (pipeline run resume) path predates and lacks this design.

### Impact Explanation
If an attacker can enumerate or otherwise learn a pending task run's UUID (e.g., through a leaked `responseURL`, log exposure, or a bridge/external-adapter integration that is not fully trusted), they can:
1. Submit a race response before the genuine external adapter responds, injecting an attacker-controlled value/error into the pipeline run (e.g., manipulating a price feed value or VRF-adjacent bridge task result) — directly analogous to manipulating settle-flip randomness in the Switchboard report.
2. Repeatedly call `Resume` for the same or unrelated `taskID`s to disrupt legitimate job runs, since there's no restriction preventing repeat completion attempts once a run is suspended and awaiting a specific responder.

This does not require any privileged role or session — it is reachable directly on the node's public HTTP API surface if unauthenticated routes are exposed.

### Likelihood Explanation
Likelihood depends on whether `runID`/`taskID` UUIDs (effectively bearer tokens for resumption) can be discovered by unprivileged parties. Since the audit event name explicitly flags this route as `UnauthedRunResumed`, this endpoint was clearly designed with the assumption that the UUID unguessability is the only defense — this is architecturally identical to relying on secrecy of an oracle-generated seed/slot rather than an explicit access-control check, which is exactly the weakness Otter Audits flagged for `RandomnessCommit`. I could not fully verify from the available index whether `/v2/jobs/:ID/runs/:runID` PATCH route in `core/web/router.go` is registered inside or outside authenticated route groups (the file was found but its exact route-group placement wasn't retrievable in this pass) — this should be confirmed by a Devin session with full file access, as it changes whether this is reachable by a fully unauthenticated actor or only by anyone possessing a valid session/EI token plus a guessed run UUID.

### Recommendation
Apply the same remediation pattern Switchboard used and that Chainlink's own Vault authorizer already implements elsewhere in this codebase:
1. Restrict `Resume` calls to a single acceptance per suspended task run (reject/no-op on subsequent resumes of an already-resumed or already-completed `taskID`), similar to `RequestReplayGuard.CheckAndRecord`.
2. Bind the resuming caller to the original async task's expected responder (e.g., validate a per-run secret/token included in the `responseURL`, or scope the resume call to the specific bridge/external adapter that received the outbound async request), rather than relying solely on UUID secrecy.
3. Confirm whether this route is placed inside an authenticated route group in `core/web/router.go`; if not, treat the task UUID as a security-critical secret and audit for any paths where it could leak (logs, error messages, stored `meta`).

### Proof of Concept
1. Create a webhook/bridge job with an `async=true` bridge task, causing the pipeline runner to suspend the run and return a `responseURL` containing `/v2/resume/<taskID>` to the external adapter (confirmed suspend/resume flow in `runner_test.go`). [9](#0-8) 
2. Before the legitimate external adapter (bridge) responds, an attacker who has obtained/guessed `taskID` sends:
   `PATCH /v2/jobs/:ID/runs/<taskID>` with a crafted JSON body (`pipeline.ResumeRequest`).
3. `PipelineRunsController.Resume` decodes the attacker's body and calls `ResumeJobV2` → `ResumeRun` → `UpdateTaskRunResult`, which unconditionally overwrites the task's `output`/`error` and restarts the pipeline with the attacker's value, with no check for prior completion or caller identity. [10](#0-9) [11](#0-10)

### Citations

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

**File:** core/services/pipeline/runner.go (L730-755)
```go
}

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

**File:** core/services/pipeline/orm.go (L271-308)
```go
func (o *orm) UpdateTaskRunResult(ctx context.Context, taskID uuid.UUID, result Result) (run Run, start bool, err error) {
	if result.OutputDB().Valid && result.ErrorDB().Valid {
		panic("run result must specify either output or error, not both")
	}
	err = o.transact(ctx, func(tx *orm) error {
		sql := `
		SELECT pipeline_runs.*, pipeline_specs.dot_dag_source "pipeline_spec.dot_dag_source", job_pipeline_specs.job_id "job_id"
		FROM pipeline_runs
		JOIN pipeline_task_runs ON (pipeline_task_runs.pipeline_run_id = pipeline_runs.id)
		JOIN pipeline_specs ON (pipeline_specs.id = pipeline_runs.pipeline_spec_id)
		JOIN job_pipeline_specs ON (job_pipeline_specs.pipeline_spec_id = pipeline_specs.id)
		WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended')
		FOR UPDATE`
		if err = tx.ds.GetContext(ctx, &run, sql, taskID); err != nil {
			return fmt.Errorf("failed to find pipeline run for task ID %s: %w", taskID.String(), err)
		}

		// Update the task with result
		sql = `UPDATE pipeline_task_runs SET output = $2, error = $3, finished_at = $4 WHERE id = $1`
		if _, err = tx.ds.ExecContext(ctx, sql, taskID, result.OutputDB(), result.ErrorDB(), time.Now()); err != nil {
			return fmt.Errorf("failed to update pipeline task run: %w", err)
		}

		if run.State == RunStatusSuspended {
			start = true
			run.State = RunStatusRunning

			sql = `UPDATE pipeline_runs SET state = $2 WHERE id = $1`
			if _, err = tx.ds.ExecContext(ctx, sql, run.ID, run.State); err != nil {
				return fmt.Errorf("failed to update pipeline run state: %w", err)
			}
		}

		return loadAssociations(ctx, tx.ds, []*Run{&run})
	})

	return run, start, err
}
```

**File:** core/logger/audit/audit_types.go (L1-1)
```go
package audit
```

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
}
```

**File:** core/services/pipeline/runner_test.go (L796-806)
```go
		if !assert.NoError(t, err) {
			return
		}
		assert.Contains(t, reqBody.ResponseURL, "http://localhost:6688/v2/resume/")
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Chainlink-Pending", "true")
		response := map[string]any{}
		if !assert.NoError(t, json.NewEncoder(w).Encode(response)) {
			return
		}
	})
```
