### Title
User Enumeration via Response-Timing in Local/LDAP/OIDC Login (`CreateSession`) - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `/sessions` login endpoint exhibits a timing side-channel that lets a remote attacker distinguish between valid and invalid usernames/emails, mirroring the Mautic `GHSA-3ggv-qwcp-j6xg` bug class (fast-fail on unknown user vs. slow bcrypt comparison on known user).

### Finding Description
`SessionsController.Create` binds attacker-supplied JSON directly to `sr clsessions.SessionRequest` and calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)` with no rate limiting or pre-authentication [1](#0-0) . The default local authenticator's `CreateSession` first does `FindUser`, and returns immediately with an error if the lookup fails — no password hashing/comparison is performed in that path:

```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	...
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
``` [2](#0-1) 

`CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is intentionally slow (bcrypt cost factor) [3](#0-2) . Consequently:
- Unknown email → `FindUser` fails fast (single indexed SQL lookup, no bcrypt) → fast response.
- Known email → bcrypt comparison always executes (~tens to hundreds of ms depending on cost) before the "invalid password" error is returned → measurably slower response.

The same asymmetric pattern (fast-path fail on unknown user, slow bcrypt-gated path on known user) repeats in the LDAP and OIDC local-fallback authenticators: `localLoginFallback` in `core/sessions/ldapauth/ldap.go` [4](#0-3)  and `core/sessions/oidcauth/oidc.go` [5](#0-4) , and in `TestPassword`/`localLoginFallback` variants used by `SetPassword`/`DeleteAPIToken` flows [6](#0-5) .

This is exactly the bug class described in the Mautic advisory: timing differs based on whether password hashing occurred, enabling user enumeration via response timing, with no dummy-hash/constant-time countermeasure implemented anywhere in these authenticators.

### Impact Explanation
An unauthenticated remote attacker hitting `POST /sessions` can statistically distinguish valid registered emails from invalid ones purely from response latency, without needing valid credentials. This does not by itself leak credentials, but it materially assists targeted brute-force/credential-stuffing campaigns against the Chainlink node's operator/admin accounts (which control job runs, key management, and other privileged node operations), consistent with CVSS `AC:H` (requires many timing samples) and no direct confidentiality/integrity impact, matching the Medium severity of the original Mautic finding.

### Likelihood Explanation
Exploitation requires statistical timing analysis (multiple requests, averaging out network jitter), which raises the attack complexity but is a well-established technique (as referenced by OWASP's account enumeration testing guide in the original advisory) and requires no authentication or privileges — the endpoint is reachable by any network client that can reach the node's API.

### Recommendation
Implement a timing-safe login path analogous to Mautic's `TimingSafeFormLoginAuthenticator` fix: always perform an equivalent-cost dummy `bcrypt` comparison (or otherwise pad execution time to a constant floor) when `FindUser` fails, so that unknown-email and known-email-wrong-password paths take statistically indistinguishable time in `core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go`, and `core/sessions/oidcauth/oidc.go`. Additionally, consider adding basic rate limiting to `/sessions` to reduce the number of timing samples an attacker can gather.

### Proof of Concept
1. Register/know one valid node user email `admin@example.com`.
2. Send repeated `POST /sessions` requests with `{"email":"admin@example.com","password":"wrong"}` and measure response time — average time includes one bcrypt comparison.
3. Send repeated `POST /sessions` requests with `{"email":"doesnotexist@example.com","password":"wrong"}` — average time is the fast-fail `FindUser` SQL miss with no bcrypt call.
4. Compare distributions: the valid-email requests are consistently slower by roughly the bcrypt comparison cost, allowing an attacker to enumerate valid emails purely from timing without any valid credentials, reproducing the `CreateSession` code path in [2](#0-1) .

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
