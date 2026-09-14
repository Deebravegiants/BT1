## Analysis: Unauthenticated `/v2/resume/:runID` endpoint lacks dedicated spam controls

I looked for a chainlink analog to the Story `chargeFee`-modifier gap (state-changing, resource-consuming operations reachable without any cost/quota control tied specifically to the operation). The strongest match in scope is the pipeline-run resume endpoint.

### Title
Unauthenticated `/v2/resume/:runID` endpoint has no dedicated rate limit / access control, allowing free-form spam of pipeline resumption - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
`core/web/router.go` registers `PATCH /v2/resume/:runID` on an explicitly **unauthenticated** route group, separate from the `authv2` group that requires a session/API token. [1](#0-0) 
This handler, `PipelineRunsController.Resume`, parses attacker-controlled input and immediately calls `App.ResumeJobV2`, which in turn calls `pipelineRunner.ResumeRun`, potentially restarting a suspended pipeline run (spawning a goroutine that re-executes the pipeline). [2](#0-1) [3](#0-2) 

### Finding Description
The route is intentionally unauthenticated because it is the callback target for async bridge/adapter tasks: the bridge task embeds a `responseURL` of the form `.../v2/resume/<taskUUID>` for external adapters to call back into the node. [4](#0-3) 

However, unlike the rest of the write-capable API surface—which is gated by `auth.RequiresRunRole` / `auth.RequiresEditRole` / `auth.RequiresAdminRole` and sits behind the "Authenticated" rate-limit bucket intended for trusted, logged-in traffic—this endpoint is placed in a group with **no additional per-route rate limiting, no allowlist of expected callers, and no correlation to a specific job/bridge secret** beyond the unguessable UUID itself: [1](#0-0) 

Every request to this endpoint, even with a syntactically invalid or unknown `runID`, still causes the server to:
1. Parse the UUID and decode/unmarshal the JSON body,
2. Call into `ResumeJobV2` → `pipelineRunner.ResumeRun` → `orm.UpdateTaskRunResult` (a DB write attempt),
3. On a match, spin up a goroutine that fully re-executes a pipeline run. [3](#0-2) 

This is architecturally the same class of issue as the Story `chargeFee` bug: a state-changing / resource-consuming code path reachable by an unprivileged, unauthenticated caller with **no dedicated quota or economic/authentication cost attached to the specific operation**, relying only on a generic, shared rate limiter not designed for this trust boundary. The route's own audit event name, `audit.UnauthedRunResumed`, acknowledges that it is deliberately unauthenticated, which underscores that whatever throttling exists for it must be self-contained — but none is applied at the route/handler level. [5](#0-4) 

### Impact Explanation
An unauthenticated remote client can send an unbounded volume of `PATCH /v2/resume/:runID` requests. Each request forces DB I/O (`UpdateTaskRunResult`) and, when it happens to target a real pending task (or via timing/enumeration on a busy node with many pending async tasks), can trigger full pipeline re-execution goroutines. Absent a route-specific limiter, this can be used to consume node CPU/DB/goroutine resources — a resource-exhaustion / spam vector analogous to the "CL spam" impact described in the report (`AO:A/AC:L/AX:L/.../A:H`).

### Likelihood Explanation
Likelihood is moderate: exploiting it to actually resume a *specific* run requires knowing (or guessing) a live task UUID, which is hard by design. But the spam/DoS surface does not require guessing correctly — merely hitting the endpoint repeatedly with garbage UUIDs already forces parsing, unmarshalling, and an ORM round trip per request, with no endpoint-specific throttle, since the route bypasses the `authv2`-gated role/rate structure entirely.

### Recommendation
Add a dedicated, tightly-scoped rate limiter (and/or per-bridge/task token binding, e.g., requiring an unguessable secret embedded in the callback URL beyond the UUID, or short expiry) specifically for `/v2/resume/:runID`, independent of the general "Authenticated" bucket, so that unauthenticated callback traffic cannot be amplified into a resource-exhaustion vector.

### Proof of Concept
```
for i in 1..N:
  curl -X PATCH https://<node>/v2/resume/$(uuidgen) \
       -H "Content-Type: application/json" \
       -d '{"error":"", "data": {}}'
```
Repeated rapidly, each request forces a DB lookup/update attempt in `ResumeRun` with no dedicated per-route throttling — only the generic "authenticated" bucket shared with the rest of `/v2/*` applies. [6](#0-5) 

**Caveat / uncertainty:** I was not able to fully retrieve the exact numeric defaults for `WebServer.RateLimit().Authenticated()` vs `Unauthenticated()` from `config_web_server.go` within the available tool calls, so I cannot confirm precisely how generous the shared bucket is in the default configuration; this affects how severe the DoS window is in practice, but does not change the underlying finding that the endpoint has no dedicated, endpoint-specific throttle or authentication tied to its resource cost.

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
