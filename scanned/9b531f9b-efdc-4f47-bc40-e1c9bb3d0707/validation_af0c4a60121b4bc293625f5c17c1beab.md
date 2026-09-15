### Title
LDAP Authentication Bypass via Unauthenticated (Empty-Password) Bind - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authentication provider's `CreateSession` and `TestPassword` functions authenticate a user solely based on whether `conn.Bind(dn, password)` returns a `nil` error, without ever validating that `password` is non-empty [1](#0-0) . Per RFC 4513 §5.1.2, an LDAP `Bind` request with a non-empty DN and an *empty* password is defined as an "unauthenticated bind," which many LDAP servers (when not explicitly hardened) will accept and return success for, without verifying the caller knows the real credential. This is structurally identical to the CVE-2016-9463 bug class: the local application treats "the remote auth backend didn't return an error" as proof of a validated identity, when the backend's default/permissive behavior (anonymous/unauthenticated success) does not actually assert that.

### Finding Description
`SessionsController.Create` binds the unauthenticated client's JSON body directly into `sessions.SessionRequest{Email, Password}` with no `required` validation on `Password` [2](#0-1) , and `SessionRequest.Password` has no binding constraints [3](#0-2) .

This request flows into `ldapAuthenticator.CreateSession`, which builds the bind DN from the attacker-supplied `sr.Email` and performs `conn.Bind(searchBaseDN, sr.Password)` [4](#0-3) . If `sr.Password` is an empty string and the target DN exists, an RFC-4513-compliant LDAP server will treat this as an "unauthenticated bind" and return `nil` (success) rather than a bind error — this is standard, common LDAP server behavior, not an attacker-controlled misconfiguration, and is directly analogous to the SMB backend's anonymous-auth acceptance in CVE-2016-9463. Because the code only checks `if err = conn.Bind(...); err != nil { ... }`, a `nil` return is treated as a fully authenticated login: `returnErr` stays `nil`, `l.FindUser(ctx, escapedEmail)` is called to resolve the user's role, a session row is inserted into `ldap_sessions` with that user's real role, and `audit.AuthLoginSuccessNo2FA` is emitted [5](#0-4) . The local-admin fallback path (`localLoginFallback`) is never reached because `returnErr` never gets set in this flow.

The same missing empty-password check exists in `TestPassword`, used for password-change re-authentication flows [6](#0-5) .

### Impact Explanation
An unauthenticated remote attacker who knows (or guesses) a valid user's email address (admin panel emails are often predictable/enumerable) can authenticate as that user — including a node Admin — by submitting an empty password to `POST /sessions`, provided the operator's configured upstream LDAP server permits unauthenticated binds (the RFC-4513 default unless the operator has explicitly disabled it). This yields full session/role impersonation (`sessions.User.Role` from the real LDAP group mapping), i.e., authentication/role bypass and potential full administrative takeover of the Chainlink node's web/API surface — matching the "concrete authentication or role bypass" acceptance criterion.

### Likelihood Explanation
Reachable directly from an unauthenticated client via the public `POST /sessions` endpoint with no privileges required [2](#0-1) . Exploitability depends on the operator's LDAP server allowing unauthenticated/anonymous binds — a common, non-hardened default per RFC 4513 — matching the same "not disabled by default on the auth backend" condition that made CVE-2016-9463 exploitable. Note the LDAP backend itself is optional/off by default in this application (`LDAPAuth` is one of several `AuthenticationProviderName` options) [7](#0-6) , so only deployments that enable LDAP auth are affected — mirroring the CVE's own caveat that the SMB backend must be enabled to be affected.

### Recommendation
Add an explicit rejection of empty/blank passwords before calling `conn.Bind` in both `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`, e.g., return an authentication error immediately if `sr.Password == ""` (or `password == ""`), never forwarding an empty credential to the LDAP `Bind` call. Additionally, add `binding:"required"` to `SessionRequest.Password` in `core/sessions/session.go` as defense in depth.

### Proof of Concept
1. Configure/target a Chainlink node with the LDAP auth provider enabled (`AuthenticationProviderName: ldap`), pointed at an LDAP server that permits unauthenticated binds (RFC 4513 default behavior).
2. As an unauthenticated client, send:
```
POST /sessions
Content-Type: application/json

{"email": "victim-admin@example.com", "password": ""}
```
3. `SessionsController.Create` binds this into `SessionRequest` and calls `AuthenticationProvider().CreateSession` [8](#0-7) .
4. `ldapAuthenticator.CreateSession` performs `conn.Bind(dn, "")`; the upstream LDAP server returns success (unauthenticated bind) [4](#0-3) .
5. The server creates a valid session cookie mapped to `victim-admin@example.com`'s real role, and the attacker now holds an authenticated session with that user's privileges.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L404-411)
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

**File:** core/sessions/ldapauth/ldap.go (L504-517)
```go
func (l *ldapAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
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

**File:** core/sessions/authentication.go (L17-21)
```go
const (
	LocalAuth AuthenticationProviderName = "local"
	LDAPAuth  AuthenticationProviderName = "ldap"
	OIDCAuth  AuthenticationProviderName = "oidc"
)
```
