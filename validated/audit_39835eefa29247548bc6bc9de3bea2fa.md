This confirms the analog: `PATCH /v2/resume/:runID` is registered in the fully unauthenticated route group and requires only knowledge of a task UUID (bearer capability), not any user/API-key/session authentication.### Title
Unauthenticated `/v2/resume/:runID` endpoint lets any unprivileged client finalize a pipeline task run with attacker-controlled data - (File: core/web/router.go)

### Summary
The external report describes `mintRebalancer(uint256 amount)` in USSD.sol — a state-mutating function that should only be callable by a privileged component (the rebalancer) but has no access-control check, so any unprivileged caller can invoke it and corrupt protocol state/value. The closest reachable analog in this repository is the `PATCH /v2/resume/:runID` route, which is deliberately mounted in the *unauthenticated* route group and lets any network client without a session, API token, or external-initiator credential resolve a "pending" pipeline task with attacker-supplied `value`/`error`, exactly like an unguarded state-mutating entry point.

### Finding Description
In `core/web/router.go`, the `v2Routes` function registers: [1](#0-0) 

`unauthedv2.PATCH("/resume/:runID", prc.Resume)` is bound to the top-level `unauthedv2` group, which has **no** `auth.Authenticate(...)` middleware, unlike every other job/pipeline-run mutating route which is behind `authv2` (session or API-token auth) via `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`.

The handler itself, `PipelineRunsController.Resume`, performs no authentication or authorization check of its own: [2](#0-1) 

It parses the `runID` path parameter directly as a task UUID, decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest{Error, Value}`, converts it via `ToResult()`, and calls `App.ResumeJobV2(ctx, taskID, result)` — which ultimately calls `runner.ResumeRun` → `orm.UpdateTaskRunResult`: [3](#0-2) [4](#0-3) 

`UpdateTaskRunResult` writes the attacker-controlled `Value`/`Error` directly into `pipeline_task_runs.output`/`error` for any task row matching the UUID whose parent run is in `running` or `suspended` state, then flips the run back to `running` and resumes pipeline execution with that data injected as the task's output. There is no verification that the caller is the bridge/external adapter that originally issued the pending async request, no HMAC/signature check, and no session/API-key/external-initiator check — the only "secret" is the unguessable UUID itself, which is treated purely as a bearer capability token embedded in the `responseURL` sent to the external bridge adapter (`core/services/pipeline/task.bridge.go`, `finalizeAndMarshalBridgeRequestData`, embedding `/v2/resume/<uuid>` — confirmed via `task.bridge_test.go` assertions against that URL pattern). The route/action is explicitly acknowledged as unauthenticated in the audit trail itself: `audit.UnauthedRunResumed` is the event name logged on success.

This mirrors the reported bug class: a state-mutating action (`mintRebalancer` / here, "finalize task with attacker output") that is supposed to be restricted to a privileged caller (the rebalancer contract / here, the specific external bridge adapter that owns the pending async task) but is reachable by any unprivileged actor who can supply (or brute-force/leak/observe via logs, telemetry, network egress, or a compromised/malicious external adapter) the 128-bit task UUID.

### Impact Explanation
If a task UUID is ever observed by, replayed by, or guessed by an unauthorized party (e.g., leaked in bridge request logs, exposed via a misconfigured/compromised adapter, an SSRF/log-scraping vector, or simply because the responseURL is transmitted in plaintext to a third-party HTTP bridge over the network), that party can:
- Forge the "result" of an in-flight async bridge task (e.g., price/data feed values used downstream in OCR/VRF/keeper jobs), directly corrupting the finalized job run output with attacker-chosen data — analogous to unauthorized minting of state/value in the reported contract bug.
- Prematurely resume/finish a suspended pipeline run with arbitrary fabricated data before the legitimate external adapter responds, causing incorrect on-chain reports/transactions to be built from forged inputs.
- Do this without possessing any node credentials, API keys, or session — a full authentication bypass on a state-mutating endpoint.

This is capped in severity relative to the reference finding because the "capability" here (an unguessable, per-task UUID) still constitutes some barrier, so it's not literally callable by "everyone" with zero precondition. It does not directly move funds through this endpoint alone, but it can corrupt any downstream data pipeline that is fed by an async bridge task — a legitimate concrete integrity/confidentiality gap that the codebase's own naming (`UnauthedRunResumed`) recognizes.

### Likelihood Explanation
Exploitation requires knowledge of a specific pending task UUID. Attackers cannot enumerate all pending tasks, but the UUID is transmitted unauthenticated over HTTP(S) to third-party bridge/adapter endpoints as part of the `responseURL`, is present in bridge telemetry (`BridgeTelemetry`), and could be captured by anyone with access to that data path (network intermediary, compromised adapter, log aggregation misconfiguration, or a malicious/misbehaving external adapter operator who is not supposed to have write access to the Chainlink node's API). Since the endpoint intentionally has zero authentication (not even the External Initiator credential scheme used elsewhere), the barrier is "possession of the URL," not cryptographic or role-based authorization — this is a materially weaker control than every other state-mutating route in the same router.

### Recommendation
- Require the responding party to present a bound secret/HMAC (e.g., sign the resume payload with a per-task secret established when the async request was dispatched, verified server-side) rather than relying solely on UUID possession as a bearer token.
- At minimum, bind resumption to the specific bridge/external-initiator identity that issued the outbound request (similar to `AuthenticateExternalInitiator`), and reject resumes for tasks not owned by the authenticated caller.
- Add rate limiting/anomaly detection specific to `/v2/resume/:runID` distinct from the general unauthenticated rate limit, and avoid logging or including the raw resume URL in verbose logs/telemetry that could leak the capability token.

### Proof of Concept
1. A job with an async bridge task (`async=true`) is created; when triggered, the bridge task sends a request to the external adapter containing `responseURL = https://<node>/v2/resume/<taskUUID>` (confirmed by `finalizeAndMarshalBridgeRequestData` in `core/services/pipeline/task.bridge.go`).
2. Any network party who obtains this URL (via traffic interception, adapter compromise, log exposure, or telemetry) can, without any Chainlink API key or session cookie, issue:
   `PATCH /v2/resume/<taskUUID>` with body `{"value": "<attacker-controlled JSON>"}`
   directly to the node's public HTTP interface, since the route is mounted on `unauthedv2` with no `auth.Authenticate` middleware (`core/web/router.go:243`).
3. `PipelineRunsController.Resume` decodes the body and calls `ResumeJobV2` → `runner.ResumeRun` → `orm.UpdateTaskRunResult`, which writes the attacker's value into `pipeline_task_runs` and resumes the run, propagating the forged value through the rest of the pipeline DAG — with the only audit trace being an `UnauthedRunResumed` log entry recorded after the fact. [5](#0-4)

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

**File:** core/services/pipeline/task.bridge.go (L339-378)
```go
// finalizeAndMarshalBridgeRequestData merges job meta, upstream inputs, and async resume URL into requestData,
// writes the merged map back through requestData for use by makeHTTPRequest, and returns the JSON body for logging
// and telemetry.
func (t *BridgeTask) finalizeAndMarshalBridgeRequestData(lggr logger.Logger, vars Vars, inputValues []any, requestData *MapParam, includeInputAtKey StringParam) ([]byte, error) {
	var metaMap MapParam

	meta, _ := vars.Get("jobRun.meta")
	switch v := meta.(type) {
	case map[string]any:
		metaMap = MapParam(v)
	case nil:
	default:
		lggr.Warnw(`"meta" field on task run is malformed, discarding`,
			"task", t.DotID(),
			"meta", meta,
		)
	}

	merged := withRunInfo(*requestData, metaMap)
	if t.IncludeInputAtKey != "" {
		if len(inputValues) > 0 {
			merged[string(includeInputAtKey)] = inputValues[0]
		}
	}

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

	*requestData = merged
	return json.Marshal(merged)
}
```
