## Title
Fixed-window rate limiter on `/sessions` login endpoint can be gamed at window boundaries to double the effective brute-force budget - (File: core/web/router.go)

### Summary
The Oracle bug is a "reset at a discrete time boundary" issue: computing `block.timestamp / 1 days` creates a hard edge where an attacker can act once right before the boundary and once right after, getting two bites for the price of one and defeating a protection that was designed to force a full interval of manipulation. The same *class* of bug — a client-controlled action gated by a fixed calendar/clock window that resets sharply at its boundary — exists in the chainlink node's unauthenticated `/sessions` login-attempt rate limiter, which is reachable directly by an unprivileged network client.

### Finding Description
`core/web/router.go` builds the rate limiter for the login endpoint using the `ulule/limiter` library configured with a fixed `Period`/`Limit` pair and an in-memory store: [1](#0-0) 

This limiter is applied to the unauthenticated `/sessions` (login) route: [2](#0-1) 

with the limit/period sourced from `WebServer.RateLimit.Unauthenticated` / `UnauthenticatedPeriod` (default: 5 requests / 20s): [3](#0-2) 

A fixed-window rate limiter counts requests inside window boundaries derived from wall-clock time (e.g., `now / period`), the same integer-division-truncation pattern used by the Oracle's `block.timestamp / 1 days`. Because the window resets sharply, an attacker can send the allowed quota (5 requests) at the very end of one window (e.g., at t=19.9s) and immediately send another full quota (5 requests) once the new window opens (e.g., t=20.1s). In roughly 200ms of wall-clock time the attacker gets 2x the intended budget of unauthenticated login/brute-force attempts, exactly mirroring how the Oracle's two-day protection could be defeated with two manipulations only seconds apart, straddling the day boundary.

The existing test only checks that a burst exceeding the limit within a single window is rejected; it does not exercise the boundary-straddling case, so this behavior is untested and unnoticed: [4](#0-3) 

### Impact Explanation
This weakens brute-force protection on the credential/session endpoint that is reachable by any unauthenticated network client. While a single boundary crossing only doubles (not eliminates) the throttle, an attacker can repeat the straddle at every window boundary, achieving a sustained ~2x effective rate versus the configured `Unauthenticated`/`UnauthenticatedPeriod` limit indefinitely. This is analogous to a quota/rate-limit bypass on an authentication-adjacent endpoint (unprivileged client, no special access required), which matches the accepted bug classes (authentication protection weakening / quota bypass) even though it does not grant outright authentication bypass by itself.

### Likelihood Explanation
Likelihood is moderate: exploitation requires precise timing (submitting bursts right at window edges), which is straightforward for an automated brute-force script but requires the attacker to synchronize with the server's window boundaries (these can be inferred from response timing/behavior or simply brute-forced by continuously bursting at high frequency). No source-code access or privileged access is needed — only network access to the gateway's public login endpoint.

### Recommendation
Replace the fixed-window strategy with a sliding-window (or token-bucket) algorithm, which the `ulule/limiter` library also supports, so the quota is enforced continuously rather than resetting at a hard boundary. At minimum, add jitter-resistant tracking (e.g., track timestamps of the last N requests and count how many fall within a trailing period ending "now", instead of using a fixed epoch-aligned window) so that no two-window straddle can double the allowed attempts.

### Proof of Concept
1. Configure default settings (`Unauthenticated = 5`, `UnauthenticatedPeriod = '20s'`).
2. At t=19.9s (just before a 20s window boundary as tracked by the `ulule/limiter` memory store), send 5 POST requests to `/sessions` with invalid credentials — all succeed (return 401, not 429), consuming the window's quota.
3. At t=20.1s (just after the boundary), send 5 more POST requests to `/sessions` — the fixed window has reset, so all 5 succeed again.
4. In ~200ms wall-clock time, 10 login attempts were made against a nominal "5 per 20s" limit — double the intended throttle, repeatable at every subsequent boundary.

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

**File:** core/config/docs/core.toml (L273-281)
```text
[WebServer.RateLimit]
# Authenticated defines the threshold to which authenticated requests get limited. More than this many authenticated requests per `AuthenticatedRateLimitPeriod` will be rejected.
Authenticated = 1000 # Default
# AuthenticatedPeriod defines the period to which authenticated requests get limited.
AuthenticatedPeriod = '1m' # Default
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
