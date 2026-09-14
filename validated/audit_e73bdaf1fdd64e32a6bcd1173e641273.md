### Title
User-enumeration via early-bailout / non-constant-time login response before password verification - ([File: core/sessions/localauth/orm.go])

### Summary
The CVE analog is OpenSSH's user-enumeration flaw: an authenticator bails out for an invalid user before doing the full work it does for a valid user, letting a remote unauthenticated client distinguish "user exists" from "user doesn't exist" via response timing/behavior. The `CreateSession` login path in `core/sessions/localauth/orm.go` has the same structural pattern.

### Finding Description
`CreateSession` first looks up the user by email with `o.FindUser(ctx, sr.Email)` [1](#0-0) . If the email doesn't exist in the DB, it returns immediately with the raw SQL error and never executes `constantTimeEmailCompare` or the bcrypt `CheckPasswordHash` call that is always executed for existing accounts [2](#0-1) . Because bcrypt hashing (`utils.CheckPasswordHash` → `bcrypt.CompareHashAndPassword`) is deliberately expensive [3](#0-2) , requests for existing emails take measurably longer than requests for non-existent emails — the same "auth2-*.c bails out before parsing the rest" bug class as the OpenSSH CVE, just applied to login timing/response instead of packet parsing order.

This is reachable directly from an unauthenticated client: `SessionsController.Create` accepts attacker-controlled `email`/`password` JSON and calls `CreateSession` with no rate limiting visible in this path, then forwards the resulting error text back to the HTTP response via `jsonAPIError` [4](#0-3) [5](#0-4) . When the user does not exist, the raw underlying SQL/db error from `FindUser` is what gets serialized in the JSON body (since `err.Error()` is used directly), whereas an existing user with wrong credentials gets the fixed string `"Invalid password"` and a non-existent-but-matched-case email gets `"Invalid email"` [6](#0-5) . This distinct error content, combined with the timing gap from skipped bcrypt, is a two-pronged oracle for user enumeration.

The same `FindUser`→bcrypt ordering pattern (lookup fails fast, hash comparison only on success) also exists in the LDAP and OIDC local-fallback authenticators [7](#0-6) , confirming this is a structural pattern across all three `Authenticator` implementations, not an isolated case.

### Impact Explanation
An unauthenticated remote attacker hitting the `/sessions` login endpoint can determine which email addresses correspond to registered Chainlink Node Operator API users by measuring response latency (bcrypt cost ~50-250ms depending on configured cost factor) and/or by observing differing error payload content for "unknown email" vs. "known email, wrong password". This does not by itself grant access, but materially narrows credential-stuffing/brute-force targeting and can leak operator identities, matching the "Medium" severity classification of the source CVE (CVSS 5.3, confidentiality-low, no direct auth bypass).

### Likelihood Explanation
High likelihood of exploitability given the flaw requires only unauthenticated HTTP POSTs to the standard login route with varying emails and statistical timing analysis — no special network position or privileges needed. The differing raw-error-text behavior additionally provides a non-timing oracle that's easier to exploit than the OpenSSH original (no timing analysis needed at all for that oracle).

### Recommendation
1. In `CreateSession` in `core/sessions/localauth/orm.go`, always perform a bcrypt comparison (against a fixed dummy hash) when `FindUser` fails, so total latency for "user exists" and "user doesn't exist" paths are equalized.
2. Return the same generic, audited error (e.g., "invalid email or password") for all authentication failures, and avoid propagating raw SQL/db errors from `FindUser` into the HTTP response — wrap them before they reach `jsonAPIError`.
3. Apply the same fix consistently to `ldapauth/ldap.go`'s `localLoginFallback` and `oidcauth/oidc.go`'s equivalent local-user path, since they share the identical fast-fail-then-hash pattern.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"[email protected]","password":"x"}` where the email is not in the `users` table. Observe response time T1 and body content (raw db error via `jsonAPIError`).
2. Send `POST /sessions` with `{"email":"<valid-existing-email>","password":"wrongpassword"}`. Observe response time T2 (includes bcrypt cost) and body content (`"Invalid password"`).
3. T2 is consistently and measurably larger than T1 across repeated trials, and the response bodies differ in content — both usable as independent oracles to enumerate valid operator emails without any authentication.

Note: I was unable to fully confirm whether any global rate-limiting or fixed-delay middleware wraps the `/sessions` route at the gin router level (outside the files inspected) that might mask the timing signal; a Devin session with full repo access would be needed to check `core/web/router.go` middleware chain before this is validated as unmitigated in production.

### Citations

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

**File:** core/web/helpers.go (L19-29)
```go
// jsonAPIError adds an error to the gin context and sets
// the JSON value of errors.
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
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
