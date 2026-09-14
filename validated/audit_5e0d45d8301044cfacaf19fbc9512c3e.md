Based on my investigation, I found a strong analog to this bug class in the chainlink node's HTTP gateway.

### Title
Unauthenticated `PATCH /v2/jobs/:ID/runs/:runID` Resume endpoint accepts arbitrary task results without validating the caller is the originating bridge/adapter - ([File: core/web/pipeline_runs_controller.go])

### Summary
The Lens bug is a "check bypass via alternate path": the block-status check enforced on the normal follow path is skipped entirely on the migration path (`tryMigrate`), letting an unprivileged actor produce a state (following) that should have been blocked. The chainlink analog is `PipelineRunsController.Resume`, which lets *any* unauthenticated caller resume a suspended async pipeline task and inject its own result value, with no verification that the caller is the external adapter/bridge that the pending task was actually waiting on.

### Finding Description
When a `bridge` task is run with `async=true`, the pipeline suspends and gives the external adapter a callback URL of the form `.../v2/resume/<taskID>` built from a randomly generated `taskID` (a UUID) [1](#0-0) . The corresponding `Resume` handler decodes an arbitrary JSON body into a `pipeline.ResumeRequest`, converts it to a `pipeline.Result`, and calls `App.ResumeJobV2` directly — there is no authentication check (no session, API-token, or external-initiator check) gating this handler, and no verification that the request actually originated from the adapter that was invoked for that specific task: [2](#0-1) 

The audit log call is literally named `audit.UnauthedRunResumed`, confirming this endpoint is explicitly unauthenticated by design: [3](#0-2) 

Internally, `ResumeJobV2` forwards straight into the pipeline runner without any further authorization: [4](#0-3) [5](#0-4) 

This mirrors the Lens pattern precisely: the "primary" trigger path for a bridge task (the outbound `BridgeTask` request/response) is implicitly trusted, but there exists an *alternate* path (the resume callback) that produces the same effect (completing/advancing the pipeline run) while omitting any authentication/ownership check that ties the caller to the specific pending task.

### Impact Explanation
Because the `taskID` is the only "secret" gating this endpoint, and it is a client-visible identifier that is also persisted/returned in job run resources (e.g. `pipeline_task_runs`), any actor who can view or predict/leak a pending task's UUID can:
- Inject a forged/manipulated result into a running OCR/pipeline job before the true external adapter response arrives, corrupting oracle observation data at the pipeline level.
- Cause spurious job run completions or errors for jobs they do not control, effectively bypassing whatever access controls exist on the job/bridge itself.

This is analogous to the "blocked follower can keep follow" impact category: an unprivileged actor achieves a state transition (an authenticated-looking, "legitimate" resume) through a code path that doesn't carry the checks the primary path relies on for trust.

### Likelihood Explanation
Exploitation requires knowledge of a valid, still-pending `taskID` (UUID). This is not brute-forceable in practice given UUID entropy, but the endpoint being completely unauthenticated (by explicit design, per the `UnauthedRunResumed` audit event) means the security boundary rests entirely on UUID secrecy rather than defense-in-depth (e.g., a shared bridge secret, HMAC, or binding to the external adapter's expected response). Any leakage of the task ID (logs, network capture, response bodies, monitoring dashboards) is sufficient for exploitation, and there is no rate limiting or secondary check visible in this handler.

### Recommendation
Bind the resume callback to the specific bridge/adapter invocation cryptographically (e.g., HMAC-sign the callback URL with a per-bridge or per-run secret, similar to `ExternalInitiator.OutgoingSecret`/`OutgoingToken`), and verify that signature in `Resume` before calling `ResumeJobV2`. Alternatively, require the resuming request to present the bridge's configured outgoing token/secret so an unrelated caller who merely discovers the UUID cannot inject results.

### Proof of Concept
1. Configure a webhook/bridge-backed job with an `async=true` bridge task pointing at an external adapter that responds with `X-Chainlink-Pending: true`, as shown in the test setup [6](#0-5) .
2. Observe/obtain the generated `taskID` for the pending task (e.g., via job run detail API, logs, or network capture of the outbound bridge request body which includes `responseURL`).
3. As an unauthenticated third party, send `PATCH /v2/jobs/<jobID>/runs/<taskID>` with an attacker-controlled JSON body matching `pipeline.ResumeRequest`.
4. Observe that `PipelineRunsController.Resume` accepts the request without any authentication and forwards the attacker-supplied value into `ResumeJobV2` → `pipelineRunner.ResumeRun`, advancing/completing the run with forged data before (or instead of) the legitimate adapter's real response.

Note: I could not fully verify from the indexed code whether any additional middleware wraps this specific route in `router.go` (the file was truncated before reaching the `/runs` route registrations), so it's possible — though not confirmed from what's indexed — that some outer group-level auth middleware could apply. Given the endpoint is explicitly named `UnauthedRunResumed` in the audit log and its handler code performs no `auth.GetAuthenticatedUser`/token check itself, I am confident this route is intentionally public; a Devin session with full file access could confirm the exact route registration in `core/web/router.go`.

### Citations

**File:** core/services/pipeline/task.bridge_test.go (L615-669)
```go
func TestBridgeTask_AsyncJobPendingState(t *testing.T) {
	t.Parallel()

	db := pgtest.NewSqlxDB(t)
	cfg := configtest.NewTestGeneralConfig(t)

	id := uuid.New()

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
		assert.Equal(t, fmt.Sprintf("%s/v2/resume/%v", cfg.WebServer().BridgeResponseURL(), id.String()), reqBody.ResponseURL)
		w.Header().Set("Content-Type", "application/json")

		// w.Header().Set("X-Chainlink-Pending", "true")
		response := map[string]any{"pending": true}
		if !assert.NoError(t, json.NewEncoder(w).Encode(response)) {
			return
		}
	})

	server := httptest.NewServer(handler)
	defer server.Close()
	feedURL, err := url.ParseRequestURI(server.URL)
	require.NoError(t, err)

	orm := bridges.NewORM(db)
	_, bridge := cltest.MustCreateBridge(t, db, cltest.BridgeOpts{URL: feedURL.String()})

	task := pipeline.BridgeTask{
		Name:        bridge.Name.String(),
		RequestData: ethUSDPairing,
		Async:       "true",
	}
	c := clhttptest.NewTestLocalOnlyHTTPClient()
	trORM := pipeline.NewORM(db, logger.TestLogger(t), cfg.JobPipeline().MaxSuccessfulRuns())
	specID, err := trORM.CreateSpec(t.Context(), pipeline.Pipeline{}, *sqlutil.NewInterval(5 * time.Minute))
	require.NoError(t, err)
	task.HelperSetDependencies(cfg.JobPipeline(), cfg.WebServer(), orm, specID, id, c)

	result, runInfo := task.Run(t.Context(), logger.TestLogger(t), pipeline.NewVarsFrom(nil), nil)
	assert.True(t, runInfo.IsPending)
	assert.False(t, runInfo.IsRetryable)

	require.NoError(t, result.Error)
	require.Nil(t, result.Value)
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
