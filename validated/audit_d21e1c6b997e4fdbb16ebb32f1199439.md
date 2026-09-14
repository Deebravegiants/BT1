### Title
Unauthenticated `/v2/resume/:runID` endpoint allows anyone with a task UUID to inject arbitrary results into a suspended pipeline run without state/ownership validation - ([File: core/web/pipeline_runs_controller.go])

### Summary
The Olympus report shows `claimRewards()` performing a privileged action (paying out rewards) without validating that the caller's vault state still entitles them to it — the only "authorization" was ever having deposited, with no check that they still hold LP. The chainlink analog is `PipelineRunsController.Resume`, mounted on the **unauthenticated** route group, which resumes a suspended pipeline task run and injects a caller-supplied value/error based solely on knowledge of a `runID` (task UUID) — with no secret/token/HMAC verification that the caller is the legitimate bridge/adapter that originated the async request.

### Finding Description
The route is registered without any auth middleware: [1](#0-0) 

The handler decodes attacker-controlled JSON body (`value`/`error`) and calls `ResumeJobV2`/`ResumeRun` using only the `runID` path parameter as identification — no token, no external-initiator secret, no signature check: [2](#0-1) 

The only server-side guard is that the underlying pipeline task run must be in `running`/`suspended` state — there is no check that the requester is the actual bridge/adapter that was given the callback URL: [3](#0-2) 

This URL is normally handed out only to the external bridge as part of the async `responseURL` field embedded in the outgoing HTTP request body: [4](#0-3) 

Unlike the Olympus bug, this isn't a missing "did the user actually still qualify" check on a repeatable claim — it's a missing "is this caller actually authorized to act on this resource" check. The design relies entirely on UUID (task ID) secrecy as a bearer credential, with no compensating authentication factor (comparable to the `ExternalInitiator` access-key/secret pattern used elsewhere, e.g. `core/web/auth/auth.go:119-149`, which chainlink otherwise reserves for privileged run-triggering flows). If a task UUID is leaked (logs, error messages, intermediary proxies, referrer headers, timing/UUID predictability, or a compromised bridge/adapter), any unauthenticated party can complete/overwrite the pending task's result exactly once while it remains `suspended`, injecting arbitrary attacker-chosen data into the job pipeline (e.g., a price feed value, VRF/keeper decision input, or any bridge-driven `pipeline.Result`), instead of the legitimate bridge's actual answer.

### Impact Explanation
Successful exploitation lets an unprivileged attacker impersonate the external adapter/bridge for a specific pending async task and inject an arbitrary result/error into the node's pipeline before the real bridge responds (a race, but a feasible one given no rate-limiting or authentication on this endpoint). Because pipeline outputs can feed on-chain transmissions (OCR reports, VRF fulfillment inputs, keeper actions), this can result in fund-impacting incorrect data being reported/transmitted by the node — matching the "unauthorized job run / fund movement / cross-user response confusion" acceptance criteria.

### Likelihood Explanation
Likelihood depends on task-UUID confidentiality; the UUID is a v4 random value normally known only to the specific bridge that receives the `responseURL`. This lowers likelihood versus the Olympus bug (which required no secret at all), but the identifier is the sole authorization mechanism for a state-changing, unauthenticated write into the pipeline — a bearer-token-by-obscurity design, with no secondary check (e.g., no per-task shared secret, no requester-address binding) despite the codebase elsewhere favoring symmetric-secret auth for external initiators. Exposure vectors (bridge logs, HTTP proxies/CDNs logging paths, error responses that echo the URL) are plausible in production Chainlink node deployments.

### Recommendation
Bind resumption to a per-task secret (e.g., HMAC over the task ID with a per-bridge or per-run secret, similar to `ExternalInitiator.OutgoingToken`/`OutgoingSecret`), and require it as a header/token distinct from the UUID in the path. At minimum, add rate limiting and audit-alerting distinct from `UnauthedRunResumed` (which already acknowledges the unauthenticated nature) for repeated/duplicate resume attempts on the same `runID`, and verify the requester matches the bridge configured for that task's spec name where derivable.

### Proof of Concept
1. Deploy a job with an `async=true` bridge task; the bridge adapter receives `responseURL = https://node/v2/resume/<taskUUID>` in its request body per `finalizeAndMarshalBridgeRequestData` in `core/services/pipeline/task.bridge.go`.
2. An unauthenticated third party who obtains `<taskUUID>` (via logs, proxy history, timing, or a compromised bridge) sends: `PATCH /v2/resume/<taskUUID>` with body `{"value": "<attacker-controlled result>"}`.
3. Because the route bypasses `auth.Authenticate` entirely (`core/web/router.go:243`) and `UpdateTaskRunResult` only checks the run's state, not caller identity (`core/services/pipeline/orm.go:271-308`), the attacker's value is accepted and the pipeline is resumed with it — before or instead of the legitimate bridge response.

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
