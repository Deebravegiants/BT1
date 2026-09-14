Based on the analysis, chainlink's local-auth login flow (`POST /sessions`) exhibits the same timing side-channel bug class as the reported CVE.

### Title
User Enumeration via Timing Side-Channel in Local Authentication Login Endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The `CreateSession` handler for the `/sessions` login endpoint performs a fast-fail database lookup for non-existent emails, but performs a comparatively slow `bcrypt.CompareHashAndPassword` operation when the email exists but the password is wrong. This timing asymmetry lets an unauthenticated network attacker distinguish valid from invalid emails/usernames with a single request, exactly mirroring the reported 4ga Boards CVE-2026-41418 bug class.

### Finding Description
`SessionsController.Create` binds the login JSON and forwards it to `AuthenticationProvider().CreateSession(ctx, sr)` [1](#0-0) .

The local-auth implementation of `CreateSession` first calls `FindUser`, which issues a `SELECT * FROM users WHERE lower(email) = lower($1)` query. If the email doesn't exist, the SQL layer returns `sql.ErrNoRows` almost immediately and the function returns early — **no bcrypt operation is ever invoked**: [2](#0-1) 

If the email *does* exist, the code proceeds to a constant-time email comparison and then calls `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword` — a deliberately slow, computationally expensive operation: [3](#0-2) [4](#0-3) 

The `constantTimeEmailCompare` call only protects against timing differences in the *string comparison* of email values — it does nothing to equalize the cost between "user not found" (fast DB miss) and "user found, wrong password" (slow bcrypt call). Because bcrypt's cost factor (`bcrypt.DefaultCost` = 10) is intentionally expensive (tens of milliseconds), the response-time difference between a non-existent email and a valid email with a wrong password is large and trivially observable over the network — identical in nature to the timing gap described in the reported CVE for the boards application's `POST /api/access-tokens` endpoint.

The same pattern is repeated in the OIDC and LDAP local-admin fallback authenticators, which share the identical logic shape (`localLoginFallback` in both `oidc.go` and `ldap.go`) [5](#0-4) [6](#0-5) .

### Impact Explanation
An unauthenticated attacker with network access to the Chainlink node's operator UI/API can send crafted `POST /sessions` requests and measure response latency to enumerate valid operator/admin email addresses. Confirmed valid emails/usernames are high-value targets for subsequent credential-stuffing, phishing, or brute-force attacks against a node operator's admin account, which controls job specs, keys, and potentially fund-moving jobs. This is a confidentiality-only (no direct auth bypass) issue, consistent with the CVSS 5.3 (C:L/I:N/A:N) rating of the reference CVE.

### Likelihood Explanation
Likelihood is high: the endpoint is unauthenticated by design (it *is* the login endpoint), requires no special network position, and the timing gap (DB-miss vs. bcrypt compare) is large and consistent enough to be distinguished with a small number of samples, even over a real network — as demonstrated by the reference report's single-request detection.

### Recommendation
Perform a dummy/constant-cost bcrypt comparison (against a static or randomly-hashed dummy password) whenever `FindUser` fails to find the email, so that the total processing time for "user not found" and "user found, wrong password" cases converges. Alternatively, enforce a fixed minimum response time for the entire `CreateSession` code path (e.g., via a floor-and-wait pattern) before returning any error, in both `localauth`, `oidcauth`, and `ldapauth` implementations.

### Proof of Concept
1. Send `POST /sessions` with a known-invalid email and any password; observe fast (~sub-millisecond to a few ms, DB round-trip only) rejection.
2. Send `POST /sessions` with a valid, existing operator email and an incorrect password; observe a measurably slower rejection (tens of milliseconds, dominated by `bcrypt.CompareHashAndPassword`).
3. Repeat across several candidate emails; the set of emails producing the slower response time constitutes valid accounts on the node — no credentials required.

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
