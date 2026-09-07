# [M] Vikunja has a Rate-Limit Bypass for Unauthenticated Users via Spoofed Headers

## Summary
Severity: Medium
Advisory: GHSA-m547-hp4w-j6jx
CVE: CVE-2026-29794
CWE: CWE-807
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-m547-hp4w-j6jx
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.8 <2.2.0

## Details
### Summary
Unauthenticated users are able to bypass the application's built-in rate-limits by spoofing the `X-Forwarded-For` or `X-Real-IP` headers due to the rate-limit relying on the value of `(echo.Context).RealIP`. 

### Details
In the first file below, the rate-limit for unauthenticated users can be observed being populated with the `ip` value. In the second file, it shows it using the `c.RealIP()` function for the `ip` case. Due to this, the rate-limit will rely on the value of one of the two mentioned headers (`X-Forwarded-For` or `X-Real-IP`). These can be spoofed by users client-side in order to completely bypass any unauthenticated rate-limits in place.

Some reverse proxies like Traefik will overwrite this value by default, but others will not, leaving any deployment that either isn't using a reserve proxy that specifically overwrites the header's value or isn't using a reverse proxy vulnerable. 

**File 1:** pkg\routes\routes.go:318
```go
// This is the group with no auth
	// It is its own group to be able to rate limit this based on different heuristics
	n := a.Group("")
	setupRateLimit(n, "ip")

	// Docs
	n.GET("/docs.json", apiv1.DocsJSON)
	n.GET("/docs", apiv1.RedocUI)

	// Prometheus endpoint
	setupMetrics(n)

	// Separate route for unauthenticated routes to enable rate limits for it
	ur := a.Group("")
	rate := limiter.Rate{
		Period: 60 * time.Second,
		Limit:  config.RateLimitNoAuthRoutesLimit.GetInt64(),
	}
	rateLimiter := createRateLimiter(rate)
	ur.Use(RateLimit(rateLimiter, "ip"))
```
**File 2:** pkg\routes\rate_limit.go:41
```go
// RateLimit is the rate limit middleware
func RateLimit(rateLimiter *limiter.Limiter, rateLimitKind string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c *echo.Context) (err error) {
			var rateLimitKey string
			switch rateLimitKind {
			case "ip":
				rateLimitKey = c.RealIP()
			case "user":
				auth, err := auth2.GetAuthFromClaims(c)
				if err != nil {
					log.Errorf("Error getting auth from jwt claims: %v", err)
				}
				rateLimitKey = "user_" + strconv.FormatInt(auth.GetID(), 10)
			default:
				log.Errorf("Unknown rate limit kind configured: %s", rateLimitKind)
			}
```

### PoC
1. Download and run the default docker compose file via the instructions here: [https://vikunja.io/install/](https://vikunja.io/install/). Do not configure a proxy.
2. Once running, navigate to the application in a web browser that is using a web proxy, such as Burp Suite.
3. Attempt to authenticate to the application with an invalid username and password.
4. In the web proxy's logs, locate the request to the `/api/v1/login` endpoint. Observe that the response contains rate-limit details:
```http
HTTP/1.1 403 Forbidden
Cache-Control: no-store
Content-Type: application/json
Vary: Origin
X-Ratelimit-Limit: 10
X-Ratelimit-Remaining: 9
X-Ratelimit-Reset: 1772224455
Date: Fri, 27 Feb 2026 20:33:16 GMT
Content-Length: 54

{"code":1011,"message":"Wrong username or password."}
```
5. Add the `X-Forwarded-For` header with an arbitrary value, like so: `X-Forwarded-For: FakeValue`. Send the request 10 times, or until the rate-limit is at zero.
6. Modify the `X-Forwarded-For` headers value to be different, like so: `X-Forwarded-For: NewValue`.
7. Observe that the `X-Ratelimit-Remaining` header's value has reset its countdown and is back at `9`. 

### Impact
Unauthenticated users can abuse endpoints available to them for different potential impacts. The immediate concern would be brute-forcing usernames or specific accounts' passwords. This bypass allows unlimited requests against unauthenticated endpoints.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-m547-hp4w-j6jx
- https://nvd.nist.gov/vuln/detail/CVE-2026-29794
- https://github.com/go-vikunja/vikunja/commit/a498dd69915a006c07e9d82660a2185d7e8136ee
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
