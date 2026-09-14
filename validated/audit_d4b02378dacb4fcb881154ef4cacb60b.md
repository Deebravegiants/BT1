### Title
LDAP authentication bypass via zero-length (unauthenticated) Bind - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` in `core/sessions/ldapauth/ldap.go` forwards the client-supplied `sr.Password` directly into `conn.Bind(searchBaseDN, sr.Password)` with no check that the password is non-empty. This is the same bug class as the reported CVE-2019-14910 (Keycloak/LDAP): the LDAP protocol treats a bind with a zero-length password as an "unauthenticated bind" (RFC 4513 §5.1.2), which most LDAP servers accept and return success for — regardless of whether the supplied DN/credentials are actually valid. The result is that `conn.Bind()` returns `nil` error for an attacker who supplies a known/guessable email and an empty password string, even though no real credential was validated.

### Finding Description
`CreateSession` is reachable from the unauthenticated, internet-facing `POST /sessions` endpoint (`core/web/sessions_controller.go`, `SessionsController.Create`), which binds the raw JSON body into `sessions.SessionRequest{Email, Password}` with no validation on `Password` (`core/sessions/session.go`). [1](#0-0) [2](#0-1) 

`CreateSession` then does:
```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
    returnErr = errors.New("unable to log in with LDAP server. Check credentials")
}
``` [3](#0-2) 

There is no check anywhere in this file (or the config/session types) rejecting an empty `sr.Password` before it's passed to `Bind`. If the underlying LDAP server permits unauthenticated binds (the default in RFC 4513-compliant deployments unless the operator explicitly disables it), `conn.Bind(dn, "")` returns success (`err == nil`) without the server actually verifying any credential — the "identity" bound is anonymous/unauthenticated, but the client library reports success for the supplied DN.

Because `err == nil`, `returnErr` is never set at the bind step, and execution proceeds directly to:
```go
foundUser, err := l.FindUser(ctx, escapedEmail)
``` [4](#0-3) 
If the email belongs to a real, active directory user who is a member of one of the configured RBAC groups, `FindUser` succeeds and returns that user's real role. `returnErr` stays `nil`, and the function proceeds to create a full authenticated session for that user/role and audit-logs a successful login: [5](#0-4) 

The `TestPassword` function on the same struct has the identical unguarded `conn.Bind(searchBaseDN, password)` pattern. [6](#0-5) 

This directly parallels the referenced advisory's root cause: LDAP client/server semantics (StartTLS vs. binding) are misused such that "authentication succeeds even if invalid password has [been] entered." Here the mechanism is unauthenticated bind rather than StartTLS negotiation, but the resulting bug class (CWE-287/CWE-288: improper/missing authentication via LDAP bind misuse) and impact (attacker impersonates a legitimate user without knowing their password) are the same.

### Impact Explanation
An unprivileged, unauthenticated remote attacker who knows or can guess a valid directory user's email (email addresses are often not secret — corporate format, prior breaches, UI enumeration, etc.) can obtain a fully authenticated Chainlink node web session with that user's real role (up to Admin) by submitting an empty-string password to `POST /sessions`. This is a full authentication bypass with direct account/role takeover, gated only by whether the operator's upstream LDAP server permits unauthenticated binds (a common default absent explicit hardening). Given `Role` can be Admin, this can lead to full control of node configuration, job management, and key/secret operations exposed via the authenticated web/API surface.

### Likelihood Explanation
Requires: (1) the node configured with `AuthenticationMethod = 'ldap'`, and (2) the upstream LDAP/AD server not explicitly disabling unauthenticated binds. Many LDAP/AD deployments leave unauthenticated bind enabled by default (RFC 4513 recommends but does not mandate disabling it), so this is a realistic, commonly-encountered misconfiguration rather than an exotic edge case. No special network position or privileges are needed — a single unauthenticated HTTP POST is sufficient.

### Recommendation
Reject empty/zero-length `sr.Password` (and any other unauthenticated-bind-triggering values) before calling `conn.Bind` in both `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`. Return the standard "invalid credentials" error identically to the failure path so as not to introduce a timing/behavior side channel. Additionally, consider validating that the DN actually authenticated with a non-anonymous identity where the underlying LDAP library exposes such information.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` pointing at an LDAP server that has not explicitly disabled unauthenticated bind (default in many deployments).
2. Identify or guess the email of a real directory user who is a member of one of the configured RBAC groups (e.g., `AdminUserGroupCN`).
3. Send:
```
POST /sessions
Content-Type: application/json

{"email":"victim@example.com","password":""}
```
4. `conn.Bind(dn, "")` in `CreateSession` succeeds (unauthenticated bind, `err == nil`), `FindUser` resolves the victim's real role, and a valid session cookie is returned for the victim's account/role — without ever knowing the victim's real password.

Note: I was unable to fully confirm from the available test file (`core/sessions/ldapauth/ldap_test.go`) whether an empty-password `CreateSession` test case exists to explicitly guard against this, since a targeted grep on that file failed; this doesn't change the root-cause finding in `ldap.go` itself, which contains no empty-password guard.

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

**File:** core/sessions/session.go (L14-22)
```go
// SessionRequest encapsulates the fields needed to generate a new SessionID,
// including the hashed password.
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```

**File:** core/sessions/ldapauth/ldap.go (L405-411)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L413-420)
```go
	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L440-456)
```go
	session := sessions.NewSession()
	_, err = l.ds.ExecContext(
		ctx,
		"INSERT INTO ldap_sessions (id, user_email, user_role, localauth_user, created_at) VALUES ($1, $2, $3, $4, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
		isLocalUser,
	)
	if err != nil {
		l.lggr.Errorf("unable to create new session in ldap_sessions table %v", err)
		return "", fmt.Errorf("error creating local LDAP session: %w", err)
	}

	l.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
```

**File:** core/sessions/ldapauth/ldap.go (L511-517)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
```
