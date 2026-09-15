## Title
Path Traversal via unsanitized `profile` parameter in LOOP plugin pprof proxy handler - (`core/web/loop_registry.go`)

### Summary
The `pluginPPROFHandler` in `core/web/loop_registry.go` forwards debug/pprof requests to an internal LOOP plugin process. It builds the outbound URL by directly concatenating the `profile` route parameter — taken unsanitized from the incoming HTTP request — into the target path string, exactly the bug class described in the Snipe-IT `displaySig` advisory (CWE-23): a filename/path segment taken from an HTTP route parameter is concatenated into a path with no cleaning or allowlisting. [1](#0-0) 

### Finding Description
`pluginPPROFHandler` retrieves the `profile` parameter straight from the gin route and interpolates it into the pprof URL string that is sent to the internal LOOP plugin server: [2](#0-1) 

Unlike the plugin-name lookup (`l.registry.Get(pluginName)`), which validates that the plugin exists, there is no validation, allowlisting, or path-cleaning applied to `profile` before it is placed into the constructed URL (`"http://%s:%d/debug/pprof/"+gc.Param("profile")`). A caller can supply `..` segments or other path elements in `profile`, letting the resulting request escape the intended `/debug/pprof/` namespace on the plugin's local HTTP server and reach other endpoints exposed by that plugin process, or manipulate the query string via injected `?`/`&` characters since `pprofURLVals` builds a query string on top of an already attacker-controlled path.

This handler is registered under the authenticated route group and reachable by any authenticated node-API user, not just admins — the router comment marks it "Debug routes accessible via authentication" and attaches it to `authv2` without an explicit role-elevation wrapper (unlike most other admin/edit-gated routes in the same file). [3](#0-2) 

The companion handler `pluginMetricHandler` follows the same lookup-then-fixed-path pattern (safe, since it hardcodes `/metrics`), reinforcing that `pluginPPROFHandler` is the outlier that fails to apply the same discipline to a user-controlled segment. [4](#0-3) 

### Impact Explanation
An authenticated node-API caller (even one with a low-privilege/view-only role, since the route is not wrapped in `RequiresEditRole`/`RequiresAdminRole`) can control the trailing path segment of an internal request made by the Chainlink node to a LOOP plugin's local debug HTTP server. This can be leveraged to reach unintended internal endpoints of that plugin process beyond the sanctioned `/debug/pprof/*` surface, potentially disclosing additional internal state or triggering unintended plugin behavior — the same class of impact as the original advisory (unauthorized read of resources outside the intended, sandboxed path).

### Likelihood Explanation
Likelihood is high for any deployment that runs LOOP plugins and exposes the node's authenticated web API, since exploitation requires only a valid low-privilege authenticated session and a single crafted request with a manipulated `profile` route parameter — no additional race conditions or privileged access needed.

### Recommendation
Sanitize/allowlist the `profile` parameter before use (e.g., reject any value containing `/`, `..`, or characters outside an expected pprof-profile-name charset), and construct the outbound URL with `url.URL{Path: path.Join(...)}` plus a post-join prefix check (mirroring the containment check already used in `core/services/workflows/syncer/v2/fetcher.go`), rather than raw string concatenation. Additionally, consider requiring an elevated role for this debug-forwarding endpoint given its access to internal plugin process endpoints.

### Proof of Concept
1. Authenticate as any user with a valid Chainlink node API session/token (any role, since the route lacks `RequiresEditRole`/`RequiresAdminRole`).
2. Send `GET /plugins/<validPluginName>/pprof/../../../<other-internal-path>` (the exact route pattern is registered via `metricRoutes`/`pluginPPROFHandler` wiring in `core/web/router.go`).
3. Observe that the resulting outbound request to `http://<loopHostName>:<PrometheusPort>/debug/pprof/../../../<other-internal-path>` is sent verbatim to the plugin's internal HTTP server, potentially returning data or behavior from an endpoint the pprof proxy was not intended to expose.

### Citations

**File:** core/web/loop_registry.go (L96-128)
```go
func (l *LoopRegistryServer) pluginMetricHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		gc.Data(http.StatusNotFound, "text/plain", fmt.Appendf(nil, "plugin %q does not exist", html.EscapeString(pluginName)))
		return
	}

	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/metrics", l.loopHostName, p.EnvCfg.PrometheusPort)
	req, err := http.NewRequestWithContext(gc.Request.Context(), http.MethodGet, pluginURL, nil)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error creating plugin metrics request: %s", err))
		return
	}
	res, err := l.promClient.Do(req)
	if err != nil {
		msg := "plugin metric handler failed to get plugin url " + html.EscapeString(pluginURL)
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q metrics", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```

**File:** core/web/loop_registry.go (L150-166)
```go
func (l *LoopRegistryServer) pluginPPROFHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		gc.Data(http.StatusNotFound, "text/plain", fmt.Appendf(nil, "plugin %q does not exist", html.EscapeString(pluginName)))
		return
	}

	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
	urlVals, timeout := pprofURLVals(gc)
	if s := urlVals.Encode(); s != "" {
		pluginURL += "?" + s
	}
	l.logger.Infow("Forwarding plugin pprof request", "plugin", pluginName, "url", pluginURL)
	l.doRequest(gc, "GET", pluginURL, nil, timeout, pluginName)
}
```

**File:** core/web/router.go (L441-447)
```go
		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```
