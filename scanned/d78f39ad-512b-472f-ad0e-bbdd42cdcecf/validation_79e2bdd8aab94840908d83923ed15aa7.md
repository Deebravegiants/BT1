## Finding

CVE-2020-25400 describes a cross-domain CORS policy misconfiguration in Taskcafe that lets a remote, unauthenticated attacker read sensitive data (an access token) via cross-origin requests. The chainlink node's Operator UI web server has an analogous CORS configuration pattern.

### Title
Insecure CORS configuration combines wildcard origin with credentialed requests - (File: core/web/router.go)

### Summary
The chainlink node's HTTP router builds its CORS policy with `AllowCredentials: true` unconditionally, and separately allows the operator to configure `AllowOrigins = '*'`, which sets `AllowAllOrigins = true` on the same `cors.Config`. This combination — wildcard origin plus enabled credentials — is the same class of cross-domain trust misconfiguration exploited in CVE-2020-25400, where an overly permissive cross-domain policy allowed disclosure of authenticated session data to any origin.

### Finding Description
The router builds its CORS middleware in `uiCorsHandler`: [1](#0-0) 

Notice `AllowCredentials: true` is set regardless of the origin policy, and if the configured `AllowOrigins` value is `"*"`, `AllowAllOrigins` is also set to `true` on the exact same config object, rather than the code refusing wildcard+credentials together or explicitly disabling credentials in that case.

This middleware is wired into the main router covering all of the authenticated API surface, including session cookie handling: [2](#0-1) 

The node's own documentation explicitly advertises the wildcard option as a supported configuration: [3](#0-2) 

And a dedicated test confirms that setting `AllowOrigins = '*'` causes any arbitrary origin to receive a `200 OK` (i.e., CORS-approved) response from an authenticated route: [4](#0-3) 

Because `AllowCredentials: true` is baked in independent of the origin setting, if an operator (or a default/example deployment) sets `AllowOrigins = '*'`, the `gin-contrib/cors` middleware must echo back the specific requesting `Origin` header (rather than literally responding with `*`) in order for browsers to accept the credentialed response per the Fetch/CORS spec. The practical effect is that any third-party website can issue credentialed (cookie-carrying) XHR/fetch requests to the node's session-protected JSON/GraphQL API and read the responses in the victim's browser — this is functionally the same "overly permissive cross-domain policy leaking authenticated data" bug class as CVE-2020-25400, just triggered via the `AllowOrigins` config knob instead of a hardcoded `crossdomain.xml`/`clientaccesspolicy.xml`.

### Impact Explanation
If a node operator enables `AllowOrigins = '*'` (a documented, supported setting), any malicious website visited by an authenticated node-UI user can perform credentialed cross-origin requests against the node's session-authenticated REST/GraphQL endpoints (job specs, bridge configuration, keys metadata, etc.), exfiltrating data that should be confined to the legitimate UI origin. This is a session/cross-user response confusion issue reachable from an unprivileged, unauthenticated remote attacker's webpage against an authenticated victim's session.

### Likelihood Explanation
Exploitation requires the operator to have configured `AllowOrigins = '*'`. This is not the default (`http://localhost:3000,http://localhost:6688`), but it is explicitly documented and offered as a legitimate option for the "UI to work from any URL." Because `AllowCredentials: true` is never conditioned on the origin policy, this is a straightforward misconfiguration trap rather than a hardening recommendation properly enforced in code — the code never rejects or warns against the combination.

### Recommendation
Disallow `AllowCredentials: true` whenever `AllowAllOrigins` (wildcard) is set — either refuse to start with that config combination, or force `AllowCredentials = false` when `AllowOrigins = '*'` in `uiCorsHandler` (`core/web/router.go`). Consider validating this combination at config-load time and emitting a hard error, consistent with the general CORS spec guidance that credentials and wildcard origins must not be combined.

### Proof of Concept
1. Configure a node with `[WebServer] AllowOrigins = '*'`.
2. Log into the operator UI (sets `clsession` cookie).
3. Visit an attacker-controlled page that issues `fetch('https://node-host:6688/v2/chains/evm', {credentials: 'include'})` from any origin.
4. Because `uiCorsHandler` sets both `AllowAllOrigins: true` and `AllowCredentials: true`, the response is CORS-approved and readable by the attacker page, as confirmed by the `TestCors_OverrideOrigins` wildcard cases returning `http.StatusOK` for arbitrary origins. [4](#0-3)

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

**File:** docs/CONFIG.md (L507-515)
```markdown
### AllowOrigins
```toml
AllowOrigins = 'http://localhost:3000,http://localhost:6688' # Default
```
AllowOrigins controls the URLs Chainlink nodes emit in the `Allow-Origins` header of its API responses. The setting can be a comma-separated list with no spaces. You might experience CORS issues if this is not set correctly.

You should set this to the external URL that you use to access the Chainlink UI.

You can set `AllowOrigins = '*'` to allow the UI to work from any URL, but it is recommended for security reasons to make it explicit instead.
```

**File:** core/web/cors_test.go (L43-72)
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

	for _, test := range tests {
		t.Run(test.origin, func(t *testing.T) {
			t.Parallel()
			config := configtest.NewGeneralConfig(t, func(c *chainlink.Config, s *chainlink.Secrets) {
				c.WebServer.AllowOrigins = new(test.allow)
			})
			app := cltest.NewApplicationWithConfig(t, config)

			client := app.NewHTTPClient(nil)

			headers := map[string]string{"Origin": test.origin}
			resp, cleanup := client.Get("/v2/chains/evm", headers)
			defer cleanup()
			cltest.AssertServerResponse(t, resp, test.statusCode)
		})
	}
```
