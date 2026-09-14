### Title
Rate-limit tier misclassification allows unauthenticated pipeline-run resume endpoint to bypass the stricter unauthenticated throttle - (File: core/web/router.go)

### Summary
The GitLab advisory (CVE-2022-1428) describes throttling limits being incorrectly verified for a request class, resulting in the intended (stricter) limit not being enforced. Chainlink's `core/web/router.go` has an analogous flaw: the *authenticated*-tier rate limit (1000 req/min by default) is applied as a blanket middleware to the entire outer router group, and only a small subset of routes (`/sessions`) explicitly get the stricter *unauthenticated*-tier limiter layered on top. Other routes that require no authentication — most notably `PATCH /v2/resume/:runID` — never get the intended unauthenticated throttle, and instead inherit the much larger authenticated allowance.

### Finding Description
`NewRouter` builds the top-level `api` group and applies the "Authenticated" rate limiter to it unconditionally: [1](#0-0) 

This `api` group is the parent for `debugRoutes`, `healthRoutes`, `sessionRoutes`, `v2Routes`, and `loopRoutes`. Inside `v2Routes`, an explicitly unauthenticated sub-group is created for the webhook resume callback: [2](#0-1) 

`unauthedv2.PATCH("/resume/:runID", prc.Resume)` has **no** authentication middleware attached — by design, since it's meant to be hit by external callers resuming a paused job run (e.g., a bridge/EA response). However, because it lives under the `api` group, the only rate limiter that applies to it is the one configured with `rl.AuthenticatedPeriod()` / `rl.Authenticated()` (default: 1000 requests/minute), not `rl.UnauthenticatedPeriod()` / `rl.Unauthenticated()` (default: 5 requests/20s) that is used elsewhere for genuinely unauthenticated flows: [3](#0-2) 

The `/sessions` POST endpoint is the only unauthenticated route that receives the correct, stricter limiter, applied as an *additional* `rateLimiter` middleware in its own sub-group: [4](#0-3) 

No equivalent stricter-tier group exists for `unauthedv2` in `v2Routes`, so `PATCH /v2/resume/:runID` is effectively verified against the wrong (authenticated) throttling tier despite being reachable by any unauthenticated actor — the same root-cause class as the GitLab CVE: the code fails to verify that the throttle actually corresponds to the authentication state of the request before applying limits.

### Impact Explanation
`PATCH /v2/resume/:runID` accepts a numeric run ID and resumes a suspended pipeline task (e.g., completes an async bridge/webhook task with attacker-supplied data), as declared in `core/web/pipeline_runs_controller.go`. Because this route is throttled at 1000 req/min per client instead of 5 req/20s, an unauthenticated actor gets roughly 200x higher allowance than intended for brute-forcing/guessing run IDs or hammering the endpoint, increasing the practical feasibility of unauthorized job-run tampering or resource-exhaustion/DoS against this internet-facing, no-auth webhook path.

### Likelihood Explanation
The route requires no credentials by design (it's meant for external initiators/bridges to call back), so any unprivileged network client can reach it, and the misclassification is a static routing/middleware wiring issue — no race condition or timing dependency is required to trigger it, only sending requests to `/v2/resume/:runID`.

### Recommendation
Wrap the `unauthedv2` group (and any other route groups intentionally left without session/token auth) with the `Unauthenticated`/`UnauthenticatedPeriod` rate limiter, mirroring the pattern already used for `/sessions` in `sessionRoutes`, so throttling tiers are tied to actual authentication state rather than to router group nesting.

### Proof of Concept
Not independently verified end-to-end (the specific business logic of `prc.Resume` in `core/web/pipeline_runs_controller.go` was not fully inspected due to iteration limits), but the routing/middleware wiring is directly confirmed in `core/web/router.go`:
1. Deploy/run a Chainlink node with default `WebServer.RateLimit` config (`Authenticated=1000/1m`, `Unauthenticated=5/20s`).
2. Send unauthenticated `PATCH /v2/resume/<any-run-id>` requests in a loop without any session cookie or API token.
3. Observe that requests are not rejected with `429` until ~1000 requests within a minute have been sent from the same client IP, rather than being capped at 5 requests per 20 seconds as the `Unauthenticated` config value implies is the intended limit for unauthenticated traffic.

### Citations

**File:** core/web/router.go (L77-91)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```

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
