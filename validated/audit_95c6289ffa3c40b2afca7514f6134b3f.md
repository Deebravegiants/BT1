### Title
Unescaped HTML injection via service check names in `/health` endpoint - (File: `core/web/health_controller.go`)

### Summary
The `Health` handler renders health-check results as raw HTML when a client negotiates `text/html`, and interpolates check `Name`, `Status`, and `Output` fields directly into the HTML response without any escaping.

### Finding Description
`HealthController.Health` builds a list of `presenters.Check` from the application's `HealthChecker` (name, status, error output) and, when the client's `Accept` header negotiates `gin.MIMEHTML`, calls `newCheckTree(checks).WriteHTMLTo(c.Writer)` [1](#0-0) . `writeHTMLTo` writes each node's `Name`, `Status`, and `Output` straight into HTML via `fmt.Fprintf`/`WriteRawLinef` with no HTML-escaping (no use of `html.EscapeString` or `template/html`) [2](#0-1) . This is structurally the same bug class as the reported CVE: user/attacker-influenced string content is placed into an HTML-rendering context without neutralizing HTML-parser-sensitive sequences (e.g., `</pre>`, `<script>`, `"` breaking the `title="%s"` attribute).

The `Output` field is populated from `err.Error()` of internal health-checker errors [3](#0-2) , and `Name`/keys come from registered service names in the `checkTree` structure built from `presenters.Check.Name` [4](#0-3) .

### Impact Explanation
If an error message surfaced through the health checker ever contains attacker-influenced content (e.g., an upstream URL, a malformed payload description, or any string reflecting user/external input processed by a registered service/health-checked component), it would be reflected unescaped into the HTML page served at `/health`. This could enable stored/reflected HTML or script injection served from the node's own origin to any client that requests the `text/html` variant of the health page.

### Likelihood Explanation
I could not confirm from the indexed code whether the `/health` route is authenticated/gated or reachable by an unauthenticated actor, nor could I confirm that any health-checker error message is derived from attacker-controlled input rather than purely internal/operator-controlled state (e.g., DB connectivity strings, RPC endpoint names configured by the node operator). Both of these are required to establish this as an unprivileged-actor-reachable vulnerability per the validation rules. Based on what is indexed, `Health`/`Readyz` wiring in `core/web/router.go` did not show up with an explicit auth middleware in the searched context, and I was unable to fully trace the route registration and middleware chain within the available iterations.

### Recommendation
Escape all dynamic values (`Name`, `Status`, `Output`) with `html.EscapeString` (or render via Go's `html/template` instead of manual `fmt.Fprintf`/`io.WriteString` HTML construction) before writing them into `checkTree.writeHTMLTo`, and confirm that error messages surfaced by the health checker never embed unsanitized external input.

### Proof of Concept
Not independently verified — would require confirming (a) an unauthenticated route to `/health` with `Accept: text/html`, and (b) a registered service health-check whose error `Output` or `Name` reflects attacker-controlled data, e.g. a check name or error string containing `"><script>alert(1)</script>`. I was not able to confirm both conditions from the available code index.

Given the unresolved reachability/authentication question and the unconfirmed attacker-controlled-input path, I cannot assert this meets the "concrete... impact" bar with full confidence, but the code-level absence of escaping in `core/web/health_controller.go` is a real, demonstrable defect matching the reported bug class.

### Citations

**File:** core/web/health_controller.go (L99-106)
```go
	for name, err := range errors {
		status := HealthStatusPassing
		var output string

		if err != nil {
			status = HealthStatusFailing
			output = err.Error()
		} else if failing {
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

**File:** core/web/health_controller.go (L176-199)
```go
func newCheckTree(checks []presenters.Check) checkTree {
	slices.SortFunc(checks, presenters.CmpCheckName)
	root := make(checkTree)
	for _, c := range checks {
		parts := strings.Split(c.Name, ".")
		node := root
		for _, short := range parts[:len(parts)-1] {
			n, ok := node[short]
			if !ok {
				n = checkNode{Subs: make(checkTree)}
				node[short] = n
			}
			node = n.Subs
		}
		p := parts[len(parts)-1]
		node[p] = checkNode{
			Name:   c.Name,
			Status: c.Status,
			Output: c.Output,
			Subs:   make(checkTree),
		}
	}
	return root
}
```

**File:** core/web/health_controller.go (L254-261)
```go
		if _, err := fmt.Fprintf(w, `
    <summary title="%s"%s><span class="%s">%s</span></summary>`, node.Name, expand, node.Status, short); err != nil {
			return err
		}
		if node.Output != "" {
			if _, err := w.WriteRawLinef("    <pre>%s</pre>", node.Output); err != nil {
				return err
			}
```
