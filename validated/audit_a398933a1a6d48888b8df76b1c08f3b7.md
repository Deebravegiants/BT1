Found a genuinely unauthenticated endpoint with an analogous root cause: `unauthedv2.PATCH("/resume/:runID", prc.Resume)` at [1](#0-0)  — this is registered on `unauthedv2` (no auth middleware at all), unlike every other pipeline-run/job route which requires `auth.RequiresRunRole` or session/token auth, e.g. `userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))` [2](#0-1) .

### Title
Unauthenticated Pipeline Run Resume Endpoint Allows Arbitrary Run-State Manipulation - (File: core/web/router.go, core/web/pipeline_runs_controller.go)

### Summary
The `/v2/resume/:runID` route is mounted on the `unauthedv2` route group with zero authentication middleware, in contrast to every other job/pipeline-run mutation endpoint in the router which is gated behind session/token auth and a role check (`RequiresRunRole`, `RequiresEditRole`, etc.). This mirrors the AVideo `on_publish_done.php` bug class: a callback-style endpoint intended to be invoked by an internal/trusted caller (in this case, presumably async task/bridge callbacks resuming a paused pipeline task) is exposed on the public HTTP surface without any authentication or authorization check [1](#0-0) .

### Finding Description
`v2Routes` explicitly separates route groups by trust level: `unauthedv2 := r.Group("/v2")` has no auth middleware attached, while `authv2` requires `auth.AuthenticateByToken`/`auth.AuthenticateBySession`, and `userOrEI` requires either a valid external-initiator token or a user session [3](#0-2) . Only `PATCH /resume/:runID` is registered on `unauthedv2` [4](#0-3) , calling `PipelineRunsController.Resume`. This handler is not visible in the indexed snippets (only `Show` and `Create` were retrieved from `core/web/pipeline_runs_controller.go`), so I could not directly confirm what state changes `Resume` performs on a `runID`. Given the naming and the surrounding `pipeline` package's task-resumption semantics (`core/services/pipeline/scheduler.go` handles pending/async task completion), this endpoint's purpose is very likely to let an async task (e.g., a bridge adapter callback) report task completion and unblock a paused pipeline run.

### Impact Explanation
If `Resume` accepts attacker-controlled `runID` and body content to mark a task/run as resumed/completed with arbitrary data, an unauthenticated attacker could:
- Enumerate or guess `runID` values and forcibly resume/terminate pending pipeline runs (denial-of-service against jobs waiting on async bridge results), directly analogous to the AVideo unauthenticated stream-termination bug.
- Potentially inject falsified task results into a running pipeline if `Resume` writes attacker-supplied data into the task result before continuing the DAG, which could corrupt job outputs feeding on-chain reports.

I was not able to confirm the exact write/side-effect logic of `Resume` from the retrieved snippets, so the severity of data injection vs. mere run disruption is uncertain without reading `pipeline_runs_controller.go`'s `Resume` function body directly.

### Likelihood Explanation
High reachability: the route requires no authentication of any kind and is reachable from any unprivileged network client that can reach the node's HTTP API, same as `stats.json.php`/`on_publish_done.php` in the original report. The only barrier is guessing/enumerating a valid `runID`, which for a sequential integer primary key is often trivially brute-forceable.

### Recommendation
Restrict `/v2/resume/:runID` to legitimate internal callers only: require the same token/HMAC-based authentication used for bridge/external-adapter callbacks, or move it behind `authv2`/`userOrEI` with an explicit `RequiresRunRole` check, mirroring how `/v2/jobs/:ID/runs` is protected. If it must remain unauthenticated for legacy async-bridge compatibility, add a shared-secret validation (e.g., matching a resume token generated per-run) so only the task that was actually paused can resume it, rather than being wide open to any caller with a runID [4](#0-3) .

### Proof of Concept
1. Identify an active/paused pipeline run ID (e.g., sequential integers, or observed via other unauthenticated/lower-trust endpoints).
2. Send an unauthenticated request:
```
curl -X PATCH "https://your-node.example/v2/resume/<runID>" -d '{"..."}'
```
3. Because this route sits on `unauthedv2` with no middleware, the request reaches `PipelineRunsController.Resume` without any credential check, unlike all sibling run-mutation endpoints, potentially altering or terminating the paused pipeline run's state.

Note: due to index limits I could not retrieve the full body of `PipelineRunsController.Resume` to confirm exactly what mutation occurs on `runID`; a Devin session with full repo access should inspect `core/web/pipeline_runs_controller.go`'s `Resume` function to verify whether it performs a privileged state change (write) versus a benign no-op, before treating this as fully confirmed.

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
