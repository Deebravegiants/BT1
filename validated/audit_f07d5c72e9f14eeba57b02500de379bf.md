Audit Report

## Title
LDAP unauthenticated ("anonymous") bind allows authentication bypass in `CreateSession` - (`File: core/sessions/ldapauth/ldap.go`)

## Summary
`ldapAuthenticator.CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go` pass the attacker-supplied `sr.Password`/`password` directly to `conn.Bind()` without ever checking whether it is empty. Per RFC 4513, an LDAP simple bind with a non-empty DN and an empty password is defined as an "unauthenticated bind," which many LDAP/AD servers accept as successful rather than rejecting as invalid credentials, so this code path can incorrectly treat such a bind as proof of valid authentication.

## Finding Description
`CreateSession` builds `searchBaseDN` from the attacker-supplied, unauthenticated `sr.Email` and calls `conn.Bind(searchBaseDN, sr.Password)` with no check that `sr.Password` is non-empty: [1](#0-0) . If `Bind` returns `nil`, the code proceeds to call `l.FindUser` to resolve the (attacker-chosen) user's role and mints a valid session, storing it in `ldap_sessions` and returning the session ID to the caller: [2](#0-1) . The identical unguarded pattern exists in `TestPassword`: [3](#0-2) .

Tracing the request path confirms this is reachable by any unauthenticated network client: `SessionsController.Create` binds the raw JSON body directly into `clsessions.SessionRequest` with no validation on the `Password` field's length/emptiness, then calls `CreateSession` directly: [4](#0-3) . The `SessionRequest` struct itself performs no validation: [5](#0-4) . The only defensive measure in the LDAP code is `ldap.EscapeFilter` on the email for filter-injection protection — it does not address the empty-password unauthenticated-bind case at all: [6](#0-5) .

This is a genuine gap in the node's own code: regardless of how the operator's LDAP/AD directory is configured, well-written LDAP client code should defensively reject empty passwords before ever calling `Bind`, precisely because RFC 4513 unauthenticated-bind semantics are a known, common trap. The code does not do this.

## Impact Explanation
If the configured LDAP/AD server permits unauthenticated binds (a common default/misconfiguration on many directory servers, not unique to any one Chainlink operator's setup but a widely-encountered directory behavior), an unauthenticated network client who knows or guesses the email of any user mapped into an LDAP group corresponding to `AdminUserGroupCN`/`EditUserGroupCN` can submit that email with an empty password to `/sessions` and receive a valid, privileged session cookie — a full authentication/role bypass, up to Admin access over the node's key/job/fund-moving API surface. This maps to the in-scope "node API authentication or role bypass" impact category.

## Likelihood Explanation
The HTTP request itself needs no credentials and is reachable at the unauthenticated `/sessions` endpoint via `SessionsController.Create`, so the only external precondition is the upstream directory server's bind policy plus knowledge/guessing of a valid, privileged email. Given RFC 4513 unauthenticated bind is a widely known, sometimes-default LDAP/AD behavior, and the Chainlink code makes zero effort to guard against it, likelihood is realistic for any deployment using LDAP auth without a hardened directory-side unauthenticated-bind restriction.

## Recommendation
Reject empty (or whitespace-only) passwords before calling `conn.Bind()` in both `CreateSession` and `TestPassword` — e.g., immediately return an authentication error if `sr.Password == ""` / `password == ""`. Treat a `Bind` success with an empty password as invalid unconditionally, independent of what the LDAP server reports, since this is the class of RFC 4513 unauthenticated-bind pitfall the `go-ldap` client does not itself guard against.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against a directory that permits unauthenticated binds.
2. Identify/guess the email of a user in the configured `AdminUserGroupCN` LDAP group.
3. `POST /sessions` with `Content-Type: application/json` and body `{"email":"known-admin@example.com","password":""}`.
4. `SessionsController.Create` forwards this unchecked to `ldapAuthenticator.CreateSession`, which calls `conn.Bind(searchBaseDN, "")`; a directory permitting unauthenticated binds returns success, `FindUser` resolves the Admin role, and a valid session cookie is issued to the unauthenticated caller — confirmable via a Go unit test mocking `ldapClient.CreateEphemeralConnection`/`Bind` to succeed on an empty password and asserting `CreateSession` returns a non-empty session ID.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L413-456)
```go
	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}

	isLocalUser := false
	if returnErr != nil {
		// Unable to log in against LDAP server, attempt fallback local auth with credentials, case of local CLI Admin account
		// Successful local user sessions can not be managed by the upstream server and have expiration handled by the reaper sync module
		foundUser, returnErr = l.localLoginFallback(ctx, sr)
		isLocalUser = true
	}

	// If err is still populated, return
	if returnErr != nil {
		return "", returnErr
	}

	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

	// Save session, user, and role to database. Given a session ID for future queries, the LDAP server will not be queried
	// Sessions are set to expire after the duration + creation date elapsed, and are synced on an interval against the upstream
	// LDAP server
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

**File:** core/sessions/session.go (L16-22)
```go
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```
