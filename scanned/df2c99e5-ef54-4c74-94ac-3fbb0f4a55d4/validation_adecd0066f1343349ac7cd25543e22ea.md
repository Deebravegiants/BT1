### Title
External Initiator (webhook) token authentication is only protected by the generic 1000 req/min "Authenticated" rate limit, not the strict "Unauthenticated" brute-force throttle used for login - ([File: core/web/router.go])

### Summary
Chainlink's `/v2/jobs/:ID/runs` and `/v2/ping` endpoints accept pre-auth requests carrying an External Initiator "webhook" credential pair (`X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret`) via `auth.AuthenticateExternalInitiator`. Unlike the `/sessions` login endpoint, which is deliberately placed in a dedicated route group using the strict `Unauthenticated` rate limit (5 requests / 20s), the External Initiator auth path is nested only under the top-level `api` group, which applies the much more permissive `Authenticated` rate limit (1000 requests / 1m) regardless of whether the request is actually authenticated yet. This mirrors the OpenClaw class of bug: a pre-auth secret-guessing endpoint that is rate-limited far more loosely than the application's own explicit brute-force protections, enabling high-throughput guessing of the External Initiator secret.

### Finding Description
The webserver applies a single global rate limiter to the entire `api` route group before any authentication occurs: [1](#0-0) 

For the login flow, the developers explicitly recognized the need for a stricter, dedicated throttle and created a separate `unauth` sub-group scoped to `/sessions` using `rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()` (5 requests per 20 seconds): [2](#0-1) 

This intent is confirmed by the existing test `TestSessions_RateLimited`, which asserts that repeated bad-credential POSTs to `/sessions` get throttled with HTTP 429 after only 5 attempts: [3](#0-2) 

However, the External Initiator (webhook) authentication path — `auth.AuthenticateExternalInitiator`, used to trigger job runs via `POST /v2/jobs/:ID/runs` and to probe liveness via `GET /v2/ping` — receives no equivalent dedicated throttle. It is registered as a plain sub-group of `r` (the `api` group), inheriting only the loose 1000 req/min limiter: [4](#0-3) 

The authentication logic itself simply looks up the initiator by `AccessKey` and does a constant-time compare of the hashed `Secret`, returning a generic `auth.ErrorAuthFailed` on mismatch with no additional throttling or backoff: [5](#0-4) [6](#0-5) 

Because the surrounding rate limiter treats this as part of the generic "authenticated" bucket (1000/min) rather than the "unauthenticated"/pre-auth bucket the application already defines and uses for `/sessions`, an unauthenticated caller can issue far more guesses per unit time against the `AccessKey`/`Secret` pair than the application's own security model intends for pre-auth credential validation.

### Impact Explanation
An attacker who can reach the node's HTTP API (the same "internet-facing gateway" surface as `/sessions`) can attempt External Initiator `AccessKey`/`Secret` guesses at up to 1000 requests/minute per IP instead of the 5/20s ceiling the application deliberately enforces for other pre-auth credential checks. If an operator provisions an External Initiator with a weak or short/rotated secret (the mechanism itself does not enforce secret strength), this asymmetry meaningfully increases the practical guessing budget available to an unprivileged network client, and a successful guess grants the "Run" role — allowing the attacker to trigger arbitrary webhook job runs (`SessionUserKey` is set to `clsessions.User{Role: clsessions.UserRoleRun}`), i.e., unauthorized job execution.

### Likelihood Explanation
Exploitability requires network access to the node's web API (already required for `/sessions` brute forcing, which the code explicitly defends against) and requires External Initiators to be enabled/configured with reachable job-run endpoints. Chainlink's default `AccessKey`/`Secret` generation uses long random values (`utils.NewSecret(utils.DefaultSecretSize)`), so brute-forcing a default-strength secret is not practical even at 1000 req/min; likelihood is elevated only when weaker/custom secrets are used, matching the "weak webhook secret" precondition in the analog advisory.

### Recommendation
Move the External Initiator (and generally any pre-auth credential-bearing) route group to use the stricter `rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()` limiter (or a dedicated per-credential/IP throttle with backoff) prior to `auth.AuthenticateExternalInitiator` succeeding, consistent with the existing `/sessions` pattern, so that the effective request budget for guessing tokens matches the intended brute-force protection rather than the generic 1000/min "authenticated" bucket.

### Proof of Concept
1. Provision an External Initiator with `POST /v2/external_initiators` and note its `Name`/`URL`, obtaining an `AccessKey` but not the `Secret` (attacker perspective: secret unknown).
2. Create a webhook job referencing that initiator.
3. As an unauthenticated client, send up to ~1000 `POST /v2/jobs/:ID/runs` requests per minute with header `X-Chainlink-EA-AccessKey: <known-accesskey>` and varying `X-Chainlink-EA-Secret` guesses, per the flow validated by `TestTokenAuthRequired_BadTokenCredentials`: [7](#0-6) 
4. Observe that only the generic 1000/min limiter applies (HTTP 401 for wrong secret, no HTTP 429 until far higher volume), unlike the `/sessions` endpoint which returns HTTP 429 after 5 failed attempts in 20 seconds.

### Citations

**File:** core/web/router.go (L77-85)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)
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

**File:** core/web/router.go (L449-457)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
}
```

**File:** core/web/router_test.go (L92-125)
```go
func TestTokenAuthRequired_BadTokenCredentials(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	eia := auth.NewToken()
	url := cltest.WebURL(t, "http://localhost:8888")
	eir := &bridges.ExternalInitiatorRequest{
		Name: uuid.New().String(),
		URL:  &url,
	}
	ea, err := bridges.NewExternalInitiator(eia, eir)
	require.NoError(t, err)
	err = app.BridgeORM().CreateExternalInitiator(ctx, ea)
	require.NoError(t, err)

	request, err := http.NewRequestWithContext(ctx, http.MethodGet, ts.URL+"/v2/ping/", bytes.NewBufferString("{}"))
	require.NoError(t, err)
	request.Header.Set("Content-Type", web.MediaType)
	request.Header.Set("X-Chainlink-EA-AccessKey", eia.AccessKey)
	request.Header.Set("X-Chainlink-EA-Secret", "every unpleasant commercial color from aquamarine to beige")

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	resp, err := client.Do(request)
	require.NoError(t, err)

	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
}
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

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```
