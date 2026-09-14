Confirmed: `loggerFunc` (registered globally via `engine.Use(...)` at [1](#0-0) ) wraps every route including `/query` (the GraphQL endpoint) at [2](#0-1) . It logs the full raw request body via `readBody`/`readSanitizedJSON`, which only redacts **top-level** JSON keys against a small hardcoded blacklist.

### Title
Sensitive credentials in nested GraphQL request bodies are logged in plaintext due to shallow top-level-only redaction - (File: core/web/router.go)

### Summary
The Chainlink node's HTTP request logging middleware attempts to redact sensitive fields (passwords, secrets) from logged request bodies, but the redaction logic only inspects top-level JSON keys. Since the node's primary API surface, GraphQL (`POST /query`), always wraps user-supplied sensitive data one level deeper inside a `variables` object, the redaction is bypassed entirely and secrets are written to node logs in cleartext.

### Finding Description
Every HTTP request passes through `loggerFunc`, applied globally via `engine.Use(...)`: [1](#0-0) . For each request it reads and logs the entire body: [3](#0-2) .

The body is passed through `readBody` → `readSanitizedJSON`, which unmarshals the JSON into a flat `map[string]any` and redacts only keys matching a fixed blacklist (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`, or any key containing "password"): [4](#0-3) .

This blacklist check operates on the top-level keys of the decoded JSON object only — it does not recurse into nested objects. The node's GraphQL API is mounted at `POST /query` and is subject to the same `loggerFunc` middleware: [2](#0-1) . GraphQL request bodies are always shaped as `{"query": "...", "variables": {...}}`, so any sensitive field supplied by the client — e.g. `variables.input.password` (login, `createAPIToken`, password change) — sits inside a nested object under the top-level key `variables`, not `password` itself. As a result, `isBlacklisted("variables")` returns `false` and the entire `variables` object, including the plaintext password, is preserved unredacted and written to the log at Debug level.

This is confirmed by the shape of GraphQL mutations exercised in tests, e.g. `createAPIToken` sends `{"input": {"password": "..."}}` as `variables` [5](#0-4) , and the equivalent for session/login flows sends `email`/`password` similarly nested. The legacy `/sessions` REST endpoint is safe because it posts a flat `{"email":..., "password":...}` object where `password` is a top-level key that the blacklist does catch — but the GraphQL path, which is now the primary API used by the UI/CLI, is not.

### Impact Explanation
Any unprivileged client (an attacker attempting/failing login, or a legitimate admin) sending a GraphQL mutation containing a password (login attempts, password changes, API token creation) causes that plaintext password to be persisted in the node's Debug logs. Anyone with read access to node logs (log aggregation systems, support tooling, misconfigured log shipping, or an attacker who gains any log-read access) can recover operator credentials, directly enabling full node takeover (fund movement via job/transaction management, key management, bridge/EI configuration). This mirrors the underlying bug class in the reported incident: sensitive tokens/secrets being disclosed via inadequately protected logging/storage paths.

### Likelihood Explanation
High reachability: this triggers on completely standard, unprivileged use of the primary GraphQL API (e.g., every login attempt — including failed ones from any external client), with no special preconditions other than the node running with Debug-level logging enabled (a common non-default-but-realistic operational configuration for troubleshooting). No authentication bypass is needed to trigger the log write itself; the vulnerability is in what gets persisted whenever any client (including an attacker probing credentials) hits `/query`.

### Recommendation
Make `readSanitizedJSON` recursively walk nested objects/arrays and redact blacklisted keys at any depth, not just the top level. Additionally, consider redacting the whole `variables` payload for the GraphQL endpoint by default, or maintaining an explicit denylist of sensitive GraphQL field names (`password`, `secret`, `newPassword`, `oldPassword`, `token`, `accessKey`, `webauthndata`) applied recursively before logging.

### Proof of Concept
1. Run a Chainlink node with Debug-level logging.
2. Send `POST /query` with body:
```json
{"query":"mutation($input: CreateAPITokenInput!){ createAPIToken(input:$input){ ... on CreateAPITokenSuccess { token { accessKey secret } } } }","variables":{"input":{"password":"SuperSecretAdminPass123"}}}
```
3. Observe the node's debug log line emitted by `loggerFunc` — the `body` field contains the full JSON including `"password":"SuperSecretAdminPass123"` in cleartext, because `readSanitizedJSON` only redacted top-level keys (`query`, `variables`), not the nested `password` field inside `variables.input`.

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

**File:** core/web/resolver/api_token_test.go (L40-49)
```go
	variables := map[string]any{
		"input": map[string]any{
			"password": defaultPassword,
		},
	}
	variablesIncorrect := map[string]any{
		"input": map[string]any{
			"password": "wrong-password",
		},
	}
```
