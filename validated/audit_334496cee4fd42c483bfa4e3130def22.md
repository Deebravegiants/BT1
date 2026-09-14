### Title
Login Endpoint Username Enumeration via Authentication Timing Side-Channel - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated session-creation endpoint (`POST /sessions`, handled by `SessionsController.Create`) exhibits a measurable timing difference between "user does not exist" and "user exists, wrong password" responses, allowing an anonymous attacker to enumerate valid Chainlink node UI usernames — the same bug class as CVE-2025-43754 (Liferay login timing enumeration).

### Finding Description
`SessionsController.Create` accepts an unauthenticated `SessionRequest{Email, Password}` and forwards it to `AuthenticationProvider().CreateSession`. [1](#0-0) 

In the local authenticator, `CreateSession` first performs a fast DB lookup via `FindUser`. If the email does not exist, it returns immediately with an error — no bcrypt operation is performed. If the email does exist, execution proceeds to `constantTimeEmailCompare` and then `utils.CheckPasswordHash`, which runs an expensive bcrypt comparison, followed by an additional `GetUserWebAuthn` DB query: [2](#0-1) 

Because bcrypt hashing/verification is intentionally slow (unlike a DB miss), the two code paths ("unknown email" vs "known email, wrong password") have significantly different response latencies. The same pattern — fast-fail on `FindUser`/DB lookup errors, followed by bcrypt-based `CheckPasswordHash` only when a matching row exists — is repeated in the LDAP and OIDC local-fallback authenticators: [3](#0-2) [4](#0-3) 

Additionally, prior to even calling `CreateSession`, `SessionsController.Create` calls `GetUserWebAuthn(ctx, sr.Email)` unauthenticated, which is another email-keyed DB round trip whose behavior/timing can differ based on whether the account and its associated WebAuthn tokens exist: [5](#0-4) 

This is directly analogous to the reported Liferay vulnerability: the server's processing time for a login request differs measurably depending on whether the submitted account exists, enabling username enumeration (CWE-208) without needing valid credentials.

### Impact Explanation
An unauthenticated attacker can distinguish valid vs. invalid node-admin email/usernames purely from response timing on the public `POST /sessions` endpoint, without triggering lockouts or audit alerts tied to failed logins for nonexistent accounts. Confirmed usernames materially reduce the effort of subsequent credential-stuffing, password-spraying, or social-engineering attacks against a Chainlink node's operator/API-user accounts, which control fund-relevant and job-management functionality.

### Likelihood Explanation
Exploitation only requires unauthenticated HTTP access to the node's `/sessions` endpoint and repeated timing measurements (standard technique, statistically robust against network jitter with enough samples). No special privileges, node trust, or internal access are required, making likelihood moderate-to-high wherever the node's web UI/API is network reachable.

### Recommendation
Normalize authentication timing regardless of whether the account exists: always perform a dummy bcrypt comparison (e.g., against a static/precomputed hash) when `FindUser` fails, so both "unknown user" and "wrong password" paths take comparable time. Apply the same fix uniformly across `core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go`, and `core/sessions/oidcauth/oidc.go`. Additionally, consider moving the pre-check `GetUserWebAuthn` call in `core/web/sessions_controller.go` to occur only after a successful password check, or ensure it also executes at constant time/behavior for unknown emails.

### Proof of Concept
1. As an unauthenticated client, send repeated `POST /sessions` requests with `email=known_admin@example.com&password=wrong` and measure response latency (bcrypt path executed).
2. Send repeated `POST /sessions` requests with `email=random_nonexistent@example.com&password=wrong` and measure latency (fast DB-miss path, no bcrypt).
3. Aggregate timing samples (e.g., median over 50+ requests per candidate) — the bcrypt path is consistently and measurably slower, allowing an attacker to distinguish valid from invalid emails and enumerate node user accounts without any authenticated access.

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

**File:** core/sessions/ldapauth/ldap.go (L622-641)
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
