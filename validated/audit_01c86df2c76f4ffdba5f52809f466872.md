### Title
Unauthenticated Health/Readiness Endpoints Leak Internal Error Details - (File: core/web/health_controller.go)

### Summary
The `/health`, `/health.txt`, and `/readyz?full=true` endpoints are registered without any authentication middleware, and `Health`/`Readyz` return the raw error text of every failing internal health check to any caller. This is directly analogous to CVE-2014-5209 (NTP mode 6/7 `GET_RESTRICT`), where an unprivileged/unauthenticated actor can send a simple request/parameter and receive internal system-state information not intended for public disclosure.

### Finding Description
`healthRoutes` registers these handlers on the `api` route group, which only has rate-limiting and session middleware — not `auth.Authenticate`: [1](#0-0) 

Compare this to `debugRoutes` and the `DELETE /sessions` route, which explicitly wrap their handlers in `auth.Authenticate(...)`: [2](#0-1) [3](#0-2) 

`HealthController.Readyz` returns per-check error strings (`output = err.Error()`) when the caller passes `?full=true`, with no authentication check: [4](#0-3) 

`HealthController.Health` unconditionally returns the failing checks' error text (`output = err.Error()`) for every request, again without any authentication gate: [5](#0-4) 

The codebase itself acknowledges this class of risk: `PublicReadyz` was added specifically to avoid "leaking internal service state on publicly reachable endpoints," explicitly contrasting itself with `Readyz`: [6](#0-5) 

That mitigation, however, only applies to the new `PublicReadyz` route — the original `Readyz` (with `?full=true`) and `Health`/`Health.txt` endpoints remain reachable without authentication and still leak check output: [7](#0-6) 

The existing test suite confirms these endpoints are reachable via a plain unauthenticated client (`app.NewHTTPClient(nil)`), only validating status codes, not confirming any auth requirement: [8](#0-7) 

The `Checker` interface returns raw `error` values keyed by internal component/service name (e.g. DB connectivity, dependent service names, subsystem identifiers), which are surfaced verbatim to the client: [9](#0-8) 

### Impact Explanation
An unauthenticated network client hitting the node's HTTP API can enumerate internal subsystem/service names and their exact error messages (e.g. database connection failures, dependency host/port info embedded in error strings, subsystem naming conventions). While this does not directly move funds or bypass job execution, it is an information-disclosure vulnerability that reveals internal architecture/state to an unprivileged actor — the same bug class as the reported NTP CVE (unauthenticated disclosure of internal state via a control/query parameter). This can materially aid reconnaissance for further attacks (e.g., targeting a specific failing dependency, learning internal hostnames/ports from error text).

### Likelihood Explanation
High: these routes are mounted on the standard node API surface with only rate limiting, no authentication is required, and `?full=true` is a trivial, undocumented-but-discoverable query parameter. Any client capable of reaching the Chainlink node's HTTP port (which is often exposed for operational tooling) can trigger this.

### Recommendation
- Require authentication (or restrict to a private-only listener) for `Readyz` when `?full=true` is requested, and for `Health`/`Health.txt`, mirroring the approach already taken for `PublicReadyz`.
- Alternatively, strip error message content from the public/unauthenticated variants and only expose pass/fail booleans, keeping detailed diagnostics behind `auth.Authenticate`.
- Audit all `Checker`-backed error messages to ensure they never embed secrets or sensitive connection details, as defense in depth.

### Proof of Concept
1. Start a Chainlink node with default configuration and no auth headers.
2. Force a health check to fail (e.g., break DB connectivity or any registered `HealthReporter`).
3. Send `GET /health` or `GET /readyz?full=true` without any session cookie or API key.
4. Observe the response includes `Output` fields with the raw internal error text for each failing check, as returned by `checker.IsReady()`/`checker.IsHealthy()`, confirming unauthenticated disclosure of internal state — analogous to the NTP mode 6/7 `GET_RESTRICT` disclosure.

### Citations

**File:** core/web/router.go (L77-92)
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

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}
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

**File:** core/web/router.go (L220-228)
```go
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

**File:** core/web/health_controller.go (L83-116)
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
```

**File:** core/web/health_controller_test.go (L23-59)
```go
func TestHealthController_Readyz(t *testing.T) {
	t.Parallel()
	var tt = []struct {
		name   string
		ready  bool
		status int
	}{
		{
			name:   "not ready",
			ready:  false,
			status: http.StatusServiceUnavailable,
		},
		{
			name:   "ready",
			ready:  true,
			status: http.StatusOK,
		},
	}
	for _, tc := range tt {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			app := cltest.NewApplicationWithKey(t)
			healthChecker := new(mocks.Checker)
			healthChecker.On("Start").Return(nil).Once()
			healthChecker.On("IsReady").Return(tc.ready, nil).Once()
			healthChecker.On("Close").Return(nil).Once()

			app.HealthChecker = healthChecker
			require.NoError(t, app.Start(t.Context()))

			client := app.NewHTTPClient(nil)
			resp, cleanup := client.Get("/readyz")
			t.Cleanup(cleanup)
			assert.Equal(t, tc.status, resp.StatusCode)
		})
	}
}
```

**File:** core/services/health.go (L17-32)
```go
// Checker provides a service which can be probed for system health.
type Checker interface {
	// Register a service for health checks.
	Register(service services.HealthReporter) error
	// Unregister a service.
	Unregister(name string) error
	// IsReady returns the current readiness of the system.
	// A system is considered ready if all checks are passing (no errors)
	IsReady() (ready bool, errors map[string]error)
	// IsHealthy returns the current health of the system.
	// A system is considered healthy if all checks are passing (no errors)
	IsHealthy() (healthy bool, errors map[string]error)

	Start() error
	Close() error
}
```
