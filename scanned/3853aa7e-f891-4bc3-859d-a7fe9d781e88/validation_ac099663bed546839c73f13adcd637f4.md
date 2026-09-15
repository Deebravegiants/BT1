### Title
Incomplete credential redaction in HTTP request-body debug logging - (File: core/web/router.go)

### Summary
The chainlink node's HTTP request logging middleware `loggerFunc` reads and logs every incoming request body (and query string) at Debug level, redacting only fields whose key name contains the substring "password". This mirrors the CVE-2023-51390 bug class: a component logs out inbound configuration/credential-bearing payloads in plaintext, relying on an incomplete, hard-coded blacklist rather than exhaustively sanitizing sensitive fields.

### Finding Description
`loggerFunc` in `core/web/router.go` is installed as global middleware on every API route via `NewRouter`. [1](#0-0) 
It reads the full request body, buffers it, then logs it via `readBody`/`readSanitizedJSON`, and logs the query string via `redact`: [2](#0-1) 

Both sanitization helpers rely on a single, shallow, substring-based blacklist: [3](#0-2) 

Key weaknesses in this redaction logic:
1. **Only top-level keys are inspected.** `readSanitizedJSON` unmarshals into `map[string]any` and copies non-blacklisted values verbatim without recursing into nested objects/arrays, so any credential nested one level deep (e.g., inside a job spec's TOML string, an object body, or a config sub-map) is logged unredacted.
2. **The blacklist is name-based and incomplete**, covering only `password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password` (or any key containing the substring `password`). It does not cover other credential-bearing field names used elsewhere in the codebase, such as `IncomingToken`/`OutgoingToken`/`OutgoingSecret`/`AccessKey` (`core/bridges/bridge_type.go`, `core/bridges/external_initiator.go`), `ClientSecret` (WebServer OIDC), `AuthToken` (Pyroscope/Prometheus), or LDAP/API-key/secret style fields.
3. Because this logging is unconditional middleware applied to **every** route (`api.Use(...)` chain), any authenticated (or even attempted) request body — including ones from lower-privileged sessions/API tokens hitting endpoints they're allowed to call — gets written to the node's Debug logs verbatim for any field not literally named with "password" in it.

This is directly analogous to the journalpump CVE: a logging code path dumps a submitted configuration/credential payload to the log pipeline with only partial, ad hoc redaction, so real credential material intended to remain secret is written in plaintext into logs that may be shipped to file storage, log aggregation, or forwarded off-node (e.g., via `Log.File`, or downstream log shipping configured by the operator).

### Impact Explanation
If Debug logging is enabled (a supported, documented log level, not a debug-only build flag — see `docs/CONFIG.md` / `core/config/docs/core.toml` `[Log] Level` options), any credential field not named with "password" that is submitted through the API (e.g., bridge/external-initiator secrets returned or manipulated through admin endpoints, OIDC client secrets, audit logger auth headers echoed in requests, or any nested secret inside a JSON body) is captured in the node's logs. These logs are often persisted to disk (`Log.File`) or shipped to external aggregators, giving any actor with log access — which may have a different (lower) trust boundary than the API itself — a path to credential disclosure. This satisfies the "key/secret disclosure" acceptance criterion.

### Likelihood Explanation
Requires the node operator to have `Log.Level = 'debug'` configured, which is a supported, non-default but commonly-used operational setting (e.g., explicitly used in the project's own txtar test fixtures `testdata/scripts/node/validate/disk-based-logging.txtar`). No special privilege is needed by the client sending the request — the vulnerability is in the server-side logging path, triggered by the mere existence of any authenticated (or default-open) endpoint request containing a credential field the blacklist doesn't recognize.

### Recommendation
- Replace the substring/top-level blacklist approach with a recursive sanitizer that walks nested JSON structures.
- Expand (or better, invert) the sensitive-field detection to a broader denylist/allowlist covering known credential field names used across the codebase (`token`, `secret`, `key`, `clientsecret`, `authtoken`, `accesskey`, `apikey`, etc.), or avoid logging raw bodies altogether at Debug level, only logging a redacted/allow-listed subset of fields per route.
- Consider gating full-body debug logging behind an explicit, separately-documented opt-in flag distinct from general `debug` log level, given the operational risk of accidentally shipping credentials to log sinks.

### Proof of Concept
1. Configure the node with `Log.Level = 'debug'` and `Log.File.Dir` set (as in `testdata/scripts/node/validate/disk-based-logging.txtar`).
2. Send an authenticated API request to any endpoint whose JSON body contains a credential-bearing field whose name does not contain "password" (e.g., a nested object `{"config": {"clientSecret": "abcd1234"}}`, or any object with `token`/`secret`/`accesskey`-style keys).
3. Inspect the node's log output/log file — `loggerFunc` will have logged the `body` field of the request verbatim (since `isBlacklisted` only matches "password"-like keys and `readSanitizedJSON` doesn't recurse into nested objects), exposing the credential in plaintext in the log stream. [4](#0-3) [5](#0-4)

### Citations

**File:** core/web/router.go (L63-72)
```go
	tls := config.WebServer().TLS()
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

**File:** core/web/router.go (L608-658)
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

func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

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
