### Title
Account enumeration via observable login timing discrepancy in `CreateSession` (`/sessions` endpoint) - (File: `core/sessions/localauth/orm.go`)

### Summary
The local-auth login path (`POST /sessions`, handled by `SessionsController.Create`) only performs the expensive bcrypt password comparison when the supplied email resolves to an existing user row. For non-existent emails, the code path returns immediately after a failed DB lookup, before any bcrypt hashing occurs. This reproduces the exact bug class described in GHSA-7rw5-9f7q-xj36: an unauthenticated attacker can distinguish registered vs. unregistered emails by measuring response latency.

### Finding Description
`SessionsController.Create` accepts unauthenticated JSON login requests and forwards them to `AuthenticationProvider().CreateSession`: [1](#0-0) 

In the local-auth implementation, `CreateSession` first calls `FindUser`, which issues a single SQL `SELECT ... WHERE lower(email) = lower($1)` query. If the email does not exist in the `users` table, the function returns the DB error (`sql.ErrNoRows`-derived) immediately — no `constantTimeEmailCompare` and, critically, no `utils.CheckPasswordHash` (bcrypt) call ever executes: [2](#0-1) 

Only when the email *does* match an existing row does the code proceed to `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))`, which wraps `bcrypt.CompareHashAndPassword`: [3](#0-2) 

Because bcrypt is intentionally slow (tens to hundreds of milliseconds depending on cost factor) and is only invoked on the "user found" branch, a non-existent email returns in the time of a single indexed DB lookup, while an existing email's request always take measurably longer even with a wrong password. The `constantTimeEmailCompare` call present in this function only protects against timing differences in the email string comparison itself — it does nothing to close the much larger structural gap of "bcrypt runs or doesn't run" depending on user existence.

The same structural pattern (`FindUser`/lookup succeeds or fails → gate on bcrypt) is repeated in the LDAP and OIDC local-fallback authenticators (`localLoginFallback` in `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`), and in `TestPassword` implementations, all reachable via the same unauthenticated login/password-check surfaces. [4](#0-3) [5](#0-4) 

### Impact Explanation
An unauthenticated attacker sending requests to `POST /sessions` can enumerate valid Chainlink node operator/admin email accounts purely from response timing, without triggering any error-message difference (both cases return HTTP 401 with a generic-looking body). Confirmed accounts can then be targeted for password spraying or credential-stuffing against the node's admin UI, which controls job management, keys, and other sensitive operations. This matches CWE-208 (Observable Timing Discrepancy) and is directly analogous to the reported class in open-webui.

### Likelihood Explanation
The endpoint is unauthenticated and internet/network reachable by design (it's the login entry point of the operator UI). No special privileges, rate-limit bypass tricks, or race conditions are needed — sending sequential low-rate requests (one at a time with a short delay, as in the original report) is sufficient to stay under any coarse brute-force throttling while still exposing the bcrypt-vs-no-bcrypt timing gap. The gap size (bcrypt cost, `bcrypt.DefaultCost`) is large and consistent, making the signal easy to measure repeatedly for confirmation.

### Recommendation
Ensure a constant-cost operation (e.g., always perform a bcrypt comparison against either the real hash or a fixed dummy/placeholder hash) runs on every login attempt regardless of whether `FindUser` succeeds, so response time no longer depends on account existence. Apply the same fix uniformly to `core/sessions/localauth/orm.go` (`CreateSession`, `TestPassword`), `core/sessions/oidcauth/oidc.go` (`localLoginFallback`, `TestPassword`), and `core/sessions/ldapauth/ldap.go` (`localLoginFallback`, `TestPassword`), since all share the same "lookup-then-conditionally-hash" pattern.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"admin@example.com","password":"wrongpassword"}` for a known/registered email — measure response time (includes one bcrypt comparison, e.g., ~100+ ms depending on cost factor).
2. Send `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrongpassword"}` — measure response time (only a DB lookup, sub-millisecond to a few ms, no bcrypt).
3. Repeat several times to average out DB/network jitter. Both requests return HTTP 401 with generic error bodies, but the timing difference reliably distinguishes existing accounts from non-existing ones, exactly mirroring the reported `joe@example.com` (186 ms) vs `larry@example.com` (9 ms) pattern in the referenced advisory.

### Citations

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

**File:** core/utils/utils.go (L131-135)
```go
// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L624-641)
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
```

**File:** core/sessions/oidcauth/oidc.go (L580-596)
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
```
