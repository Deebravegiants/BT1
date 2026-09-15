### Title
GraphQL mutation passwords (e.g. `CreateAPIToken`, `UpdateUserPassword`) are logged in plaintext in the web request debug log due to shallow, top-level-only body redaction - ([File: core/web/router.go])

### Summary
The gin request-logging middleware `loggerFunc` logs the full HTTP request body via `readBody`/`readSanitizedJSON`, which only redacts keys found at the top level of the parsed JSON object. The GraphQL endpoint (`POST /query`) wraps all mutation input (including passwords) inside a nested `variables.input.password` field, which is never inspected or redacted by the blacklist logic, so plaintext passwords sent to authenticated GraphQL mutations such as `CreateAPIToken` and `UpdateUserPassword` are written to the node's debug logs.

### Finding Description
`loggerFunc` is registered as global middleware on the gin engine and applies to every route, including `/query` [1](#0-0) . On every request it buffers the body, lets the handler execute, then logs the body via `readBody` at `Debug` level [2](#0-1) .

`readBody` calls `readSanitizedJSON`, which unmarshals the body into a `map[string]any` and only checks the **top-level keys** of that map against `isBlacklisted` (which matches literal names like `password`, `newpassword`, `oldpassword`, or any key containing the substring `"password"`) [3](#0-2) .

For classic REST endpoints (e.g. `POST /v2/user/token` with body `{"password":"..."}`), the `password` key is at the top level, so it is redacted correctly, as seen in `UserController.NewAPIToken` [4](#0-3) .

However, the GraphQL endpoint `POST /query` submits mutation arguments as a nested JSON structure: `{"query": "...", "variables": {"input": {"password": "..."}}}`. The top-level keys of this body are `query`, `variables`, and possibly `operationName` — never `password`. Because `readSanitizedJSON` does not recurse into nested objects, the `password` field embedded in `variables.input.password` passes through unredacted and is written verbatim to the log.

This directly affects real GraphQL mutations that accept a raw password argument, such as:
- `CreateAPIToken(Input struct{ Password string })`, which authenticates a user's password to mint an API access key/secret [5](#0-4) 
- `UpdateUserPassword` (visible near the same file, using `Input struct{...}` with old/new password fields).

The GraphQL endpoint is guarded by `auth.AuthenticateGQL`, so this is reachable by any already-authenticated (or in the case of a session/API-token-holding, potentially lower-privileged) client submitting a normal mutation call — no special/privileged access or malicious peer is required.

### Impact Explanation
Any user's login password submitted to confirm sensitive operations (e.g., issuing a new API token, or changing their password) is persisted in cleartext in the node's application logs whenever `Log.Level = 'debug'` (a supported, documented configuration, not a hidden or unsupported mode). If those logs are exported, shipped to a log aggregator, or bundled and shared for support/debugging (mirroring exactly the CVE-2025-54120 scenario — logs are not automatically shared, but the risk exists once someone forwards them), an attacker gaining access to the log file recovers the plaintext account password. Given the password is used both for UI login and for confirming API token creation, this is a direct password/credential-disclosure issue with high severity, matching the "secret redaction" analog class described in scope.

### Likelihood Explanation
Requires only: (1) the node operator running with `Log.Level = 'debug'` (a normal, documented, non-privileged config that many operators use for troubleshooting) and (2) any authenticated (or even minimally privileged) client invoking a password-carrying GraphQL mutation like `CreateAPIToken`. This is a routine legitimate action (e.g. the UI itself calls `CreateAPIToken` to mint API keys), so the vulnerable code path executes during normal operation without any adversarial input — the bug is purely in the logging/redaction logic, not in an attacker-crafted payload. Likelihood of the leak occurring is high; the residual risk (someone reading/sharing that log) mirrors the original CVE's stated risk.

### Recommendation
- Make `readSanitizedJSON` recursively redact blacklisted keys at every nesting level (walk `map[string]any` and `[]any` recursively), not just the top level.
- Alternatively/complementarily, avoid logging the raw GraphQL body at all for the `/query` endpoint, or strip password-like fields from `variables` before logging using an explicit denylist of GraphQL mutation input fields.
- Add regression tests asserting that GraphQL mutation bodies containing `variables.input.password` are redacted in the request log output, mirroring existing `TestCheckLoginAuditLog`-style coverage.

### Proof of Concept
1. Start a chainlink node with `Log.Level = 'debug'` in `config.toml`.
2. Authenticate as a normal user (obtain session cookie).
3. Send a GraphQL mutation to `POST /query`:
```json
{
  "query": "mutation CreateAPIToken($input: CreateAPITokenInput!) { createAPIToken(input: $input) { ... on CreateAPITokenSuccess { token { accessKey secret } } } }",
  "variables": { "input": { "password": "MyRealLoginPassword123!" } }
}
```
4. Observe the node's debug log emitted by `loggerFunc` (`core/web/router.go:556-567`): the `"body"` field contains the full JSON body including `"password":"MyRealLoginPassword123!"` in plaintext, because `isBlacklisted` in `readSanitizedJSON` only inspected the top-level keys `query` and `variables`, never descending into `variables.input.password`. [3](#0-2) [6](#0-5) [5](#0-4)

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

**File:** core/web/router.go (L588-658)
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

**File:** core/web/user_controller.go (L243-274)
```go
// NewAPIToken generates a new API token for a user overwriting any pre-existing one set.
func (u *UserController) NewAPIToken(c *gin.Context) {
	ctx := c.Request.Context()
	var request clsession.ChangeAuthTokenRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to create API token"))
		return
	}
	// In order to create an API token, login validation with provided password must succeed
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
	newToken := auth.NewToken()
```

**File:** core/web/resolver/mutation.go (L990-1006)
```go
func (r *Resolver) CreateAPIToken(ctx context.Context, args struct {
	Input struct{ Password string }
}) (*CreateAPITokenPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	session, ok := webauth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return nil, errors.New("Failed to obtain current user from context")
	}
	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

	err = r.App.AuthenticationProvider().TestPassword(ctx, dbUser.Email, args.Input.Password)
```
