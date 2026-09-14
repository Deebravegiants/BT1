Confirmed: `CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword` [1](#0-0) , which is computationally expensive (unlike the fast, cheap DB lookup that fails when a user doesn't exist). This creates the exact timing asymmetry described in CVE-2022-40482.

### Title
Timing-based user enumeration via early return in local login authentication - (File: core/sessions/localauth/orm.go)

### Summary
The `CreateSession` login flow performs an early return when `FindUser` fails to locate an account by email, skipping the expensive bcrypt password comparison entirely. When the email does exist, bcrypt's `CompareHashAndPassword` runs, adding a measurable, consistent delay. This mirrors the exact root cause in CVE-2022-40482 (Laravel's `hasValidCredentials` early return before password hashing), enabling an unauthenticated attacker to distinguish valid from invalid emails by measuring response time on the public `/sessions` login endpoint.

### Finding Description
`sessionRoutes` registers `POST /sessions` on the **unauthenticated** router group (`unauth.POST("/sessions", sc.Create)`) [2](#0-1) . The `SessionsController.Create` handler first calls `GetUserWebAuthn` (a DB query keyed by email) and then forwards to the configured `AuthenticationProvider().CreateSession` [3](#0-2) .

In the local authentication provider, `CreateSession` looks up the user first and returns immediately on failure, prior to any password verification:
```go
user, err := o.FindUser(ctx, sr.Email)
if err != nil {
    return "", err
}
...
if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
    ...
}
``` [4](#0-3) 

`CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, a deliberately slow, cost-tunable hashing algorithm [1](#0-0) . When the submitted email does not exist, the handler returns after only a cheap SQL `SELECT ... WHERE lower(email)=lower($1)` miss. When the email does exist but the password is wrong, the handler additionally executes the bcrypt comparison, adding tens of milliseconds of latency. This produces a reliably distinguishable timing signal between "email not found" and "email found, wrong password" — the identical bug class described in CVE-2022-40482.

The same early-return-before-hash pattern is duplicated in the LDAP and OIDC local-login fallback paths (`localLoginFallback` in `core/sessions/ldapauth/ldap.go:624-641` and `core/sessions/oidcauth/oidc.go:580-596`), both reachable via the same unauthenticated `/sessions` route depending on configured `AuthenticationProvider`.

### Impact Explanation
An unauthenticated remote attacker can enumerate valid admin/API user email addresses registered on a Chainlink node by measuring response timing on the public login endpoint, without needing any credentials. This does not directly grant access but is a meaningful reconnaissance primitive that narrows credential-stuffing / brute-force targeting against a Chainlink node's admin UI, consistent with the "Medium" severity and CVSS vector of the underlying CVE (confidentiality-only impact, no integrity/availability effect).

### Likelihood Explanation
The `/sessions` endpoint is explicitly unauthenticated and internet-facing by design (it's the login endpoint) [2](#0-1) . Exploitation only requires sending repeated login POSTs and statistically measuring latency, a well-established technique (timing side channels, including HTTP/2 multiplexed "timeless" variants per the referenced advisory). The endpoint is rate-limited (`rl.UnauthenticatedPeriod()`), which raises the practical difficulty but does not eliminate the signal, since rate limiting reduces request volume rather than removing the underlying constant-time gap.

### Recommendation
Perform a constant-time-equivalent password check regardless of whether the user was found — e.g., always run `bcrypt.CompareHashAndPassword` against a valid dummy/fixed hash when `FindUser` fails, before returning the generic "invalid email/password" error, so that both code paths take statistically indistinguishable time. Apply the same fix to `localLoginFallback` in the LDAP and OIDC authenticators.

### Proof of Concept
1. Deploy a Chainlink node with one known-registered admin email (`admin@example.com`).
2. Send repeated `POST /sessions` requests with `{"email":"admin@example.com","password":"wrong"}` and time the responses (path: found user → bcrypt compare → reject).
3. Send repeated `POST /sessions` requests with `{"email":"doesnotexist@example.com","password":"wrong"}` and time the responses (path: `FindUser` DB miss → immediate return, no bcrypt call).
4. Average timings over many samples (accounting for rate limiting/backoff) show a statistically significant, consistent latency gap for existing vs. non-existing emails, allowing account enumeration — mirroring the PoC methodology in the referenced `ephort/laravel-user-enumeration-demo`.

### Citations

**File:** core/utils/utils.go (L131-135)
```go
// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
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

**File:** core/web/sessions_controller.go (L41-60)
```go
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
