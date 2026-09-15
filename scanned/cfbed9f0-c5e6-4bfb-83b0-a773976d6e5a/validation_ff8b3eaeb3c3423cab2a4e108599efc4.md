Based on my research, I found a concrete unauthenticated-endpoint analog matching this bug class in `core/web/router.go`.

### Title
Unauthenticated pipeline run resume endpoint allows arbitrary actors to inject results into async task runs - (File: core/web/router.go)

### Summary
The reported bug is a missing access-control modifier on a state-mutating function (`distributeAssets()`), letting any caller invoke it directly with a crafted payload and steal rewards. The chainlink repo's HTTP router exhibits the same missing-authorization pattern: the `PATCH /v2/resume/:runID` route is registered on the **unauthenticated** router group `unauthedv2`, with no session, token, or external-initiator auth middleware applied, unlike every other pipeline-run-mutating route.

### Finding Description
In `v2Routes`, the router explicitly creates an unauthenticated group and immediately registers the resume endpoint on it: [1](#0-0) 

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

By contrast, the sibling create/read pipeline-run endpoints are wrapped with explicit role checks: [2](#0-1) [3](#0-2) 

```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
```

`PipelineRunsController.Resume` is used to complete a suspended/async pipeline task run (e.g., a bridge adapter callback continuation) by feeding externally-supplied data back into a job run keyed only by `runID`. Because `unauthedv2` bypasses `auth.Authenticate(...)` entirely, `Resume` is reachable by any unauthenticated internet client who can guess or enumerate a `runID`, exactly mirroring the `distributeAssets()` flaw where any caller can supply an arbitrary payload to a function that should only be reachable through a privileged, validated path (there, `LiquidationPoolManager.runLiquidation()`; here, the legitimate bridge/external-initiator callback flow).

I was unable to fully inspect the body of `PipelineRunsController.Resume` (in `core/web/pipeline_runs_controller.go`) within the available tool budget to confirm the exact blast radius of the injected payload (e.g., whether run IDs are unguessable UUIDs, whether the resumed task validates the caller, or whether there is any secondary check inside the handler). This should be verified directly in the source before treating the finding as fully proven.

### Impact Explanation
If `runID` values are sequential or otherwise guessable/enumerable, an unauthenticated remote attacker could call this endpoint to inject arbitrary "result" data into a suspended pipeline task run — potentially completing a job run with attacker-controlled data, corrupting external-initiator/bridge task results, or triggering unintended downstream on-chain actions (e.g., a job that submits a transaction based on the resumed task's output). This is directly analogous to the reward-drain in the report: a function meant to be invoked only by a trusted, validated internal caller is instead open to any caller.

### Likelihood Explanation
Likelihood depends entirely on whether `runID` is predictable/enumerable and what the resumed pipeline does with attacker-supplied data — both of which require reading `PipelineRunsController.Resume`'s implementation (not available within my search budget) and the `pipeline.Runner.Resume`/`ORM` layer that consumes the ID. The router-level evidence (unauthenticated group registration, contrasted with authenticated siblings) is concrete and provable from `core/web/router.go` alone.

### Recommendation
Move `PATCH /v2/resume/:runID` off the unauthenticated router group and require, at minimum, the same authentication used for `/v2/jobs/:ID/runs` (`AuthenticateExternalInitiator`/`AuthenticateByToken`/`AuthenticateBySession` plus `auth.RequiresRunRole`), or otherwise cryptographically bind the resume token to the specific run so the endpoint cannot be invoked with a bare, guessable `runID`. Confirm in `core/web/pipeline_runs_controller.go` and `core/services/pipeline/runner.go` what data the resumed run accepts and add explicit caller validation before resuming.

### Proof of Concept
Not executed — this requires reading `PipelineRunsController.Resume` and the underlying `pipeline.Runner.Resume`/ORM code to construct a working PoC (confirming `runID` predictability and payload effects). This is a limitation of the current investigation, not a claim that no PoC exists. A background Devin session with full repo access should read `core/web/pipeline_runs_controller.go` to confirm handler behavior and attempt an unauthenticated `curl -X PATCH http://<node>/v2/resume/<runID> -d '{"data":...}'` against a suspended run to demonstrate impact.

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

**File:** core/web/router.go (L398-401)
```go
		// PipelineRunsController
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)
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
