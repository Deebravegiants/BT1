Confirmed: `jsonAPIError` serializes `err.Error()` directly into the JSON response body sent to the unauthenticated caller [1](#0-0) , and `SessionsController.Create` forwards whatever error `CreateSession` returns verbatim to `jsonAPIError` with a 401 status [2](#0-1) . This endpoint is reachable unauthenticated at `POST /sessions` [3](#0-2) .

### Title
Login endpoint leaks account-state via distinguishable error messages, enabling user enumeration and active-directory reconnaissance (LDAP auth) - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The `/sessions` login endpoint returns the raw `error.Error()` string from `AuthenticationProvider.CreateSession` to the unauthenticated caller. For the LDAP authentication driver, `FindUser`/`CreateSession` return distinct, descriptive error strings depending on whether the email doesn't exist, exists but is inactive, exists but has no assigned role groups, or the password was wrong. This is the same bug class as ALPINE-CVE-2018-6188 (Django `confirm_login_allowed()`): the login flow discloses account-state details before/independently of credential validation, letting an unauthenticated caller distinguish "no such user" from "user exists but inactive/unassigned."

### Finding Description
`ldapAuthenticator.CreateSession` performs an LDAP bind, and on bind failure calls `l.FindUser` and then `l.localLoginFallback`, returning whichever error occurs [4](#0-3) . `FindUser` returns highly specific errors depending on account state: `errors.New("user not active")` when the user exists in the directory but the configured `ActiveAttribute` marks them inactive [5](#0-4) , `ErrUserNotInUpstream` (`"LDAP query returned no matching users"`) when the email has no LDAP entry [6](#0-5) , and `ErrUserNoLDAPGroups` (`"user present in directory, but matching no role groups assigned"`) when found but ungrouped. `localLoginFallback` separately distinguishes `"invalid email"` vs `"invalid password"` [7](#0-6) . All of these errors flow unmodified back through `SessionsController.Create` to `jsonAPIError`, which serializes `err.Error()` straight into the HTTP response body [2](#0-1) [1](#0-0) . This is functionally identical to the Django CVE's root cause: `confirm_login_allowed()`-style account-state checks (active/inactive, present/absent, grouped/ungrouped) are surfaced to the requester as distinguishable text before or independent of a successful credential match.

### Impact Explanation
An unauthenticated network client can send arbitrary emails to `POST /sessions` and use the returned error text to enumerate valid user accounts and learn their LDAP-side status (inactive, missing group/role assignment) without any credentials. This assists targeted phishing, credential-stuffing prioritization (skip inactive accounts, target active ones), and reconnaissance of the node's user/role configuration — a concrete case of "cross-user response confusion" / information disclosure in an unprivileged, internet-facing authentication path.

### Likelihood Explanation
High for the local admin fallback path (`"invalid email"` vs `"invalid password"` is always distinguishable regardless of LDAP configuration) [7](#0-6) . For the full LDAP-active-attribute distinctions, likelihood depends on the operator having configured `WebServer.LDAP.ActiveAttribute` [8](#0-7) , but when configured the "user not active" branch is always reachable pre-authentication.

### Recommendation
Return a single generic, constant error message (e.g., "invalid email or password") for all authentication-decision branches in `FindUser`, `CreateSession`, and `localLoginFallback` for both LDAP and other authenticator drivers, and move the detailed diagnostic text into server-side logs only (as is already done via `l.lggr.Infof/Errorf` in several branches). Ensure `SessionsController.Create` does not forward provider-internal error text to the client on authentication failure.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `ActiveAttribute` set.
2. `POST /sessions` with `{"email":"realuser@example.com","password":"anything"}` for a known-inactive LDAP account → response body contains `"user not active"`.
3. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"anything"}` → response body contains `"LDAP query returned no matching users"`.
4. The differing, descriptive error text lets the caller distinguish valid-but-inactive accounts from nonexistent ones without valid credentials, confirmed by the existing test assertions on these exact strings [9](#0-8)  and the direct wiring in [2](#0-1) .

### Citations

**File:** core/web/helpers.go (L21-29)
```go
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

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/router.go (L210-215)
```go
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
```

**File:** core/sessions/ldapauth/ldap.go (L53-53)
```go
var ErrUserNotInUpstream = errors.New("LDAP query returned no matching users")
```

**File:** core/sessions/ldapauth/ldap.go (L140-142)
```go
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L396-433)
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
```

**File:** core/sessions/ldapauth/ldap.go (L622-641)
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
```

**File:** core/config/docs/core.toml (L252-255)
```text
# ActiveAttribute is an optional user field to check truthiness for if a user is valid/active. This is only required if the LDAP provider lists inactive users as members of groups
ActiveAttribute = '' # Default
# ActiveAttributeAllowedValue is the value to check against for the above optional user attribute
ActiveAttributeAllowedValue = '' # Default
```

**File:** core/sessions/ldapauth/ldap_test.go (L103-141)
```go
func TestORM_FindUser_NotActive(t *testing.T) {
	t.Parallel()
	ctx := t.Context()

	mockLdapClient := mocks.NewLDAPClient(t)
	mockLdapConnProvider := mocks.NewLDAPConn(t)
	mockLdapClient.On("CreateEphemeralConnection").Return(mockLdapConnProvider, nil)
	mockLdapConnProvider.On("Close").Return(nil)

	// Initialize LDAP Authentication Provider with mock client
	_, ldapAuthProvider := setupAuthenticationProvider(t, mockLdapClient)

	// User present in Upstream but not active
	user1 := cltest.MustRandomUser(t)
	expectedResults := ldap.SearchResult{
		Entries: []*ldap.Entry{
			{
				DN: "cn=User One,ou=Users,dc=example,dc=com",
				Attributes: []*ldap.EntryAttribute{
					{
						Name:   "organizationalStatus",
						Values: []string{"INACTIVE"},
					},
					{
						Name:   "uid",
						Values: []string{user1.Email},
					},
				},
			},
		},
	}

	// On search performed for validateUsersActive
	mockLdapConnProvider.On("Search", mock.AnythingOfType("*ldap.SearchRequest")).Return(&expectedResults, nil)

	// User not active, expect error
	_, err := ldapAuthProvider.FindUser(ctx, user1.Email)
	require.ErrorContains(t, err, "user not active")
}
```
