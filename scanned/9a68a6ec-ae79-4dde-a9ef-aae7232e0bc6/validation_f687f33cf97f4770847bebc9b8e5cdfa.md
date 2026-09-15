### Title
Login brute-force rate limit bypass via IPv6 address rotation on `/sessions` - ([File: core/web/router.go])

### Summary
The `/sessions` login endpoint (`POST /sessions`), which handles unauthenticated credential submission, is protected solely by an IP-keyed in-memory rate limiter. The limiter's bucket key is derived from the raw client IP string with no IPv6 canonicalization or subnet-level aggregation, mirroring the same bug class described in CVE-2026-15144 for `@fastify/rate-limit`: an IPv6-capable client can rotate through many distinct addresses in its own allocated range (commonly a /64 or larger) and defeat the per-IP rate limit boundary, allowing sustained credential brute-forcing.

### Finding Description
`core/web/router.go`'s `sessionRoutes` wires the unauthenticated login route to a dedicated rate limiter keyed by client IP: [1](#0-0) 

The limiter itself is constructed with `mgin.NewMiddleware(limiter.New(store, rate))` from `github.com/ulule/limiter/v3`, which by default extracts the bucket key from `gin.Context.ClientIP()` verbatim (no IPv6 normalization, no `/64` or similar prefix masking): [2](#0-1) 

The rate limit values themselves come straight from config (`Unauthenticated`/`UnauthenticatedPeriod`), and the intent of this limiter is explicitly to throttle repeated failed login attempts, as shown by the existing brute-force test: [3](#0-2) 

Because the bucket key is the literal client IP string with no subnet-level aggregation, a client with access to an IPv6 range (a single residential/ISP allocation typically grants a /64, i.e. 2^64 addresses) can issue each login attempt from a different source address within that range. Each distinct address gets its own independent rate-limit bucket in the in-memory store, so the effective global limit on login attempts against a single account is never enforced — the same underlying weakness as the reported `@fastify/rate-limit` CVE, just manifesting through `ulule/limiter`'s default IP-keying used directly by chainlink's node web server rather than through a proxy-trust misconfiguration.

Note that `engine.RemoteIPHeaders = nil` prevents header-spoofing (`X-Forwarded-For`) from being used to fake the IP, so this analog specifically requires the attacker to actually possess/route from multiple real IPv6 addresses (not merely forge a header) — this is exactly the scenario the CVE describes.

### Impact Explanation
This weakens brute-force protection on the primary node login endpoint (`POST /sessions`, `SessionsController.Create`). An attacker with IPv6 connectivity can bypass the `Unauthenticated` rate limit and mount a distributed-looking credential-guessing attack against operator accounts, increasing the practical likelihood of successful account takeover of the Chainlink node's web UI/API, which controls sensitive node operations (jobs, keys, transactions).

### Likelihood Explanation
Exploitation requires only unprivileged network access to the node's web server and control of an IPv6 address range — a low bar for any attacker with a modern ISP-assigned IPv6 block or cloud IPv6 allocation, and no special configuration (like a misconfigured trusted-proxy setup) is needed, unlike some other IP-rate-limit-bypass variants.

### Recommendation
Replace or wrap the default `ulule/limiter` IP key extraction used in `rateLimiter()` (`core/web/router.go`) with a key generator that canonicalizes IPv6 addresses and truncates them to a configurable subnet prefix (e.g., default /64, matching the fix pattern in `@fastify/rate-limit` 11.2.0) before use as the rate-limit bucket key, and collapses IPv4-mapped IPv6 addresses to their IPv4 form. Apply this specifically to the `/sessions` unauthenticated rate limiter and any other IP-keyed limiter guarding authentication-sensitive endpoints.

### Proof of Concept
1. Deploy a Chainlink node with default `WebServer.RateLimit.Unauthenticated` settings and IPv6 connectivity reachable directly to the node (no untrusted proxy headers involved, per `engine.RemoteIPHeaders = nil`).
2. From an attacker host owning an IPv6 /64 (or larger) allocation, send repeated `POST /sessions` requests with guessed credentials, binding each outbound connection to a different source address within the owned IPv6 range (e.g., via `bind()`/`SO_BINDTODEVICE` with sequentially incremented host bits).
3. Observe that each new source address receives its own fresh rate-limit bucket in the `ulule/limiter` memory store keyed by `ClientIP()`, so the `Unauthenticated`/`UnauthenticatedPeriod` limit (which the existing `TestSessions_RateLimited` test confirms triggers a `429` after a fixed number of attempts from one IP) never engages across the rotated addresses, allowing unlimited login attempts.

### Citations

**File:** core/web/router.go (L136-143)
```go
func rateLimiter(period time.Duration, limit int64) gin.HandlerFunc {
	store := memory.NewStore()
	rate := limiter.Rate{
		Period: period,
		Limit:  limit,
	}
	return mgin.NewMiddleware(limiter.New(store, rate))
}
```

**File:** core/web/router.go (L207-217)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
```

**File:** core/web/router_test.go (L127-156)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
	require.NoError(t, err)

	resp, err := client.Do(request)
	require.NoError(t, err)
	assert.Equal(t, 429, resp.StatusCode)
}
```
