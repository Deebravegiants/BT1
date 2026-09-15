### Title
Unauthenticated bypass of role-based resume authorization on pipeline run resumption endpoint - (`core/web/pipeline_runs_controller.go`)

### Summary
`PipelineRunsController.Resume` is mounted on an unauthenticated route group in `core/web/router.go`, allowing any unauthenticated network client to resume a suspended pipeline run (e.g., completing a bridge/HTTP task callback) without any session, API token, or role check, in contrast to every other job-run mutating endpoint (`Create`, `Index`, `Show`) which require session/token authentication and at least the `run` role.

### Finding Description
The route `PATCH /v2/resume/:runID` is explicitly registered in the *unauthenticated* router group before the authenticated `authv2` group is constructed: [1](#0-0) 

```
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)

authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
	auth.AuthenticateByToken,
	auth.AuthenticateBySession,
))
```

This means `PipelineRunsController.Resume` never passes through `auth.Authenticate`, `auth.RequiresRunRole`, `auth.RequiresEditRole`, or `auth.RequiresAdminRole` — all of which are enforced on the sibling job-run-related endpoints such as `POST /v2/jobs/:ID/runs` (`auth.RequiresRunRole`) per `core/web/router.go`, and confirmed by the RBAC test map entry `{"POST", "/v2/jobs/MOCK/runs", false, true, true}` in `core/web/auth/auth_test.go`. [2](#0-1) 

The handler itself does not perform any additional authorization, token-secret, or ownership validation of the caller against the `runID` — it only validates that `runID` parses as a UUID, decodes the JSON body into a `pipeline.ResumeRequest`, and calls `prc.App.ResumeJobV2(ctx, taskID, result)` directly. The only nod to the unauthenticated nature of this call is the audit log entry `audit.UnauthedRunResumed`, indicating this gap was a deliberate design tradeoff for external callback flows (e.g., bridge adapters posting resume results), rather than an oversight caught by RBAC tests. Nonetheless, the endpoint accepts any `runID` UUID and any resume payload from an anonymous caller, with the only "secret" being the run's UUID itself, which is not treated as a high-entropy authentication credential anywhere else in the authorization model (unlike API access-key/secret pairs used elsewhere).

This mirrors the CVE-2019-6995 bug class: an internet-facing endpoint performing a state-changing action (resuming/completing a job run, analogous to commenting) is reachable from an unprivileged/unauthenticated context because the route is not wrapped by the intended access-control middleware that gates equivalent actions elsewhere in the same subsystem.

### Impact Explanation
An unauthenticated network client that can guess or observe a pending run's UUID (e.g., leaked in logs, timing side channels, or enumerable if UUID generation/exposure is weak) can inject arbitrary resume results into a suspended pipeline task, forcing task completion with attacker-controlled data. Because `ResumeJobV2` drives the pipeline execution engine, this can corrupt job outputs, prematurely complete/terminate a run, or feed falsified data into downstream on-chain-facing tasks — a data-integrity and process-integrity impact within a subsystem that ultimately can influence job execution and reported values.

### Likelihood Explanation
Exploitability is gated entirely by whether an external, unprivileged actor can obtain a valid pending `runID` (UUID) for a resumable task. If UUIDs are unpredictable and never disclosed to untrusted parties, exploitation likelihood is low; however, because no additional secret or role check exists at this endpoint (unlike bridge/EI authentication elsewhere), the security boundary here relies solely on UUID secrecy, which is a materially weaker control than the role-based/token-based access-control model used for every comparable job-run mutation endpoint in the same controller.

### Recommendation
Require the resuming caller to authenticate (e.g., via bridge/external-initiator token validated against the specific task/run, similar to `auth.AuthenticateExternalInitiator`) or bind resumption to a per-run, high-entropy, single-use secret validated server-side, rather than relying on the `runID` UUID alone as an implicit bearer credential. Additionally, confirm whether this route is intentionally scoped for a specific internal caller (e.g., only reachable from local task callbacks) and, if so, restrict it at the network/ingress layer, not merely via UUID obscurity.

### Proof of Concept
Given a pending pipeline run with a known/observed `runID` (UUID), an unauthenticated client can execute:
```
curl -X PATCH https://<node>/v2/resume/<runID> \
  -H "Content-Type: application/json" \
  -d '{"value": "<attacker-controlled result>"}'
```
This request reaches `PipelineRunsController.Resume` without any `Authorization`/session cookie/API key headers because the route is registered on `unauthedv2` in `core/web/router.go`, bypassing the `auth.Authenticate` middleware chain and role checks (`RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`) enforced on all other job-run endpoints.

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
