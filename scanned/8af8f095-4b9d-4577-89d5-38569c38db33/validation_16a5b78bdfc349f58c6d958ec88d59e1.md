## Title
Username (Email) Enumeration via Timing Oracle in Local Auth `CreateSession` / `/sessions` Login Endpoint - (File: `core/sessions/localauth/orm.go`)

### Summary
The unauthenticated `POST /sessions` login endpoint calls `orm.CreateSession`, which first looks up the user by email and returns immediately on a lookup failure — *before* any bcrypt password comparison is performed. Only when a user record is found does the code proceed to call `utils.CheckPasswordHash`, which invokes `bcrypt.CompareHashAndPassword` (inherently slow, ~tens to ~100ms depending on cost factor). This produces a large, remotely measurable timing gap between "email exists" and "email does not exist" requests, exactly matching the reported GoFiber `BasicAuth` timing-oracle bug class (CWE-203): the default authorizer short-circuits and skips the expensive hash comparison for unknown identities.

### Finding Description
The login flow is: [1](#0-0) 

`sessionRoutes` mounts `POST /sessions` on the *unauthenticated* group and routes it to `SessionsController.Create`: [2](#0-1) 

`Create` calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`. With the default `LocalAuth` provider, this resolves to `orm.CreateSession`: [3](#0-2) 

The critical logic:
```go
user, err := o.FindUser(ctx, sr.Email)
if err != nil {
    return "", err   // fast path — no user found, returns immediately
}
...
if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {  // bcrypt, slow
    ...
}
```

`FindUser` performs a simple, fast SQL lookup: [4](#0-3) 

`CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is deliberately slow (tunable work factor): [5](#0-4) 

So for a **nonexistent email**, the request returns almost instantly (DB miss only). For a **valid email with wrong password**, the request must pay the full bcrypt cost (`~50–150ms` at default cost) before returning an error. This is functionally identical to the reported GoFiber bug: the code takes a "verified, exists" branch vs. a "not found" branch, and only the "exists" branch pays for the expensive comparison. The same pattern also exists in the LDAP and OIDC local-fallback authenticators, which share this structure: [6](#0-5) [7](#0-6) 

Note that `constantTimeEmailCompare` in `orm.go` is a red herring for this bug — it only guards against timing differences *within* the "user found" branch (comparing an already-fetched email against the input), it does nothing to equalize the found-vs-not-found timing gap: [8](#0-7) 

### Impact Explanation
An unauthenticated, unprivileged remote attacker hitting `POST /sessions` can distinguish valid Chainlink node user emails from invalid ones purely by measuring response latency, without needing correct credentials or triggering account lockouts. This is a username-enumeration primitive (CWE-203) against the node's operator/admin/API accounts. Once valid emails are known, an attacker can focus credential-stuffing/brute-force efforts (subject to the existing rate limiter) only on real accounts, and can map out which admin/edit/run-role accounts exist on an internet-facing node — informing further targeted attacks against fund-movement and job-management endpoints gated by these very accounts.

### Likelihood Explanation
The `/sessions` endpoint is intentionally public/unauthenticated (`unauth.POST("/sessions", sc.Create)`), so the attack requires no privileges. The endpoint is rate-limited (`rl.UnauthenticatedPeriod()/rl.Unauthenticated()`), which slows but does not prevent statistical timing measurement — attackers can average across the permitted request budget over time, and the timing gap (bcrypt-scale, i.e., tens of ms or more) is large enough to be distinguishable even over a noisy network with a modest number of samples. This mirrors the reported advisory's core claim (bcrypt timing ratio is large, ~1,000,000:1 in the worst case, though effective ratio here is milliseconds vs. microseconds due to added DB round trip on the "not found" path).

### Recommendation
Ensure constant-time behavior regardless of whether the user exists:
- In `orm.CreateSession` (and the LDAP/OIDC `localLoginFallback` equivalents), when `FindUser`/lookup fails, still perform a dummy `bcrypt.CompareHashAndPassword` against a fixed dummy hash before returning the error, so total execution time is equalized between "user found" and "user not found" paths.
- Alternatively, always fetch a (real or dummy) hashed password and always invoke `utils.CheckPasswordHash` unconditionally, only branching on the boolean results afterward.
- Consider using a fixed minimum handler duration (e.g., padding the response to a floor latency) as a defense-in-depth measure on the `/sessions` endpoint.

### Proof of Concept
1. Create/identify one legitimate user email on the node (e.g., via a normal signup or default admin bootstrap).
2. Send repeated `POST /sessions` requests with `{"email":"<valid-email>","password":"wrong"}` and measure round-trip time — observe response consistently gated by bcrypt cost (tens of ms+).
3. Send the same volume of requests with `{"email":"<random-nonexistent-email>","password":"wrong"}` — observe consistently faster responses (DB miss only, no bcrypt call).
4. Statistically distinguishing the two populations (e.g., averaging over N requests within rate-limit budget) reveals which candidate emails correspond to real accounts, without ever learning a correct password.

### Citations

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

**File:** core/sessions/localauth/orm.go (L43-59)
```go
// FindUser will attempt to return an API user by email.
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}

// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}

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

**File:** core/sessions/localauth/orm.go (L232-241)
```go
const constantTimeEmailLength = 256

func constantTimeEmailCompare(left, right string) bool {
	length := mathutil.Max(constantTimeEmailLength, len(left), len(right))
	leftBytes := make([]byte, length)
	rightBytes := make([]byte, length)
	copy(leftBytes, left)
	copy(rightBytes, right)
	return subtle.ConstantTimeCompare(leftBytes, rightBytes) == 1
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
