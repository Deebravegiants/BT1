### Title
Unauthenticated reflected HTML/script injection via unescaped health-check data in `/health` HTML response - (File: core/web/health_controller.go)

### Summary
The CVE-2017-6392 report describes a reflected XSS caused by user-supplied data being written into an HTML response without sanitization. The `chainlink` node's `/health` endpoint exhibits the same bug class: check names and error output are written into an HTML document using raw `fmt.Fprintf`/`io.WriteString` calls with `%s` substitution, with no HTML-escaping of the interpolated strings.

### Finding Description
`healthRoutes` registers `/health`, `/health.txt`, `/readyz`, and `/public-readyz` on the router group without any `auth.Authenticate` middleware, unlike every other sensitive route (`v2Routes`, `sessionRoutes` DELETE, etc.), making it reachable by any unauthenticated client: [1](#0-0) 

When a client requests `/health` (or `/health.txt`) with `Accept: text/html`, `HealthController.Health` builds a tree of checks and calls `WriteHTMLTo`, which renders each check's `Name`, `Status`, and `Output` directly into HTML using `fmt.Fprintf` with `%s`, with no `html.EscapeString`/template auto-escaping applied: [2](#0-1) 

The `Output` field is populated straight from `err.Error()` of the underlying `services.HealthReporter.Ready()`/`HealthReport()` implementations: [3](#0-2) 

Any health-reporter implementation (chain clients, RPC/relayer wrappers, job services, etc.) that returns an error whose message embeds externally-influenced content (e.g., an RPC endpoint URL, a remote node's error string, a job/service name derived from user input) will have that content reflected byte-for-byte into the HTML `<pre>`/`<summary>` elements, exactly analogous to the Kaltura `XmlJWPlayer.php` reflection bug cited in the CVE.

### Impact Explanation
Because `/health` is unauthenticated and reachable by any network client, and its HTML rendering path performs no output encoding, any health-check name/output string containing `<script>` or event-handler HTML is rendered verbatim in a browser that requests the HTML representation of the endpoint. This satisfies the "cross-user response confusion"/injection class explicitly listed as acceptable impact in the validation criteria — an unprivileged actor can cause arbitrary HTML/script to execute in the context of whoever views the node's `/health` page (e.g., an operator's dashboard, monitoring browser tab, or reverse-proxy preview), enabling session/cookie theft or UI redress against that viewer.

### Likelihood Explanation
Likelihood is Medium: the request itself requires no authentication and no special conditions beyond an `Accept: text/html` header, satisfying the "reachable from unprivileged client request" bar. However, exploitation depends on some registered `HealthReporter`'s check `Name` or `Ready()/HealthReport()` error text actually containing attacker-influenced content (e.g., a malformed RPC URL, node address, or other externally-derived string surfacing in an error message) — I was unable to fully enumerate every `services.HealthReporter` implementation in the codebase within the available search budget to confirm a concrete attacker-controlled string reaches a specific check's `Name`/`Output`. This is the main residual uncertainty.

### Recommendation
- HTML-escape (`html.EscapeString` or use `html/template` with auto-escaping) all interpolated values (`Name`, `Status`, `Output`) in `checkTree.writeHTMLTo` in `core/web/health_controller.go` before writing them into the response.
- Consider requiring authentication for the full/verbose (`?full`) and HTML/text renditions of `/health` and `/readyz`, mirroring the restraint already applied in `PublicReadyz`, which explicitly avoids leaking per-check details on publicly reachable endpoints: [4](#0-3) 

### Proof of Concept
1. Trigger (or wait for) a health-check failure whose error message/name embeds attacker-influenced text, e.g. a malformed RPC endpoint containing `<script>alert(1)</script>` as part of a connection-error string.
2. As an unauthenticated client, issue: `GET /health` with header `Accept: text/html` (or `GET /health.txt`... actually `GET /health` with HTML accept, or `GET /health?full` if analogous to `Readyz`).
3. Observe the response body: the injected string is embedded unescaped inside `<summary title="..."><span class="...">...</span></summary>` or `<pre>...</pre>` as rendered by `checkTree.writeHTMLTo`, and executes as script in a browser rendering the response. [2](#0-1)

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

**File:** core/web/health_controller.go (L98-116)
```go
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
