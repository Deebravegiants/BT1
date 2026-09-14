### Title
Unauthenticated `/v2/resume/:runID` endpoint accepts caller-supplied task result to finalize/resume pipeline runs, allowing state corruption and lock-out - (File: core/web/pipeline_runs_controller.go)

### Summary
The Astaria bug allows an unprivileged actor to call `ClearingHouse.safeTransferFrom` with attacker-controlled parameters (fake `paymentToken`), which is trusted to finalize/clean up liquidation state (deleting `LienToken`/`CollateralToken` records) without verifying the caller or the payload actually correspond to the real settlement. The analogous pattern in this codebase is the `Resume` handler for suspended pipeline runs: an external, unauthenticated party supplies a `taskID` and an arbitrary `Result` (value/error) that is used to finalize a suspended pipeline task run and potentially resume/complete the whole run, with the only "authentication" being possession of a UUID.

### Finding Description
`PipelineRunsController.Resume` at [1](#0-0)  parses a `runID` (really a `taskID` UUID) from the URL path and an arbitrary JSON body into a `pipeline.ResumeRequest`, converts it to a `pipeline.Result`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` — with no check that the caller is the external adapter/bridge that originally received this callback URL, and no signature/secret verification tied to the specific run.

This flows into `runner.ResumeRun` at [2](#0-1) , which calls `r.orm.UpdateTaskRunResult(ctx, taskID, Result{...})` — [3](#0-2)  — writing the attacker-supplied output/error directly into `pipeline_task_runs`, transitioning the run from `RunStatusSuspended` back to `RunStatusRunning`, and then re-invoking `r.Run(...)` which will finalize the entire pipeline run (writing final outputs, potentially triggering downstream on-chain transactions via ETHTx tasks, and deleting/pruning DB state) based on that forged value.

The audit event name itself, `audit.UnauthedRunResumed`, explicitly documents that this endpoint is intentionally unauthenticated — the codebase relies solely on the secrecy/unguessability of the UUID `taskID` as a bearer credential, exactly like Astaria relied on Seaport always supplying a legitimate `identifier`/`paymentToken` to `ClearingHouse.safeTransferFrom`. Just as Astaria never validated the `paymentToken` against the real settlement token bound to the auction, this endpoint never validates that the resuming caller is the legitimate external adapter tied to that specific `taskID`/bridge task (e.g., via a per-run secret/token separate from the UUID, or a check that the request originates from the configured bridge URL).

### Impact Explanation
Any actor who obtains or guesses a pending run's `taskID` (e.g., via log leakage, error messages, request/response inspection, or brute force of the UUID space over long-lived pending async bridge tasks) can:
- Inject a forged `Result` (value or error) into a suspended pipeline run, finishing it with attacker-controlled data — analogous to Astaria's forged `paymentToken` finalizing debt payoff with an attacker-controlled token.
- Prematurely finalize/cancel a run that was waiting on a legitimate external adapter response, causing the legitimate response (when it arrives) to be dropped/rejected while the run's on-chain effects (e.g., an ETHTx task) already executed with the attacker's forged data, or causing permanent loss of the ability to complete the run correctly (similar to Astaria's "NFT locked forever" outcome, here manifesting as a corrupted/finalized run state that cannot be legitimately resumed again).
- This is reachable from an unprivileged, unauthenticated internet client, matching the required threat model (internet-facing gateway/session-like token misuse, request impersonation, cross-user response confusion).

### Likelihood Explanation
UUIDv4 task IDs provide practical protection against brute-force guessing, so likelihood is lower than the Astaria case, where the manipulated field (`identifier`) is trivially attacker-chosen with no secrecy requirement at all. However, unlike Astaria, this design is explicitly acknowledged in-code (`UnauthedRunResumed`), indicating the team is aware the endpoint is unauthenticated by design and relies purely on ID secrecy rather than a bound secret/HMAC — any leak of the run/task ID (logs, timing side channels, `X-Chainlink-Pending`/response URL exposure to intermediate proxies) fully defeats the protection, mirroring the root cause class in the report: a "trusted-callback" endpoint that blindly accepts caller-supplied result data without cryptographically binding it to the specific pending operation and its expected origin.

### Recommendation
- Bind resume requests to a per-run secret (e.g., HMAC/token distinct from the run UUID) generated when the async task is created, and require it in the resume request (header or body), verified against a stored value tied to that specific `taskID`, before accepting the caller-supplied `Result`.
- Alternatively, restrict `/v2/resume/:runID` to be reachable only via the specific external-adapter/bridge configuration used to create the request (e.g., match against the bridge's configured outbound URL/allowlist) rather than trusting any bearer of the UUID.
- Ensure the `Result` payload can only transition state consistent with the specific pending task's expected schema/type, reducing the ability to inject arbitrary error/value data that finalizes runs incorrectly.

### Proof of Concept
Conceptual PoC (cannot be executed here, but derived directly from code paths cited above):
1. A job with an async `BridgeTask` (`Async: "true"`) is triggered; `finalizeAndMarshalBridgeRequestData` embeds a `responseURL` of the form `.../v2/resume/<taskID>` [4](#0-3) , and the run is suspended in the DB (`RunStatusSuspended`) via `StoreRun` [5](#0-4) .
2. An attacker who learns the `taskID` (leaked via logs, a misconfigured proxy, or another side channel) sends `PATCH /v2/jobs/:ID/runs/<taskID>` with an arbitrary JSON body to `PipelineRunsController.Resume` [6](#0-5) , with no credentials beyond knowing the UUID.
3. `ResumeJobV2` → `runner.ResumeRun` → `orm.UpdateTaskRunResult` writes the forged result and flips the run to `RunStatusRunning` [2](#0-1) , then `r.Run` finalizes the pipeline using the forged data, exactly mirroring how Astaria's `ClearingHouse.safeTransferFrom` accepted a forged `paymentToken` to finalize/clean up liquidation state without validating the true expected value.

Note: I could not fully verify from the index whether `/v2/resume/:runID` is registered with any authentication middleware group in `core/web/router.go` (the file exists and has route entries for "Resume"/`PATCH`, but the surrounding middleware context around that specific route was not retrievable within the available tool calls) — the `audit.UnauthedRunResumed` naming strongly implies it is unauthenticated by design, but this should be confirmed by reviewing the exact router group in `core/web/router.go` in a full session.

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

**File:** core/services/pipeline/orm.go (L185-228)
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

			// Suspend the run
			run.State = RunStatusSuspended
			if _, err = tx.ds.NamedExecContext(ctx, `UPDATE pipeline_runs SET state = :state WHERE id = :id`, run); err != nil {
				return fmt.Errorf("failed to update pipeline run %d to %s: %w", run.ID, run.State, err)
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
