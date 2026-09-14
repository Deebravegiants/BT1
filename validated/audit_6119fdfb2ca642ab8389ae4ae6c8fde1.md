### Title
Unauthenticated `/v2/resume/:runID` endpoint allows arbitrary injection/overwrite of pending async job-run results - ([File: core/web/router.go], [File: core/web/pipeline_runs_controller.go])

### Summary
The `startNewRound()`/re-request anti-pattern in the external report describes a design where an external, semi-trusted responder (the VRF coordinator/service provider) can be raced or re-triggered so that it effectively gets to choose which of multiple responses is accepted, letting it pick a favorable outcome. The closest reachable analog in this codebase is the chainlink node's async pipeline resume flow: any unauthenticated actor who can reach the node's HTTP API can `PATCH /v2/resume/:runID` and supply an arbitrary task result for a pending async task, which is used verbatim to resume the pipeline/job run.

### Finding Description
`v2Routes` registers the resume endpoint in the fully **unauthenticated** group, unlike virtually every other mutating v2 endpoint which requires either a session/API token or the external-initiator `AccessKey`/`Secret` headers: [1](#0-0) 

```
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)

authv2 := r.Group("/v2", auth.Authenticate(...))
```

The handler decodes the caller-supplied JSON body into a `pipeline.Result` (value/error) and forwards it, keyed only by the task UUID from the URL, straight into `ResumeJobV2`/`ResumeRun`, which updates the DB task-run row and immediately restarts the pipeline with that value: [2](#0-1) [3](#0-2) [4](#0-3) 

The only "authentication" is possession of the task-run UUID (normally handed only to the external bridge adapter as the `responseURL` for an async bridge task, as seen in the test): [5](#0-4) 

`StoreRun` (the ORM function backing this flow) explicitly documents that the row lock exists "to prevent races with /v2/resume," and detects "restart" conditions when new task data appears mid-run, but there is no idempotency/one-shot enforcement preventing a second, differently-valued resume call from being accepted for the same task before the run completes — the design assumes only the legitimate bridge adapter holds the UUID and calls it once. [6](#0-5) 

This mirrors the reported anti-pattern's root cause: a response-provider component (the async bridge adapter here, the VRF coordinator there) is trusted to deliver exactly one truthful result, but the protocol allows a party controlling (or guessing/leaking/racing for) the identifying handle to submit a value of their choosing through an unauthenticated channel, with no cryptographic binding proving the value's provenance, and no protection against a second, favorable submission racing the first.

### Impact Explanation
If the task-run UUID is ever exposed (logged, leaked via a compromised bridge, guessable, or observed on the wire since bridge callbacks are plain HTTP POSTs to `responseURL`), any unauthenticated network client can inject or overwrite the outcome of a pending job run — including runs that feed on-chain transactions (`ETHTx` tasks) — bypassing the intended external-adapter as source of truth. This is a request-impersonation / unauthorized-run-completion class of issue reachable from a fully unprivileged actor with no session, API token, or EI credentials, directly matching the "Accept only concrete... request impersonation... unauthorized job run or fund movement" validation criteria.

### Likelihood Explanation
Exploitation requires knowledge of a specific pending task's UUID. This is a real but non-trivial barrier (UUIDs are not brute-forceable in practice), so likelihood is lower than a fully open endpoint, but the complete absence of authentication on a mutating, run-completing endpoint is itself the anti-pattern: legitimate use should still require some node-level credential/HMAC binding the resume token to the specific initiating request, analogous to "increase the waiting period until the request has been fulfilled" in the original report — here the fix is to require possession-proof (e.g., signed/HMAC'd callback token) rather than a bare UUID, and reject a second resume once the task is no longer pending.

### Recommendation
- Bind the resume UUID to a per-request secret/HMAC (not just a bare UUID) so a leaked/guessed identifier alone cannot be used to inject a result.
- Enforce one-shot resume semantics: reject `PATCH /v2/resume/:runID` if the task is no longer `IsPending()`, closing the race window `StoreRun`'s comment alludes to.
- Consider requiring the async task's owning bridge to be resolvable/verified (e.g., via `OutgoingToken`/`OutgoingSecret` used for external initiators) so the resume call can be attributed to the expected adapter rather than accepted from any source.

### Proof of Concept
1. Create a job with an `async=true` bridge task; the bridge receives a `responseURL` of the form `http://<node>/v2/resume/<taskID>` (confirmed in `core/services/pipeline/runner_test.go` `Test_PipelineRunner_AsyncJob_InstantRestart`, lines 783-806).
2. Obtain/guess/leak `<taskID>` before the legitimate bridge responds (e.g., via bridge logs, network capture, or a compromised bridge dependency).
3. Send `PATCH /v2/resume/<taskID>` with an attacker-chosen `{"value": ..., "error": ...}` body to the node with no authentication headers at all — the unauthenticated route in `core/web/router.go` line 243 accepts it.
4. `PipelineRunsController.Resume` → `ChainlinkApplication.ResumeJobV2` → `runner.ResumeRun` → `orm.UpdateTaskRunResult` commits the attacker's value and resumes/finishes the pipeline (`core/services/pipeline/runner.go` lines 732-755), potentially driving a downstream on-chain transaction with attacker-controlled data before or instead of the genuine bridge response.

### Citations

**File:** core/web/router.go (L238-249)
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
	{
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

**File:** core/services/pipeline/runner_test.go (L783-806)
```go
func Test_PipelineRunner_AsyncJob_InstantRestart(t *testing.T) {
	db := pgtest.NewSqlxDB(t)

	btcUSDPairing := utils.MustUnmarshalToMap(`{"data":{"coin":"BTC","market":"USD"}}`)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var reqBody adapterRequest
		payload, err := io.ReadAll(r.Body)
		if !assert.NoError(t, err) {
			return
		}
		defer r.Body.Close()
		err = json.Unmarshal(payload, &reqBody)
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

**File:** core/services/pipeline/orm.go (L185-222)
```go
// StoreRun will persist a partially executed run before suspending, or finish a run.
// If `restart` is true, then new task run data is available and the run should be resumed immediately.
func (o *orm) StoreRun(ctx context.Context, run *Run) (restart bool, err error) {
	err = o.transact(ctx, func(tx *orm) error {
		finished := run.FinishedAt.Valid
		if !finished {
			// Lock the current run. This prevents races with /v2/resume
			sql := `SELECT id FROM pipeline_runs WHERE id = $1 FOR UPDATE;`
			if _, err = tx.ds.ExecContext(ctx, sql, run.ID); err != nil {
				return fmt.Errorf("failed to select pipeline run %d: %w", run.ID, err)
			}

			taskRuns := []TaskRun{}
			// Reload task runs, we want to check for any changes while the run was ongoing
			if err = tx.ds.SelectContext(ctx, &taskRuns, `SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1`, run.ID); err != nil {
				return fmt.Errorf("failed to select piepline task run %d: %w", run.ID, err)
			}

			// Construct a temporary run so we can use r.ByDotID
			tempRun := Run{PipelineTaskRuns: taskRuns}

			// Diff with current state, if updated, swap run.PipelineTaskRuns and early return with restart = true
			for i, tr := range run.PipelineTaskRuns {
				if !tr.IsPending() {
					continue
				}

				// Look for new data
				if taskRun := tempRun.ByDotID(tr.DotID); taskRun != nil && !taskRun.IsPending() {
					// Swap in the latest state
					run.PipelineTaskRuns[i] = *taskRun
					restart = true
				}
			}

			if restart {
				return nil
			}
```
