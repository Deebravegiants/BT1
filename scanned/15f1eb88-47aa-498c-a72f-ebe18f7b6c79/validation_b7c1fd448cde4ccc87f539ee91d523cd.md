Based on the code retrieved, there is a genuinely unauthenticated, state-mutating route registered in the chainlink node's HTTP router that is structurally analogous to the `testFinalizeSettlement()` issue: a publicly reachable endpoint that lets any unauthenticated caller mutate pipeline-run state.

### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Unprivileged State Mutation - (File: core/web/router.go)

### Summary
The route `PATCH /v2/resume/:runID` is registered in a router group explicitly created without any authentication middleware, unlike virtually every other mutating endpoint in the node.

### Finding Description
`v2Routes` sets up an `unauthedv2` group with no `auth.Authenticate(...)` wrapper and binds `prc.Resume` to it: [1](#0-0) 

Compare this to every other mutating route in the same function, all of which are wrapped in `authv2` (guarded by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), or `userOrEI` (guarded by `auth.AuthenticateExternalInitiator`/token/session) and role checks like `auth.RequiresRunRole`: [2](#0-1) 

This mirrors the `HarTokenSale.testFinalizeSettlement()` bug class: a state-transition entrypoint (`Resume`, analogous to `_finalizeSettlement()`) that is reachable by anyone with no ownership/role/session check, allowing an unprivileged caller to force a resume/completion transition on a pipeline run resource it should not control.

### Impact Explanation
Any unauthenticated network client that can reach the node's HTTP API can call this endpoint with an arbitrary `runID` and attempt to resume/finalize pipeline task runs (used to unblock suspended tasks, e.g. bridge/external adapter async callbacks). This could let an attacker forge premature or malicious resume data for pending runs, corrupt or short-circuit the intended execution/finalization flow of jobs — functionally similar to forcing an unauthorized state finalization, without any owner/session check, exactly the class of bug described in the report (unauthorized caller forcing an irreversible/high-impact state transition).

### Likelihood Explanation
High. The route is unconditionally mounted on the public HTTP router with no authentication middleware at all — reachability requires nothing more than network access to the node's API port, the same "any address can call it" condition described in the original report.

### Recommendation
Require the `Resume` route to go through the standard authentication chain (bridge/external-initiator token auth, since resumes are normally driven by bridge/adapter callbacks) rather than being placed in the `unauthedv2` group, and validate that the caller is authorized to resume the specific `runID` (e.g., matching bridge/task ownership), analogous to removing/gating `testFinalizeSettlement()` in the original report.

### Proof of Concept
Not independently executable from the index alone (no runtime/browser access), but the vulnerable code path is directly demonstrated by the router wiring: [3](#0-2)  shows `unauthedv2.PATCH("/resume/:runID", prc.Resume)` with zero auth middleware, in contrast to all sibling mutating routes requiring `auth.Authenticate`.

**Note:** I was unable to retrieve the body of `PipelineRunsController.Resume` or `pipeline.Runner.Resume` due to a tool error on the final iteration, so I cannot confirm what internal checks (if any) exist inside the handler itself beyond the router-level gate. This should be verified directly in `core/web/pipeline_runs_controller.go` and `core/services/pipeline/runner.go` — if the confidence there is that `runID` alone is sufficient to identify/authorize the mutation (as is typical for bridge callback resume flows), the finding stands as high-severity; if additional secret/token validation exists inside the handler that isn't visible from the router, severity should be downgraded accordingly.

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

**File:** core/web/router.go (L449-457)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
}
```
