### Title
Unescaped health-check error/output strings rendered as raw HTML on unauthenticated `/health` and `/readyz` endpoints - ([File: core/web/health_controller.go])

### Summary
The Jetty advisory (CVE-2019-17632) concerns default error-response generation that embeds exception messages into HTML without escaping, enabling reflected XSS. The same bug class exists in chainlink's node health endpoints: `checkTree.writeHTMLTo` writes `Check.Name` and `Check.Output` (which is populated from `err.Error()`) directly into an HTML response using `fmt.Fprintf` with `%s`, with no HTML-escaping.

### Finding Description
`Health` and `Readyz` build a list of `presenters.Check` from `checker.IsHealthy()` / `checker.IsReady()`, setting `Output = err.Error()` for any failing check: [1](#0-0) 

When the client negotiates `text/html`, `Health` calls `newCheckTree(checks).WriteHTMLTo(c.Writer)`: [2](#0-1) 

`writeHTMLTo` writes the check name into an HTML `title` attribute and the check output into a `<pre>` block using raw `%s` formatting — no `html.EscapeString`/template escaping is applied to either field: [3](#0-2) 

Both endpoints are registered with no authentication middleware. `healthRoutes` is mounted directly on the `api` group, which only applies rate-limiting/session middleware, not the `auth.Authenticate` middleware used by every other sensitive route group (`/v2/...`, `/debug/vars`, etc.): [4](#0-3) [5](#0-4) 

Any error message surfaced through a registered health check (service errors, DB/RPC connectivity errors, or any downstream text that ends up in `err.Error()`) is reflected verbatim into the HTML document served to whoever requests `/health` with an HTML-accepting client — mirroring the Jetty issue where uncontrolled exception text is embedded into HTML error output without encoding.

### Impact Explanation
If any health-check error string ever contains HTML/JS metacharacters (e.g., a chain RPC endpoint's error text, a service name/URL configured by an operator, or any downstream error propagated through Go's `error.Error()`), it is rendered unescaped in the browser DOM of anyone loading `/health`. Because this endpoint is unauthenticated and typically exposed for load-balancer/monitoring checks (sometimes on a network reachable by other tenants or dashboards embedding these URLs), this is a reflected/stored XSS sink (CWE-79) reachable without any credentials — a direct analog to the CVSS "UI:R/S:C" Jetty case (a victim must view the crafted health page).

### Likelihood Explanation
Exploitability is bounded by attacker control over the error text that flows into `Output`. In most default configurations, health-check errors come from internal service/DB/RPC state, which a fully unprivileged remote client cannot directly inject. This lowers likelihood relative to the Jetty case (where the exception message could reflect malformed request data). However, the underlying escaping defect is real and concrete: any future/queued health check whose error text incorporates user- or peer-supplied content (job names, URLs, or messages from external adapters/services) would become an unauthenticated stored-XSS vector with no code change needed in the check itself — only the vulnerable renderer needs a crafted string to pass through.

### Recommendation
- HTML-escape `node.Name` and `node.Output` before embedding them in `writeHTMLTo` (use `html.EscapeString` or `template/html` instead of raw `fmt.Fprintf("%s", ...)`).
- Apply the same escaping to `writeTextTo`/JSON paths is not required, but the HTML path specifically needs encoding since it is the only representation interpreted by browsers.
- Consider requiring authentication on `/readyz?full` and `/health` (already partially addressed by the existence of the reduced-detail `PublicReadyz`), or at minimum keep `/health` and `/readyz` (full) restricted to internal networks only, consistent with the comment already present in `PublicReadyz` about avoiding leakage of internal state on public endpoints.

### Proof of Concept
1. Ensure some check name or error text can be influenced to contain `"><script>alert(1)</script>` (e.g., via a component whose failure message embeds a configurable string, such as a job/service name or a chain RPC endpoint URL set via `/v2/nodes` or job configuration).
2. Send `GET /health` (or `/health` with `Accept: text/html`) unauthenticated.
3. Observe the response body via `checkTree.writeHTMLTo` — the injected string is emitted verbatim inside `<summary title="...">` / `<pre>...</pre>` with no HTML entity encoding, and executes when rendered in a browser. [3](#0-2)

### Citations

**File:** core/web/health_controller.go (L60-76)
```go
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
```

**File:** core/web/health_controller.go (L118-127)
```go
	switch c.NegotiateFormat(gin.MIMEJSON, gin.MIMEHTML, gin.MIMEPlain) {
	case gin.MIMEJSON:
		break // default

	case gin.MIMEHTML:
		if err := newCheckTree(checks).WriteHTMLTo(c.Writer); err != nil {
			hc.App.GetLogger().Errorw("Failed to write HTML health report", "err", err)
			c.AbortWithStatus(http.StatusInternalServerError)
		}
		return
```

**File:** core/web/health_controller.go (L241-262)
```go
func (t checkTree) writeHTMLTo(w *linePrefixWriter) error {
	keys := slices.AppendSeq(make([]string, 0, len(t)), maps.Keys(t))
	slices.Sort(keys)
	for _, short := range keys {
		node := t[short]
		if _, err := io.WriteString(w, `
<details open>`); err != nil {
			return err
		}
		var expand string
		if node.Output == "" && len(node.Subs) == 0 {
			expand = ` class="noexpand"`
		}
		if _, err := fmt.Fprintf(w, `
    <summary title="%s"%s><span class="%s">%s</span></summary>`, node.Name, expand, node.Status, short); err != nil {
			return err
		}
		if node.Output != "" {
			if _, err := w.WriteRawLinef("    <pre>%s</pre>", node.Output); err != nil {
				return err
			}
		}
```

**File:** core/web/router.go (L78-90)
```go
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
