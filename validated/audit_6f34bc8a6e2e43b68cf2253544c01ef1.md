### Title
User Enumeration via Authentication Timing Side-Channel in Local Login (`CreateSession`) - (File: `core/sessions/localauth/orm.go`)

### Summary
The `POST /sessions` login endpoint, handled by `SessionsController.Create`, exhibits an asymmetric response-time profile depending on whether the submitted email exists in the `users` table, mirroring the root cause of CVE-2018-20170 (OpenStack Keystone user enumeration via timing differences on `POST /v3/auth/tokens`).

### Finding Description
`SessionsController.Create` accepts an unauthenticated JSON body with `email`/`password` and forwards it to `AuthenticationProvider().CreateSession` [1](#0-0) . In the local auth implementation, `orm.CreateSession` first calls `FindUser`, which performs a fast, cheap `SELECT * FROM users WHERE lower(email) = lower($1)` DB lookup; if no row is found, the function returns immediately with an error, doing no further work [2](#0-1) . If a user IS found, the code proceeds to run `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword` — an intentionally expensive, tunable-cost operation (bcrypt with `DefaultCost`) — before returning any error [3](#0-2) [4](#0-3) .

This means:
- Invalid/non-existent email → fast DB miss, no bcrypt computation → low latency response.
- Valid email + wrong password → DB hit + full bcrypt comparison (deliberately slow, tens to hundreds of milliseconds) → high latency response.

The `constantTimeEmailCompare` helper only protects against a byte-level timing leak in the string comparison itself [5](#0-4) ; it does nothing to equalize the timing profile between "user not found" (fast path) and "user found, wrong password" (slow bcrypt path). The same pattern repeats in the LDAP (`localLoginFallback`) and OIDC (`localLoginFallback`) fallbacks [6](#0-5) [7](#0-6) .

### Impact Explanation
An unauthenticated remote client can distinguish valid registered node API user emails from invalid ones purely by measuring response latency of `POST /sessions`, without needing valid credentials. This is a low-severity information disclosure (matches the CVSS 5.3 / C:L rating of the referenced CVE) that facilitates follow-on credential-stuffing or brute-force attacks against confirmed valid accounts on the Chainlink node's operator API.

### Likelihood Explanation
The endpoint is internet/network reachable and requires no prior authentication — any client that can reach the node's operator UI/API can send login attempts. The timing gap introduced by bcrypt (as opposed to a cheap map/DB lookup miss) is large enough (order of 100ms+) to be reliably measurable over most network conditions, making this a practically exploitable enumeration channel, not just a theoretical one.

### Recommendation
Ensure constant-time behavior regardless of whether the user exists:
- When `FindUser` fails to find a row, still perform a dummy bcrypt comparison against a fixed/precomputed hash before returning the "invalid" error, so total latency is independent of user existence.
- Alternatively, always perform the bcrypt check with either the real hash (if found) or a static dummy hash of the same cost factor, and only branch on the boolean result afterward.
- Apply the fix uniformly in `core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go` (`localLoginFallback`), and `core/sessions/oidcauth/oidc.go` (`localLoginFallback`).

### Proof of Concept
1. Send `POST /sessions` with a known-nonexistent email and any password; record response time (fast — DB miss only).
2. Send `POST /sessions` with a known-valid email and an incorrect password; record response time (slow — DB hit + bcrypt compare).
3. Repeat with many candidate emails; a clear bimodal latency distribution reveals which emails correspond to real accounts, exactly as described in CVE-2018-20170 for Keystone's `POST /v3/auth/tokens`. [8](#0-7)

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

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/sessions/localauth/orm.go (L234-241)
```go
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

**File:** core/web/sessions_controller_test.go (L33-42)
```go
	tests := []struct {
		name        string
		email       string
		password    string
		wantSession bool
	}{
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
	}
```
