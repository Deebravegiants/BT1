### Title
Unauthenticated `/health` and `/readyz?full=true` endpoints disclose internal service check names and error details - ([File: core/web/health_controller.go])

### Summary
The n8n-mcp advisory describes a health-check endpoint that leaks sensitive operational metadata without requiring authentication. Chainlink's own web router exposes an analogous pattern: `/health` and `/readyz` (with `?full=true`) are mounted without any authentication middleware and return per-service check names plus raw error strings to any network-reachable, unauthenticated caller.

### Finding Description
In `core/web/router.go`, `healthRoutes` is registered directly on the `api` route group with no auth wrapper, unlike `sessionRoutes`/`v2Routes`, which explicitly gate mutating/sensitive routes behind `auth.Authenticate(...)`: [1](#0-0) 

`HealthController.Health` and `HealthController.Readyz` both iterate over `checker.IsHealthy()`/`IsReady()` results and include the raw `err.Error()` string plus internal check names (e.g. `PipelineRunner.BridgeCache`, `Mercury.WSRPCPool.CacheSet`) in the response body: [2](#0-1) [3](#0-2) 

Notably, the codebase already contains a mitigation pattern for exactly this class of issue — `PublicReadyz` was added specifically "to avoid leaking internal service state on publicly reachable endpoints" and always returns a bodyless status code: [4](#0-3) 

However, `/health` and `/readyz?full=true` remain registered on the same unauthenticated path and still emit full per-check names/error text, meaning the disclosure the `PublicReadyz` comment warns about is still reachable via the sibling endpoints.

### Impact Explanation
Any unauthenticated actor with network access to the node's HTTP API can enumerate internal service/component names and read verbatim error strings (e.g., failure reasons from ORM, RPC pools, pipeline runner, bridge cache) via `GET /health` or `GET /readyz?full=true`. This is purely an information-disclosure primitive (CWE for exposure of sensitive information), analogous in class to the n8n-mcp health-check leak, though the specific content depends on what error text underlying health reporters produce — I could not fully confirm whether any registered `HealthReporter` ever surfaces genuinely sensitive values (credentials, connection strings) versus only generic failure descriptions, since the reporter implementations are spread across many packages and I did not exhaustively review each one's error message content.

### Likelihood Explanation
High reachability: no authentication, no rate limiting beyond the general `Authenticated`/rate-limiter middleware applied to the whole `api` group, and the route is always mounted whenever the web server runs.

### Recommendation
Require authentication on `/health` and `/readyz?full=true` (or restrict the `full`/detailed views to authenticated/admin callers), mirroring how `PublicReadyz` was carved out for public consumption, and audit `HealthReporter` implementations to ensure error messages never include secrets or internal connection details.

### Proof of Concept
An unauthenticated request to the node's web server, e.g.:
```
curl http://<node-host>:<port>/readyz?full=true
curl http://<node-host>:<port>/health
```
returns a JSON body listing internal check names/status/output without any credentials, as shown by the route wiring at `core/web/router.go:220-228` (no auth middleware) and the response construction in `core/web/health_controller.go:43-139`. [5](#0-4) [6](#0-5)

### Citations

**File:** core/web/router.go (L207-228)
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

func healthRoutes(app chainlink.Application, r *gin.RouterGroup) {
	hc := HealthController{app}
	r.GET("/readyz", hc.Readyz)
	r.GET("/public-readyz", hc.PublicReadyz)
	r.GET("/health", hc.Health)
	r.GET("/health.txt", func(context *gin.Context) {
		context.Request.Header.Set("Accept", gin.MIMEPlain)
	}, hc.Health)
}
```

**File:** core/web/health_controller.go (L27-37)
```go
// PublicReadyz is a minimal readiness endpoint intended for public load balancer health checks.
// Unlike Readyz, it never returns per-check details regardless of query parameters, to avoid
// leaking internal service state on publicly reachable endpoints.
func (hc *HealthController) PublicReadyz(c *gin.Context) {
	ready, _ := hc.App.GetHealthChecker().IsReady()
	if !ready {
		c.Status(http.StatusServiceUnavailable)
		return
	}
	c.Status(http.StatusOK)
}
```

**File:** core/web/health_controller.go (L43-81)
```go
func (hc *HealthController) Readyz(c *gin.Context) {
	status := http.StatusOK

	checker := hc.App.GetHealthChecker()

	ready, errors := checker.IsReady()

	if !ready {
		status = http.StatusServiceUnavailable
	}

	c.Status(status)

	if _, ok := c.GetQuery("full"); !ok {
		return
	}

	checks := make([]presenters.Check, 0, len(errors))

	for name, err := range errors {
		status := HealthStatusPassing
		var output string

		if err != nil {
			status = HealthStatusFailing
			output = err.Error()
		}

		checks = append(checks, presenters.Check{
			JAID:   presenters.NewJAID(name),
			Name:   name,
			Status: status,
			Output: output,
		})
	}

	// return a json description of all the checks
	jsonAPIResponse(c, checks, "checks")
}
```

**File:** core/web/health_controller.go (L83-139)
```go
func (hc *HealthController) Health(c *gin.Context) {
	_, failing := c.GetQuery("failing")

	status := http.StatusOK

	checker := hc.App.GetHealthChecker()

	healthy, errors := checker.IsHealthy()

	if !healthy {
		status = http.StatusMultiStatus
	}

	c.Status(status)

	checks := make([]presenters.Check, 0, len(errors))
	for name, err := range errors {
		status := HealthStatusPassing
		var output string

		if err != nil {
			status = HealthStatusFailing
			output = err.Error()
		} else if failing {
			continue // omit from returned data
		}

		checks = append(checks, presenters.Check{
			JAID:   presenters.NewJAID(name),
			Name:   name,
			Status: status,
			Output: output,
		})
	}

	switch c.NegotiateFormat(gin.MIMEJSON, gin.MIMEHTML, gin.MIMEPlain) {
	case gin.MIMEJSON:
		break // default

	case gin.MIMEHTML:
		if err := newCheckTree(checks).WriteHTMLTo(c.Writer); err != nil {
			hc.App.GetLogger().Errorw("Failed to write HTML health report", "err", err)
			c.AbortWithStatus(http.StatusInternalServerError)
		}
		return

	case gin.MIMEPlain:
		if err := writeTextTo(c.Writer, checks); err != nil {
			hc.App.GetLogger().Errorw("Failed to write plaintext health report", "err", err)
			c.AbortWithStatus(http.StatusInternalServerError)
		}
		return
	}

	slices.SortFunc(checks, presenters.CmpCheckName)
	jsonAPIResponseWithStatus(c, checks, "checks", status)
}
```
