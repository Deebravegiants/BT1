Audit Report

## Title
OAuth authorization code disclosed in plaintext node logs via global request-body logging middleware - ([File: core/web/router.go])

## Summary
The gin router's global `loggerFunc` middleware logs the sanitized request body of every HTTP request at Debug level, but the sanitization (`isBlacklisted`) only redacts password-related keys, not OAuth-related fields like `code`. The OIDC `handleTokenExchange` handler accepts the OAuth authorization `code` in the JSON body and is registered on the same router group that inherits this logging middleware, so the code is written to node logs verbatim whenever a user completes OIDC login with Debug-level logging enabled.

## Finding Description
`NewRouter` attaches `loggerFunc(app.GetLogger())` as a global middleware on the gin engine [1](#0-0) . `loggerFunc` reads and restores the request body, then unconditionally logs it via `Debugw(..., "body", readBody(rdr, lggr), ...)` after every request [2](#0-1) . `readBody` parses the body as JSON and calls `readSanitizedJSON`, which redacts only keys present in the `blacklist` map or containing the substring "password" [3](#0-2) . The blacklist covers only `password`, `newpassword`, `oldpassword`, `current_password`, and `new_account_password` — no OAuth/token-related keys [4](#0-3) .

The OIDC token-exchange handler `handleTokenExchange` binds `ExchangeTokenRequest{Code, State}` from the JSON body, where `Code` is the OAuth authorization code from the identity provider, then calls `oi.oauth2Config.Exchange(ctx, req.Code)` [5](#0-4) [6](#0-5) . This handler is wired into the router via `app.AuthenticationProvider().ExtendRouter(api)`, where `api` is the same route group under `engine.Use(...)`, meaning it inherits `loggerFunc` [7](#0-6) . Because `code` is absent from the blacklist, it passes through `readSanitizedJSON` unredacted and is logged in cleartext at Debug level.

This is a real, code-confirmed logic gap: the redaction is a hardcoded keyword blacklist that predates the OIDC feature and was never extended to cover OAuth-specific sensitive fields.

## Impact Explanation
This is an information-disclosure issue affecting confidentiality of a single-use OAuth authorization code, not authentication bypass, key exfiltration, or fund movement. Impact is bounded: the code is single-use and short-lived (OAuth authorization codes typically expire within seconds/minutes and become invalid immediately after being exchanged by `handleTokenExchange` itself, which happens before the log line is even written since `readBody`/exchange occurs, then `c.Next()` runs the handler, then the deferred log write happens after the exchange has already consumed the code in most flows). Practical exploitation additionally requires an attacker to have read access to node Debug-level logs — a condition equivalent to log-aggregation or debug-bundle access, which is closer to operator/host-adjacent access than a capability of a fully unprivileged remote API client. The claim itself acknowledges this bound ("impact is bounded by the single-use nature of the OAuth code and the requirement for log access").

## Likelihood Explanation
Triggering the log write requires no privilege — any user completing a normal OIDC login flow causes their own authorization code to be logged. However, actually leveraging the disclosure for compromise requires: (1) the node operator to run with Debug logging enabled (not default), and (2) an attacker to separately obtain access to those logs (log aggregation system, support ticket, debug bundle) — a precondition outside the "unprivileged remote client" threat model this program is scoped to. The victim's own code being logged does not let that same unprivileged actor compromise anyone else's session or the node itself; it requires an additional log-access privilege that is explicitly excluded ("operator-only," "host-level," "database or host access" are rejection categories per the rules).

## Recommendation
Extend `blacklist`/`isBlacklisted` in `core/web/router.go` to include OAuth/session-sensitive fields (`code`, `token`, `access_token`, `id_token`, `refresh_token`, `secret`), or exempt the OIDC token-exchange route from full-body debug logging, or move to allowlist/struct-tag-driven redaction. This is a legitimate defense-in-depth hardening recommendation even though it does not meet the bar for an in-scope, unprivileged-triggerable, concretely impactful bounty finding.

## Proof of Concept
Not applicable as an accepted in-scope finding — see impact/likelihood rationale. To confirm the logging behavior for hardening purposes: enable OIDC and set `Log.Level = debug`, complete a login, and observe that the Debug log line for the token-exchange request contains the raw `code` value unredacted, per the code paths cited above.

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

**File:** core/web/router.go (L78-107)
```go
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

	err = app.AuthenticationProvider().ExtendRouter(api)
	if err != nil {
		return nil, err
	}

	return engine, nil
}
```

**File:** core/web/router.go (L534-568)
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
	}
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

**File:** core/sessions/oidcauth/oidc.go (L54-58)
```go
// ExchangeTokenRequest represents the expected JSON payload from the frontend
type ExchangeTokenRequest struct {
	Code  string `json:"code" binding:"required"`
	State string `json:"state"`
}
```

**File:** core/sessions/oidcauth/oidc.go (L163-196)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
		return
	}

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}
```
