## Title
Improper Authentication via LDAP Unauthenticated ("Anonymous") Bind Bypass in Session Creation — ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authentication provider's `CreateSession` and `TestPassword` functions pass the user-supplied password directly to `conn.Bind()` without first verifying that the password is non-empty. Per RFC 4513 §5.1.2, an LDAP `Bind` request with a non-empty DN and a *zero-length* password is defined as an "unauthenticated bind," which many LDAP servers will accept and return a success result for — without actually validating any credential. This is the same bug class as GHSA-9mgm-gcq8-86wq/CVE-2021-26117: an authentication check that is supposed to validate a password ends up trusting a bind response produced under an anonymous/unauthenticated context rather than a real credential check.

### Finding Description
`ldapAuthenticator.CreateSession` builds the bind DN from the user-supplied email and calls `conn.Bind(searchBaseDN, sr.Password)` directly: [1](#0-0) 

`sessions.SessionRequest.Password` has no `binding:"required"` tag and no non-empty validation is performed anywhere before this call: [2](#0-1) 

The unprivileged-facing HTTP handler `SessionsController.Create` binds the JSON body straight from the request with `c.ShouldBindJSON(&sr)` and forwards it unmodified to `AuthenticationProvider().CreateSession`: [3](#0-2) 

If `sr.Password` is an empty string (or entirely absent from the JSON body, defaulting to `""`), `conn.Bind(dn, "")` is issued. Per RFC 4513, an LDAP server may treat this as an "unauthenticated bind" and return `nil` (success) as long as the DN resolves to an existing entry — without checking any secret at all. Because `err` from `Bind` is `nil` in that case, `returnErr` stays `nil`, `FindUser` is subsequently called to resolve the role, and a fully authenticated `ldap_sessions` row/session cookie is created for that user — exactly mirroring the root cause described in the advisory (anonymous/unauthenticated bind mistakenly used to "verify" a password).

The same pattern exists in `TestPassword`, used to gate API token creation/regeneration: [4](#0-3) 

By contrast, the local-auth ORM correctly hashes and compares passwords via `utils.CheckPasswordHash`, so this defect is specific to the LDAP provider's reliance on the upstream server's `Bind` semantics: [5](#0-4) 

### Impact Explanation
When the LDAP authentication method is enabled and the upstream directory server permits unauthenticated binds (a common default unless explicitly hardened), an unprivileged network client who knows or guesses a valid user's email/DN (e.g. an admin's email, often predictable or discoverable) can authenticate with an empty password. This directly grants a full node session (or, via `TestPassword`, an API access token) with that user's role — a complete authentication bypass, satisfying "concrete authentication or role bypass" impact criteria.

### Likelihood Explanation
Likelihood depends on the deployment's LDAP server configuration (`ldapd`/`OpenLDAP`/`AD` default to allowing unauthenticated binds unless `disallow bind_anon` or equivalent is set). This is not a Chainlink-code-only guarantee — it requires LDAP auth mode to be enabled and the directory server to accept unauthenticated binds. However, the Chainlink code performs zero defensive check against this well-known LDAP behavior (no empty-password rejection before calling `Bind`), so any node operator using the LDAP auth mode without hardening their directory server is exposed via an unprivileged, unauthenticated HTTP request to `/sessions`.

### Recommendation
Reject empty (or effectively empty/whitespace-only) passwords in `CreateSession` and `TestPassword` before calling `conn.Bind`, e.g.:
```go
if sr.Password == "" {
    return "", errors.New("password cannot be empty")
}
```
Apply the same guard in `ldapauth.TestPassword` and at the `SessionRequest` binding level (`binding:"required"` won't catch empty string, so an explicit length/emptiness check is needed in both `CreateSession` and `TestPassword`).

### Proof of Concept
1. Configure a Chainlink node with `AuthenticationMethod = "ldap"` pointed at an LDAP server that has not disabled unauthenticated binds (default in many OpenLDAP/AD deployments).
2. As an unauthenticated network client, send:
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"admin@example.com","password":""}
```
3. `SessionsController.Create` forwards this to `ldapAuthenticator.CreateSession`, which calls `conn.Bind(dn, "")`. If the LDAP server treats this as an unauthenticated bind and returns success, the handler creates a valid session cookie for `admin@example.com`'s role, without ever having verified a real password. [6](#0-5)

### Citations

**File:** core/sessions/ldapauth/ldap.go (L404-412)
```go

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

```

**File:** core/sessions/ldapauth/ldap.go (L503-530)
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
	}
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)

	// Fall back to test local users table in case of supported local CLI users as well
	var hashedPassword string
	if err := l.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return errors.New("invalid credentials")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return errors.New("invalid credentials")
	}

	return nil
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

**File:** core/web/sessions_controller.go (L29-67)
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

	if err := saveSessionID(session, sid); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.Join(errors.New("unable to save session id"), err))
		return
	}

	jsonAPIResponse(c, Session{Authenticated: true}, "session")
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
