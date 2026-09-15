### Title
Unauthenticated pipeline run resume endpoint allows anyone to inject arbitrary task results into any node - (File: core/web/router.go)

### Summary
The External Report describes `sweepNative()` missing an `onlyOwner` modifier, letting any unprivileged caller trigger a privileged state-mutating action (draining native balance to a fixed recipient). The direct chainlink analog is the `PATCH /v2/resume/:runID` route, which is deliberately mounted **without any authentication middleware** and lets any network caller supply an arbitrary result/error payload that is fed directly into the node's pipeline runner for the given `taskID`.

### Finding Description
In `core/web/router.go`, the `v2Routes` function creates an unauthenticated router group and registers the resume handler on it, in contrast to every other v2 route which is wrapped in `auth.Authenticate(...)`: [1](#0-0) 

The handler, `PipelineRunsController.Resume`, takes the `runID` path parameter as a raw UUID, decodes an attacker-supplied JSON body into a `pipeline.ResumeRequest`, converts it into a `pipeline.Result` and passes it straight to `App.ResumeJobV2` with **no caller identity/role check of any kind**: [2](#0-1) 

`ResumeJobV2` forwards the caller-controlled `taskID` and `result.Value`/`result.Error` unchanged into the pipeline runner's `ResumeRun`: [3](#0-2) 

The only "authentication" for this endpoint is that `taskID` is a UUID that is supposed to be a secret bearer token generated per pending async task (e.g. for bridge/external-adapter callbacks). There is no additional authorization check, rate limiting, one-time-use enforcement visible at the HTTP layer, or scoping to the External Initiator that owns the run — the endpoint is registered on `unauthedv2` unconditionally, identical in spirit to `sweepNative()` lacking `onlyOwner`: a state-changing, resource-affecting action reachable by literally anyone, gated only by knowledge of an identifier value rather than by an actual authorization check.

The maintainers were clearly aware this is worth flagging — they log an explicit `audit.UnauthedRunResumed` event whenever it fires: [4](#0-3) [5](#0-4) 

This confirms the endpoint is intentionally unauthenticated by design (the `taskID` UUID is meant to function as the "capability token"), rather than an oversight — but the security guarantee rests entirely on the unguessability/secrecy of the UUID and on it never being logged, cached, or exposed anywhere. I was not able to fully verify from the indexed code whether `taskID` values are ever exposed in logs, error messages, metrics, or other side channels that would let an unprivileged actor discover a live `taskID` and hijack a pending resume before the legitimate callback does, nor whether resumption is idempotent/single-use at the datastore layer (which would bound the blast radius of a guessed or leaked ID).

### Impact Explanation
If a `taskID` is discoverable or brute-forceable by an unprivileged actor (e.g., via logs, error responses, monitoring exports, or via a compromised low-trust component), that actor can:
- Force-complete or force-fail arbitrary pending pipeline tasks with attacker-chosen values, corrupting job results.
- Race the legitimate external adapter/bridge callback to inject a poisoned value before the real result arrives, similarly to injecting falsified price/data into a job whose output can move funds (e.g., trigger an on-chain transaction task with attacker data).
This mirrors the Sweepable finding's impact category: an unprivileged caller performing a privileged, state/fund-affecting action due to a missing authorization gate, bounded here by the difficulty of learning a valid `taskID`.

### Likelihood Explanation
Likelihood is **low-to-medium** and gated by whether `taskID` values leak. The route being unauthenticated by design (confirmed via the dedicated audit event) suggests the Chainlink team has already assessed and accepted this as a known/audited pattern, which weighs against treating it as a fresh, high-confidence vulnerability. Without confirming a concrete leak path for `taskID`s in this index, I cannot elevate likelihood beyond speculative.

### Recommendation
- Verify no code path logs, returns, or otherwise exposes `taskID` values to lower-trust surfaces (HTTP responses to third parties, metrics labels, default-level logs).
- Consider requiring the resume endpoint to also validate a per-request secret/HMAC bound to the run (not just the UUID itself), and enforce single-use consumption at the DB layer with a check for prior completion before applying attacker-supplied results.
- If this is already enforced elsewhere (e.g., an existing `ErrAlreadyExists`/single-use guarantee in `ResumeRun`), document it in-code to make the security invariant explicit for future auditors, since as written the HTTP layer alone provides no defense-in-depth beyond UUID secrecy.

### Proof of Concept
1. Observe or otherwise learn a pending pipeline task's `taskID` (UUID) — e.g., through logs, metrics, or a leaked callback URL used by an external adapter/bridge.
2. Without any authentication headers/cookies, send:
   ```
   PATCH /v2/resume/<taskID>
   Content-Type: application/json

   {"value": "<attacker-controlled-value>"}
   ```
3. `PipelineRunsController.Resume` [6](#0-5)  accepts the request with zero auth checks and forwards the attacker's value into `App.ResumeJobV2` → `pipelineRunner.ResumeRun`, completing the task with attacker-controlled data instead of the legitimate external adapter/callback result.

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

**File:** core/services/chainlink/application.go (L1237-1243)
```go
func (app *ChainlinkApplication) ResumeJobV2(
	ctx context.Context,
	taskID uuid.UUID,
	result pipeline.Result,
) error {
	return app.pipelineRunner.ResumeRun(ctx, taskID, result.Value, result.Error)
}
```

**File:** core/logger/audit/audit_types.go (L93-93)
```go
	UnauthedRunResumed EventID = "UNAUTHED_RUN_RESUMED"
```
