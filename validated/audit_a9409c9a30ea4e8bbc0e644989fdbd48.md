## Analysis

I found a path-traversal analog in this chainlink repo, but I was unable to fully confirm within tool-call budget whether the route in question sits behind authenticated middleware — I note that explicitly below.

### Title
Unescaped `profile` path parameter allows request-path traversal in LOOP pprof proxy - (File: `core/web/loop_registry.go`)

### Summary
`pluginPPROFHandler` builds the outbound URL to a LOOP plugin's pprof endpoint by directly concatenating the user-supplied `profile` route parameter into both a Go format string and the resulting request URL, without any encoding or validation, mirroring the exact root cause described in the `hashi-vault-js` advisory (unescaped identifiers concatenated into a request URL, enabling path traversal / URL redirection).

### Finding Description
`pluginPPROFHandler` reads `gc.Param("profile")` and splices it straight into the URL string: [1](#0-0) 

```go
pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
```

There is no call to `url.PathEscape`/`encodeURIComponent`-equivalent, no `filepath.Clean`, and no allowlist of valid pprof profile names (`heap`, `goroutine`, `block`, etc.) before this value is used to build the outbound request via `l.doRequest` [2](#0-1) . Because `gc.Param("profile")` is inserted as part of the *format string itself* (not just as a `%s` argument), an attacker-controlled value containing `../` sequences or additional path/query syntax will be normalized by the HTTP client and can redirect the outbound request to a different path on the same internal LOOP plugin host (`l.loopHostName`) — the same class of bug as CVE-2026-55100 in `hashi-vault-js`, where unescaped identifiers were concatenated into a Vault request URL and could redirect requests to `/v1/sys/seal` instead of the intended KV path.

By contrast, `pluginMetricHandler` builds a fixed, hardcoded path (`"/metrics"`) and is not affected [3](#0-2) ; only the pprof handler concatenates a raw, attacker-controlled path segment.

### Impact Explanation
`l.loopHostName` points at the internal LOOP (plugin) host, and the forged path segment could be used to reach other endpoints exposed on that internal host (e.g., other `/debug/pprof/*` sub-paths, or, depending on what else is listening on that port, unintended internal endpoints) rather than the intended pprof profile. This is a Server-Side Request Forgery / path-confusion primitive against an internal-only service, not remote code execution, and impact is bounded by what is reachable on `loopHostName:PrometheusPort`. I was not able to confirm within the available tool budget whether the `/plugins/:name/pprof/:profile` route in `core/web/router.go` is gated behind admin/session authentication middleware — if it is (as most `/v2/*` node-admin routes typically are), the practical severity is reduced to an authenticated-admin-only issue; if it is unauthenticated, this becomes a more serious unauthenticated internal-SSRF-style bug. This distinction could not be verified with certainty in this pass.

### Likelihood Explanation
The `profile` value comes directly from the URL path (`gc.Param("profile")`) with no server-side validation against a known set of pprof profile names, so exploitation only requires sending a crafted request to this endpoint — trivial to trigger by any caller who can reach the route (whether that is any authenticated node operator or, if unauthenticated, any network client).

### Recommendation
- Validate `profile` against an explicit allowlist of supported pprof profile names (e.g., `heap`, `goroutine`, `threadcreate`, `block`, `mutex`, `trace`, `cmdline`, `profile`, `symbol`) before using it.
- If arbitrary passthrough is required, URL-encode the segment with `url.PathEscape` and build the request via `url.URL{Path: ...}` construction rather than raw `fmt.Sprintf` string concatenation, and never fold user input into the *format string* argument of `fmt.Sprintf`.
- Confirm and, if necessary, tighten authentication/authorization on the `/plugins/:name/pprof/:profile` route in `core/web/router.go`.

### Proof of Concept
A request such as:
```
GET /plugins/<validPluginName>/pprof/../../some/other/internal/path?...
```
would cause `pluginURL` to be constructed as `http://<loopHostName>:<port>/debug/pprof/../../some/other/internal/path`, which Go's HTTP client will normalize, causing the outbound proxied request to land on an unintended path on the internal LOOP host — analogous to how `../../sys/seal` redirected `hashi-vault-js` requests to `/v1/sys/seal`. [1](#0-0)

### Citations

**File:** core/web/loop_registry.go (L96-105)
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

**File:** core/web/loop_registry.go (L190-215)
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
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q pprof", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```
