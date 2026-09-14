## Analysis

The reported CVE-2026-47783 describes a **timing side-channel in credential/username verification** — a loop exits early once a valid username is found, letting an attacker infer valid usernames by measuring response time. The chainlink codebase has a directly analogous, unprivileged-reachable pattern in its local password-authentication login flow.

### Title
Timing side-channel in `POST /sessions` login flow allows unprivileged user-enumeration via response-time analysis - (File: `core/sessions/localauth/orm.go`)

### Summary
The unauthenticated session-creation endpoint (`SessionsController.Create`) short-circuits with a fast DB-only path when the supplied email does not exist, but falls through to an expensive bcrypt password comparison when the email does exist. This produces a measurable timing difference that lets any unauthenticated remote client enumerate valid user emails — the same bug class as the memcached CVE (early-exit behavior that is fast for "no match" and slow for "match" leaking which identifiers are valid).

### Finding Description
`SessionsController.Create` is a completely unauthenticated HTTP handler that accepts an email/password JSON body and forwards it to `AuthenticationProvider().CreateSession`: [1](#0-0) 

In the local-auth implementation, `CreateSession` first looks up the user by email. If the user does not exist, the function returns immediately with an error — no bcrypt hash comparison is ever performed. Only if the email *does* exist does the code proceed to `constantTimeEmailCompare` and then `utils.CheckPasswordHash`, which invokes bcrypt (a deliberately slow, cost-tunable hash): [2](#0-1) 

`utils.CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is intentionally expensive (tens of milliseconds depending on cost factor): [3](#0-2) 

The same early-exit-on-nonexistence pattern (fast path for unknown email, slow bcrypt path for known email) is repeated in the LDAP and OIDC local-fallback authenticators: [4](#0-3) [5](#0-4) 

and in the standalone `TestPassword` helpers used for CLI/admin fallback login: [6](#0-5) 

Notably, the codebase already contains a `constantTimeEmailCompare` helper specifically designed to defend against timing side channels for email comparison, showing the developers are aware of this bug class — but it only guards the string comparison *after* the existence check has already leaked information via the DB-lookup/no-bcrypt fast path: [7](#0-6) 

Additionally, `SessionsController.Create` calls `GetUserWebAuthn(ctx, sr.Email)` before invoking `CreateSession`, which is a second unauthenticated, pre-auth database query keyed directly on attacker-supplied email — a separate query surface but consistent with the design gap (no dummy/constant-cost work is performed for the "does this identity exist" question): [8](#0-7) 

### Impact Explanation
An unauthenticated remote attacker can send repeated `POST /sessions` requests with candidate emails and measure response latency: fast responses indicate the email is not a registered user; slow responses (bcrypt-cost dominated) indicate the email is valid. This enables systematic account/user enumeration against the node's operator/admin UI login endpoint, which can be leveraged for targeted credential stuffing, phishing, or as a precursor to brute-forcing MFA-less accounts. This affects the node operator authentication surface, which is explicitly in scope (session/token handling).

### Likelihood Explanation
The endpoint is fully unauthenticated and internet-facing by default (`/sessions`), requires no special preconditions, and the bcrypt cost differential is generally large enough (tens of ms) to be statistically distinguishable over many samples even with network jitter, making this a realistic, low-effort probe for an unprivileged actor.

### Recommendation
Perform a constant-cost operation on the "user not found" path — e.g., always run a dummy bcrypt comparison against a fixed/precomputed hash when `FindUser` fails, before returning the auth error — so the response timing is statistically indistinguishable between "unknown email" and "known email, wrong password" across all three authenticators (`localauth`, `ldapauth`, `oidcauth`) and their `TestPassword` fallbacks.

### Proof of Concept
1. Send `POST /sessions` with a known-valid email and a wrong password; measure response time (dominated by bcrypt compare, e.g., ~50-150ms depending on cost factor).
2. Send `POST /sessions` with a random/nonexistent email; measure response time (fast DB-miss path, no bcrypt call) — see the early `return "", err` at [9](#0-8) .
3. Repeat over many samples for a set of candidate emails to statistically separate "exists" vs "does not exist" based on mean latency, confirming user enumeration without any credentials.

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
