### Title
Unauthenticated `/readyz` and `/health` endpoints leak internal service state to anonymous callers - (File: `core/web/health_controller.go`)

### Summary
The Chainlink node's HTTP API exposes `GET /readyz` and `GET /health` (plus `/health.txt`) without any authentication middleware. When queried with `?full` (for `/readyz`) or by default (for `/health`), these endpoints return a detailed JSON/HTML/plaintext breakdown of every internal health-check name and its associated error output. This mirrors the CVE-2017-7589 bug class: an unauthenticated/"anonymous" caller hitting an info-style endpoint and receiving a 200 response containing internal service details that should require privilege.

### Finding Description
`healthRoutes` registers these handlers directly on the base `api` router group with no `auth.Authenticate(...)` wrapper, unlike almost every other data-returning route in the router: [1](#0-0) 

```
debugRoutes(app, api)
healthRoutes(app, api)
sessionRoutes(app, api)
v2Routes(app, api)
loopRoutes(app, api)
``` [2](#0-1) 

The team clearly recognized that per-check detail is sensitive on a publicly reachable endpoint — that's precisely why `PublicReadyz` was created as a "minimal" variant that "never returns per-check details ... to avoid leaking internal service state on publicly reachable endpoints": [3](#0-2) 

However, the original `Readyz` handler (still mounted, unauthenticated, at `/readyz`) still honors the `?full` query parameter and returns the full list of check names and `err.Error()` output for every failing/passing check: [4](#0-3) 

Similarly, `Health` (mounted unauthenticated at `/health` and `/health.txt`) always returns every check name/status/output, and even supports content negotiation to render this as HTML or plaintext for any anonymous caller: [5](#0-4) 

The health-check subsystem in this codebase commonly wraps errors from database connectivity, RPC/EVM chain clients, subsystem readiness, etc. — the exact `err.Error()` string is echoed back verbatim in the `Output` field, so any internal detail embedded in an error message (connection strings, internal hostnames/IPs, chain RPC endpoints, stack-trace-like text) is disclosed to an unauthenticated requester exactly as in the referenced CVE (anonymous request → 200 → JSON blob containing internal network/service info).

### Impact Explanation
An unauthenticated network client can enumerate the node's internal health-check names and read raw error text for every failing subsystem. Depending on what error messages the various `HealthReporter` implementations produce (DB, RPC clients, keystores, mailboxes, etc.), this can disclose internal hostnames, IP addresses, connection details, or other operational information useful for reconnaissance/targeting, consistent with the "IP address string disclosure to anonymous user" pattern in the CVE.

### Likelihood Explanation
High likelihood of reachability: `/readyz?full` and `/health` require no session, no API token, and no external-initiator credential — only network reachability to the node's HTTP port, which for many deployments is intentionally exposed for orchestration/health-check tooling (load balancers, k8s probes). No prior privilege is needed; this is a straightforward unauthenticated GET.

### Recommendation
Restrict verbose health output (`Readyz` with `?full`, and `Health`) to internal/authenticated callers only, or strip error message bodies to non-sensitive status codes for any endpoint reachable without authentication. Follow the same pattern already established for `PublicReadyz` — separate "public, minimal" vs "internal, detailed" health endpoints, and ensure the detailed one is behind `auth.Authenticate(...)` or restricted to a private management port/network.

### Proof of Concept
```
curl -s "http://<node-host>:6688/readyz?full"
curl -s "http://<node-host>:6688/health"
```
No `Cookie`, `Authorization`, or API-key header is required; both return HTTP 200/503 along with a JSON body (`checks`) listing every internal health-check name and its raw error output, as implemented in `Readyz`/`Health` in [6](#0-5)  and mounted without auth in [2](#0-1) .

### Citations

**File:** core/web/router.go (L87-93)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
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

**File:** core/web/health_controller.go (L43-139)
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
