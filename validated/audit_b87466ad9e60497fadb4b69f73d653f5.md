I'll investigate whether there's an authentication timing-based analog in the chainlink repository, similar to the OpenSSH user-enumeration timing bug.Confirmed timing side-channel in the local login path.

### Title
User enumeration via login timing side-channel (bcrypt vs early return) - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `POST /sessions` login endpoint exhibits a timing side-channel nearly identical in root cause to CVE-2016-6210: when the submitted email does not exist, the code returns immediately without doing any password hashing work, whereas when the email exists, an expensive `bcrypt.CompareHashAndPassword` call is performed. The measurable timing difference lets a remote, unauthenticated attacker enumerate valid Chainlink node operator emails.

### Finding Description
`CreateSession` in `core/sessions/localauth/orm.go` first performs `o.FindUser(ctx, sr.Email)` and, if the email is not found, returns the error immediately [1](#0-0) . Only if a user row is found does the code proceed to `constantTimeEmailCompare` and then `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))`, which invokes bcrypt (a deliberately slow, tunable-cost KDF) [2](#0-1) . `CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword` [3](#0-2) .

This means:
- Nonexistent email → fast path (DB lookup miss, no bcrypt).
- Existing email + wrong password → slow path (bcrypt executed, cost factor `bcrypt.DefaultCost`).

This is the same bug class as CVE-2016-6210 (sshd BLOWFISH-hashing a static password only for existing/valid accounts when SHA256/512 hashing is configured, creating a timing oracle for username enumeration). Here, bcrypt is invoked only for existing emails, and skipped entirely for nonexistent ones, producing an analogous timing oracle.

The same pattern repeats in the OIDC and LDAP local-fallback paths (`localLoginFallback` in `core/sessions/oidcauth/oidc.go` and `core/sessions/ldapauth/ldap.go`), both of which first `GetContext` the user row and return early on `sql.ErrNoRows` before ever calling `CheckPasswordHash` [4](#0-3) [5](#0-4) .

The endpoint is reached via `POST /sessions`, registered unauthenticated (only rate-limited) at [6](#0-5) , and handled by `SessionsController.Create`, which calls `AuthenticationProvider().CreateSession` directly with attacker-controlled email/password [7](#0-6) .

Note that `constantTimeEmailCompare` is used deliberately elsewhere to avoid leaking whether MFA is enabled, per the comment "Do email and password check first to prevent extra database look up for MFA tokens leaking" [8](#0-7)  — showing the developers were aware of timing side-channels in this exact function but did not address the FindUser-existence timing gap that occurs before that point.

### Impact Explanation
An unauthenticated network attacker can distinguish valid operator email addresses from invalid ones purely by measuring response latency to `POST /sessions`. This does not directly compromise credentials or bypass auth, but it materially narrows the attack surface for follow-on credential-stuffing/brute-force/phishing against Chainlink node operators, whose accounts (admin/edit/run roles) control job specs, bridges, and fund-moving transactions. Impact is confined to information disclosure (valid usernames), matching CVSS classification of the analog CVE (C:H/I:N/A:N).

### Likelihood Explanation
Exploitation is straightforward and remotely reachable: it requires only repeated unauthenticated HTTP requests to `/sessions` with varying emails and timing measurement, similar to well-documented username-enumeration timing attacks. The existing rate limiter [9](#0-8)  and lockout behavior (`TestSessions_RateLimited` returns HTTP 429 after 5 attempts) [10](#0-9)  raise the bar (large sample sizes for reliable timing statistics become harder), but do not eliminate the signal, especially over a long collection window or from multiple source IPs.

### Recommendation
Perform a constant-time-equivalent operation on the "user not found" path so response timing is independent of email existence — e.g., always execute a dummy/fixed-cost bcrypt comparison against a static hash (similar in spirit to OpenSSH's later mitigation of doing a bcrypt hash for nonexistent users too, but done correctly and unconditionally) before returning the "invalid email" error, or normalize total handler latency via a fixed minimum-duration guard around the whole `CreateSession` call for both success/failure branches. Apply the same fix to the local-fallback logins in `oidcauth` and `ldapauth`.

### Proof of Concept
1. Send `POST /sessions` with a known-valid email and a wrong password; measure response latency (includes one bcrypt compare, ~50-100ms depending on cost factor).
2. Send `POST /sessions` with a random/nonexistent email; measure response latency (DB miss only, sub-millisecond to low-millisecond).
3. Repeat across many candidate emails and average out network jitter; emails whose latency clusters with step 1 are confirmed to exist in the `users` table, those clustering with step 2 do not — yielding an oracle for valid operator email enumeration without needing valid credentials.

### Citations

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L152-162)
```go
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

**File:** core/utils/utils.go (L131-135)
```go
// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
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

**File:** core/sessions/ldapauth/ldap.go (L622-642)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the LDAP server
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

**File:** core/web/sessions_controller.go (L29-60)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
	sc.App.GetLogger().Debugf("TRACE: Starting Session Creation")

	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
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
