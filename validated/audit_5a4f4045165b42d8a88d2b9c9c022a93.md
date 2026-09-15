Audit Report

## Title
LDAP Authentication Bypass via Empty Password in `CreateSession` - (File: `core/sessions/ldapauth/ldap.go`)

## Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` in `core/sessions/ldapauth/ldap.go` forward a client-supplied password directly to `conn.Bind()` without ever checking that it is non-empty. Because the `SessionRequest.Password` field has no `binding:"required"` tag and the public `/sessions` route requires no prior authentication, an unauthenticated attacker who only knows a victim's email can send an empty password and — on any LDAP/AD directory configured to accept RFC 4513 §5.1.2 unauthenticated binds — obtain a valid Chainlink session cookie assuming the victim's role.

## Finding Description
The unauthenticated route `POST /sessions` binds directly into `clsessions.SessionRequest{Email, Password}` with no required-field validation, confirmed at [1](#0-0)  and the route wiring at [2](#0-1) . `SessionsController.Create` passes the bound struct straight to `AuthenticationProvider().CreateSession` at [3](#0-2) , which dispatches to the LDAP authenticator when `AuthenticationMethod = ldap` is configured, per [4](#0-3) .

Reviewing the actual current implementation confirms the claim: `ldapAuthenticator.CreateSession` builds the bind DN from the (attacker-controlled) email and calls `conn.Bind(searchBaseDN, sr.Password)` with no check that `sr.Password` is non-empty before the call: [5](#0-4) . If the bind returns `err == nil` (as many directories do for empty-password/"unauthenticated" binds per RFC 4513 §5.1.2), the code proceeds directly to `FindUser` and issues a valid session — there is no secondary check that authentication material was actually verified. The sibling `TestPassword` credential-check path has the identical gap.

By contrast, the local-auth path uses `utils.CheckPasswordHash(sr.Password, ...)`, a bcrypt comparison that inherently fails against any real stored hash for an empty input, so that path is not vulnerable. No other validation, middleware, or role wrapper intercepts this before the LDAP bind is attempted, since `/sessions` is explicitly registered as unauthenticated in the router group.

## Impact Explanation
This maps to the in-scope "node API authentication or role bypass" impact category. On a node configured with `WebServer.AuthenticationMethod = "ldap"` against a directory that treats empty-password simple binds as successful (a well-documented default behavior class in many Active Directory deployments), an unauthenticated attacker who knows only a valid user's email can obtain a fully valid Chainlink session cookie and assume that user's role, including Admin if the targeted account has admin group membership — a complete authentication bypass and potential full account/node takeover.

## Likelihood Explanation
The attack requires a single unauthenticated HTTP POST to `/sessions` with an empty password string and knowledge of a valid email/uid — no credential, no operator access, and no host access are needed by the attacker. It is gated only on the operator's choice of LDAP as the authentication method (a supported, documented production configuration, not a test/mock-only setting) and on the directory's bind behavior, which is a known-common default rather than an exotic edge case. This mirrors a well-established authentication-bypass bug class (analogous to the cited Parse Server CVE) that defensive LDAP client code is expected to guard against regardless of backend behavior.

## Recommendation
In `ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` (`core/sessions/ldapauth/ldap.go`), reject the request immediately if `sr.Password` (or `password`) is empty, before ever calling `conn.Bind`. Additionally, consider adding `binding:"required"` to `SessionRequest.Password` in `core/sessions/session.go` as defense in depth.

## Proof of Concept
1. Configure a node with `WebServer.AuthenticationMethod = "ldap"` pointed at a directory that accepts unauthenticated simple binds.
2. Send `POST /sessions` with body `{"email":"victim@corp.com","password":""}` and no other authentication.
3. Observe that `conn.Bind(searchBaseDN, "")` returns no error, `FindUser` resolves the victim's role, and the response contains a valid session cookie for the victim's account — confirmable via a Go unit test that stubs `ldapClient.CreateEphemeralConnection`/`conn.Bind` to return `nil` for an empty password and asserts `CreateSession` returns a valid session ID instead of an error.

### Citations

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

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
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

**File:** core/services/chainlink/application.go (L588-597)
```go
	switch sessions.AuthenticationProviderName(authMethod) {
	case sessions.LDAPAuth:
		var err error
		authenticationProvider, err = ldapauth.NewLDAPAuthenticator(
			opts.DS, cfg.WebServer().LDAP(), cfg.Insecure().DevWebServer(), globalLogger, auditLogger,
		)
		if err != nil {
			return nil, errors.Wrap(err, "NewApplication: failed to initialize LDAP Authentication module")
		}
		syncer := ldapauth.NewLDAPServerStateSyncer(opts.DS, cfg.WebServer().LDAP(), globalLogger)
```

**File:** core/sessions/ldapauth/ldap.go (L396-420)
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

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}
```
