Confirmed: the GraphQL mutations `createAPIToken` and `updateUserPassword` accept passwords via nested `variables.input.password` / `variables.input.oldPassword`/`newPassword` fields [1](#0-0) [2](#0-1) , and these requests flow through the global `/query` POST route protected only by `loggerFunc`, which is registered as a global `engine.Use()` middleware for every route including GraphQL [3](#0-2) .

## Root cause

`loggerFunc` reads the full request body and logs it at Debug level via `readBody`/`readSanitizedJSON` [4](#0-3) . The redaction logic in `readSanitizedJSON` only inspects **top-level** keys of the parsed JSON object and redacts a value only if the key itself matches the `blacklist` (or contains the substring `"password"`): [5](#0-4) 

Because the GraphQL protocol wraps mutation arguments inside a nested `"variables"` object — e.g. `{"query": "...", "variables": {"input": {"password": "..."}}}` for `createAPIToken`, or `{"input": {"oldPassword": "...", "newPassword": "..."}}` for `updateUserPassword` — the sensitive key `password`/`oldPassword`/`newPassword` is never a top-level key of the request JSON. `readSanitizedJSON`'s non-recursive `for k, v := range dst` loop [6](#0-5)  only sees `"query"` and `"variables"` as top-level keys, neither of which is blacklisted, so the entire `variables` object — including the plaintext password/secret payload — is logged verbatim at Debug level.

This is a close analog of the Nomad CVE-2025-1296 bug class (CWE-532, sensitive-value exposure in logs due to insufficient/incomplete redaction in a request-logging path), though here the leaked value is the user's plaintext password rather than a workload identity token, and it manifests through the internet-facing GraphQL gateway rather than an audit subsystem.

### Title
Plaintext passwords leaked in Debug-level HTTP request logs for GraphQL mutations due to non-recursive JSON redaction - (File: `core/web/router.go`)

### Summary
The Gin request-logging middleware `loggerFunc` logs the full JSON request body for every API call, including the GraphQL `/query` endpoint. Its sanitization helper `readSanitizedJSON` only redacts top-level JSON keys matching a password blacklist, but GraphQL requests nest sensitive fields (e.g., `password`, `oldPassword`, `newPassword`) inside a `variables` object, so they bypass redaction entirely and are written to logs in plaintext.

### Finding Description
`loggerFunc` is registered globally via `engine.Use(...)` and therefore wraps every route, including `POST /query` (GraphQL) [3](#0-2) . It reads the raw request body and logs it via `readBody`, which calls `readSanitizedJSON` for redaction [7](#0-6) . `readSanitizedJSON` unmarshals the body into a flat `map[string]any` and only redacts entries whose top-level key matches `isBlacklisted` [8](#0-7) [9](#0-8) . GraphQL request bodies place mutation arguments under a nested `variables` key — for example the `createAPIToken` mutation's `CreateAPITokenInput.password` and the `updateUserPassword` mutation's `UpdatePasswordInput.oldPassword`/`newPassword` fields [1](#0-0) [2](#0-1) . Since the redaction only checks the top level (`query`, `variables`), the nested passwords are logged unredacted at Debug level.

### Impact Explanation
Any unprivileged HTTP client that calls the authenticated `/query` GraphQL endpoint with `createAPIToken` or `updateUserPassword` (or any other mutation carrying sensitive nested input) causes the node to write the plaintext password to its own logs. If Debug logging is enabled (a supported, documented configuration) or logs are forwarded/aggregated to a centralized system, this results in plaintext credential disclosure (CWE-532) to anyone with log access — matching the confidentiality-only impact profile of the referenced CVE (C:H/I:N/A:N).

### Likelihood Explanation
Likelihood is moderate: exploitation requires Debug-level logging to be enabled on the node (not default) and requires the attacker/observer to have access to application logs, but no special privilege is required to trigger the leak itself — a normal authenticated user's `updateUserPassword` or `createAPIToken` call, or even an unauthenticated call that reaches the middleware before authentication fails, generates the leaking log line since `loggerFunc` runs before route-specific auth checks.

### Recommendation
Make `readSanitizedJSON`'s redaction recursive so it walks nested objects/arrays (including under `variables`), or apply the blacklist check to GraphQL variable payloads specifically before logging. Alternatively, exclude the `/query` route body from verbose logging entirely, or ensure the blacklist is enforced against every JSON path, not just top-level keys.

### Proof of Concept
1. Enable Debug logging (`Log.Level = 'debug'`).
2. As an authenticated user, send:
```
POST /query
{
  "query": "mutation UpdateUserPassword($input: UpdatePasswordInput!) { updateUserPassword(input: $input) { ... } }",
  "variables": {"input": {"oldPassword": "CurrentPlainText123", "newPassword": "NewPlainText456"}}
}
```
3. Inspect node logs — the `loggerFunc` Debug log line's `"body"` field will contain the full `variables` object with `oldPassword`/`newPassword` unredacted, because `readSanitizedJSON` only checked the top-level keys `query`/`variables` against the blacklist [6](#0-5) .

### Citations

**File:** core/web/schema/type/api_token.graphql (L6-8)
```text
input CreateAPITokenInput {
    password: String!
}
```

**File:** deployment/environment/web/sdk/internal/schema.graphql (L1117-1120)
```text
input UpdatePasswordInput {
    oldPassword: String!
    newPassword: String!
}
```

**File:** core/web/router.go (L64-99)
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
	if prometheus != nil {
		engine.Use(prometheus.Instrument())
	}
	engine.Use(helmet.Default())
	rl := config.WebServer().RateLimit()
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
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())

	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

**File:** core/web/router.go (L534-567)
```go
func loggerFunc(lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		buf, err := io.ReadAll(c.Request.Body)
		if err != nil {
			lggr.Error("Web request log error: ", err.Error())
			// Implicitly relies on limits.RequestSizeLimiter
			// overriding of c.Request.Body to abort gin's Context
			// inside io.ReadAll.
			// Functions as we would like, but horrible from an architecture
			// and design pattern perspective.
			if !c.IsAborted() {
				c.AbortWithStatus(http.StatusBadRequest)
			}
			return
		}
		rdr := bytes.NewBuffer(buf)
		c.Request.Body = io.NopCloser(bytes.NewBuffer(buf))

		start := time.Now()
		c.Next()
		end := time.Now()

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

**File:** core/web/router.go (L588-606)
```go
func readBody(reader io.Reader, lggr logger.Logger) string {
	buf := new(bytes.Buffer)
	_, err := buf.ReadFrom(reader)
	if err != nil {
		lggr.Warn("unable to read from body for sanitization: ", err)
		return "*FAILED TO READ BODY*"
	}

	if buf.Len() == 0 {
		return ""
	}

	s, err := readSanitizedJSON(buf)
	if err != nil {
		lggr.Warn("unable to sanitize json for logging: ", err)
		return "*FAILED TO READ BODY*"
	}
	return s
}
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
