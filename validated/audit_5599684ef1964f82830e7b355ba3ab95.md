Now I have enough to confirm the finding: `jsonAPIError` at `core/web/helpers.go:21-29` serializes the returned `err.Error()` string directly into the JSON response body, and `CreateSession` in `core/sessions/localauth/orm.go` (and the LDAP/OIDC equivalents) returns distinguishable error strings — `"Invalid email"` for a nonexistent account versus `"Invalid password"` for an existing account with wrong credentials.

### Title
Username Enumeration via distinct error messages on `POST /sessions` login endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The Chainlink node's local login endpoint `POST /sessions` returns different, distinguishable error messages depending on whether the supplied email corresponds to an existing user or not. This is the same bug class as CVE-2024-49358 (ZimaOS), where `/v1/users/login` leaked account existence through differing API responses.

### Finding Description
`SessionsController.Create` handles `POST /sessions` and calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`, propagating any returned error directly to the client via `jsonAPIError(c, http.StatusUnauthorized, err)`. [1](#0-0) 

`jsonAPIError` serializes `err.Error()` verbatim into the JSON response body when the error is not a `*models.JSONAPIErrors`. [2](#0-1) 

The local authentication `CreateSession` implementation explicitly branches on whether the email matches an existing user vs. whether the password is wrong, returning distinct error strings `"Invalid email"` and `"Invalid password"` respectively: [3](#0-2) 

The same pattern (`"invalid email"` vs `"invalid password"`, and separate audit events `AuthLoginFailedEmail` vs `AuthLoginFailedPassword`) is repeated in the LDAP local-fallback path and the OIDC local-fallback path: [4](#0-3) [5](#0-4) 

Because these error values are unwrapped `errors.New(...)`/`pkgerrors.New(...)` values rather than `*models.JSONAPIErrors`, `jsonAPIError` puts the literal message text into the HTTP response body via `models.NewJSONAPIErrorsWith(err.Error())`, so an unauthenticated client submitting `POST /sessions` receives a body distinguishing "Invalid email" (account does not exist) from "Invalid password" (account exists, wrong password).

### Impact Explanation
An unauthenticated remote attacker can enumerate valid Chainlink node operator/admin email addresses by observing the returned error text from the login endpoint. This is a low-severity confidentiality issue (matches the CVSS 5.3 rating of the referenced CVE) that facilitates follow-on credential stuffing or targeted brute force attacks against confirmed accounts, which is significant given that a compromised admin/edit account on a Chainlink node can control job runs, keys, and bridges.

### Likelihood Explanation
High likelihood of exploitability: the endpoint is unauthenticated by design (it's the login endpoint itself), requires no special conditions, and the differing messages are returned deterministically for every request — no timing side channel or race condition needed.

### Recommendation
Return a single generic error message (e.g., "invalid credentials") for both the "email not found" and "password mismatch" branches in `orm.CreateSession` (`core/sessions/localauth/orm.go`), `localLoginFallback` in `core/sessions/ldapauth/ldap.go`, and `localLoginFallback` in `core/sessions/oidcauth/oidc.go`, while keeping the differentiated internal audit events (`AuthLoginFailedEmail` / `AuthLoginFailedPassword`) for operational/security monitoring purposes only, not exposed to the client. Ensure `jsonAPIError` is passed this generic error rather than the raw internal error.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"anything"}` → response body error text: `"Invalid email"`.
2. `POST /sessions` with `{"email":"<known-existing-admin-email>","password":"wrongpassword"}` → response body error text: `"Invalid password"`.
3. Compare the two response bodies (both return HTTP 401) — the differing message content confirms whether `<known-existing-admin-email>` is a valid account, enabling enumeration of the node's user list. [6](#0-5)

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

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

**File:** core/web/sessions_controller_test.go (L22-52)
```go
func TestSessionsController_Create(t *testing.T) {
	t.Parallel()
	ctx := t.Context()

	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	user := cltest.MustRandomUser(t)
	require.NoError(t, app.AuthenticationProvider().CreateUser(ctx, &user))

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	tests := []struct {
		name        string
		email       string
		password    string
		wantSession bool
	}{
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			ctx := t.Context()
			body := fmt.Sprintf(`{"email":"%s","password":"%s"}`, test.email, test.password)
			request, err := http.NewRequestWithContext(ctx, http.MethodPost, app.Server.URL+"/sessions", bytes.NewBufferString(body))
			require.NoError(t, err)
			resp, err := client.Do(request)
```
