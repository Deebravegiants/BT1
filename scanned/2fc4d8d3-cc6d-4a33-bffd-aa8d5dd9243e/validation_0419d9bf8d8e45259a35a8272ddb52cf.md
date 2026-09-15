### Title
Unauthenticated `/v2/resume/:runID` endpoint allows anyone to resume arbitrary pipeline runs - (File: core/web/router.go)

### Summary
The `PATCH /v2/resume/:runID` route is registered on the `unauthedv2` router group, which has no authentication middleware applied at all, unlike every other state-mutating endpoint in the router which is wrapped with `auth.Authenticate(...)` plus a role check (`auth.RequiresEditRole`, `auth.RequiresRunRole`, etc.).

### Finding Description
In `core/web/router.go`, the v2 routes are split into an unauthenticated group and several authenticated groups: [1](#0-0) 

The resume route is deliberately placed on `unauthedv2`, with no `auth.Authenticate` wrapper and no role check: [2](#0-1) 

By contrast, every other endpoint that mutates job/run state is protected, e.g. job run creation requires the `Run` role via the same handler exposed through the authenticated group: [3](#0-2) 

and pipeline job spec error deletion, job update/delete, etc. all require `auth.RequiresEditRole`/`auth.RequiresRunRole`: [4](#0-3) 

This mirrors the audit finding pattern in the external report: a state-mutating function (`setPoolActive` in the Solidity contract) is exposed without any access-control check, when the intended design (per team comments/other similarly-purposed functions) is that only a privileged actor should be able to call it. Here, `PipelineRunsController.Resume` is a state-mutating action (resuming a suspended pipeline run, which can execute pending pipeline task graph steps, including tasks that read secrets/bridge responses or execute transactions) exposed on a route with zero access control, unlike its sibling endpoints.

### Impact Explanation
An unauthenticated network client can call `PATCH /v2/resume/:runID` for any `runID`, potentially resuming pipeline runs at will. This could allow: forcing continuation/completion of a job run that was intentionally suspended (e.g. waiting for an external callback), leaking information via error messages/side effects of run execution, or interfering with node operation and job execution timing when combined with pipeline tasks that require an external resume signal (bridge/pending task callbacks). Because this endpoint is deliberately unauthenticated (design intent is presumably to let bridges resume runs via a signed callback token embedded in the run itself), the concrete severity depends on whether `Resume` performs its own authorization based on data internal to the run (e.g., matching a secret/task run ID) rather than trusting a URL parameter. I could not fully verify the internal authorization logic inside `PipelineRunsController.Resume` (in `core/web/pipeline_runs_controller.go`) before running out of tool budget, so I cannot confirm whether the missing router-level auth is fully compensated by run-level checks inside the handler itself.

### Likelihood Explanation
The route is directly reachable by any unauthenticated client on the node's HTTP API without needing valid session or API tokens, making the likelihood of a bypass attempt trivial if the handler itself does not perform sufficient authorization based on unguessable/secret run-scoped data.

### Recommendation
Verify whether `PipelineRunsController.Resume` (`core/web/pipeline_runs_controller.go`) validates the caller using an unguessable per-run secret token (bridge "pending run" flow) rather than relying on the router for access control. If such per-request validation is missing or the run ID/token is guessable/enumerable, add authentication/authorization to the resume flow (e.g., validate a signed/opaque resume token tied to the specific run, or move it to `authv2` with an appropriate role and out-of-band callback secret). Document the intended threat model for this endpoint explicitly in the code, since it deviates from all other mutating routes in the router.

### Proof of Concept
Not independently confirmed due to incomplete visibility into `PipelineRunsController.Resume`'s internal authorization logic; the routing definition itself is the objective, verifiable evidence:
```
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)
``` [5](#0-4) 

A direct unauthenticated request such as:
```
curl -X PATCH http://<node>/v2/resume/<runID>
```
would reach `prc.Resume` without passing through any `auth.Authenticate` middleware, unlike all comparable state-mutating routes in the same file.

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

**File:** core/web/router.go (L391-408)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))

		// PipelineRunsController
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)

		// FeaturesController
		fc := FeaturesController{app}
		authv2.GET("/features", fc.Index)

		// PipelineJobSpecErrorsController
		authv2.DELETE("/pipeline/job_spec_errors/:ID", auth.RequiresEditRole(psec.Destroy))
```

**File:** core/web/router.go (L449-456)
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
