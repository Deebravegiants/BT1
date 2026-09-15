## Vulnerability Analog Found

### Title
Unauthenticated `/v2/resume/:runID` endpoint allows any unprivileged caller to complete/hijack a pending pipeline task run by guessing or leaking a UUID - ([File: core/web/pipeline_runs_controller.go])

### Summary
The Sherlock report describes `rollLoan` being callable by any address (not just the intended counterparty) because the contract checks only that the caller matches a previously-recorded lender, rather than verifying the caller is authorized to trigger the specific action for that resource. The chainlink analog is `PipelineRunsController.Resume`, which resumes an in-flight, suspended pipeline (async bridge) task using only a bare UUID as the authorization token, with no verification that the caller is the specific bridge/external adapter the request was actually sent to.

### Finding Description
`BridgeTask.finalizeAndMarshalBridgeRequestData` embeds a callback URL of the form `<bridgeResponseURL>/v2/resume/<taskUUID>` into the outgoing request sent to an external adapter/bridge when a task is marked `async=true`: [1](#0-0) 

The corresponding server-side handler, `PipelineRunsController.Resume`, accepts a `PATCH` to `/v2/resume/:runID`, parses only a UUID from the path, and directly calls `App.ResumeJobV2` to write attacker/caller-supplied `value`/`error` into the suspended task run and restart the pipeline - with the audit log itself explicitly labeling this as `audit.UnauthedRunResumed`: [2](#0-1) [3](#0-2) 

`ResumeRun` in the pipeline runner then trusts the supplied value/error unconditionally to unblock the suspended run and resumes pipeline execution using that data: [4](#0-3) 

The only thing gating this state-mutating action is knowledge of the task run's UUID - there is no bridge-specific shared secret, HMAC signature, or check that the caller is the specific adapter the outgoing request was sent to. This mirrors the `rollLoan` root cause: a privileged, state-changing action (finalizing loan terms / finalizing a job-run result) is reachable by anyone who satisfies a weak, resource-identifier-only check, rather than a check that verifies the caller is the specific authorized counterparty for that resource.

### Impact Explanation
If a task-run UUID is disclosed (e.g., via logs, error messages, network observation of the outbound bridge request, or a job-run listing endpoint accessible to a lower-privileged/read-only session), any unauthenticated network client can:
- Inject an arbitrary value/error for a pending bridge/external-adapter task, directly controlling the data that flows into the rest of the pipeline (e.g., a price, an on-chain tx trigger, or any downstream computation dependent on that task's output).
- Effectively impersonate the external adapter's response, causing "unauthorized job run" output manipulation, analogous to the lender manipulating loan terms without borrower consent in the source report.

### Likelihood Explanation
Likelihood depends on whether the UUID is treated as an unguessable secret and never exposed. UUIDv4 space makes blind guessing impractical, but this is "security by obscurity" for an endpoint explicitly named `UnauthedRunResumed` - any leak of the ID (logging, monitoring dashboards, shared proxy logs, or a race where an attacker observes the outbound bridge request before the real adapter responds) fully compromises the resume action with no further authentication check.

### Recommendation
Add authentication/authorization to the resume flow beyond the bare UUID: bind the resume token to bridge-specific credentials (e.g., a per-request HMAC signed with the bridge's `OutgoingSecret`/`OutgoingToken`, similar to the external initiator's `AuthenticateExternalInitiator` scheme), and verify the caller/IP or shared secret before accepting `value`/`error` in `PipelineRunsController.Resume`.

### Proof of Concept
1. Create a job with an `async=true` bridge task; the node dispatches a request containing `responseURL: .../v2/resume/<taskUUID>` to the configured bridge.
2. Obtain `<taskUUID>` (e.g., via any log exposure, request/response interception, or timing/race observation before the legitimate adapter replies).
3. Send `PATCH /v2/resume/<taskUUID>` with an attacker-chosen JSON body (`pipeline.ResumeRequest`) directly to the node, with no authentication headers.
4. The node accepts the request unconditionally (as confirmed by the `UnauthedRunResumed` audit event) and resumes the pipeline using the attacker-supplied value, exactly as if the real bridge/adapter had responded. [5](#0-4) [1](#0-0) 

**Caveat:** I could not fully confirm the exact Gin route registration/middleware wrapping (`router.go`) for `/v2/resume/:runID` within the available context (only match counts were retrievable, not the route definition body), so I cannot state with certainty whether any additional middleware wraps this route beyond what the `Resume` handler itself does. However, the explicit `audit.UnauthedRunResumed` naming and the handler's own logic strongly indicate this endpoint is intentionally unauthenticated by design, relying solely on UUID secrecy.

### Citations

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

**File:** core/web/pipeline_runs_controller.go (L131-160)
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
```

**File:** core/logger/audit/audit_types.go (L1-1)
```go
package audit
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
