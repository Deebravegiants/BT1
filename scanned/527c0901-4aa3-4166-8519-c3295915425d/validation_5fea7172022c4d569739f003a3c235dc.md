### Title
Unauthenticated health-check endpoints leak internal service/check names and error details - (File: core/web/health_controller.go)

### Summary
The `/health`, `/health.txt`, and `/readyz?full=true` routes are registered without any authentication middleware, yet `Readyz` and `Health` (unlike the hardened `PublicReadyz`) return per-check names and raw error output to any unauthenticated caller.

### Finding Description
`healthRoutes` mounts `/readyz`, `/public-readyz`, `/health`, and `/health.txt` directly on the base router group, which only has rate limiting and session middleware applied — no `auth.Authenticate(...)` wrapper is used, unlike every other informational route in `v2Routes`/`debugRoutes` (which require `auth.AuthenticateByToken`/`AuthenticateBySession`). [1](#0-0) 

`PublicReadyz` was explicitly hardened with a comment stating it "never returns per-check details regardless of query parameters, to avoid leaking internal service state on publicly reachable endpoints." [2](#0-1) 

However, `Readyz` (mounted at `/readyz`, also unauthenticated) still returns per-check `Name` and `Output` (which includes `err.Error()`) whenever the caller supplies `?full=true`: [3](#0-2) 

Similarly, `Health` (mounted at `/health` and `/health.txt`, unauthenticated) unconditionally returns the full list of check names and error outputs in JSON, HTML, or plaintext form to any caller, with no session/token check at all: [4](#0-3) 

This mirrors the OpenProject bug class: an endpoint deliberately left public for infrastructure/monitoring purposes (crawlers/robots.txt in OpenProject; k8s load-balancer readiness checks here) inadvertently discloses internal state that the rest of the authenticated surface is designed to protect — regardless of whatever authentication policy an operator believes is enforced across the node's API.

### Impact Explanation
An unauthenticated network client can enumerate internal service/check names (e.g., subsystem names, chain/relayer identifiers) and raw error strings from `IsHealthy`/`IsReady`, which may include details about failing subsystems, configuration issues, or connectivity problems. This is an information-disclosure issue rather than an authentication or fund-movement bypass; the leaked data could aid reconnaissance for further attacks (e.g., identifying misconfigured/unhealthy components to target) but does not by itself grant access to keys, sessions, or job execution.

### Likelihood Explanation
High likelihood of reachability: `/health`, `/health.txt`, and `/readyz` are always mounted unauthenticated by design (needed for load balancers/k8s probes) and require no special network position — any client that can reach the node's HTTP API can query them, including `?full=true` on `/readyz`.

### Recommendation
Apply the same restriction implemented for `PublicReadyz` to `Readyz` and `Health`/`health.txt`: never emit per-check names or `err.Error()` output to unauthenticated callers. Either (a) require authentication for the detailed (`full`/default) variants and keep only a boolean-status endpoint public, or (b) strip check names/output entirely from the public routes and only emit them behind `auth.Authenticate(...)`, consistent with how `debugRoutes` gates `/debug/vars`. [5](#0-4) 

### Proof of Concept
1. As an unauthenticated client, send `GET /health` (or `/health.txt`, or `/readyz?full=true`) to a running chainlink node.
2. Observe the JSON/plaintext/HTML response contains the full list of internal check names and, for any failing check, the raw error message — without any session cookie or API token, and even if the node's other API routes require authentication. [6](#0-5)

### Citations

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
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

**File:** core/web/health_controller_test.go (L61-110)
```go
func TestHealthController_PublicReadyz(t *testing.T) {
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
			healthChecker.On("IsReady").Return(tc.ready, nil)
			healthChecker.On("Close").Return(nil).Once()

			app.HealthChecker = healthChecker
			require.NoError(t, app.Start(t.Context()))

			client := app.NewHTTPClient(nil)

			// Base path returns status only, no body.
			resp, cleanup := client.Get("/public-readyz")
			t.Cleanup(cleanup)
			assert.Equal(t, tc.status, resp.StatusCode)
			body, err := io.ReadAll(resp.Body)
			require.NoError(t, err)
			assert.Empty(t, body)

			// ?full=true must NOT expose per-check details on this endpoint.
			respFull, cleanupFull := client.Get("/public-readyz?full=true")
			t.Cleanup(cleanupFull)
			assert.Equal(t, tc.status, respFull.StatusCode)
			bodyFull, err := io.ReadAll(respFull.Body)
			require.NoError(t, err)
			assert.Empty(t, bodyFull)
		})
	}
}
```
