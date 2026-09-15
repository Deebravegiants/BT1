### Title
Unauthenticated user enumeration via distinguishable login error messages - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint returns raw, distinguishable error text for "email does not exist" versus "email exists but password is wrong," allowing an unauthenticated caller to enumerate valid Chainlink node operator account emails — the same bug class as CVE-2023-41323 (GLPI unauthenticated user enumeration).

### Finding Description
`SessionsController.Create` is the public, unauthenticated HTTP handler for `POST /sessions` [1](#0-0) . It forwards attacker-controlled credentials to `AuthenticationProvider().CreateSession`, and on any failure returns the raw underlying Go error directly to the client via `jsonAPIError`, which serializes `err.Error()` verbatim into the JSON response body: [2](#0-1) 

The local-auth implementation of `CreateSession` produces materially different errors depending on whether the account exists:

```
user, err := o.FindUser(ctx, sr.Email)
if err != nil {
    return "", err   // raw sql.ErrNoRows -> "sql: no rows in result set"
}
...
if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
    return "", pkgerrors.New("Invalid password")   // distinct message for known accounts
}
``` [3](#0-2) 

- Unknown email → `FindUser` fails with `sql.ErrNoRows`, and that raw driver error string (`"sql: no rows in result set"`) is propagated unmodified back to `SessionsController.Create` and out to the HTTP client.
- Known email + wrong password → the distinct string `"Invalid password"` is returned instead.

Both paths result in HTTP 401 [4](#0-3) , but the JSON `detail` field text differs, giving an unauthenticated attacker a binary oracle: submit an email + arbitrary password and read the error text to determine whether that email is a registered node user.

The OIDC authenticator's local-admin fallback path has the same structural issue — `FindUser` there also returns a distinct `"user not found"` message versus `"invalid password"` for existing accounts [5](#0-4) [6](#0-5) .

### Impact Explanation
This directly matches "Accept: cross-user response confusion / authentication bypass-adjacent disclosure" criteria — it discloses which email addresses are valid node operator/admin accounts without any authentication. Given Chainlink node UIs/APIs are often reachable by operations teams, contractors, or partially exposed environments, enumerating valid admin/API user emails materially aids follow-on credential-stuffing, phishing, or brute-force attacks against the node's authentication surface (`core/web/auth/auth.go` `AuthenticateBySession`/`AuthenticateByToken` gate access to job runs, keys, and bridge configuration) [7](#0-6) .

### Likelihood Explanation
High: the endpoint requires no authentication, no rate-limiting is evident in the reviewed code path, and the request is a single unauthenticated POST with attacker-chosen email/password. The oracle is deterministic (not timing-based), making automated enumeration trivial.

### Recommendation
Normalize the error response for `CreateSession` failures so that "user not found" and "invalid password" (and any other authentication-provider-specific errors) return an identical generic message (e.g., "Invalid email or password") and identical HTTP status code, in `core/sessions/localauth/orm.go`, `core/sessions/oidcauth/oidc.go`, and `core/sessions/ldapauth/ldap.go`. Additionally, `jsonAPIError` in `core/web/sessions_controller.go`'s `Create` handler should map authentication errors to a fixed, generic message before serialization rather than passing through `err.Error()` from the authentication provider, and constant-time behavior (already partially implemented via `constantTimeEmailCompare`) should be extended to cover the "user not found" branch so timing does not reintroduce the oracle.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@node.local","password":"x"}` → response body contains `{"errors":[{"detail":"sql: no rows in result set"}]}` (or the OIDC/LDAP driver's `"user not found"`/`"no users found with provided email"` equivalents) [8](#0-7) .
2. `POST /sessions` with `{"email":"knownadmin@node.local","password":"x"}` → response body contains `{"errors":[{"detail":"Invalid password"}]}` [9](#0-8) .
3. Diffing these two response bodies across a wordlist of candidate emails lets an unauthenticated attacker enumerate valid node user accounts.

### Citations

**File:** core/web/sessions_controller.go (L27-60)
```go
// Create creates a session ID for the given user credentials, and returns it
// in a cookie.
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

**File:** core/web/helpers.go (L19-29)
```go
// jsonAPIError adds an error to the gin context and sets
// the JSON value of errors.
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```

**File:** core/sessions/localauth/orm.go (L43-46)
```go
// FindUser will attempt to return an API user by email.
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
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

**File:** core/sessions/oidcauth/oidc.go (L279-295)
```go
func (oi *oidcAuthenticator) FindUser(ctx context.Context, email string) (clsessions.User, error) {
	email = strings.ToLower(email)

	var foundUser clsessions.User

	if err := oi.ds.GetContext(ctx, &foundUser, SQLSelectUserbyEmail, email); err != nil {
		// If the error is not that no local user was found, log and exit
		if errors.Is(err, sql.ErrNoRows) {
			return clsessions.User{}, errors.New("user not found")
		}

		oi.lggr.Errorf("error searching users table: %v", err)
		return clsessions.User{}, errors.New("error finding user")
	}

	return foundUser, nil
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

**File:** core/web/auth/auth.go (L52-71)
```go
// AuthenticateBySession authenticates the request by the session cookie.
//
// Implements authMethod
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```
