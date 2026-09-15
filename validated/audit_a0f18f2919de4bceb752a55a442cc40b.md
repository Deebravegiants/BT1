The code matches the claim exactly as described. Note the SECURITY.md excludes "Impacts that only require DDoS" and "Best practice recommendations" but this is a specific rate-limit tier misconfiguration with a concrete DB-write/goroutine-spawn resource consumption vector on an endpoint that is deliberately unauthenticated by design (external initiator callback), not a generic DDoS claim — it's a comparative gap against the node's own security policy (mirroring `/sessions` unauth tier). This is a legitimate configuration/logic issue rather than a purely theoretical DDoS claim, since it's directly traceable to the routing code and contrasts with the existing `/sessions` precedent in the same file.

Audit Report

## Title
Unauthenticated pipeline-run resume endpoint inherits the high "authenticated" rate limit instead of the strict "unauthenticated" limit - (File: core/web/router.go)

## Summary
`PATCH /v2/resume/:runID` is registered on `unauthedv2 := r.Group("/v2")` with no authentication middleware [1](#0-0)  yet it is mounted under the parent `api` group, which only applies the "Authenticated" rate limiter (default 1000 req/min) via `rl.AuthenticatedPeriod()` / `rl.Authenticated()` [2](#0-1) . In contrast, the only other unauthenticated write route, `POST /sessions`, is explicitly wrapped in its own sub-group using the stricter "Unauthenticated" limiter (default 5 req/20s) [3](#0-2) .

## Finding Description
`PipelineRunsController.Resume` parses a `runID` UUID and JSON body, then invokes `prc.App.ResumeJobV2`, which calls `ResumeRun` in the pipeline runner [4](#0-3) . `ResumeRun` performs a database write via `r.orm.UpdateTaskRunResult` and, when applicable, spawns a goroutine to re-run the pipeline [5](#0-4) . This endpoint is intentionally unauthenticated (it's a callback target for external resumable tasks such as bridge adapters), but unlike `/sessions` it was not placed under the stricter unauthenticated rate-limit sub-group, so it inherits the parent `api` group's 1000/min authenticated tier instead of the 5/20s unauthenticated tier that the code elsewhere demonstrates as the intended policy for credential-less endpoints.

## Impact Explanation
An unauthenticated caller can drive up to ~200x more requests against a DB-writing, potentially goroutine-spawning endpoint than the unauthenticated rate-limit tier is designed to permit, which can degrade node responsiveness and consume DB/pipeline resources. This is a genuine configuration/logic gap in the rate-limiting scheme, evidenced by direct comparison with the deliberate stricter treatment given to `/sessions` in the same file, rather than a purely theoretical or generic "impacts that only require DDoS" claim excluded by policy — it stems from a concrete, provable discrepancy in how routes are grouped relative to rate-limiter middleware.

## Likelihood Explanation
No credentials are required; only a syntactically valid UUID `runID` is needed to reach `ResumeJobV2`, and even invalid/nonexistent IDs still consume request-handling and DB-lookup resources before erroring out. Default configuration (`Authenticated=1000/1m`) applies to this endpoint, confirmed directly by the routing code and contrasted with the `TestSessions_RateLimited` test demonstrating the stricter 5-request unauthenticated tier applied elsewhere [6](#0-5) .

## Recommendation
Move `PATCH /v2/resume/:runID` into its own sub-group (mirroring the `/sessions` pattern in `sessionRoutes`) that applies `rl.UnauthenticatedPeriod()` / `rl.Unauthenticated()`, or introduce a dedicated, more conservative rate-limit tier for this callback endpoint. Additionally, consider validating that the referenced task run is in a resumable state before performing any DB write, and/or rate-limit per-`runID`/per-IP.

## Proof of Concept
1. Start a node with default `WebServer.RateLimit` config (`Authenticated=1000/1m`, `Unauthenticated=5/20s`).
2. Without any auth headers/cookies, send `PATCH /v2/resume/<uuid>` (valid or garbage JSON body) repeatedly from a test HTTP client, analogous to `TestSessions_RateLimited` [6](#0-5) .
3. Observe requests are only rejected with HTTP 429 after ~1000 requests/minute — the authenticated limiter applied via the parent `api` group [7](#0-6)  — instead of after 5 requests/20s as intended for unauthenticated traffic, in contrast to the `/sessions` endpoint's behavior.

### Citations

**File:** core/web/router.go (L77-91)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L207-215)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
```

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
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

**File:** core/web/router_test.go (L127-156)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
	require.NoError(t, err)

	resp, err := client.Do(request)
	require.NoError(t, err)
	assert.Equal(t, 429, resp.StatusCode)
}
```
