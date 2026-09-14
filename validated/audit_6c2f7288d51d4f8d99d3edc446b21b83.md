### Title
Username-Dependent Timing Side-Channel in Local Authentication Login Enables Account Enumeration - (File: core/sessions/localauth/orm.go)

### Summary
The local authentication provider's `CreateSession` function returns immediately when the submitted email does not match any user in the database, skipping the computationally expensive bcrypt password comparison. When the email does exist, `utils.CheckPasswordHash` (bcrypt) is always invoked. This produces a measurable response-time difference between "unknown user" and "known user, wrong password" requests, directly matching the root cause pattern described in the RansomLook CVE-2026-78551 report.

### Finding Description
`orm.CreateSession` first calls `o.FindUser(ctx, sr.Email)`, which issues `SELECT * FROM users WHERE lower(email) = lower($1)`. If no user is found, the function returns the DB error immediately: [1](#0-0) 

Only when a user row is found does the code proceed to the constant-time email comparison and, critically, the bcrypt verification via `utils.CheckPasswordHash`: [2](#0-1) 

Because bcrypt is deliberately slow (by design, to resist brute-forcing), and it is only invoked on the "user exists" code path, an unauthenticated attacker measuring response latency of `POST /sessions` can distinguish valid emails (slow, bcrypt executed) from invalid emails (fast, short-circuited at the DB lookup) — the exact bug class described in the external report. The same pattern is duplicated in the LDAP and OIDC local-fallback authenticators (`localLoginFallback` in `core/sessions/ldapauth/ldap.go:622-642` and `core/sessions/oidcauth/oidc.go:578-597`), which perform the DB lookup before invoking `utils.CheckPasswordHash`. [3](#0-2) [4](#0-3) 

### Impact Explanation
An unauthenticated remote attacker can enumerate valid Operator UI / Node API usernames (emails) by observing timing differences on the `/sessions` endpoint. This is a purely informational leak (username enumeration) rather than a full authentication bypass, but it materially aids follow-on credential-stuffing or targeted password-guessing attacks against confirmed accounts. Unlike the RansomLook report's second issue (unthrottled brute force via a spoofable client IP), the underlying Chainlink node **does** rate-limit unauthenticated requests to `/sessions` (5 requests / 20s by default) and does **not** trust client-supplied `X-Forwarded-For`/`X-Real-IP` headers for rate-limiting (`engine.RemoteIPHeaders = nil`), so the brute-force/DoS component of the original CVE is not reproducible here. [5](#0-4) [6](#0-5) 

### Likelihood Explanation
High reachability: the `/sessions` endpoint is unauthenticated and internet-facing by design, and no code changes are needed to trigger the timing difference — any client can submit varying emails and measure response time. However, network jitter and the rate limit (5 req/20s per client IP) constrain the practical speed of measurement/enumeration, making this a lower-severity, best-effort side channel rather than a reliable oracle.

### Recommendation
Perform a dummy bcrypt comparison (against a precomputed/random hash) on the "user not found" path in `orm.CreateSession`, `ldapAuthenticator.localLoginFallback`, and `oidcAuthenticator.localLoginFallback`, so that both branches perform equivalent-cost work before returning an error, matching the RansomLook fix pattern of always executing password verification with a dummy hash when the username is unknown.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"nonexistent@x.com","password":"whatever"}` and measure response time (fast — short-circuited by `FindUser` error at `core/sessions/localauth/orm.go:145-148`).
2. Send `POST /sessions` with a known valid email and an incorrect password; measure response time (slower — bcrypt executed at `core/sessions/localauth/orm.go:159`).
3. Repeat across many candidate emails within the rate-limit window; statistically distinguish valid vs. invalid accounts by response latency.

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

**File:** core/sessions/ldapauth/ldap.go (L624-639)
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
```

**File:** core/sessions/oidcauth/oidc.go (L580-594)
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
```

**File:** core/web/router.go (L48-50)
```go
func NewRouter(app chainlink.Application, prometheus *ginprom.Prometheus) (*gin.Engine, error) {
	engine := gin.New()
	engine.RemoteIPHeaders = nil // don't trust default headers: "X-Forwarded-For", "X-Real-IP"
```

**File:** core/web/router.go (L207-216)
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
```
