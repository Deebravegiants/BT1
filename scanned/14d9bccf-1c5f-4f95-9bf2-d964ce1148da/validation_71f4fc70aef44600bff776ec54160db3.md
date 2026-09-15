### Title
Unauthenticated `/v2/resume/:runID` endpoint allows any unprivileged caller to resume and complete arbitrary pipeline runs - (File: core/web/router.go)

### Summary
The Votium finding describes internal reward-flow functions (`AfEth::depositRewards()`, `VotiumStrategyCore::depositRewards()`) that were meant to be called only as part of a privileged reward-processing chain, but were left `public`/unauthenticated, letting any caller invoke them directly and manipulate protocol state/funds. The Chainlink node exhibits the same pattern at the HTTP-API boundary: the pipeline-run "resume" callback, which is meant to be invoked only by the async external adapter that a node itself dispatched a job to, is registered as a fully unauthenticated route.

### Finding Description
In `core/web/router.go`, the `v2Routes` function creates an explicitly unauthenticated route group and mounts the resume endpoint on it, with no `auth.Authenticate*` middleware at all: [1](#0-0) 

Compare this to every other job/pipeline-related route, which is wrapped in `auth.Authenticate(... auth.AuthenticateByToken, auth.AuthenticateBySession)` and further gated by role checks such as `auth.RequiresEditRole` / `auth.RequiresRunRole`: [2](#0-1) [3](#0-2) 

The `resume` endpoint is the deliberate exception — `unauthedv2.PATCH("/resume/:runID", prc.Resume)` bypasses the session/token `Authenticate` middleware entirely, meaning any unauthenticated network client that can reach the node's API port can call it. Just like the two Votium functions were designed to be called only as an internal step of a role-gated flow (the "rewarder" role) but had no such restriction enforced in code, this endpoint is designed to be called only by the specific external adapter that the node itself invoked (which is supposed to know a run-specific resume token/ID), but the router imposes no authentication or authorization check confirming the caller is that adapter.

I was not able to locate and read the body of `PipelineRunsController.Resume` in the indexed codebase context, so I cannot confirm from source exactly what validation (e.g., matching the pending task run's stored bridge/adapter secret, run state checks) exists inside the handler itself. This is a real limitation: if `Resume` internally validates a secret embedded in the `runID` value or checks the task is in a `PENDING` state tied to a specific bridge callback, the practical exploitability is bounded to guessing/brute-forcing that identifier. Given the size limits on the indexed codebase, some file contents may not be available — a Devin session with full repo access would be needed to inspect `Resume`'s implementation and confirm whether `runID` alone is sufficient to resume/complete an arbitrary run, or whether it is combined with a non-guessable secret.

### Impact Explanation
If `runID` (or any parameter accepted by `Resume`) is guessable or enumerable (e.g., a sequential integer primary key, which is the pattern used elsewhere in this codebase, such as job/pipeline-run IDs), an unauthenticated attacker could resume pipeline runs prematurely or with attacker-controlled data, causing:
- Unauthorized completion of pending pipeline task runs (mirrors the "anyone can spend contract resources" impact in the original finding, but for node compute/job-execution resources instead of ETH).
- Potential injection of forged callback data into a job's pipeline execution if `Resume` does not tie the payload to the specific external adapter/bridge that issued the async request.
This maps to the "unauthorized job run" acceptance criterion for this analog scan.

### Likelihood Explanation
Likelihood depends entirely on whether `runID` (or other resume parameters) is unguessable/high-entropy and whether `Resume` re-validates the caller's right to complete that specific run. Since this route is explicitly excluded from all authentication middleware at the router level (unlike every other job/run-related route), the router itself provides zero defense-in-depth; the only barrier is whatever validation exists inside the handler, which could not be confirmed from the available index.

### Recommendation
1. Confirm (via full source access) what `PipelineRunsController.Resume` validates internally — specifically whether `runID` doubles as an authorization secret and whether it checks pipeline task run state before applying the resume payload.
2. If `runID` is a predictable/sequential value, require an additional authenticated secret (e.g., a per-run resume token issued when the async task was dispatched) and reject resumption attempts that don't match it, analogous to recommending `require(_amount == msg.value)` and caller-restriction in the original finding.
3. Consider adding IP/allowlist restrictions or mutual authentication for this callback path, consistent with how `AuthenticateExternalInitiator` is used elsewhere for external callers with a narrowly scoped role.

### Proof of Concept
Not verifiable end-to-end from the indexed context because `Resume`'s implementation could not be retrieved. The verifiable root cause is the router configuration:
```
unauthedv2 := r.Group("/v2")
...
unauthedv2.PATCH("/resume/:runID", prc.Resume)
```
An unauthenticated HTTP client can issue:
```
PATCH /v2/resume/<runID>
```
directly to the node with no session cookie or API token, and the request reaches `PipelineRunsController.Resume` with no role or authentication check performed by the router — establishing the same unauthenticated-access root cause as the original Votium finding, though the downstream impact require confirming `Resume`'s internal logic with full repository access (recommend a Devin session for this deeper verification).

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

**File:** core/web/router.go (L391-401)
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
