Audit Report

## Title
Improper Authentication via LDAP Unauthenticated ("Anonymous") Bind Bypass in Session Creation — ([File: core/sessions/ldapauth/ldap.go])

## Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` pass the user-supplied password directly to `conn.Bind()` without ever checking that it is non-empty [1](#0-0) [2](#0-1) . Per RFC 4513 §5.1.2, a bind with a valid DN and zero-length password is defined as an "unauthenticated bind" that many LDAP servers will accept as a successful result without validating any secret, allowing an unprivileged HTTP client to authenticate as any known user by supplying an empty password.

## Finding Description
The unauthenticated `POST /sessions` HTTP endpoint binds the request body directly into `sessions.SessionRequest` and forwards it unmodified to the configured authentication provider [3](#0-2) . `SessionRequest.Password` carries no `binding:"required"` tag or emptiness constraint [4](#0-3) , so a JSON body with `"password":""` (or the field omitted) reaches `CreateSession` unchanged.

In the LDAP provider, the bind DN is built from the caller-supplied email and `conn.Bind(searchBaseDN, sr.Password)` is called with no prior check on `sr.Password` length [5](#0-4) . If the LDAP server treats the empty-password bind as an RFC 4513 "unauthenticated bind" and returns success, `err` is `nil`, `returnErr` stays `nil`, `FindUser` resolves the user's role, and a valid `ldap_sessions` entry/session cookie is created — without any real credential having been checked. The identical unguarded pattern exists in `TestPassword`, which gates API token issuance [6](#0-5) .

By contrast, the local-auth provider correctly performs a hashed comparison via `utils.CheckPasswordHash` before establishing a session [7](#0-6) , confirming that the LDAP path is missing an equivalent defensive check that is standard practice given this well-known LDAP protocol behavior (the same root-cause pattern as GHSA-9mgm-gcq8-86wq / CVE-2021-26117).

## Impact Explanation
When LDAP auth is enabled and the backing directory server permits unauthenticated binds (a common default for OpenLDAP/AD unless explicitly hardened), an unprivileged network client who knows a valid user's email can obtain a fully authenticated node session or API token for that user's role by submitting an empty password — a complete authentication bypass mapping directly to the "node API authentication or role bypass" impact class.

## Likelihood Explanation
Exploitability is gated on the LDAP auth mode being enabled and the external directory server accepting unauthenticated binds; it does not manifest against the default local-auth provider. However, Chainlink's own code performs zero defensive validation against this well-documented RFC 4513 behavior, so any LDAP-mode deployment that hasn't explicitly disabled unauthenticated binds on its directory server is exposed via a single unauthenticated `POST /sessions` request — a realistic, repeatable, low-effort attack path once the precondition (LDAP mode + unhardened server) is met.

## Recommendation
Reject empty (or whitespace-only) passwords in both `CreateSession` and `TestPassword` before calling `conn.Bind`, e.g.:
```go
if len(strings.TrimSpace(sr.Password)) == 0 {
    return "", errors.New("password cannot be empty")
}
```
Apply the same guard in `ldapauth.TestPassword`, and additionally consider validating non-empty password at the `SessionRequest` binding/controller layer as defense in depth.

## Proof of Concept
1. Configure a Chainlink node with `AuthenticationMethod = "ldap"` against an LDAP server that has not disabled unauthenticated binds.
2. Send `POST /sessions` with body `{"email":"admin@example.com","password":""}`.
3. `SessionsController.Create` forwards the request unmodified to `ldapAuthenticator.CreateSession`, which issues `conn.Bind(dn, "")`; if the server returns success per RFC 4513 unauthenticated-bind semantics, the handler creates a valid session cookie for the target user without ever validating a real credential. A Go unit test can mock `ldapClient.CreateEphemeralConnection` / `conn.Bind` to return `nil` for an empty password and assert that `CreateSession` returns a valid session ID instead of an error.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L403-420)
```go
	var returnErr error

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L503-516)
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
	if err == nil {
		return nil
```

**File:** core/web/sessions_controller.go (L35-57)
```go
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
