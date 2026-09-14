This is a strong analog. The `SessionsController.Create` handler passes the raw error from `CreateSession` directly back to the HTTP client, and the local/OIDC/LDAP authentication providers return **distinguishable error messages** for "email not found" vs. "wrong password," letting an unauthenticated caller enumerate valid usernames/emails via the login endpoint — the same bug class as the goauthentik recovery-flow enumeration.

### Title
Username/email enumeration via distinguishable login error messages - (File: core/web/sessions_controller.go)

### Summary
The `/sessions` login endpoint returns different, attacker-visible error strings depending on whether the submitted email exists in the system, allowing an unauthenticated user to enumerate valid Chainlink node accounts.

### Finding Description
`SessionsController.Create` binds the `SessionRequest` and calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`, then forwards the underlying error verbatim to the client with `jsonAPIError(c, http.StatusUnauthorized, err)` [1](#0-0) .

In the local auth provider, `CreateSession` first looks up the user by email via `FindUser`, and if the email doesn't match the returned record it explicitly returns `"Invalid email"`, whereas a wrong password returns a distinct `"Invalid password"` error: [2](#0-1) 

The same asymmetric pattern exists in the OIDC and LDAP authenticators' local-login fallback paths, both returning `"invalid email"` vs `"invalid password"` as distinct errors: [3](#0-2) [4](#0-3) 

Because `jsonAPIError` propagates the exact `err` string to the HTTP response body without normalization, an unauthenticated caller submitting arbitrary emails to `/sessions` can distinguish "account exists, wrong password" from "no such account" purely from the response content — a direct instance of the same enumeration primitive flagged in goauthentik's recovery flow (distinct message shown for "user doesn't exist").

Additionally, prior to calling `CreateSession`, the handler queries `GetUserWebAuthn(ctx, sr.Email)` for MFA tokens; while that call itself degrades gracefully (empty list, no error) for nonexistent users, it demonstrates the same code path treats unauthenticated identification as safe to fully process before any authentication succeeds [5](#0-4) .

### Impact Explanation
An attacker can enumerate valid operator/API-user emails on a Chainlink node without any credentials, which is a stepping stone toward targeted credential-stuffing, phishing, or brute-force attacks against confirmed accounts of a node's admin/edit/run users. This does not itself grant access but weakens the authentication boundary described in the "concrete authentication or role bypass" and "cross-user response confusion" acceptance criteria.

### Likelihood Explanation
Trivial to exploit: any unauthenticated client can POST to the login endpoint with a candidate email/password and observe the distinct error text returned in the JSON API error response. No special configuration (e.g., a "recovery flow") is required — the default local-auth login path is always reachable.

### Recommendation
Normalize authentication failure messages returned from `CreateSession` (and its LDAP/OIDC equivalents) to a single generic message (e.g., `"invalid email or password"`) regardless of whether the email lookup or the password check failed, and ensure `jsonAPIError` in `sessions_controller.go` does not leak internal distinguishing error text to unauthenticated callers. Consider adding a constant-time delay / uniform response path so that the MFA-required branch also doesn't act as an existence oracle.

### Proof of Concept
1. `POST /sessions` with `{"email":"knownadmin@node.example","password":"wrong"}` → response error body contains `"Invalid password"` (from `orm.go` line 161) [6](#0-5) .
2. `POST /sessions` with `{"email":"doesnotexist@node.example","password":"wrong"}` → response error body contains `"Invalid email"` (from `orm.go` line 156, since `FindUser` fails and returns that error directly, and/or the `constantTimeEmailCompare` mismatch path) [7](#0-6) .
3. By comparing the two distinct HTTP 401 response bodies, the attacker determines which candidate emails are valid registered accounts on the node.

### Citations

**File:** core/web/sessions_controller.go (L41-47)
```go
	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}
```

**File:** core/web/sessions_controller.go (L56-60)
```go
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
