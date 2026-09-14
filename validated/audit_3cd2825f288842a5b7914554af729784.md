### Title
Unauthenticated `/v2/resume/:runID` endpoint accepts arbitrary pipeline resume "responses" based solely on a matchable ID - ([File: core/web/router.go])

### Summary
The DNS reply verification bug (CVE-2022-22846) is a case of accepting a reply as valid based only on a correlation ID, with no additional authentication of the responder. The Chainlink node exposes an analogous pattern at `/v2/resume/:runID`: it is mounted in the fully **unauthenticated** route group and resumes a suspended pipeline task purely by matching the path UUID against a pending `pipeline_task_runs.id`, with no bearer token, HMAC, or other secret binding the "response" to the specific outstanding "request" (the outbound bridge call).

### Finding Description
`v2Routes` registers the resume endpoint outside of any authentication middleware: [1](#0-0) 

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

The handler itself performs no additional authentication check - it only parses the UUID from the URL and forwards the caller-supplied result body straight into `ResumeJobV2`: [2](#0-1) 

`ResumeJobV2` → `pipelineRunner.ResumeRun` → `orm.UpdateTaskRunResult`, whose *only* correlation check is a SQL match on the task ID plus run-state filter: [3](#0-2) 

```go
sql := `... WHERE pipeline_task_runs.id = $1 AND pipeline_runs.state in ('running', 'suspended') FOR UPDATE`
```

This is the async-bridge-task callback URL, generated as `/v2/resume/<taskRun.uuid>`: [4](#0-3) 

The only "secret" that ties a legitimate external-adapter response to its originating request is the unpredictability of the `taskID` UUID itself - functionally equivalent to the DNS query ID acting as the sole authenticator of a "reply." There is no signature, shared secret, or bearer token issued alongside the resume URL that the endpoint verifies. Any client that can view, log, proxy, or guess a live `taskID` (e.g. via server logs, a misconfigured intermediary bridge adapter, SSRF-adjacent leakage, or exhaustive prediction against a running node with many concurrent pending async jobs) can inject an arbitrary `value`/`error` for that pending task run and force the pipeline to resume with attacker-controlled data - exactly analogous to a spoofed DNS reply being accepted because only the transaction ID matched.

### Impact Explanation
An attacker who obtains or predicts a pending task-run UUID can:
- Impersonate the external adapter's response and inject arbitrary `value`/`error` into a running pipeline (cross-user/cross-request response confusion), which then flows into downstream tasks (e.g., `median`, `multiply`, ultimately an `ETHTx` task), potentially corrupting on-chain reported data or triggering fund-moving transactions with attacker-influenced inputs.
- This is unauthenticated by design (no session/API token required), so it is reachable directly by any unprivileged network client, differing from the mitigations seen elsewhere in the codebase (e.g., the gateway/vault handlers, which additionally validate method match, signer quorum, and duplicate/tamper detection before accepting a "response" as legitimate — see `core/services/gateway/handlers/vault/handler.go:480-534`).

### Likelihood Explanation
Exploitability depends entirely on the secrecy of the UUID, which is not treated as a credential anywhere in the code (it's just a v4 UUID exposed in the `responseURL` sent to the external bridge). It can leak through node logs, HTTP proxies, external-adapter logs, or man-in-the-middle interception of the outbound bridge call, and there is no rate limiting or anomaly detection at this route observed in `core/web/router.go`. Likelihood is therefore dependent on operational exposure of the callback URL rather than any cryptographic weakness, which is a materially different risk profile than a true auth bypass, but structurally matches the reported bug class (accepting a "reply" solely via ID match).

### Recommendation
Bind the resume callback to an additional per-run secret (e.g., HMAC-signed token or bearer secret embedded in the response URL and verified server-side) rather than relying solely on the UUID's unpredictability, and/or restrict `/v2/resume/:runID` to be reachable only from trusted bridge/adapter network egress paths with request-level rate limiting and audit alerting on mismatched or repeated resume attempts.

### Proof of Concept
1. Configure an async bridge task; the node exposes `responseURL = http://<node>/v2/resume/<taskUUID>` to the external adapter (`core/services/pipeline/task.bridge.go:364-373`).
2. An attacker who observes/derives `<taskUUID>` (via logs, proxy, or leaked adapter request) sends: `PATCH /v2/resume/<taskUUID>` with a crafted JSON body (`{"data":"attacker-controlled"}`) directly to the node - no session cookie or API key required (`core/web/router.go:243`).
3. `PipelineRunsController.Resume` decodes the body and calls `App.ResumeJobV2` unconditionally (`core/web/pipeline_runs_controller.go:134-161`).
4. `orm.UpdateTaskRunResult` matches purely on `taskID` and resumes the pipeline with the attacker's payload (`core/services/pipeline/orm.go:271-308`), completing the run using forged data instead of the legitimate adapter's response.

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

**File:** core/services/pipeline/task.bridge.go (L364-373)
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
```
