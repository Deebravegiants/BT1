### Title
Unauthenticated `/v2/resume/:runID` Endpoint Allows Hijacking of Pending Async Pipeline Runs - (File: core/web/router.go / core/web/pipeline_runs_controller.go)

### Summary
Chainlink exposes a `PATCH /v2/resume/:runID` route that is deliberately mounted with **no authentication middleware**, in the same `unauthedv2` route group with no user/session/API-key/EI check. [1](#0-0)  The handler accepts a bare `runID` (which is actually a task UUID) and a JSON body, and uses it to resume a suspended pipeline task (`ResumeJobV2` → `ResumeRun` → `UpdateTaskRunResult`), feeding attacker-supplied `value`/`error` data back into the paused pipeline run. [2](#0-1) [3](#0-2) 

### Finding Description
This is architecturally analogous to the n8n `/chat` hijack: an unauthenticated network endpoint that resumes/interacts with a specific *waiting execution* purely on the basis of possessing an opaque identifier, with no ownership/ACL check tying the caller to the run.

- The route is registered explicitly outside any auth group: `unauthedv2 := r.Group("/v2"); ... unauthedv2.PATCH("/resume/:runID", prc.Resume)`, contrasted directly against the `authv2` group that wraps nearly every other `/v2` route in `auth.Authenticate(...)`. [1](#0-0) 
- `PipelineRunsController.Resume` parses `runID` as a `uuid.UUID` (the task's `TaskRun.ID`), decodes a JSON `ResumeRequest` body, and calls `App.ResumeJobV2(ctx, taskID, result)` with zero authorization checks — no session, token, or external-initiator credential is required or even read. [4](#0-3) 
- The handler even logs the action to the audit trail under the label `audit.UnauthedRunResumed`, confirming this lack-of-auth is intentional/known-by-design (it's meant for bridge/external-adapter async callbacks), not a bug in isolation — but it inherits the exact risk pattern in the report: security relies entirely on the secrecy of a single identifier (`runID`/task UUID) rather than on any authentication of the caller. [5](#0-4) 
- `ResumeRun` unconditionally calls `UpdateTaskRunResult` with the caller-supplied value/error and restarts the pipeline if the ORM reports the task can proceed — there is no check that the resumer is the same party (e.g., the External Adapter/bridge) that originally issued the pending request. [6](#0-5) 

If a `runID`/task UUID is disclosed or guessable through any channel (logs, error messages, response bodies, timing, or a lower-privileged authenticated user who can view job runs via `GET /jobs/:ID/runs/:runID` which is only gated by generic `auth.Authenticate` with no ownership scoping) an unauthenticated remote attacker can submit arbitrary `value`/`error` payloads to resume/influence the downstream workflow exactly as in the n8n advisory.

### Impact Explanation
An attacker who obtains a valid pending task/run UUID can inject arbitrary data into the resumption of that pipeline run, influencing subsequent pipeline tasks (e.g., data written to on-chain, downstream computations, ETH tx tasks) without any authentication. This maps to "unauthorized job run or fund movement" / "cross-user response confusion" categories in the validation criteria, since the resumed value feeds directly into task graph outputs that can drive `ETHTx` and other consequential tasks.

### Likelihood Explanation
Exploitability is gated by the difficulty of obtaining a valid, still-pending task UUID (v4 UUID, high entropy) — this is a real mitigating factor, analogous to the n8n advisory itself being rated only Medium/CVSS `AC:H` for the same reason (attacker must "identify a valid execution ID"). However, this design is intentional (this endpoint exists to let external bridge adapters call back asynchronously), and the codebase's own audit-log naming (`UnauthedRunResumed`) shows the maintainers are aware this endpoint trusts the ID alone. Any leak of the UUID (via logs, error responses, a less-privileged authenticated user viewing run details, or a compromised/malicious adapter response echoing it) is sufficient for exploitation, matching the report's precondition structure closely.

### Recommendation
- Bind the resume token to the specific external adapter/bridge that requested the pending task (e.g., an HMAC/shared-secret per bridge, or scoping the resume token to the bridge's outgoing secret already present in `bridges.ExternalInitiator.OutgoingSecret/OutgoingToken`), rather than trusting the bare task UUID.
- Rate-limit and monitor `/v2/resume/:runID` more aggressively than generic authenticated routes, since it is intentionally unauthenticated.
- Ensure task UUIDs are never leaked to lower-privileged/unauthenticated surfaces (verify `GET /jobs/:ID/runs/:runID` and any callback logging paths do not echo raw resume UUIDs to non-owning users).
- Add expiration/one-shot invalidation immediately after first successful resume, and reject resumes for tasks not in the exact expected pending state (verify current `UpdateTaskRunResult` already enforces state; extend to prevent replay of the same UUID after completion).

### Proof of Concept
1. Configure a job with an async bridge task (`type=bridge async=true`), which suspends and expects an external adapter callback to `PATCH /v2/resume/:runID`, as demonstrated by the existing test harness pattern. [7](#0-6) 
2. Obtain/guess the pending task's UUID (`id` in that test) through any leak channel.
3. Send an unauthenticated request:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"value": "<attacker-controlled result>"}
   ```
4. Because `unauthedv2.PATCH("/resume/:runID", prc.Resume)` requires no credentials, the server accepts the request, calls `ResumeJobV2` → `ResumeRun`, and resumes the pipeline with the attacker-supplied value, exactly mirroring the n8n `/chat` hijack pattern of resuming another party's waiting execution with attacker input. [8](#0-7) [4](#0-3)

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

**File:** core/services/pipeline/task.bridge_test.go (L615-666)
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
```
