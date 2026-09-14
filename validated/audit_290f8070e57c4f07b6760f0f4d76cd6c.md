### Title
User enumeration via differing error messages in `/sessions` login endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The Zitadel advisory describes an unauthenticated user-enumeration flaw where login/password-reset endpoints return distinguishable responses for valid vs. invalid user identifiers. Chainlink's local-auth login flow (`POST /sessions`) has an analogous flaw: the `CreateSession` implementation returns different, unredacted error strings depending on whether the submitted email exists in the database, and this error is propagated verbatim to the unauthenticated HTTP client.

### Finding Description
`SessionsController.Create` is reachable without authentication (only rate-limited) at `/sessions` [1](#0-0) . It forwards the raw error from `AuthenticationProvider().CreateSession` straight into the JSON API error response: `jsonAPIError(c, http.StatusUnauthorized, err)` [2](#0-1) .

Inside the local-auth ORM, `CreateSession` first calls `FindUser`, and if the email is not present in the `users` table, it returns the raw SQL lookup error immediately: `user, err := o.FindUser(ctx, sr.Email); if err != nil { return "", err }` [3](#0-2) . This underlying error originates from `findUser`, which is a direct `sqlx` query and returns the raw `sql.ErrNoRows`-style error when no matching row exists: [4](#0-3) .

By contrast, when the email *does* exist but the password is wrong, a distinctly different, hand-written error string is returned: `o.auditLogger.Audit(audit.AuthLoginFailedPassword, ...); return "", pkgerrors.New("Invalid password")` [5](#0-4) .

Because these two error paths produce textually different messages ("sql: no rows in result set" / DB driver error vs. `"Invalid password"`), and both are surfaced through the same unauthenticated `/sessions` endpoint with the same HTTP status code (`401 Unauthorized`), an attacker can distinguish "email exists" from "email does not exist" purely from the response body content — the same class of bug as the Zitadel advisory (CWE-203/204).

The existing rate limiter on the `/sessions` route mitigates but does not eliminate the enumeration primitive [1](#0-0) ; the test suite confirms both cases return a 4xx generically, but does not assert response body equivalence, so message content is not currently controlled/tested for parity: [6](#0-5) .

### Impact Explanation
An unauthenticated attacker can enumerate valid Chainlink node operator usernames/emails by submitting login attempts and comparing error response bodies. This directly maps to the "unauthorized... cross-user response confusion" / disclosure category called out in the rules, since it discloses which accounts exist on a self-hosted Chainlink node's admin UI/API, aiding subsequent credential-stuffing or targeted attacks against the node operator's admin account (which controls job runs, keys, and fund movement transactions).

### Likelihood Explanation
Likelihood is limited but non-zero: the endpoint is internet-facing when the node's operator UI/API is exposed, requires no privileges to reach, and rate limiting (`rl.Unauthenticated()`) only throttles requests rather than blocking enumeration outright [1](#0-0) . The number of valid emails on a typical node is small (often a single admin), which somewhat limits real-world value of enumeration, but the code path itself is exploitable given network access to `/sessions`.

### Recommendation
Normalize error handling in `CreateSession` (and the LDAP/OIDC `localLoginFallback` variants, which have the same pattern at [7](#0-6)  and [8](#0-7) ) so that "user not found" and "password mismatch" return the exact same generic error (e.g., `"invalid credentials"`) with the same HTTP status, timing profile, and body — never leaking the raw SQL/driver error to the client.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"nonexistent@test.com","password":"anything"}` and observe the response body contains a raw DB-style error surfaced via `FindUser`'s failure at `core/sessions/localauth/orm.go:144-148`.
2. Send `POST /sessions` with `{"email":"<valid-admin-email>","password":"wrongpassword"}` and observe the response body instead contains `"Invalid password"` from `core/sessions/localauth/orm.go:159-162`.
3. The differing body content (independent of the shared 401 status code) lets the attacker distinguish valid vs. invalid emails, confirming account existence without authentication.

### Citations

**File:** core/web/router.go (L207-215)
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
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
}
```

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/web/sessions_controller_test.go (L22-80)
```go
func TestSessionsController_Create(t *testing.T) {
	t.Parallel()
	ctx := t.Context()

	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	user := cltest.MustRandomUser(t)
	require.NoError(t, app.AuthenticationProvider().CreateUser(ctx, &user))

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	tests := []struct {
		name        string
		email       string
		password    string
		wantSession bool
	}{
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			ctx := t.Context()
			body := fmt.Sprintf(`{"email":"%s","password":"%s"}`, test.email, test.password)
			request, err := http.NewRequestWithContext(ctx, http.MethodPost, app.Server.URL+"/sessions", bytes.NewBufferString(body))
			require.NoError(t, err)
			resp, err := client.Do(request)
			require.NoError(t, err)
			defer func() { require.NoError(t, resp.Body.Close()) }()

			if test.wantSession {
				require.Equal(t, http.StatusOK, resp.StatusCode)

				cookies := resp.Cookies()
				sessionCookie := web.FindSessionCookie(cookies)
				require.NotNil(t, sessionCookie)

				decrypted, err := cltest.DecodeSessionCookie(sessionCookie.Value)
				require.NoError(t, err)
				user, err := app.AuthenticationProvider().AuthorizedUserWithSession(ctx, decrypted)
				require.NoError(t, err)
				assert.Equal(t, test.email, user.Email)

				b, err := io.ReadAll(resp.Body)
				require.NoError(t, err)
				assert.Contains(t, string(b), `"attributes":{"authenticated":true}`)
			} else {
				require.GreaterOrEqual(t, resp.StatusCode, 400, "Should not be able to create session")
				// Ignore fixture session
				sessions, err := app.AuthenticationProvider().Sessions(ctx, 1, 2)
				require.NoError(t, err)
				assert.Empty(t, sessions)
			}
		})
	}
```

**File:** core/sessions/ldapauth/ldap.go (L624-642)
```go
func (l *ldapAuthenticator) localLoginFallback(ctx context.Context, sr sessions.SessionRequest) (sessions.User, error) {
	var user sessions.User
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err := l.ds.GetContext(ctx, &user, sql, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		l.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		l.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L580-597)
```go
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
}
```
