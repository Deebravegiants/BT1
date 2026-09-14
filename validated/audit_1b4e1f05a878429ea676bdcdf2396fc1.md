Based on my research, I found one plausible analog to the CVE-2026-1616 pattern (unsanitized query-derived value concatenated directly into a URL used for a backend/proxied request), but I could not fully confirm its authentication exposure before running out of tool calls.

## What I found

`core/web/loop_registry.go`'s `pluginPPROFHandler` builds an outbound URL to an internal LOOP-plugin pprof endpoint by directly string-concatenating a route parameter into the URL, with no path cleaning or validation: [1](#0-0) 

```go
func (l *LoopRegistryServer) pluginPPROFHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	...
	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
	urlVals, timeout := pprofURLVals(gc)
	if s := urlVals.Encode(); s != "" {
		pluginURL += "?" + s
	}
	...
	l.doRequest(gc, "GET", pluginURL, nil, timeout, pluginName)
}
```

`gc.Param("profile")` comes straight from the request path and is spliced into the format string used to build the proxied backend URL, then that request is forwarded via `doRequest` [2](#0-1)  with no `filepath.Clean`/prefix check comparable to what's done elsewhere in the same codebase, e.g. `newFileFetcher` explicitly guards against traversal with `filepath.Clean` + basePath prefix check [3](#0-2) , and `gzipFileHandler.ServeHTTP` does `path.Clean(upath)` before serving [4](#0-3) . The pprof handler has no equivalent normalization for the `profile` parameter, which structurally matches the OSIM bug class (untrusted request data concatenated into a path/URL used by a downstream fetch, enabling traversal outside the intended subpath — e.g. `../` sequences reaching other endpoints on the internal LOOP host/port).

## Why I cannot confirm this as a valid finding

I was unable to verify, before running out of tool-call budget, whether the routes registered for `LoopRegistryServer` (in `core/web/router.go`) are:
- reachable by an unprivileged/unauthenticated actor (e.g., mounted for external Prometheus scraping, similar to `discoveryHandler` which the code comments say "must be accessible to external prom for scraping" [5](#0-4) ), or
- gated behind the same authenticated/admin session middleware used for other `/v2/...` admin endpoints (which would make this an operator-only path, explicitly out of scope per your rules).

My `grep_search` against `core/web/router.go` matched content but the tool did not return the actual matched lines/context before the iteration budget was exhausted, so I could not confirm the route registration, path prefix, or middleware chain for `pluginPPROFHandler`/`pluginMetricHandler`.

## Conclusion

I cannot assert a confirmed, unprivileged-actor-reachable vulnerability with certainty given this gap. Rather than fabricate the exploitability/authentication context, I recommend a follow-up Devin session (with full file/terminal access) to read `core/web/router.go` in full and confirm:
1. Whether `/plugins/:name/debug/pprof/:profile` (or similar) is registered without authentication middleware.
2. Whether `gc.Param("profile")` can contain `/../` sequences that Gin's router does not already normalize before dispatch (Gin generally does clean `.` segments in path matching, which would mitigate this — this also needs verification against the specific Gin version/config used).

If you want, I can have that follow-up investigation done and only then produce the strict vulnerability report format — I won't fabricate a CVE-style report without confirming reachability and authentication, since doing so would not meet the "prove root cause with exact file/function support" bar you set.

### Citations

**File:** core/web/loop_registry.go (L52-58)
```go
// discoveryHandler implements service discovery of prom endpoints for LOOPs in the registry
func (l *LoopRegistryServer) discoveryHandler(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	groups := make([]*targetgroup.Group, 0, 1+len(l.registry.List()))

	// add node metrics to service discovery
	groups = append(groups, pluginGroup(l.discoveryHostName, l.exposedPromPort, "/metrics"))
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

**File:** core/web/loop_registry.go (L190-205)
```go
func (l *LoopRegistryServer) doRequest(gc *gin.Context, method, url string, body io.Reader, timeout time.Duration, pluginName string) {
	ctx, cancel := context.WithTimeout(gc.Request.Context(), timeout)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error creating plugin pprof request: %s", err))
		return
	}
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		msg := "plugin pprof handler failed to post plugin url " + html.EscapeString(url)
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}
	defer res.Body.Close()
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L222-231)
```go
		fullPath := filepath.Clean(u.Path)

		// ensure that the incoming request URL is either relative or absolute but within the basePath
		if !filepath.IsAbs(fullPath) {
			// If it's not absolute, we assume it's relative to the basePath
			fullPath = filepath.Join(basePath, fullPath)
		}
		if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
			return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
		}
```

**File:** core/web/middleware.go (L196-208)
```go
// Implements http.Handler
func (f *gzipFileHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	upath := r.URL.Path
	if !strings.HasPrefix(upath, "/") {
		upath = "/" + upath
		r.URL.Path = upath
	}

	fpath := path.Clean(upath)
	if strings.HasSuffix(fpath, "/") {
		http.NotFound(w, r)
		return
	}
```
