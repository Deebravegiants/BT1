This confirms the timing side channel: in `CreateSession` (`core/sessions/localauth/orm.go:144-162`), when `sr.Email` does not exist, `FindUser` fails immediately at the SQL lookup and the function returns at line 146-148 without ever invoking `utils.CheckPasswordHash`. When the email *does* exist, the code proceeds to `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))` (`core/utils/utils.go:131-135`), which wraps `bcrypt.CompareHashAndPassword` — a deliberately slow, computationally expensive operation. This produces a measurable, consistent timing difference between "user not found" and "user found, wrong password" responses on the unauthenticated `POST /sessions` login endpoint (`core/web/sessions_controller.go:29-68`), enabling remote username enumeration exactly analogous to CVE-2022-44022's PwnDoc timing side-channel. The same pattern independently exists in the LDAP (`core/sessions/ldapauth/ldap.go:624-642`) and OIDC (`core/sessions/oidcauth/oidc.go:580-597`) local-fallback login paths.

### Title
Login endpoint leaks valid account existence via authentication response timing (bcrypt vs. fast-fail) - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated session-creation endpoint (`POST /sessions`, handled by `SessionsController.Create`) calls `AuthenticationProvider().CreateSession`, which performs a fast database miss for nonexistent emails but performs an expensive bcrypt comparison for existing emails with any password, creating a timing oracle for user enumeration.

### Finding Description
`SessionsController.Create` in [1](#0-0)  accepts unauthenticated, attacker-controlled `email`/`password` and forwards it to `AuthenticationProvider().CreateSession`.

In the local auth provider, `CreateSession` first looks up the user by email via `FindUser`, and returns immediately on error (i.e., a nonexistent email) before any password hashing occurs: [2](#0-1) 

For an email that *does* exist, the code always reaches `utils.CheckPasswordHash`, which wraps bcrypt's `CompareHashAndPassword` — an intentionally slow (tunable-cost) hashing comparison: [3](#0-2) 

Because the "email not found" path short-circuits before the bcrypt call while the "email found, password wrong" path always executes bcrypt, the two cases have measurably different response latencies (bcrypt at default cost typically adds tens to ~100ms versus a fast indexed SQL miss). This lets an unauthenticated remote attacker distinguish valid from invalid usernames purely from response timing, exactly the bug class in CVE-2022-44022 (PwnDoc). The comment at line 152-153 in `orm.go` ("Do email and password check first to prevent extra database look up for MFA tokens leaking...") shows the authors were aware of and mitigated a *related* MFA-presence timing leak, but the more fundamental existing-account-vs-bcrypt timing gap on `FindUser` failure was not addressed. The identical pattern (DB miss returns early, existing user always hits `utils.CheckPasswordHash`) also appears in the LDAP local-fallback path [4](#0-3)  and OIDC local-fallback path [5](#0-4) .

### Impact Explanation
An unauthenticated remote attacker can enumerate valid Chainlink node operator/admin email addresses by measuring response times to the `/sessions` login endpoint. Knowing valid account emails materially aids follow-up attacks (credential stuffing, phishing, targeted brute force, and social engineering) against a node's administrative API, which controls sensitive functions like job management and fund-affecting operations. This is a confidentiality-only issue (no direct auth bypass), consistent with the Medium/CVSS 5.3 rating of the original CVE.

### Likelihood Explanation
The `/sessions` endpoint is exposed to any client able to reach the node's web UI/API and requires no prior authentication or privilege, so exploitation only requires network access and repeated timing measurements (statistically averaging out noise), which is a well-established low-effort technique.

### Recommendation
Ensure `CreateSession` performs constant-time work regardless of whether the account exists — e.g., always perform a dummy bcrypt comparison against a fixed/dummy hash when `FindUser` fails, or perform the email lookup and hash comparison in a way whose total execution time doesn't depend on account existence. Apply the same fix consistently to the LDAP and OIDC local-fallback authentication code paths.

### Proof of Concept
1. Create one account, e.g. `existing@node.local`, with any password.
2. Send repeated `POST /sessions` requests with `{"email":"existing@node.local","password":"wrong"}` and measure round-trip time (should include a bcrypt comparison delay).
3. Send repeated `POST /sessions` requests with `{"email":"nonexistent@node.local","password":"wrong"}` and measure round-trip time (fails at the `FindUser` DB miss before bcrypt is invoked).
4. Compare the average latencies over many samples — the existing-account requests will consistently show a measurable additional delay attributable to the bcrypt call in [6](#0-5) , allowing the attacker to distinguish valid from invalid emails without valid credentials.

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
