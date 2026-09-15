### Title
Unauthenticated `/health` and `/health?full=1`/`/readyz?full=1` endpoints disclose internal node topology, chain IDs, and connectivity error details - ([File: core/web/health_controller.go])

### Summary
The CVE-2019-10046 analog is an unauthenticated information-disclosure bug where a public endpoint reveals internal configuration/session details. In this codebase, `healthRoutes` registers `/health`, `/health.txt`, and `/readyz` on the root router group with no authentication middleware, and these handlers return detailed internal service names, per-chain identifiers, and error strings describing connectivity/internal state to any unauthenticated caller.

### Finding Description
`healthRoutes` mounts `HealthController.Health` and `HealthController.Readyz` directly on the top-level `api` group in `NewRouter`, with no `auth.Authenticate` wrapper, unlike almost every other informative endpoint (e.g. `/v2/config`, which requires session/token auth and role checks) <cite repo="Alyssadaypin/chainlink--019" path="core/web/router.go" start="87="90" /> [1](#0-0) .

`HealthController.Health` builds a `checks` list keyed by internal service/component name (e.g. `EVM.<chainID>`, `EVM.<chainID>.HeadTracker.HeadListener`, `CRE.DispatcherWrapper`) and includes free-text `Output` derived from internal error values whenever a check is failing [2](#0-1) . This is returned in full to any unauthenticated requester hitting `/health` (JSON/HTML/plain-text formats all supported) [3](#0-2) .

Similarly, `Readyz` accepts a `?full=1` query parameter and, when present, returns the same kind of per-check breakdown with status and error output for every internal check, without authentication [4](#0-3) . The codebase's own doc comment on `PublicReadyz` explicitly acknowledges this exact risk for `Readyz`: "Unlike Readyz, it never returns per-check details regardless of query parameters, to avoid leaking internal service state on publicly reachable endpoints," confirming that `Readyz`/`Health` are recognized internally as leaking internal service state when exposed publicly [5](#0-4) .

A real example of what is disclosed is captured in the test fixture, which shows chain IDs and internal head-tracker/listener connectivity error text ("Listener connected = false, receiving heads = false") returned in the response body [6](#0-5) .

### Impact Explanation
An unauthenticated network client can enumerate a Chainlink node's internal architecture: which chains/EVM chain IDs are configured, which internal subsystems exist (BridgeStatusReporter, CRE, HeadTracker, HeadBroadcaster, LogBroadcaster, Relayer, etc.), and detailed failure/error text about node connectivity state. This is directly analogous to the Pydio CVE's disclosure of session timeout/config/library info to unauthenticated attackers — it aids reconnaissance and targeting of a node (e.g., knowing exactly which chain a node runs, or that its RPC/head listener is down) without requiring any credentials.

### Likelihood Explanation
High likelihood of exploitation: no authentication, no special preconditions, and the endpoint is meant to be reachable (health checks are commonly exposed to load balancers/monitoring, and there is no network-layer restriction enforced in the route registration itself — `/public-readyz` is the only endpoint intentionally hardened for public exposure, implying `/health` and `/readyz?full=1` are not).

### Recommendation
Restrict `/health` (and `/readyz` with `full` query) to authenticated/internal callers only, mirroring the `PublicReadyz` pattern (return minimal status without per-check breakdown) for any endpoint reachable without authentication, or require `auth.Authenticate` middleware on `/health` and `/readyz` and keep only `/public-readyz` unauthenticated with the current minimal-disclosure behavior.

### Proof of Concept
```
curl http://<node-host>:6688/health
curl "http://<node-host>:6688/readyz?full=1"
```
Both return HTTP 200/207/503 responses containing per-check JSON entries with internal service names (e.g. `EVM.1399100.HeadTracker.HeadListener`) and error text, with no `Authorization`/session cookie required [7](#0-6) [1](#0-0) .

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

**File:** core/web/testdata/body/health.json (L30-73)
```json
    {
      "type": "checks",
      "id": "EVM.1399100",
      "attributes": {
        "name": "EVM.1399100",
        "status": "passing",
        "output": ""
      }
    },
    {
      "type": "checks",
      "id": "EVM.1399100.BalanceMonitor",
      "attributes": {
        "name": "EVM.1399100.BalanceMonitor",
        "status": "passing",
        "output": ""
      }
    },
    {
      "type": "checks",
      "id": "EVM.1399100.HeadBroadcaster",
      "attributes": {
        "name": "EVM.1399100.HeadBroadcaster",
        "status": "passing",
        "output": ""
      }
    },
    {
      "type": "checks",
      "id": "EVM.1399100.HeadTracker",
      "attributes": {
        "name": "EVM.1399100.HeadTracker",
        "status": "passing",
        "output": ""
      }
    },
    {
      "type": "checks",
      "id": "EVM.1399100.HeadTracker.HeadListener",
      "attributes": {
        "name": "EVM.1399100.HeadTracker.HeadListener",
        "status": "failing",
        "output": "Listener connected = false, receiving heads = false"
      }
```
