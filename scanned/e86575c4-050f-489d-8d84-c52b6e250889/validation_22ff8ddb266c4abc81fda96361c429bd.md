### Title
User enumeration via distinguishable login error messages in `SessionsController.Create` - (File: core/web/sessions_controller.go)

### Summary
The GLPI CVE-2023-41323 report describes an unauthenticated user being able to enumerate valid logins because the login endpoint returns different responses depending on whether the submitted account exists. The same bug class exists in this codebase's local session-creation flow: the HTTP handler propagates the raw error string from the authentication ORM directly to the unauthenticated client, and that error string differs depending on whether the email exists.

### Finding Description
`SessionsController.Create` forwards whatever error `AuthenticationProvider().CreateSession` returns straight to the client with `jsonAPIError(c, http.StatusUnauthorized, err)`: [1](#0-0) 

The local auth ORM's `CreateSession` produces two distinct, textually different errors depending on which check fails:
- `"Invalid email"` when the submitted email does not match a known user
- `"Invalid password"` when the email matches but the password does not [2](#0-1) 

Both errors are returned unmodified up through `CreateSession` to the HTTP layer, so an unauthenticated caller hitting `POST /sessions` with an arbitrary email/password pair can distinguish "email not registered" (`Invalid email`) from "email registered but wrong password" (`Invalid password`), directly enumerating which emails have accounts on the node. The same email/password-distinguishing pattern (and identical `"invalid email"` / `"invalid password"` error strings) is repeated in the LDAP and OIDC local-fallback authenticators as well: [3](#0-2) [4](#0-3) 

The developers already added `constantTimeEmailCompare` to avoid timing-based enumeration on the email comparison, but that protection is defeated because the resulting error *message* itself — not just timing — differs and is sent back to the client verbatim.

### Impact Explanation
An unauthenticated attacker can send crafted login attempts (`POST /sessions`) with a list of candidate emails and observe the `errors` field in the JSON API response (`Invalid email` vs `Invalid password`) to determine which email addresses correspond to real operator/user accounts on the Chainlink node. This is limited to disclosure of account existence (no direct auth bypass), matching the Medium severity/impact profile of the referenced GLPI CVE (CVSS 5.3, confidentiality-only). Knowing which emails are valid accounts materially aids follow-on credential-stuffing or targeted phishing/brute-force attacks against the node's admin UI.

### Likelihood Explanation
High likelihood of exploitability: the login endpoint is unauthenticated and internet/LAN reachable by design (it's the login form), requires no special conditions, and the distinguishing error text is returned unconditionally on every failed attempt with no rate limiting evident in this code path.

### Recommendation
Return a single generic error (e.g., `"invalid credentials"`) for all `CreateSession` failure paths (bad email, bad password, MFA errors where feasible) before it reaches `jsonAPIError`, in all three authenticators (`core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go`, `core/sessions/oidcauth/oidc.go`). Keep the detailed `"Invalid email"` / `"Invalid password"` distinction only in internal audit logs (already emitted via `auditLogger.Audit(audit.AuthLoginFailedEmail...)` / `AuthLoginFailedPassword...`), not in the value returned to the HTTP layer. Additionally consider normalizing response timing/length between the two failure branches.

### Proof of Concept
1. `POST /sessions` with `{"email":"unknown@x.com","password":"anything"}` → response body contains `"Invalid email"`.
2. `POST /sessions` with `{"email":"knownadmin@company.com","password":"wrongpass"}` → response body contains `"Invalid password"`.
3. Iterate over a candidate email list; any response containing `"Invalid password"` (rather than `"Invalid email"`) confirms the email is a registered account, enumerating valid users without authentication. [1](#0-0) [5](#0-4)

### Citations

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
