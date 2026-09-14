### Title
Unauthenticated pipeline run resume endpoint allows unauthorized injection of task results - (File: core/web/pipeline_runs_controller.go)

### Summary
The `PipelineRunsController.Resume` handler, mounted at `PATCH /v2/resume/:runID`, is registered on the completely unauthenticated router group (`unauthedv2`), and accepts an arbitrary caller-supplied `value`/`error` result body that is applied directly to the pipeline task identified only by the `runID` path parameter, with no verification that the caller is the legitimate bridge/external adapter that was asked to fulfill that specific task.

### Finding Description
The route is registered without any auth middleware: [1](#0-0) 
```
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")
	...
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

The handler itself only parses the `runID` (a UUID identifying a specific paused pipeline `taskID`) from the URL and unmarshals an attacker/caller-controlled JSON body directly into a `pipeline.ResumeRequest`, then feeds it into `ResumeJobV2` without checking that the requester is the bridge adapter that the async task was actually dispatched to: [2](#0-1) 
```
func (prc *PipelineRunsController) Resume(c *gin.Context) {
	taskID, err := uuid.Parse(c.Param("runID"))
	...
	rr := pipeline.ResumeRequest{}
	decoder := json.NewDecoder(c.Request.Body)
	err = errors.Wrap(decoder.Decode(&rr), "failed to unmarshal JSON body")
	...
	result, err := rr.ToResult()
	...
	if err := prc.App.ResumeJobV2(c.Request.Context(), taskID, result); err != nil {
	...
	prc.App.GetAuditLogger().Audit(audit.UnauthedRunResumed, map[string]any{"runID": c.Param("runID")})
```

Downstream, `ResumeRun` in the pipeline runner writes the caller-supplied `value`/`err` straight into the task run result and restarts the pipeline from that point: [3](#0-2) 

This mirrors the `SecuritizeSwap::buy` bug-class exactly: the endpoint trusts a caller-supplied identifier (`runID`, analogous to `_senderInvestorId`) as sufficient proof of authorization to act on behalf of the entity that identifier represents (the specific async bridge callback), without any secondary check that the actual caller is who they claim to be (i.e., the bridge/external adapter that was given that `runID`). The only "authentication" here is possession of the UUID value, with no signature, shared secret, or binding to the originating bridge/adapter. If a `runID` is ever leaked, logged, guessable, or observable (e.g., via monitoring, logs, error messages, or a malicious/compromised bridge partially exposing it), any unauthenticated network client can complete or corrupt that specific job run.

### Impact Explanation
Pipeline runs driven from resumed async bridge tasks can feed values used in on-chain writes (e.g., price feeds, OCR observations, or other downstream transactions). Anonymous injection of an attacker-chosen `value`/`error` into a specific, targeted run — as long as its `runID` is known — allows request impersonation of the legitimate async responder and can corrupt job outputs or force premature/incorrect completion of a run, i.e., unauthorized job run manipulation with potential downstream fund-movement impact, matching the "unauthorized job run" and "request impersonation" categories called out in the validation criteria.

### Likelihood Explanation
Exploitation requires knowledge of the specific `runID` (task UUID), which is not itself a widely broadcast secret. This bounds likelihood, but the design pattern is structurally identical to the reported bug class: it substitutes "does this ID belong to a registered/expected entity" for "is the caller cryptographically proven to be that entity." Any leak of the UUID (via bridge-side logs, error responses, browser history, proxies, or a compromised/careless bridge) is sufficient for exploitation, and the audit event is explicitly named `UnauthedRunResumed`, indicating the project itself flags this route as deliberately unauthenticated and worth auditing.

### Recommendation
Bind the resume capability to a verifiable secret rather than only the run/task UUID — e.g., include an HMAC-signed token or per-run secret in the `responseURL` given to the bridge, and validate it in `Resume` before applying the caller-supplied result, analogous to how `AuthenticateExternalInitiator` validates access key/secret pairs elsewhere in the codebase (`core/web/auth/auth.go`).

### Proof of Concept
1. Create a job with an async bridge task; the node dispatches a request to the bridge including a `responseURL` of the form `http://<node>/v2/resume/<runID>`.
2. An attacker who obtains or guesses `<runID>` (e.g., via a leaky bridge, proxy log, or shared infrastructure) sends:
   ```
   PATCH /v2/resume/<runID>
   Content-Type: application/json

   {"data": "<attacker-controlled value>"}
   ```
3. Because `/v2/resume/:runID` is in the `unauthedv2` group [1](#0-0) , this request requires no credentials.
4. `Resume` decodes the body and calls `App.ResumeJobV2(ctx, taskID, result)` [4](#0-3) , injecting the attacker's value into the pipeline run and resuming it, exactly as if the legitimate bridge had responded — without any verification that the request originated from the actual bridge/adapter tied to that run.

### Citations

**File:** core/web/router.go (L238-243)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)
```

**File:** core/web/pipeline_runs_controller.go (L134-160)
```go
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
