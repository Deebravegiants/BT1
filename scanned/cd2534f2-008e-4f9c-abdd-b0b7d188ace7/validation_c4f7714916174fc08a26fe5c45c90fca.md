### Title
User Enumeration via Login Response-Timing Side Channel in Session Creation - ([File: core/sessions/localauth/orm.go])

### Summary
The `/sessions` login endpoint's `CreateSession` flow performs a fast-failing database lookup for a user's email, and only executes the expensive bcrypt password hash comparison when a user record is actually found. This produces a measurable timing difference between "email does not exist" and "email exists, password wrong" responses, directly analogous to CVE-2024-26268 (Liferay user enumeration via response-time comparison).

### Finding Description
`CreateSession` in the local authentication provider first calls `FindUser`, which executes `SELECT * FROM users WHERE lower(email) = lower($1)` and immediately returns an error if no row matches: [1](#0-0) 

If the email doesn't exist, the function returns almost immediately after a single indexed SQL lookup. If the email does exist, execution proceeds to `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))`, which performs a deliberately slow bcrypt comparison (bcrypt's whole design goal is to be computationally expensive, typically tens of milliseconds), before returning "Invalid password". This asymmetry — fast rejection for unknown emails vs. slow rejection for known emails with wrong passwords — leaks account existence through response timing, exactly the bug class described in the report (CWE-203).

The identical pattern is repeated in the other two pluggable authentication providers that also expose a login/`CreateSession` path reachable from the unauthenticated `/sessions` endpoint: [2](#0-1) [3](#0-2) 

Although these providers use `constantTimeEmailCompare` to avoid leaking information via string-comparison timing on the email field itself, this does not address the far larger timing signal introduced by conditionally invoking bcrypt only when a row is found — the DB lookup fails fast for nonexistent users, while `CheckPasswordHash` (a slow, intentionally expensive hash comparison) is executed only for existing users.

The endpoint is reachable by any unauthenticated remote client via `SessionsController.Create`, which calls `AuthenticationProvider().CreateSession(ctx, sr)` directly with attacker-supplied `sr.Email`/`sr.Password`: [4](#0-3) 

### Impact Explanation
An unauthenticated remote attacker can send repeated POST requests to `/sessions` with different candidate emails and measure response latency to determine whether each email corresponds to a registered Chainlink node operator/admin account. This does not directly compromise credentials or session tokens, but it discloses valid account identifiers (CWE-203), which materially aids follow-on targeted credential stuffing, phishing, or brute-force attacks against the node's admin/API-user accounts — consistent with the Medium severity and low-impact (C:L) classification of the reference CVE.

### Likelihood Explanation
Likelihood is moderate-to-high: the endpoint is internet-facing (subject to the operator's network exposure of the Operator UI/API), requires no authentication or special privileges to probe, and the timing signal (bcrypt cost factor vs. a single indexed SQL SELECT) is large and consistently reproducible over many samples, making statistical timing attacks straightforward even over a network with typical jitter.

### Recommendation
Remove the account-existence-dependent branching before the password check. Standard mitigations include:
1. Always perform a constant-cost, dummy password-hash comparison (e.g., against a precomputed dummy bcrypt hash) when `FindUser` returns "not found", so the total response time is statistically indistinguishable from the "found, wrong password" case.
2. Alternatively, perform the `CheckPasswordHash` step against a fixed dummy hash in all cases before branching on whether the user exists, ensuring uniform latency regardless of email validity.
3. Apply the same fix uniformly to `core/sessions/localauth/orm.go` `CreateSession`, `core/sessions/ldapauth/ldap.go` `localLoginFallback`, and `core/sessions/oidcauth/oidc.go` `localLoginFallback`.

### Proof of Concept
1. Register one known user account (e.g. `real-admin@node.local`) with a strong password on a running Chainlink node.
2. Send repeated `POST /sessions` requests with `{"email":"real-admin@node.local","password":"wrong"}` and record response time (triggers `FindUser` success + `CheckPasswordHash` bcrypt compare).
3. Send repeated `POST /sessions` requests with `{"email":"nonexistent-user@node.local","password":"wrong"}` and record response time (triggers `FindUser` failure, fast SQL-only path, no bcrypt call).
4. Compare mean/median latencies across many trials (statistically averaging out network jitter, e.g. hundreds of requests each) — the known-email requests will show a consistent latency increase corresponding to bcrypt's cost factor, confirming the account's existence can be inferred without valid credentials.

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
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
