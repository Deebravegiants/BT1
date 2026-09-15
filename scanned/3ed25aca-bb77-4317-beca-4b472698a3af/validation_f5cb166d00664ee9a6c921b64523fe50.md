## Analysis: Grafana forgot-password user enumeration analog in Chainlink

The Grafana CVE-2022-39307 bug class is "endpoint returns a distinguishable response revealing whether a submitted identity exists." I traced the closest unauthenticated-reachable analog in this codebase: the `/sessions` login endpoint (`SessionsController.Create`) leaks raw, distinguishable backend error strings for "unknown email" vs. "wrong password," which is a stronger enumeration primitive than the original Grafana bug.

### Title
Unauthenticated login endpoint (`POST /sessions`) leaks distinguishable error messages enabling user/email enumeration - ([File: core/sessions/localauth/orm.go])

### Summary
The default local-auth `CreateSession` implementation returns the raw, unwrapped database error (`sql.ErrNoRows`) when the submitted email does not match any user, but returns a distinct, custom `"Invalid password"` error when the email exists but the password is wrong. Both errors are forwarded verbatim to the unauthenticated HTTP client by `SessionsController.Create` via `jsonAPIError`, which serializes `err.Error()` directly into the JSON API response body. This lets any unauthenticated caller distinguish valid from invalid emails.

### Finding Description
`SessionsController.Create` handles `POST /sessions` without any authentication, calling `AuthenticationProvider().CreateSession(ctx, sr)`: [1](#0-0) 

For the local auth provider, `CreateSession` first calls `FindUser`, and on failure returns the underlying error immediately, before any constant-time comparison or generic error wrapping: [2](#0-1) 

`FindUser`/`findUser` simply executes a SQL lookup and propagates whatever error `sqlx` returns (i.e., `sql.ErrNoRows` for a nonexistent email), unwrapped: [3](#0-2) 

In contrast, when the email *does* exist but the password is wrong, a distinct, human-readable message is returned: [4](#0-3) 

Both code paths funnel into `jsonAPIError(c, http.StatusUnauthorized, err)`, which places `err.Error()` directly into the JSON response body when the error is not already a `*models.JSONAPIErrors`: [5](#0-4) 

As a result:
- Unknown email → HTTP 401 body containing `sql: no rows in result set` (or similar driver-specific text).
- Known email + wrong password → HTTP 401 body containing `Invalid password`.

This is a textbook oracle for username/email enumeration, directly analogous to the Grafana `sent-reset-email` bug where a JSON response distinguished "user not found" from other outcomes.

### Impact Explanation
An unauthenticated attacker can enumerate valid Chainlink node operator/API-user emails by observing the response body of repeated `POST /sessions` requests. Confirmed valid emails can then be targeted for credential stuffing or brute-force password attacks, and the leaked list of accounts also reveals internal user/organization information (aligned with CWE-200/209, information disclosure through error messages). This matches the "cross-user response confusion" / information-disclosure class explicitly accepted by the validation rules.

### Likelihood Explanation
The `/sessions` endpoint is unauthenticated and internet-facing by design (it's the login endpoint). The only mitigating control present is a per-request-count rate limiter that returns HTTP 429 after 5 failed attempts: [6](#0-5) 

Rate limiting slows down bulk enumeration but does not prevent it (an attacker can still enumerate slowly, or across multiple source IPs/limiter windows), so the underlying oracle remains exploitable.

### Recommendation
Normalize the error path in `orm.CreateSession` (and equivalent LDAP/OIDC fallbacks) so that "user not found" and "invalid password" produce the exact same generic error object/message (e.g., always return a fixed `pkgerrors.New("invalid email or password")` for both cases) before it ever reaches `jsonAPIError`, and ensure the lookup either way takes constant time (a dummy bcrypt comparison should be performed even when the user isn't found, to avoid a timing side channel).

### Proof of Concept
```
POST /sessions
{"email":"doesnotexist@example.com","password":"anything"}
→ 401 {"errors":[{"detail":"sql: no rows in result set"}]}

POST /sessions
{"email":"knownuser@example.com","password":"wrongpassword"}
→ 401 {"errors":[{"detail":"Invalid password"}]}
```
The differing `detail` field lets an attacker enumerate which emails correspond to real accounts.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/localauth/orm.go (L43-59)
```go
// FindUser will attempt to return an API user by email.
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}

// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}

func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
}
```

**File:** core/sessions/localauth/orm.go (L144-157)
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
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/web/helpers.go (L19-29)
```go
// jsonAPIError adds an error to the gin context and sets
// the JSON value of errors.
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
