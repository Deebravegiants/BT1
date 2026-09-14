### Title
Username Enumeration via Timing Attack in Local Login Endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `/sessions` login endpoint short-circuits before performing an expensive `bcrypt` comparison when the supplied email does not match a user in the database. This causes login attempts for valid usernames to take measurably longer than attempts for invalid usernames, allowing an unauthenticated remote attacker to enumerate valid Chainlink node user accounts — the same bug class described in the external report for `@sync-in/server`.

### Finding Description
`SessionsController.Create` in [1](#0-0)  is reachable by any unauthenticated client and forwards the raw `SessionRequest` to `AuthenticationProvider().CreateSession`.

In the local authentication provider, `CreateSession` first calls `FindUser`, which performs a DB lookup keyed on email, and returns immediately with an error if no row is found — before ever touching the password comparison logic: [2](#0-1) 

Only when a matching user row exists does the code proceed to `constantTimeEmailCompare` and then `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword`: [3](#0-2) 

`bcrypt.CompareHashAndPassword` is intentionally computationally expensive (tunable work factor), so a request for a valid email incurs one bcrypt round-trip (tens to low-hundreds of milliseconds depending on cost factor) while a request for a nonexistent email returns almost immediately after a single indexed SQL lookup. This is the exact root-cause pattern cited in the external report: a lack of a matched user causing early short-circuiting and a resulting timing discrepancy.

The same short-circuit pattern is repeated in the other authentication providers' local-fallback paths, all reachable through the same unauthenticated `/sessions` endpoint depending on configured auth driver:
- `oidcauth.localLoginFallback` [4](#0-3) 
- `ldapauth.localLoginFallback` [5](#0-4) 

Additionally, `TestPassword` in each provider performs a SQL lookup and returns a generic error immediately if no row is found, before any bcrypt hashing occurs, exhibiting the same timing asymmetry: [6](#0-5) 

### Impact Explanation
An unauthenticated remote attacker can distinguish valid from invalid node usernames purely by measuring response latency on `/sessions` (or `/api/v2/...` `TestPassword`-backed flows), without needing valid credentials. This lets attackers build a list of valid admin/operator emails on a Chainlink node, materially aiding targeted credential stuffing, password spraying, and phishing/social-engineering campaigns against a node operator's authentication surface. It does not by itself yield authentication bypass or secret disclosure, consistent with the Medium severity and Confidentiality-Low CVSS rating of the referenced advisory.

### Likelihood Explanation
The `/sessions` endpoint requires no authentication and no rate limiting is visible in this code path (only `sc.App.WakeSessionReaper()` runs afterward). The timing signal (presence/absence of a bcrypt round trip) is large and consistent, making this practically exploitable with standard timing-attack tooling (e.g., the TickTock Burp extension referenced in the source report) against any externally reachable Chainlink node UI/API.

### Recommendation
Normalize response timing for the login path regardless of whether a user is found:
- Always perform an equivalent-cost dummy bcrypt comparison (e.g., against a static/precomputed hash) when `FindUser` returns no result, before returning the "invalid credentials" error.
- Apply the same normalization to `TestPassword` in `localauth`, `oidcauth`, and `ldapauth`.
- Consider rate limiting/backoff on `/sessions` to further reduce enumeration and brute-force feasibility.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"admin@example.com","password":"wrong"}` where `admin@example.com` is a valid, existing node user — measure response time (will include a bcrypt compare, e.g. ~100-300ms depending on cost factor).
2. Send `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrong"}` — measure response time (returns immediately after `FindUser` SQL miss, typically single-digit ms).
3. Repeating both requests many times and comparing average latency distributions (as done with TickTock Enum in the original report) reliably distinguishes valid from invalid emails, confirming the enumeration channel, mirroring the exact flow in `orm.CreateSession` at [2](#0-1) .

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
