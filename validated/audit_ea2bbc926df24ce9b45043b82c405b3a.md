Confirmed: `jsonAPIError` at [1](#0-0)  serializes `err.Error()` verbatim into the JSON response body sent back to the client, and `SessionsController.Create` passes the raw error from `CreateSession` straight through with `jsonAPIError(c, http.StatusUnauthorized, err)` [2](#0-1) . The local-auth `CreateSession` implementation returns three distinguishable error paths for the unauthenticated `/sessions` login endpoint: a raw `sql.ErrNoRows`-derived error when the email doesn't exist in the DB, `"Invalid email"` when the email doesn't match (unreachable given the query, but present), and `"Invalid password"` when the email exists but the password is wrong [3](#0-2) .

### Title
Unauthenticated `/sessions` login endpoint leaks user-existence via distinguishable error messages (user enumeration) - ([File: core/sessions/localauth/orm.go])

### Summary
The Chainlink node's local-auth login flow (`POST /sessions`) returns different, verbatim error text depending on whether the submitted email exists in the `users` table versus whether the password is wrong, and this raw error text is forwarded unmodified to the unauthenticated HTTP client.

### Finding Description
`SessionsController.Create` handles the unauthenticated `/sessions` route registered in `sessionRoutes` [4](#0-3) . It calls `AuthenticationProvider().CreateSession(ctx, sr)` and on any failure returns the error directly to the caller via `jsonAPIError(c, http.StatusUnauthorized, err)` [2](#0-1) . `jsonAPIError` embeds `err.Error()` into the JSON body returned to the client [1](#0-0) .

In the local-auth ORM (the default `AuthenticationMethod = 'local'`), `CreateSession` first looks up the user by email; if no row is found, the raw `sql.ErrNoRows`-derived DB error is returned immediately [5](#0-4) . If the user exists but the password is wrong, a distinct `"Invalid password"` error is returned instead [6](#0-5) . Because these two error strings differ and are both surfaced verbatim to an unauthenticated caller, an attacker can distinguish "email not registered" from "email registered, wrong password" by inspecting the HTTP response body — this is the same bug class as CVE-2018-16703 (user enumeration via login page responses that allows subsequent targeted brute force).

The endpoint does have an unauthenticated rate limiter (`WebServer.RateLimit.Unauthenticated`, default 5 requests / 20s) applied via `rateLimiter(rl.UnauthenticatedPeriod(), rl.Unauthenticated())` [7](#0-6) , confirmed by `TestSessions_RateLimited` which shows the 6th request within the window receives HTTP 429 [8](#0-7) . This rate limit constrains volume but does not fix the information leak — an attacker can still enumerate a small set of high-value emails within the limit, or enumerate slowly across the rate-limit window over time.

### Impact Explanation
An unauthenticated remote attacker can determine which email addresses are registered as Chainlink node API users by observing distinct error text ("sql: no rows..." vs "Invalid password") returned from `POST /sessions`. This does not itself grant access, but it materially aids follow-on targeted credential-stuffing/brute-force attacks against confirmed accounts (including the node's `admin` account), matching the CVSS 5.3 / Medium characterization of the referenced CVE (confidentiality-only impact, no direct authentication bypass).

### Likelihood Explanation
The `/sessions` endpoint is reachable by any unauthenticated network client that can reach the node's web server (default port 6688) [9](#0-8) . No privileges are required. The rate limiter (5 req/20s by default) increases the effort needed but does not prevent gradual enumeration; likelihood is moderate.

### Recommendation
Normalize the error returned by `CreateSession`/`SessionsController.Create` for all failure cases ("user not found", "invalid email", "invalid password") to a single generic message (e.g., "invalid credentials") and log the detailed reason server-side only via the existing audit logger calls (`audit.AuthLoginFailedEmail`, `audit.AuthLoginFailedPassword`) rather than returning it to the client.

### Proof of Concept
```
POST /sessions {"email":"nonexistent@nowhere.com","password":"x"}
-> HTTP 401, body contains raw "sql: no rows in result set" style error

POST /sessions {"email":"knownadmin@node.com","password":"wrongpass"}
-> HTTP 401, body contains "Invalid password"
```
The differing response bodies allow an attacker to enumerate valid node user emails before attempting password brute force, within the bounds of the unauthenticated rate limit.

### Citations

**File:** core/web/helpers.go (L21-29)
```go
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
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
