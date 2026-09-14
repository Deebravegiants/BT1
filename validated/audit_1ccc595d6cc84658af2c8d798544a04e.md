### Title
Unauthenticated `PATCH /v2/resume/:runID` endpoint allows anyone to resume/complete pipeline runs without any access control - ([File: core/web/router.go])

### Summary
The `cancelAfterRandomnessRequest()` bug class is "a state-changing, privileged operation that natspec/design intends to be restricted, but is exposed without any authentication/authorization check, letting an unprivileged caller invoke it." The closest reachable analog in chainlink is the `PATCH /v2/resume/:runID` route, which is registered in the *unauthenticated* route group and lets any anonymous HTTP client resume a pipeline task run and inject its result, with zero authentication.

### Finding Description
In `core/web/router.go`, the `v2Routes` function explicitly creates an unauthenticated group and mounts the resume endpoint on it, before any of the `authv2`/`userOrEI` authenticated groups are wired up: [1](#0-0) 

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

Compare this to every other mutating route in the same file, which is wrapped in `authv2` and additionally gated by `auth.RequiresEditRole`, `auth.RequiresRunRole`, or `auth.RequiresAdminRole` (e.g. `authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))`, `userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))`). The `/v2/resume/:runID` route has none of that: no session cookie, no API token, no external-initiator header check, nothing.

The handler itself, `PipelineRunsController.Resume`, only validates that `runID` parses as a UUID and that the JSON body decodes into a `pipeline.ResumeRequest`; it performs no ownership/ACL check before calling `prc.App.ResumeJobV2`: [2](#0-1) 

`ResumeJobV2` forwards directly to the pipeline `Runner.ResumeRun`, which unconditionally writes the caller-supplied `value`/`error` into the task run and restarts the pipeline: [3](#0-2) 

The only trace that this endpoint is "special" is an audit-log call using an event literally named `UnauthedRunResumed`: [4](#0-3) 

That name signals the authors were aware this is an unauthenticated code path, but — mirroring the Sherlock report's pattern — there is no code enforcing that only the intended caller (e.g., the specific external adapter/bridge that owns the pending async task) can hit it. Any unauthenticated network client that can reach the node's HTTP API can call this endpoint for *any* `runID` UUID they can obtain or guess, and inject arbitrary success/error results, driving the pipeline forward or corrupting run state.

### Impact Explanation
An unprivileged actor with network access to the node's web server can:
- Resume/complete pending pipeline task runs (typically bridge/external-adapter async callbacks) with attacker-chosen result payloads, without any credential.
- Force premature completion of a run, inject falsified data into a job pipeline (potentially feeding bad data downstream into on-chain-facing tasks), or repeatedly hit the endpoint to interfere with legitimate resumptions.
- This is a state-changing action against a node's job-execution pipeline reachable purely by an unprivileged/unauthenticated HTTP request — matching the report's core issue of "no access control on a function that should be privileged."

The severity is somewhat mitigated by the fact that `runID` is a randomly-generated UUID (task run ID) that must be known/guessed by the attacker; it is not literally callable by "anyone" without any secret. This differs from the original report where the round ID is fully public/predictable. Still, the endpoint is a genuine, code-confirmed authentication gap on a mutating, pipeline-altering action, consistent with the requested "unauthorized job run" impact category.

### Likelihood Explanation
Likelihood is bounded by the difficulty of learning a valid, still-pending `runID`. In deployments where task run IDs leak through logs, external adapter requests, webhooks, or other side channels (a realistic occurrence in bridge/external-adapter integrations), exploitation likelihood is meaningful. The complete absence of any auth check (not even a shared secret specific to the bridge) means the only protection is UUID unguessability, which is a weak, defense-in-depth-only control rather than deliberate authorization.

### Recommendation
- Require the resume request to authenticate as the specific bridge/external adapter that owns the pending async task (e.g., verify a per-task shared secret/HMAC issued when the async task was created, not just the UUID).
- Alternatively, move `/v2/resume/:runID` into the authenticated `userOrEI` group and require `auth.RequiresRunRole`, plus validate that the resuming caller corresponds to the bridge that originated the async task.
- At minimum, add rate limiting and stricter validation to reduce the blast radius of the existing unauthenticated design, and rename/repurpose the `UnauthedRunResumed` audit event only after the access-control gap is closed, since currently it merely documents rather than mitigates the issue.

### Proof of Concept
1. Deploy a chainlink node and create a job containing an async (bridge/external adapter) task; note or observe a resulting `taskID` (UUID) for a pending run, e.g. via logs or by monitoring bridge callback traffic.
2. Without any session cookie, API token, or EI header, send:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"value": "attacker-controlled-result"}
   ```
   directly to the node's HTTP listener from an unauthenticated client.
3. Observe (per `core/web/router.go:243` and `core/web/pipeline_runs_controller.go:134-161`) that the request succeeds with HTTP 200, `ResumeJobV2`/`Runner.ResumeRun` is invoked, and the pipeline run resumes using the attacker-supplied value — with zero authentication having occurred anywhere in the request path.

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
