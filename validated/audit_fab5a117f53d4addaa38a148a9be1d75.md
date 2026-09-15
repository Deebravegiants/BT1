Audit Report

## Title
LDAP Authentication Bypass via Unauthenticated (Empty-Password) Bind - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` and `TestPassword` pass the client-supplied `sr.Password` directly to `conn.Bind(searchBaseDN, sr.Password)` without first rejecting an empty/blank password. If the configured upstream LDAP server allows "unauthenticated bind" per RFC 4513 §5.1.2 (a common, though increasingly discouraged, server default for a non-empty DN with an empty password), `Bind` returns `nil`, and chainlink's code treats this as a successful credential check, proceeding to issue a full authenticated session with the role mapped to that DN in LDAP.

## Finding Description
The public, unauthenticated endpoint `POST /sessions` (`SessionsController.Create`) binds the request body into `sessions.SessionRequest`, which places no constraint on `Password` being non-empty: [1](#0-0) [2](#0-1) 

`CreateSession` then binds using the raw, unvalidated password: [3](#0-2) 

There is no guard anywhere in `CreateSession`, `TestPassword`, `SessionRequest`, or the HTTP controller layer that rejects an empty or blank password before delegating to `conn.Bind`. This is confirmed by searching the codebase for any `password == ""`/length checks in the LDAP auth path — none exist — and by inspecting the test suite (`core/sessions/ldapauth/ldap_test.go`), which contains no test covering empty-password rejection. `TestPassword` has the identical unguarded pattern: [4](#0-3) 

By contrast, the local auth provider explicitly performs a hashed password comparison and never forwards a raw password to a third-party bind call: [5](#0-4) 

If `conn.Bind` succeeds (`err == nil`), `returnErr` remains `nil`, so the code proceeds to `FindUser`, inserts a row into `ldap_sessions`, and returns a valid session ID/cookie for the targeted user's email and mapped role — with no verification that a real credential match occurred.

## Impact Explanation
This maps to the in-scope impact category of node API authentication/role bypass. An attacker who knows or guesses a valid LDAP-registered email can obtain a fully authenticated, role-mapped Chainlink node session (potentially Admin) without any valid password, provided the upstream LDAP server accepts unauthenticated binds. The vulnerable code is entirely within chainlink's own `CreateSession`/`TestPassword` logic — it fails to enforce the fundamental security invariant that a non-empty credential must be supplied and actually verified, and it blindly trusts the semantics of a third-party protocol (`Bind`) that has a well-documented "success without verification" edge case (RFC 4513 §5.1.2, historically responsible for real-world CVEs in other LDAP-consuming software).

## Likelihood Explanation
Exploitability is conditioned on the operator's specific choice of `WebServer.AuthenticationMethod = 'ldap'` combined with an upstream LDAP server that has not disabled unauthenticated binds (RFC 4513 explicitly recommends servers disable this by default in modern deployments, and many maintained directory servers, e.g. modern OpenLDAP/AD configurations, reject empty-password simple binds out of the box). This makes the practical likelihood dependent on third-party server configuration rather than solely on chainlink's own default behavior — chainlink ships no LDAP server, so the vulnerable condition requires a specific upstream misconfiguration/legacy behavior on infrastructure outside chainlink's control. However, chainlink's code provides zero defense-in-depth against this well-known protocol pitfall, which is a legitimate coding flaw independent of any particular server's configuration, since a secure implementation should never delegate an empty credential to a third-party authentication mechanism as proof of identity.

## Recommendation
In `ldapAuthenticator.CreateSession` and `TestPassword` (core/sessions/ldapauth/ldap.go), explicitly reject empty or whitespace-only passwords before calling `conn.Bind`, e.g.:
```go
if strings.TrimSpace(sr.Password) == "" {
    return "", errors.New("unable to log in with LDAP server. Check credentials")
}
```
Additionally, consider adding non-empty password validation at the `sessions.SessionRequest` binding layer (core/sessions/session.go) to close this class of bug uniformly across all authentication providers, and consider using `conn.UnauthenticatedBind` detection or explicit protocol-level disallowance as defense-in-depth.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against an upstream LDAP server that permits unauthenticated binds.
2. Send: `POST /sessions` with body `{"email":"victim-admin@example.com","password":""}`.
3. Observe `conn.Bind(searchBaseDN, "")` returns `nil` per RFC 4513 unauthenticated-bind semantics; `CreateSession` proceeds to `FindUser`, inserts an `ldap_sessions` row, and returns a valid session cookie for `victim-admin@example.com` with the mapped role, without the real password ever being known.
4. A Go unit test using the existing `mocks.LDAPConn`/`mocks.LDAPClient` scaffolding (as used in `ldap_test.go`) mocking `Bind` to return `nil` for an empty password, followed by asserting `CreateSession` returns a valid session ID, would concretely demonstrate the bypass at the code level (independent of any real LDAP server).

### Citations

**File:** core/web/sessions_controller.go (L29-39)
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

**File:** core/sessions/ldapauth/ldap.go (L396-411)
```go
func (l *ldapAuthenticator) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return "", errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	var returnErr error

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L503-514)
```go
// TestPassword tests if an LDAP login bind can be performed with provided credentials, returns nil if success
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
