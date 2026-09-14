### Title
Non-recursive JSON body redaction in the node's debug request logger leaks secrets nested in request payloads - (File: `core/web/router.go`)

### Summary
The Chainlink node's HTTP request logging middleware (`loggerFunc`) sanitizes request bodies before writing them to the debug log via `readSanitizedJSON`/`redact`, but the sanitizer only inspects **top-level** JSON keys against a small hardcoded blacklist. Any sensitive field nested one level deeper (e.g. inside a `variables` object for the node's GraphQL endpoint, or any nested object body) bypasses redaction entirely and is written in plaintext to the node's log file/`AUDIT`/debug sink — the same bug class as CVE-2026-0905 (insufficient policy enforcement causing sensitive data to leak into a log artifact).

### Finding Description
`loggerFunc` is installed as global middleware on the gin engine and therefore runs for every request to the node's API, including unauthenticated endpoints: [1](#0-0) 

It buffers the request body and logs it at Debug level after passing it through `readBody`: [2](#0-1) 

`readBody` calls `readSanitizedJSON`, which unmarshals the body into a flat `map[string]any` and only redacts **top-level** keys matching `isBlacklisted`: [3](#0-2) 

The blacklist itself is a small, hardcoded set of key names (`password`, `newpassword`, `oldpassword`, etc., plus a substring match on "password"): [4](#0-3) 

Because `cleaned[k] = v` copies nested objects/arrays verbatim without recursing, any secret-bearing field that is not a literal top-level key — e.g. GraphQL's `POST /query` body shape `{"query": "...", "variables": {"password": "..."}}`, or any endpoint whose payload wraps fields under an `input`/`data`/nested object — is copied through untouched and logged in cleartext: [5](#0-4) 

The GraphQL endpoint is reachable pre-authentication at the router level (auth is enforced by `auth.AuthenticateGQL` inside the handler chain, but the body is already captured and logged by the earlier global `loggerFunc` middleware regardless of auth outcome), and many mutations (e.g. password reset flows) pass sensitive values inside a nested `variables` object rather than as a bare top-level `password` key.

### Impact Explanation
When `Log.Level = 'debug'` is configured (a supported, documented configuration, see `docs/CONFIG.md`), any request whose sensitive fields are nested — most notably GraphQL mutation variables — will have those secrets (passwords, tokens, keys passed through nested request objects) written unredacted to the node's log file. An actor who later obtains that log file (via log shipping, audit forwarding, support bundle, or a `Log.File` disk write with the node's `AUDIT_LOGGER`) directly recovers credentials, mirroring the exact CVE-2026-0905 bug class of "insufficient policy enforcement causing sensitive data to leak via a log artifact."

### Likelihood Explanation
Requires the node operator to have Debug logging enabled (not default, but a documented and used configuration for troubleshooting) and requires the log artifact to be exposed to the attacker afterward (shared log bundle, misconfigured log shipping, `Log.File` dir readable, or `AuditLogger` forwarding). No special privilege is needed to trigger the vulnerable code path itself — any client hitting `/query` (or any JSON endpoint with nested secret fields) with debug logging on will have their nested secrets logged in the clear.

### Recommendation
Make `readSanitizedJSON`/`redact` recurse into nested maps and arrays, applying `isBlacklisted` at every depth, or switch to a deny-list-based deep-redaction walker (or an allow-list of loggable fields) so nested secret fields cannot bypass sanitization regardless of JSON structure.

### Proof of Concept
1. Enable `Log.Level = 'debug'` on a running Chainlink node.
2. Send `POST /query` with body:
```json
{"query":"mutation($p:String!){ setUserPassword(password:$p) }","variables":{"password":"SuperSecret123!"}}
```
3. Inspect the node's debug log output produced by `loggerFunc` — the `body` field contains `"variables":{"password":"SuperSecret123!"}` unredacted, because `readSanitizedJSON` only checked the top-level keys `query` and `variables`, not the nested `password` key.

### Citations

**File:** core/web/router.go (L64-72)
```go
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
```

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

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

**File:** core/web/router.go (L608-629)
```go
func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	err := json.Unmarshal(buf.Bytes(), &dst)
	if err != nil {
		return "", err
	}

	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}

	b, err := json.Marshal(cleaned)
	if err != nil {
		return "", err
	}
	return string(b), err
}
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
