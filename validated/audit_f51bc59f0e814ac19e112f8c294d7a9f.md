## Finding

`core/web/router.go`'s HTTP request logger logs the **entire raw JSON request body** for every request hitting the node's API — before any authentication middleware runs — and only redacts fields whose key name contains `"password"`. Any other secret-bearing field name (`secret`, `token`, `apiKey`, `accessKey`, `webAuthnData`, private keys embedded in job/bridge specs, etc.) is logged in plaintext at Debug level.

### Title
Node API request logger only redacts "password"-named fields, leaking other secrets to logs - (`core/web/router.go`)

### Summary
`loggerFunc` is registered as global middleware on the gin engine, ahead of the authenticated route group and session middleware, so it runs for **every** inbound request regardless of authentication outcome. It reads the full request body and passes it to `readSanitizedJSON`, which only redacts top-level JSON keys matching a hardcoded blacklist (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) or any key containing the substring `"password"`. Any other field carrying sensitive data — API secrets, tokens, WebAuthn assertions, or credential/URL strings embedded in job/bridge/config specs — is written verbatim into the node's Debug logs.

### Finding Description [1](#0-0) 
`loggerFunc` is wired directly on `engine.Use(...)`, applied to the whole gin engine before the `api` route group (which is where session/token auth middleware is attached). This means an unauthenticated, unprivileged caller's raw request body is captured and logged regardless of whether the request later succeeds or fails authentication. [2](#0-1) 
`loggerFunc` reads `c.Request.Body`, restores it for downstream handlers, then logs `"body": readBody(rdr, lggr)` at `Debugw`. [3](#0-2) 
`readBody` → `readSanitizedJSON` unmarshals the body into `map[string]any` and only redacts a value when `isBlacklisted(k)` is true for the top-level key. [4](#0-3) 
`isBlacklisted` only matches keys equal to (or containing the substring) `"password"`. It has no entries for `secret`, `token`, `apikey`, `accesskey`, `webauthndata`, or any nested-field redaction — the sanitizer is not recursive, so nested objects/arrays bypass the blacklist entirely even for `"password"`-named sub-fields.

Concrete request shapes in this codebase that carry non-"password"-named secrets and would be logged raw at Debug level include:
- `core/sessions/session.go` `SessionRequest.WebAuthnData` (`json:"webauthndata"`) [5](#0-4) 
- `core/web/external_initiators_controller.go` external-initiator creation bodies (name/url only in request, but any client-supplied extra JSON with a `secret`/`token` key, or malformed/probing requests containing such fields, are logged as-is) [6](#0-5) 
- Job/spec/bridge creation endpoints that accept free-form TOML/JSON strings which may embed RPC URLs with API keys or vault credentials.

### Impact Explanation
Any secret whose JSON field name does not contain "password" — sent in a request body to the node's HTTP API, by an authenticated or even unauthenticated caller (since the logger fires before auth) — is persisted in plaintext in the node's logs. If those logs are shipped to a third-party aggregator, mounted with broad read access, or exposed via debug/log endpoints, an attacker gains access to credentials/tokens without needing to compromise the primary datastore — directly analogous to the LastPass incident where secrets stored/transiting through an intermediary service were exposed. This is a `key/secret disclosure` class issue reachable from unprivileged client requests.

### Likelihood Explanation
Requires the node to run with Debug-level logging enabled (a common, often default, operational configuration for these nodes) and requires an operator/attacker to be able to read the resulting logs. The request-body capture itself requires no authentication and no special conditions — merely sending a request (even a failed login/API call) with a secret-bearing field is sufficient to have it written to logs.

### Recommendation
- Make `isBlacklisted`/`readSanitizedJSON` deny-list broader and defense-in-depth: redact by default and allow-list only known-safe fields, or use an explicit set covering `secret`, `token`, `key`, `apikey`, `accesskey`, `webauthndata`, etc.
- Make sanitization recursive over nested JSON objects/arrays, not just top-level keys.
- Consider not logging request bodies at all for authentication-adjacent endpoints (`/sessions`, external initiator, API token endpoints), or move body logging to occur only for successfully authenticated non-sensitive routes.

### Proof of Concept
1. Run a chainlink node with `Database.LogQueries`-equivalent Debug logging enabled for the web logger (i.e., `-loglevel debug` or similar).
2. Send: `POST /sessions` with body `{"email":"a@b.com","password":"pw","secret":"MY-LEAKED-TOKEN"}`.
3. Observe the node's debug log line for this request: the `password` value is replaced with `*REDACTED*`, but `"secret":"MY-LEAKED-TOKEN"` appears verbatim in the logged `body` field. [7](#0-6)

### Citations

**File:** core/web/router.go (L63-71)
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
```

**File:** core/web/router.go (L533-568)
```go
// Inspired by https://github.com/gin-gonic/gin/issues/961
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

**File:** core/web/router.go (L588-629)
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

**File:** core/sessions/session.go (L16-22)
```go
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```

**File:** core/web/external_initiators_controller.go (L62-76)
```go
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

```
