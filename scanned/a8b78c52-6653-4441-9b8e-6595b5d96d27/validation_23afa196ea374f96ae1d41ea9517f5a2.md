Confirmed: `healthRoutes` registers `/health`, `/readyz`, `/public-readyz` with **no authentication middleware** — they're mounted directly on the `api` group before any `auth.Authenticate` gate is applied, unlike `/v2` routes which require session/token auth [1](#0-0) . Any unauthenticated network client can hit `GET /health` with `Accept: text/html`.

### Title
Unescaped HTML injection in unauthenticated `/health` endpoint - (File: core/web/health_controller.go)

### Summary
The `Health` HTTP handler, reachable without any authentication, renders health-check names and error outputs directly into an HTML response using `fmt.Fprintf` with `%s`, without HTML-escaping any of the interpolated values [2](#0-1) .

### Finding Description
When a client requests `/health` with `Accept: text/html`, `Health` calls `newCheckTree(checks).WriteHTMLTo(c.Writer)` [3](#0-2) . `writeHTMLTo` writes `node.Name` into a `title` attribute and `short` (the check-name segment) into a `<span>`, and writes `node.Output` (the underlying Go `error.Error()` string from any failing subsystem check) into a `<pre>` block, all via raw `%s` formatting with no `html.EscapeString`/`template.HTMLEscapeString` call anywhere in the write path [4](#0-3) . The response is written directly to `c.Writer` with the negotiated `text/html` content type, so any `<`, `>`, `"` characters in a check name or an error string pass through unescaped into the served HTML document [5](#0-4) . This is architecturally the same root cause pattern as the reported json-sanitizer bug — untrusted structured content is emitted into an HTML-embedding context without proper escaping. This endpoint is registered without any `auth.Authenticate` middleware, unlike the `/v2` API which explicitly wraps routes in `auth.Authenticate(...)` [1](#0-0)  vs [6](#0-5) .

### Impact Explanation
If any health-check name or the wrapped error string of a failing check (e.g., an RPC/chain error, config error, or any downstream component's error message) contains attacker-influenced content (for example an RPC endpoint echoing back part of a crafted request in an error, or a job/config value surfaced in a health error), that content is reflected unescaped into HTML served to any browser that requests this endpoint. Because the endpoint requires no authentication, this could be leveraged for stored/reflected script injection against any user who views the node's health page (e.g., ops dashboards, embedded iframes, or load-balancer/monitoring UIs that render the HTML variant), potentially leading to session/cookie theft against an authenticated operator viewing the same origin.

### Likelihood Explanation
Exploitability depends on whether any reachable health-check name/output can be influenced by an external, unprivileged actor (e.g., through malformed RPC responses that get embedded verbatim in error strings, or configuration values reflected into check names). This project could not fully verify from static inspection whether any check currently produces attacker-controllable text in `Output` — the health checks are populated from internal service `IsHealthy()`/`IsReady()` implementations, which was not exhaustively enumerable within the available context. The lack of escaping itself, however, is a definite defect independent of a specific currently-known injectable check.

### Recommendation
HTML-escape all dynamic values (`node.Name`, `short`, `node.Status`, `node.Output`) before writing them into the HTML template in `writeHTMLTo`/`WriteHTMLTo`, e.g. via `html.EscapeString` or by using Go's `html/template` package instead of manual `fmt.Fprintf`/`io.WriteString` construction. Additionally, consider requiring authentication for the detailed `/health` HTML/JSON variants (as already done for `/public-readyz`) so that detailed internal state, including any future injectable content, is not exposed to unauthenticated callers.

### Proof of Concept
1. Trigger any internal health check to fail with an error message containing `"><script>alert(1)</script>` (this requires identifying a check whose `Output` reflects externally-influenced text — not confirmed to exist today, but the sink is unconditionally unescaped).
2. Send `GET /health` with header `Accept: text/html` to the unauthenticated Chainlink node HTTP server.
3. Observe the response body from `WriteHTMLTo`/`writeHTMLTo` contains the payload unescaped inside the `<summary title="...">`/`<pre>` output, as it is written via `fmt.Fprintf(w, ..., node.Name, ..., node.Status, short)` and `w.WriteRawLinef("    <pre>%s</pre>", node.Output)` with no escaping [2](#0-1) .

**Note on confidence**: I confirmed the unescaped-HTML sink and the lack of auth middleware on `/health` conclusively via source. I was not able to fully enumerate every `HealthChecker` implementation to prove a concrete externally-controllable string reaches `Output`/`Name`; this is stated as an open uncertainty above rather than asserted as proven end-to-end exploitability.

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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/health_controller.go (L118-139)
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

**File:** core/web/health_controller.go (L241-273)
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
		if len(node.Subs) > 0 {
			if err := node.Subs.writeHTMLTo(w.new("    ")); err != nil {
				return err
			}
		}
		if _, err := io.WriteString(w, "\n</details>"); err != nil {
			return err
		}
	}
	return nil
}
```
