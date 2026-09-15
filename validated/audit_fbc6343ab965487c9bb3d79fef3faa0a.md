Audit Report

## Title
Non-Recursive JSON Body Redaction Leaks Passwords/Secrets in Debug Logs - (File: core/web/router.go)

## Summary
The `loggerFunc` middleware, wired globally via `engine.Use(...)` in `NewRouter` and thus applied to `/query` (GraphQL) and `/sessions` routes, logs every request body at debug level through `readBody` → `readSanitizedJSON` [1](#0-0) [2](#0-1) . `readSanitizedJSON` only redacts blacklisted keys found at the top level of the parsed JSON object, copying nested sub-objects verbatim into the logged output [3](#0-2) .

## Finding Description
`readSanitizedJSON` unmarshals the body into `map[string]any` and iterates only the top-level keys, checking each against `isBlacklisted` (password, newpassword, oldpassword, current_password, new_account_password, or any key containing "password") [4](#0-3) . Any key not matching is copied unmodified — including entire nested objects — before being re-marshalled for the debug log line [5](#0-4) . Since GraphQL mutation arguments (e.g., `UpdatePasswordInput.oldPassword`/`newPassword`, `CreateAPITokenInput.password`) are transmitted nested under a top-level `variables` key rather than as a top-level key itself, the sanitizer never inspects them, and they are logged in plaintext whenever `Debugw` is enabled. This is confirmed directly in the current code of `core/web/router.go`, and the `/query` route is registered under the same global `loggerFunc` middleware as all other routes [6](#0-5) .

## Impact Explanation
This causes plaintext disclosure of user passwords (and API-token passwords) into node debug logs, defeating the explicit intent of the existing `blacklist`/`isBlacklisted` redaction mechanism. This falls under a secret-exfiltration impact class since credentials that are supposed to be redacted before persistence/log-shipping end up recoverable from log output.

## Likelihood Explanation
Triggering the leak requires no privilege beyond making a normal `/query` or `/sessions` request with a password-bearing GraphQL mutation (e.g., `updateUserPassword`, `createAPIToken`) — this is fully reachable by any authenticated (or, for login, unauthenticated) client. However, actually reading the leaked value additionally requires (a) `Debugw`-level logging enabled on the node, and (b) access to the resulting log stream, which is an operator/log-infrastructure artifact rather than something a remote unprivileged network attacker can read directly. This reduces but does not eliminate real-world likelihood, since debug logging is common during troubleshooting and logs are frequently shipped to shared aggregators with a broader audience than password-holders.

## Recommendation
Make `readSanitizedJSON` recursive: walk nested maps and slices and redact any key matching `isBlacklisted` at every nesting level (not just top level) before marshalling the value used in the debug log line.

## Proof of Concept
1. Run a chainlink node with debug-level logging enabled.
2. POST to `/query` with body:
```json
{
  "query": "mutation UpdateUserPassword($input: UpdatePasswordInput!) { updateUserPassword(input: $input) { ... } }",
  "variables": {"input": {"oldPassword": "SuperSecret123!", "newPassword": "NewSecret456!"}}
}
```
3. Inspect the emitted `Debugw` log line from `loggerFunc` (`core/web/router.go:556-567`) and observe the `body` field contains the full `variables.input` object with `oldPassword`/`newPassword` unredacted, since only the top-level keys `query` and `variables` were checked against `isBlacklisted`.

### Citations

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
