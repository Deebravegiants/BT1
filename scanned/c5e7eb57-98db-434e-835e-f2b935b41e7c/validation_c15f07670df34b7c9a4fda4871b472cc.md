## Finding

### Title
Observable timing discrepancy in local login (`CreateSession`) allows distinguishing valid vs. invalid usernames - (File: `core/sessions/localauth/orm.go`)

### Summary
`orm.CreateSession` (and the equivalent `localLoginFallback` fallbacks in the LDAP and OIDC authenticators) look up the user by email first and return an error immediately if no row is found, only calling the password-hash comparison (`utils.CheckPasswordHash`) when a matching user exists. This produces the same class of bug as CVE-2022-34174: an unprivileged caller can measure response time on the `/sessions` login endpoint to determine whether a given email/username exists in the system, because the "invalid email" path skips the expensive password hashing/verification work that the "valid email, wrong password" path performs.

### Finding Description
The login flow entry point is `SessionsController.Create`, which forwards the request body directly to `AuthenticationProvider().CreateSession`: [1](#0-0) 

In the local authentication ORM, `CreateSession` calls `FindUser` and returns immediately on error (i.e., no matching email), before ever touching `constantTimeEmailCompare` or `utils.CheckPasswordHash`: [2](#0-1) 

Only when the email is found does the code proceed to `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))`, which performs a full password-hash comparison (a typically bcrypt-style, deliberately slow computation). This means:
- Invalid email → fast fail (only a DB SELECT, then immediate `return`).
- Valid email + wrong password → slow fail (DB SELECT + full hash comparison of the submitted password).

The exact same asymmetric pattern appears in the LDAP and OIDC local-fallback logins: [3](#0-2) [4](#0-3) 

and again in `TestPassword`, used for password-change/validation flows: [5](#0-4) 

This is precisely the bug class described in the Jenkins advisory: the login handler does not perform an equivalent-cost operation (e.g., validating against a synthetic/dummy password hash) when the username does not exist, creating a measurable timing side-channel.

### Impact Explanation
An unauthenticated network attacker hitting the `/sessions` endpoint can use response-time measurements to enumerate valid Chainlink node operator usernames/emails. This does not directly grant access, but it materially aids credential-stuffing or targeted brute-force/password-guessing campaigns against the node's admin UI/API by first identifying which accounts exist, consistent with CWE-203/CWE-208 (information exposure through timing discrepancy). Impact is capped at information disclosure of username validity — no direct auth bypass.

### Likelihood Explanation
The login endpoint is internet/network reachable by design (any client submitting `POST /sessions` with `email`/`password`), and the branch causing the timing gap is unconditionally reached on every login attempt with no rate limiting shown in the reviewed path. Because the discrepancy is deterministic and large in relative terms (a DB-only lookup vs. DB lookup + password hash verification), the attack is practically measurable over a network with enough averaged samples, similar to the original Jenkins finding.

### Recommendation
When `FindUser` (or the LDAP/OIDC lookup) fails to find a matching email, perform an equivalent-cost dummy hash comparison (e.g., `utils.CheckPasswordHash(sr.Password, syntheticHash)`) before returning the "invalid email" error, so that both the "email not found" and "email found, wrong password" code paths take a comparable amount of time. Apply the same fix consistently to `localauth/orm.go`'s `CreateSession`/`TestPassword`, `ldapauth/ldap.go`'s `localLoginFallback`, and `oidcauth/oidc.go`'s `localLoginFallback`/`TestPassword`.

### Proof of Concept
1. Create one legitimate user account (e.g., `real@example.com` / any password).
2. Send repeated `POST /sessions` requests with `{"email":"nonexistent@example.com","password":"x"}` and time the responses (baseline: DB lookup only, fast fail).
3. Send repeated `POST /sessions` requests with `{"email":"real@example.com","password":"wrongpassword"}` and time the responses (DB lookup + `CheckPasswordHash`, slower fail).
4. Average many samples for each case (to cancel network jitter); the "valid email, wrong password" case will show a statistically significant higher latency than the "invalid email" case, confirming the timing side-channel that leaks username validity.

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

**File:** core/sessions/localauth/orm.go (L308-318)
```go
// TestPassword checks plaintext user provided password with hashed database password, returns nil if matched
func (o *orm) TestPassword(ctx context.Context, email string, password string) error {
	var hashedPassword string
	if err := o.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return pkgerrors.New("no matching user for provided email")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return pkgerrors.New("passwords don't match")
	}
	return nil
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
