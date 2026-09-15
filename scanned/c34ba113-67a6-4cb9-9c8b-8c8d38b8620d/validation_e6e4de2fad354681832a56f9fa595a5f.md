Confirmed: `SessionsController.Create` is an unauthenticated POST `/sessions` endpoint that directly forwards the request body to `AuthenticationProvider().CreateSession`, which in `localauth/orm.go`'s `CreateSession` performs an early, cheap `FindUser` DB lookup and returns immediately on a non-existent email, but only runs the expensive `bcrypt.CompareHashAndPassword` (via `utils.CheckPasswordHash`) when the email *does* exist. This is precisely the bug-class described in CVE-2025-22234: the "existing user, wrong password" path is measurably slower than the "no such user" path, giving an unauthenticated caller a timing oracle to enumerate valid Chainlink node operator emails.

### Title
Timing side-channel in local login (`CreateSession`) permits unauthenticated email/username enumeration - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint (`SessionsController.Create` → `AuthenticationProvider().CreateSession`) exhibits an asymmetric-cost authentication check: a nonexistent email fails fast (a single indexed SQL lookup), while an existing email with a wrong password additionally executes `bcrypt.CompareHashAndPassword`, which is deliberately expensive (default cost factor). This mirrors the exact bug class in CVE-2025-22234/GHSA-vqxh-445g-37fc, where Spring Security's `DaoAuthenticationProvider` timing-attack mitigation (meant to make "unknown user" and "wrong password" responses take the same time) was broken, allowing username enumeration via response-time differences.

### Finding Description
`orm.CreateSession` in [1](#0-0)  first calls `o.FindUser(ctx, sr.Email)`, which runs `SELECT * FROM users WHERE lower(email) = lower($1)` [2](#0-1) . If the email doesn't exist, the function returns immediately with an error — no password hashing occurs. Only if the user is found does the code proceed to `constantTimeEmailCompare` (cheap, fixed-length compare) and then `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))`, which wraps `bcrypt.CompareHashAndPassword` [3](#0-2) . bcrypt is intentionally slow (tens of milliseconds by default cost), so the response time for "valid email, wrong password" is substantially and measurably longer than "email not found." No dummy/constant-cost hash comparison is performed for the not-found case to equalize timing, unlike what a correctly-fixed `DaoAuthenticationProvider` should do.

This request path is fully reachable by an unauthenticated caller via `SessionsController.Create` at `POST /sessions` [4](#0-3) , which passes the raw `SessionRequest{Email, Password}` straight into `CreateSession`. The same pattern is repeated in the LDAP and OIDC local-login fallbacks (`localLoginFallback`) [5](#0-4) [6](#0-5) , both of which query the user first and only run `CheckPasswordHash` if found.

### Impact Explanation
An unauthenticated network client can send repeated `POST /sessions` requests with different candidate emails and a fixed wrong password, then measure response latency to determine which emails correspond to real Chainlink node operator/admin accounts. This is a confidentiality leak (CWE-208) that facilitates targeted credential-stuffing/brute-force or social-engineering attacks against real operator accounts, and can also reveal whether WebAuthn/MFA is configured for a given account (since `GetUserWebAuthn` is called before `CreateSession` in the controller, and email existence gates that as well). Severity is Medium, matching the CVSS of the original advisory (network-reachable, low complexity, no privileges/UI required, limited confidentiality impact).

### Likelihood Explanation
The endpoint is unauthenticated and directly internet-facing (subject only to whatever network exposure the operator chooses for the node's UI API), requires no special conditions, and the timing differential from bcrypt's default cost factor is large enough (tens of ms) to be reliably distinguished over a network with a modest number of samples/averaging. Likelihood is Medium-High for a determined attacker attempting operator account enumeration.

### Recommendation
Equalize the cost of the "user not found" and "wrong password" code paths in `CreateSession`, `localLoginFallback` (LDAP and OIDC), by performing a dummy bcrypt comparison against a fixed/static hash whenever `FindUser` fails, so that both branches always execute a comparable-cost bcrypt operation before returning an error. Alternatively, add random jitter is not sufficient by itself; use the "always hash" pattern used to fix Spring Security's original CVE-2025-22228 without reintroducing CVE-2025-22234 (i.e., always invoke the password encoder/compare with either the real or a pre-computed dummy hash, never skip it).

### Proof of Concept
1. Create one legitimate node operator user (e.g. `real@node.com` with a valid password).
2. Send `POST /sessions` with `{"email":"real@node.com","password":"wrongpassword"}` and measure response time (this triggers bcrypt compare, ~tens of ms).
3. Send `POST /sessions` with `{"email":"doesnotexist@node.com","password":"wrongpassword"}` and measure response time (fails at `FindUser`, no bcrypt, much faster).
4. Repeat both requests N times and average to reduce network jitter noise; the timing distributions are statistically distinguishable, allowing an attacker to determine that `real@node.com` is a valid account without any credentials.

### Citations

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
