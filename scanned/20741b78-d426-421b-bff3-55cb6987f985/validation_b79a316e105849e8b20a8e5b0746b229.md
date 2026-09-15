## Finding: Observable Discrepancy in `/sessions` Login Endpoint (User Enumeration)

The Argo CVE describes a login endpoint returning different HTTP status codes (401 vs 404) for existing vs. non-existing usernames, letting an attacker enumerate valid accounts. Chainlink's local-auth session endpoint has an analogous — though mechanistically different — observable discrepancy: it returns the **same status code (401)** for all failure cases, but leaks the **underlying error text** in the JSON response body, which differs depending on whether the account exists.

### Root cause

`SessionsController.Create` forwards any error from `CreateSession` straight into the JSON response body via `jsonAPIError`: [1](#0-0) 

`jsonAPIError` serializes `err.Error()` verbatim into the response JSON: [2](#0-1) 

In the local-auth ORM, `CreateSession` first calls `FindUser`, and if the email doesn't exist, it returns that raw lookup error (effectively a DB "no rows" error) immediately — with a message distinct from the "Invalid password" message used when the email exists but the password is wrong: [3](#0-2) 

`findUser`/`FindUser` simply propagate the raw SQL error (e.g. `sql: no rows in result set`) when no matching user row is found: [4](#0-3) 

So for a request to `POST /sessions`:
- Unknown email → HTTP 401, body contains the raw "no rows" DB error text.
- Known email, wrong password → HTTP 401, body contains `"Invalid password"`.
- Known email, wrong password *and* MFA enrolled → different body again (`"MFA Error"`).

This is a textbook CWE-203 observable discrepancy: an unauthenticated client can distinguish "account exists" from "account does not exist" purely by inspecting the response body text, even though status codes are identical — enabling account enumeration against the node's admin/API users. The same pattern (leaking distinct "invalid email" vs "invalid password" error text) also exists in the LDAP and OIDC local-fallback authenticators: [5](#0-4) [6](#0-5) 

### Impact

An unprivileged, unauthenticated network client can enumerate valid Chainlink node operator/API-user email addresses by sending crafted `POST /sessions` requests and inspecting the returned error text, aiding follow-on credential-stuffing or targeted phishing/brute-force attacks against the node's admin API. This is limited to information disclosure (enumeration) — no rate limiting bypass or session/credential compromise. Existing rate limiting on this endpoint (5 attempts then 429, per `TestSessions_RateLimited`) somewhat mitigates but does not eliminate the enumeration risk, since it only throttles rather than blocks distinguishing responses. [7](#0-6) 

### Recommendation

Normalize the error returned by `CreateSession` (and equivalents in `ldapauth`/`oidcauth`) to a single generic message (e.g. `"invalid credentials"`) for all authentication-failure branches (unknown email, wrong password, MFA failure), so the HTTP response body — not just the status code — is indistinguishable regardless of whether the account exists.

### Proof of Concept

```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"unknown@nowhere.com","password":"x"}
```
→ 401, body: `{"errors":[{"detail":"sql: no rows in result set"}]}`

```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"realuser@company.com","password":"wrongpass"}
```
→ 401, body: `{"errors":[{"detail":"Invalid password"}]}`

The differing `detail` text lets an attacker enumerate valid emails despite the identical 401 status code.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
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

**File:** core/sessions/localauth/orm.go (L43-59)
```go
// FindUser will attempt to return an API user by email.
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}

// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}

func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
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

**File:** core/sessions/ldapauth/ldap.go (L631-639)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		l.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		l.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L586-594)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}
```

**File:** core/web/router_test.go (L127-156)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
	require.NoError(t, err)

	resp, err := client.Do(request)
	require.NoError(t, err)
	assert.Equal(t, 429, resp.StatusCode)
}
```
