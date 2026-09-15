### Title
Unauthenticated brute-force rate limiting on `/sessions` is keyed by literal client IP, allowing bypass via IPv6 address rotation - ([File: core/web/router.go])

### Summary
The Chainlink node's HTTP login endpoint (`POST /sessions`) is protected by an in-memory, per-key rate limiter that is keyed on the raw client IP address string returned by `c.ClientIP()`. Because the limiter bucket key is the exact source address (not a normalized subnet, e.g. an IPv6 /64), an attacker who controls even a small IPv6 address block can send each brute-force login attempt from a distinct address in that block, and the "Unauthenticated" rate-limit bucket resets for every new address. This mirrors the root cause of CVE-2021-22915 (Nextcloud): brute-force/rate-limit protections that do not account for IPv6 subnet allocation are trivially bypassed by attackers who can rotate addresses within a single, cheaply obtainable prefix.

### Finding Description
`NewRouter` builds the rate limiter groups directly from config values and applies them per-route: [1](#0-0) 

The unauthenticated group protecting session creation is: [2](#0-1) 

`rateLimiter` constructs an `ulule/limiter/v3` in-memory limiter via `mgin.NewMiddleware(limiter.New(store, rate))` with no custom key function, so the default gin-driver key extractor (`c.ClientIP()`) is used. Notably the router explicitly disables trusting `X-Forwarded-For`/`X-Real-IP` headers: [3](#0-2) 

which is correct hardening against IP-spoofing via headers, but it does **not** address the complementary problem: the bucket key is the full literal address (IPv4 host or full IPv6 host address) with no subnet-level aggregation. Default config only allows 5 unauthenticated requests per 20 seconds: [4](#0-3) 

The existing test confirms the limiter operates strictly per-source-address, since a single test client (single fixed IP) gets rate-limited after 5 failed attempts: [5](#0-4) 

An attacker who owns (or is assigned, e.g. by cloud/VPS providers that commonly hand out a /64 or /56 IPv6 prefix per customer) an IPv6 block can issue each POST to `/sessions` from a new address drawn from that block. Since the limiter bucket is keyed by the exact address, every request lands in a fresh, empty bucket and never accumulates toward the 5-request/20s ceiling, fully defeating the brute-force protection intended for the login endpoint.

### Impact Explanation
This allows unlimited-rate password guessing against the Chainlink node's `/sessions` login endpoint from an unprivileged network attacker, without needing to compromise any header trust (the header-spoofing vector is already closed). Successful credential guessing directly leads to unauthorized session creation and full node API access (job management, key export endpoints, fund transfer endpoints gated behind `auth.RequiresAdminRole`, etc.), which is a critical confidentiality/integrity impact consistent with the CVSS 9.8 rating of the original CVE.

### Likelihood Explanation
Obtaining an IPv6 prefix large enough to defeat a 5-attempts/20s cap is inexpensive and common (most residential and cloud IPv6 allocations are /64 or larger, providing effectively unlimited unique source addresses). No privileged access, malicious peer relationship, or special network position is required — this is purely a remote, unauthenticated client behavior against a public-facing endpoint.

### Recommendation
Key the rate limiter on a normalized subnet (e.g. mask IPv6 addresses to /64 or /56 before use as the limiter key) rather than the literal address, and/or add a secondary limiter keyed by the attempted account (`email`) so IP rotation cannot fully bypass throttling of guesses against a single credential.

### Proof of Concept
1. Configure/observe default `WebServer.RateLimit.Unauthenticated = 5`, `UnauthenticatedPeriod = '20s'` protecting `POST /sessions`.
2. From a host with an assigned IPv6 /64 (or larger) prefix, send brute-force login POST requests to `/sessions`, using a different source IPv6 address from the assigned block for each request (e.g. via `SO_BINDTODEVICE`/source-address binding, iterating the low 64 bits of the address).
3. Because `rateLimiter` keys strictly on `c.ClientIP()` per exact address, each request is counted against a brand-new bucket and never triggers the `429` response that `TestSessions_RateLimited` demonstrates occurs for a single fixed address after 5 attempts — allowing unbounded password-guessing throughput.

### Citations

**File:** core/web/router.go (L49-50)
```go
	engine := gin.New()
	engine.RemoteIPHeaders = nil // don't trust default headers: "X-Forwarded-For", "X-Real-IP"
```

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

**File:** core/web/router.go (L207-218)
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
}
```

**File:** core/config/docs/core.toml (L278-281)
```text
# Unauthenticated defines the threshold to which authenticated requests get limited. More than this many unauthenticated requests per `UnAuthenticatedRateLimitPeriod` will be rejected.
Unauthenticated = 5 # Default
# UnauthenticatedPeriod defines the period to which unauthenticated requests get limited.
UnauthenticatedPeriod = '20s' # Default
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
