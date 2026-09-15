The claim's code citations are accurate. I've confirmed the exact code in `core/web/router.go`:This is a confirmed finding. The `AuthenticateGQL` middleware does *not* block unauthenticated requests (`return` with no `c.Abort()` when no session exists) [1](#0-0) , so `/query` is reachable by unauthenticated clients, and it's up to each resolver to enforce auth — meaning `createAPIToken`/login-related mutations sent by any unprivileged actor will hit `loggerFunc` and have their bodies logged.

Audit Report

## Title
Sensitive credentials in nested GraphQL request bodies are logged in plaintext due to shallow top-level-only redaction - (File: core/web/router.go)

## Summary
`loggerFunc`, registered globally via `engine.Use(...)`, logs every request body at Debug level using `readSanitizedJSON`, which only redacts top-level JSON keys against a small hardcoded blacklist. Since GraphQL requests (`POST /query`) always nest client-supplied data under a top-level `variables` key, any sensitive field such as `variables.input.password` bypasses redaction entirely and is written to logs in cleartext.

## Finding Description
`loggerFunc` is applied globally via `engine.Use(...)` [2](#0-1)  and logs the full request body for every request, including `/query` [3](#0-2) . The body passes through `readBody` → `readSanitizedJSON`, which unmarshals into a flat `map[string]any` and only redacts top-level keys matching `isBlacklisted` (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`, or any key containing "password") [4](#0-3) . This does not recurse into nested objects, so GraphQL payloads shaped `{"query": "...", "variables": {"input": {"password": "..."}}}` have `password` preserved unredacted because `isBlacklisted("variables")` is false.

Critically, `AuthenticateGQL`, the middleware wrapping `/query` [5](#0-4) , does not reject unauthenticated requests — it only attaches a session to context if one exists and calls plain `return` (not `c.Abort()`) otherwise, deferring auth enforcement to individual resolvers [6](#0-5) . This confirms an unprivileged/unauthenticated client can reach `/query` and trigger `loggerFunc`'s body logging, satisfying the "unprivileged actor" requirement. Test fixtures confirm `createAPIToken` sends `{"input": {"password": "..."}}` as `variables` [7](#0-6) .

## Impact Explanation
Any client sending a GraphQL mutation containing a password (login attempts, password changes, API token creation) causes that plaintext password to be persisted in the node's Debug logs. Anyone with read access to node logs can recover operator credentials, enabling node takeover (job/transaction management, key management). This maps to the "key/secret exfiltration" impact category.

## Likelihood Explanation
Reachability is high: the code path triggers on standard use of the primary GraphQL API, and `/query` does not require prior authentication to be hit (auth failure just results in an unauthenticated GQL context, not a rejected request) [1](#0-0) . The only precondition is Debug-level logging enabled, which is a realistic, commonly-used operational configuration.

## Recommendation
Make `readSanitizedJSON` recursively walk nested objects/arrays and redact blacklisted keys at any depth, not just the top level. Additionally, consider redacting the whole `variables` payload for the GraphQL endpoint by default, or maintaining an explicit denylist of sensitive GraphQL field names applied recursively before logging.

## Proof of Concept
1. Run a Chainlink node with Debug-level logging.
2. Send `POST /query` with body:
```json
{"query":"mutation($input: CreateAPITokenInput!){ createAPIToken(input:$input){ ... on CreateAPITokenSuccess { token { accessKey secret } } } }","variables":{"input":{"password":"SuperSecretAdminPass123"}}}
```
3. Observe the node's debug log line emitted by `loggerFunc` — the `body` field contains the full JSON including `"password":"SuperSecretAdminPass123"` in cleartext, because `readSanitizedJSON` only redacted top-level keys (`query`, `variables`), not the nested `password` field inside `variables.input`.

### Citations

**File:** core/web/auth/gql.go (L25-47)
```go
func AuthenticateGQL(authenticator Authenticator, lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		session := sessions.Default(c)
		sessionID, ok := session.Get(SessionIDKey).(string)
		if !ok {
			return
		}

		user, err := authenticator.AuthorizedUserWithSession(ctx, sessionID)
		if err != nil {
			if errors.Is(err, clsessions.ErrUserSessionExpired) {
				lggr.Warnw("Failed to authenticate session", "err", err)
			} else {
				lggr.Errorw("Failed call to AuthorizedUserWithSession, unable to get user", "err", err)
			}
			return
		}

		ctx = WithGQLAuthenticatedSession(c.Request.Context(), user, sessionID)

		c.Request = c.Request.WithContext(ctx)
	}
```

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
