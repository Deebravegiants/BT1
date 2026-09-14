### Title
Unauthenticated Disclosure of Internal System/Health Check Error Details via `/readyz` and `/health` Endpoints - ([File: core/web/health_controller.go])

### Summary
The Chainlink node's `/readyz`, `/health`, and `/health.txt` endpoints are registered without any authentication middleware, and (unlike the purpose-built `/public-readyz` endpoint) they return raw internal error strings from every registered service's health check to any unauthenticated caller.

### Finding Description
In `healthRoutes`, the `Readyz`, `Health`, and `health.txt` handlers are mounted directly on the shared `api` route group with no `auth.Authenticate(...)` wrapper, unlike `/debug` (`debugRoutes`) or `DELETE /sessions` which explicitly require a session. [1](#0-0) 

`HealthController.Readyz` returns detailed per-check status when the `full` query parameter is present, including the raw `err.Error()` string for each failing internal component: [2](#0-1) 

`HealthController.Health` similarly returns per-check `err.Error()` output by default (no query param gating needed) and additionally supports HTML/plaintext rendering of the same data: [3](#0-2) 

Notably, `PublicReadyz` was specifically written with a comment acknowledging this exact risk — it deliberately strips all details "to avoid leaking internal service state on publicly reachable endpoints" — but `Readyz` and `Health` do not have this protection and are reachable on the same unauthenticated route group: [4](#0-3) 

Health check `Output` fields are populated straight from internal component errors (e.g., database, RPC/chain client, keystore, relayer errors), which can include internal hostnames, connection strings, file paths, or other implementation details depending on what the underlying `services.HealthReporter` implementations return as errors.

### Impact Explanation
An unauthenticated, unprivileged network client can call `GET /readyz?full=true`, `GET /health`, or `GET /health.txt` and receive verbatim error messages from every internal service/dependency check on the node. This is directly analogous to CVE-2024-52367 (disclosure of sensitive system information to an unauthorized actor), and can help an attacker fingerprint internal infrastructure (DB/RPC endpoints, internal service names, error conditions) to plan further attacks, even though it does not directly move funds or bypass authentication for privileged actions.

### Likelihood Explanation
High likelihood of reachability: no authentication or session is required, the routes are mounted on the default publicly exposed engine (`api` group, same group as `/sessions` login), and the behavior is triggered by a simple unauthenticated GET request with no rate-limiting distinct from other unauthenticated endpoints.

### Recommendation
Apply the same detail-suppression pattern used in `PublicReadyz` to `Readyz` and `Health`/`health.txt`, or require authentication (`auth.Authenticate`) for the detailed variants, ensuring only a minimal status code is returned to unauthenticated callers and detailed per-check error output is gated behind a session/API-token check.

### Proof of Concept
```
curl -s "http://<node-host>:6688/readyz?full=true"
curl -s "http://<node-host>:6688/health"
```
No `Cookie`/`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers are required; the response body contains a JSON (or HTML/plaintext) list of check names and raw error `Output` strings for any failing internal component.

### Citations

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
