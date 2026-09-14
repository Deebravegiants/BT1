### Title
Timing side-channel in local login allows unauthenticated username enumeration - ([File: core/sessions/localauth/orm.go])

### Summary
`orm.CreateSession` performs an early, fast-failing return when a submitted email is not found in the `users` table, but performs a comparatively slow `bcrypt` hash comparison when the email *does* exist. This produces a measurable response-time difference between "email exists" and "email does not exist" for an unauthenticated caller of the login endpoint, exactly the class of bug described in CVE-2025-22234 (broken timing-attack mitigation in `DaoAuthenticationProvider`, where the fix from CVE-2025-22228 caused the authenticator to skip the password-hash comparison work when the username lookup failed).

### Finding Description
The login endpoint `SessionsController.Create` (`core/web/sessions_controller.go:29-68`) is reachable without authentication and forwards user-supplied `email`/`password` to `AuthenticationProvider().CreateSession`. [1](#0-0) 

In the local authentication ORM, `CreateSession` first calls `FindUser`, and if the email doesn't match any row, it returns immediately with an error — no `bcrypt.CompareHashAndPassword` is executed. Only if the email is found does it proceed to `constantTimeEmailCompare` and then `utils.CheckPasswordHash`, which invokes `bcrypt.CompareHashAndPassword`, a deliberately expensive, cost-parameterized operation: [2](#0-1) 

`utils.CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is intentionally slow (tunable cost factor) and dominates the request latency when the email exists: [3](#0-2) 

By contrast, `findUser`'s failure path is a fast SQL miss with no expensive cryptographic work performed afterward: [4](#0-3) 

This is structurally the same defect as CVE-2025-22234: the correct mitigation (always performing the expensive password verification work regardless of whether the username exists, e.g. against a dummy/default hash) is missing, so the code short-circuits on the cheap path when the account is absent. The same fallback pattern (`localLoginFallback`) exists in `core/sessions/ldapauth/ldap.go:624-642` and `core/sessions/oidcauth/oidc.go:580-597`, both querying the user row and only performing `CheckPasswordHash` if found, reproducing the same timing gap on the local-admin-fallback login path for those authenticators. [5](#0-4) [6](#0-5) 

### Impact Explanation
An unauthenticated network client can repeatedly POST to `/sessions` with different candidate email addresses and measure response latency. Requests for existing accounts will consistently take measurably longer (bcrypt verification) than requests for non-existent accounts (fast DB miss), allowing enumeration of valid Chainlink node operator/API user accounts. This is an information-disclosure issue (CWE-208) that can be chained with credential-stuffing or targeted password-guessing/social-engineering against confirmed valid accounts. It does not by itself grant authentication bypass or fund movement.

### Likelihood Explanation
The `/sessions` endpoint is unauthenticated and internet-facing whenever the node's operator UI/API is exposed. The timing gap is intrinsic to the current control flow (bcrypt cost factor makes the difference practically detectable over the network with modest statistical sampling), and no rate limiting/lockout was found in the reviewed code guarding repeated login attempts. Exploitation only requires timing multiple requests, which is straightforward for a remote unprivileged attacker.

### Recommendation
Ensure the expensive password-verification step is always executed regardless of whether the submitted email matches an existing user — e.g., when `FindUser` returns not-found, still perform a `bcrypt.CompareHashAndPassword` against a precomputed dummy hash before returning the generic "invalid email/password" error, so total processing time is constant between the "user exists" and "user does not exist" branches. Apply the same fix to `localLoginFallback` in `ldapauth` and `oidcauth`. Consider also adding rate limiting/backoff on `/sessions` to further reduce enumeration feasibility.

### Proof of Concept
1. As an unauthenticated client, send repeated `POST /sessions` requests with `{"email":"<known-valid-email>","password":"wrong"}` and measure response time (dominated by bcrypt compare in `CreateSession`, `core/sessions/localauth/orm.go:159`).
2. Send the same volume of requests with `{"email":"<random-nonexistent-email>","password":"wrong"}` and measure response time (fast path returns at `core/sessions/localauth/orm.go:147`, skipping bcrypt entirely).
3. Statistically compare the two latency distributions (e.g., median/percentile over N samples) — the existing-email requests will show a consistent, measurable latency increase corresponding to bcrypt's cost factor, confirming the account's existence without needing the correct password.

### Citations

**File:** core/web/sessions_controller.go (L34-60)
```go
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

**File:** core/sessions/localauth/orm.go (L144-163)
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
