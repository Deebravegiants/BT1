Found a concrete analog. This confirms the vulnerability with exact code support: the `sanitized.String()` function in `core/logger/prettyconsole.go` explicitly **allows** `'\n', '\r', '\t'` through unescaped, while only escaping other control characters.

### Title
Log Injection via Unsanitized Request Path/Fields in Pretty Console Logger - (File: core/logger/prettyconsole.go, core/web/router.go)

### Summary
The Chainlink node's HTTP request logging middleware (`loggerFunc` in `core/web/router.go`) embeds unsanitized, attacker-controlled request data (URL path, headers-derived fields) directly into log entries. When rendered through the default `pretty://console` sink, the `sanitized.String()` helper in `core/logger/prettyconsole.go` deliberately preserves newline, carriage-return, and tab characters instead of escaping them, allowing an unauthenticated or low-privileged HTTP client to inject fabricated log lines/fields into the node's console log output — directly analogous to the `Rack::Sendfile` `X-Sendfile-Type` header log injection (CVE-2025-27111).

### Finding Description
The request logging middleware builds the log message directly from the raw request path: [1](#0-0) 
`c.Request.URL.Path` and other request-derived values (`query`, `body`, etc.) are passed as the zap message/fields. Zap's underlying JSON encoder would normally escape control characters (`\n` → `\\n`) when serializing to JSON, which is safe. However, when the node uses the default non-JSON console format (`JSONConsole = false`, the default per `core/config/docs/core.toml`), the `pretty://console` sink defined in `core/logger/prettyconsole.go` re-parses that already-escaped JSON with `gjson`, extracting the raw string value back out (un-escaping `\n` back into real newline bytes) and writes it to the console via `generateHeadline`/`generateDetails`.

Critically, the `sanitized.String()` function explicitly special-cases newlines, carriage returns, and tabs to be passed through untouched: [2](#0-1) 

This means any attacker-controlled string that ends up in a logged field or message (e.g., `c.Request.URL.Path`) — reachable by any unauthenticated network client, since `loggerFunc` runs on every request in `core/web/router.go` before authentication even applies — can contain raw `\n`/`\r` bytes, which will be written verbatim to the console log, forging fake log lines, timestamps, or level indicators. This is a direct structural analog to `Rack::Sendfile` writing an unsanitized `X-Sendfile-Type` header value straight into a log line.

### Impact Explanation
An unauthenticated client can craft a request path or other logged parameter containing embedded newline sequences (e.g., URL-encoded `%0A` decoded by the router into `c.Request.URL.Path`) to inject arbitrary fabricated log entries into the node operator's console/log output. This can be used to forge fake `[ERROR]`/`[CRIT]` entries, obscure the trail of an actual attack, spoof audit-adjacent log lines, or mislead log-based alerting/SIEM pipelines that scrape the pretty console output. This matches CWE-117 (Log Injection) / CWE-93 (CRLF Injection) impact class from the referenced advisory.

### Likelihood Explanation
High likelihood of reachability: `loggerFunc` is registered as global middleware (`engine.Use(..., loggerFunc(app.GetLogger()), ...)`) in `core/web/router.go`, executed for every incoming HTTP request regardless of authentication status, and the default configuration (`JSONConsole = false`) routes output through the vulnerable `pretty://console` sink. No special privileges are required — only network access to the node's web server.

### Recommendation
- In `sanitized.String()` (`core/logger/prettyconsole.go`), do not special-case `\n`, `\r`, `\t` — escape all control characters uniformly (or replace them with visible escape sequences) before writing to the console sink.
- Alternatively/additionally, sanitize/escape request-derived values (`c.Request.URL.Path`, headers, query params) before they are ever passed into `lggr.Debugw` in `core/web/router.go`.

### Proof of Concept
1. Ensure the node runs with default logging config (`JSONConsole = false`), which routes logs through `pretty://console` (`core/logger/logger.go` `newZapConfigProd`).
2. Send an HTTP request to the node with a URL path containing an encoded newline, e.g.:
   `GET /v2/fake%0A%5BCRIT%5D%20FAKE%20ALERT:%20disk%20full HTTP/1.1`
3. Gin decodes `%0A` into an actual `\n` byte, which flows into `c.Request.URL.Path`.
4. `loggerFunc` logs `fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path)` as the message via `lggr.Debugw` (`core/web/router.go:556-567`).
5. The message is JSON-encoded (escaping `\n` to `\\n`) by zap's JSON encoder, then piped to `PrettyConsole.Write`, which parses it with `gjson` and calls `generateHeadline`, which un-escapes the JSON string back to a raw string containing the literal newline.
6. `sanitized.String()` passes the `\n` through untouched, so the final console output contains an injected fake line: `[CRIT] FAKE ALERT: disk full`, indistinguishable from a genuine log entry.

### Citations

**File:** core/web/router.go (L556-567)
```go
		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
			"clientIP", c.ClientIP(),
			"errors", c.Errors.String(),
			"servedAt", end.Format("2006-01-02 15:04:05"),
			"latency", fmt.Sprintf("%v", end.Sub(start)),
		)
```

**File:** core/logger/prettyconsole.go (L135-156)
```go
type sanitized string

// String replaces control characters with Go escape sequences, except for newlines and tabs.
// See strconv.QuoteRune.
func (s sanitized) String() string {
	var out strings.Builder
	for _, r := range s {
		switch r {
		case '\n', '\r', '\t':
			// allowed
		default:
			// escape others
			if unicode.IsControl(r) {
				q := strconv.QuoteRune(r)
				out.WriteString(q[1 : len(q)-1]) // trim quotes
				continue
			}
		}
		out.WriteRune(r)
	}
	return out.String()
}
```
