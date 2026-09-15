## Finding

### Title
Login Timing Side-Channel Enables User Enumeration at `/sessions` — ([File: core/sessions/localauth/orm.go])

### Summary
The `/sessions` login endpoint's `CreateSession` handler only performs the expensive bcrypt password hash comparison when a matching user record is found in the database. When the submitted email does not exist, the function returns immediately after the fast SQL lookup fails, skipping `utils.CheckPasswordHash`. This produces a measurable, network-observable timing discrepancy that lets an unauthenticated client distinguish between valid and invalid emails — the same bug class as CVE-2025-30344 (OpenSlides login timing leak from omitted password hashing).

### Finding Description
`SessionsController.Create` in [1](#0-0)  binds the JSON request and forwards it directly to `AuthenticationProvider().CreateSession(ctx, sr)` with no artificial delay or normalization.

The local authentication provider's implementation is: [2](#0-1) 

```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	...
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		...
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		...
		return "", pkgerrors.New("Invalid password")
	}
```

`FindUser` issues a single indexed `SELECT ... WHERE lower(email) = lower($1)` query [3](#0-2) . If no row is returned, the function returns in microseconds, without ever calling `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword` [4](#0-3) . bcrypt is deliberately slow (tens of milliseconds by cost factor), so a request for a valid email incurs a clearly measurable extra delay compared to a request for a non-existent email — the identical root cause described in CVE-2025-30344 ("the system's response times differ ... The timing discrepancy stems from the omitted hashing of the password").

The same pattern is replicated in the LDAP and OIDC local-fallback code paths, `localLoginFallback` in [5](#0-4)  and [6](#0-5) , both of which perform the DB lookup and return immediately on lookup failure before any bcrypt call.

### Impact Explanation
This is reachable by any unauthenticated network client hitting the login endpoint (`POST /sessions`, handled by `SessionsController.Create`). By measuring response latency across repeated requests with different email addresses, an attacker can enumerate valid Chainlink node admin/API user accounts without any credentials. Confirmed valid emails narrow the credential-stuffing/brute-force attack surface and can be combined with weak/reused passwords to escalate to full node control (Chainlink admin API access, job management, key/secret access). This matches CVSS 3.1 vector `AV:N/AC:L/PR:N/UI:N/C:L` — network reachable, no privileges/interaction, limited confidentiality impact (account existence disclosure).

### Likelihood Explanation
High likelihood: the endpoint is unauthenticated and internet-facing by design (node operator login UI/API), the timing gap is bcrypt-scale (tens of milliseconds), and no rate limiting, response-time normalization, or dummy-hash comparison is performed on the miss path in the reviewed code. An attacker only needs standard timing-attack methodology (repeated sampling to reduce network jitter noise), a well-established technique with public tooling.

### Recommendation
Ensure constant-time behavior regardless of whether the user exists:
- On lookup miss, perform a dummy `bcrypt.CompareHashAndPassword` call against a fixed/precomputed hash before returning the "invalid email" error, so the miss path takes comparable time to the hit path.
- Alternatively, always fetch a user row (real or a static dummy user with a precomputed hash) and always execute `utils.CheckPasswordHash`, deferring the "user not found" determination until after the hash comparison.
- Apply the same fix uniformly to `core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go` (`localLoginFallback`), and `core/sessions/oidcauth/oidc.go` (`localLoginFallback`).
- Consider adding response-time-independent rate limiting on `/sessions` to further reduce enumeration feasibility.

### Proof of Concept
1. Send `POST /sessions` with `{"email": "known-admin@example.com", "password": "wrong"}` and measure response time repeatedly (median over N requests) — expect elevated latency due to bcrypt comparison in `utils.CheckPasswordHash`.
2. Send `POST /sessions` with `{"email": "definitely-not-a-user@example.com", "password": "wrong"}` and measure response time repeatedly — expect consistently lower latency since `FindUser` fails and `CreateSession` returns before any bcrypt call (per [7](#0-6) ).
3. The statistically significant latency gap between the two cases confirms the account's existence without needing correct credentials.

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

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
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
