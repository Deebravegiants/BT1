## Title
CORS misconfiguration allows credentialed cross-origin requests when `WebServer.AllowOrigins = '*'` - (File: core/web/router.go)

### Summary
Chainlink's Web UI/API server builds its CORS policy via `uiCorsHandler` in `core/web/router.go`, which hardcodes `AllowCredentials: true` while also permitting the operator-configurable `AllowOrigins` setting to be `'*'`. When set to `'*'`, `AllowAllOrigins: true` is set on the `gin-contrib/cors` config alongside `AllowCredentials: true`. This mirrors the same bug class as the hono advisory: a CORS layer configured with `credentials: true` and an unrestricted origin, which causes cookie-authenticated requests to be accepted from arbitrary third-party origins. [1](#0-0) 

### Finding Description
`uiCorsHandler` is wired into every request to the node's HTTP API (which serves the authenticated session-cookie-based GUI/API, including `/query` GraphQL and `/v2/...` REST endpoints) via `engine.Use(..., cors, ...)` in `NewRouter`. [2](#0-1) 

The handler always sets `AllowCredentials: true` (needed because the UI relies on session cookies, `sessionStore := cookie.NewStore(secret)`), and if the operator sets `AllowOrigins = '*'`, it sets `AllowAllOrigins = true` on the same config:
```go
c := cors.Config{
    ...
    AllowCredentials: true,
    MaxAge:           math.MaxInt32,
}
if ao == "*" {
    c.AllowAllOrigins = true
}
``` [3](#0-2) 

This is explicitly documented as a supported (if "not recommended") configuration option: `AllowOrigins = '*'` "allow[s] the UI to work from any URL." [4](#0-3) 

The existing test suite confirms the resulting behavior: with `AllowOrigins = "*"`, *any* `Origin` header — including origins unrelated to the deployment (`http://chainlink.com` and `http://localhost:3000` both succeed) — is accepted with an `http.StatusOK` response, i.e. the CORS layer does not fail closed for arbitrary origins despite `AllowCredentials: true` being set:
```go
{"*", "http://chainlink.com", http.StatusOK},
{"*", "http://localhost:3000", http.StatusOK},
``` [5](#0-4) 

This is the same root-cause bug class as GHSA-88fw-hqm2-52qc: a CORS middleware combining `credentials: true` with an unrestricted/wildcard origin, causing the incoming `Origin` to effectively be allowed and credentials headers to be emitted for any requester, rather than failing closed per the CORS spec's prohibition on combining `*` with credentials.

### Impact Explanation
If an operator sets `AllowOrigins = '*'` (a documented, supported value), any third-party website visited by a logged-in Chainlink node operator can issue credentialed cross-origin requests (using the operator's session cookie) against the node's authenticated API/GraphQL endpoints (`/query`, `/v2/...`) and read the responses. This can expose node configuration, job/run data, keys metadata, and other authenticated data, and potentially allow state-changing requests (e.g., job management) depending on which endpoints are reachable via simple/non-simple credentialed requests.

### Likelihood Explanation
Exploitation requires the operator to have configured `AllowOrigins = '*'`, which is explicitly offered and documented in `core/config/docs/core.toml` and `docs/CONFIG.md` as a way to "allow the UI to work from any URL." Given documentation frames it as merely "not recommended for security reasons" rather than clearly dangerous, and it is a common quick-fix for CORS troubleshooting, some deployments are plausibly running with this setting, making the likelihood non-trivial for an unprivileged remote-origin attacker once a victim operator is logged in.

### Recommendation
- Disallow (or strongly warn/reject at config-validation time) the combination of `AllowOrigins = '*'` with `AllowCredentials: true` in `uiCorsHandler` (`core/web/router.go`), consistent with the CORS specification that forbids combining a wildcard origin with credentialed requests.
- When `AllowOrigins = '*'` is configured, either disable `AllowCredentials` or require the operator to enumerate explicit trusted origins instead.
- Update documentation in `core/config/docs/core.toml`/`docs/CONFIG.md` to state clearly that `'*'` is incompatible with cookie/session-based authentication and should not be used in production.

### Proof of Concept
1. Deploy a Chainlink node with `WebServer.AllowOrigins = '*'` (a supported configuration).
2. Log in to the node's Web UI as a legitimate operator (session cookie set).
3. Have the operator visit an attacker-controlled page that issues `fetch('https://<node>/v2/...', { credentials: 'include' })` from an arbitrary origin.
4. As shown by `TestCors_OverrideOrigins` in `core/web/cors_test.go` (lines 43-55), the CORS layer accepts the request from any `Origin` with `http.StatusOK`, meaning `Access-Control-Allow-Origin`/`Access-Control-Allow-Credentials` are returned in a way that lets the browser complete the credentialed request and expose the response to the attacker page.

### Citations

**File:** core/web/router.go (L56-72)
```go
	sessionStore := cookie.NewStore(secret)
	sessionStore.Options(config.WebServer().SessionOptions())
	cors := uiCorsHandler(config.WebServer().AllowOrigins())
	if prometheus != nil {
		prometheusUse(prometheus, engine, promhttp.HandlerOpts{EnableOpenMetrics: true})
	}

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

**File:** core/web/router.go (L571-586)
```go
// Add CORS headers so UI can make api requests
func uiCorsHandler(ao string) gin.HandlerFunc {
	c := cors.Config{
		AllowMethods:     []string{"GET", "POST", "PATCH", "DELETE"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           math.MaxInt32,
	}
	if ao == "*" {
		c.AllowAllOrigins = true
	} else if allowOrigins := strings.Split(ao, ","); len(allowOrigins) > 0 {
		c.AllowOrigins = allowOrigins
	}
	return cors.New(c)
}
```

**File:** core/config/docs/core.toml (L182-185)
```text
# You should set this to the external URL that you use to access the Chainlink UI.
#
# You can set `AllowOrigins = '*'` to allow the UI to work from any URL, but it is recommended for security reasons to make it explicit instead.
AllowOrigins = 'http://localhost:3000,http://localhost:6688' # Default
```

**File:** core/web/cors_test.go (L43-55)
```go
func TestCors_OverrideOrigins(t *testing.T) {
	t.Parallel()

	tests := []struct {
		allow      string
		origin     string
		statusCode int
	}{
		{"http://chainlink.com", "http://chainlink.com", http.StatusOK},
		{"http://chainlink.com", "http://localhost:3000", http.StatusForbidden},
		{"*", "http://chainlink.com", http.StatusOK},
		{"*", "http://localhost:3000", http.StatusOK},
	}
```
