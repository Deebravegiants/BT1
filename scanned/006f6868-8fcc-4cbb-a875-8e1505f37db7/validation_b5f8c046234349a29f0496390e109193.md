Confirmed: `jsonAPIError` at [1](#0-0)  serializes `err.Error()` verbatim into the JSON response body, and `SessionsController.Create` passes through whatever error `CreateSession` returns directly to the client via `jsonAPIError(c, http.StatusUnauthorized, err)` at [2](#0-1) .

### Title
Username Enumeration via Login Response Discrepancy in `local`/`OIDC`/`LDAP` Session Creation - (File: `core/sessions/localauth/orm.go`)

### Summary
The unauthenticated `/sessions` login endpoint returns different, verbatim error text depending on whether the submitted email exists in the system, allowing an unauthenticated attacker to enumerate valid node API usernames — the same bug class as CVE-2026-24664 (Open eClass login response discrepancy).

### Finding Description
`SessionsController.Create` binds the request body and forwards it directly to `AuthenticationProvider().CreateSession(ctx, sr)`, then returns whatever error is produced verbatim to the caller through `jsonAPIError`, which serializes `err.Error()` into the JSON body unmodified: [2](#0-1) [1](#0-0) 

In `localauth.orm.CreateSession`, the very first step looks up the user by email via `FindUser`, and if it fails (non-existent account, causing `sql.ErrNoRows`), the raw error from the SQL driver/sqlx is returned immediately — *before* any password comparison happens: [3](#0-2) 

If the email exists but the password is wrong, a different, distinctly-worded error is returned instead: [4](#0-3) 

The same asymmetry exists in the `oidcauth` and `ldapauth` local-fallback login paths (`localLoginFallback`), which return `"invalid email"` for a lookup failure vs. `"invalid password"` for a match failure: [5](#0-4) [6](#0-5) 

Because these three distinct outcomes (unknown email vs. wrong password vs. success) map to three distinguishable HTTP responses (different body text, and success vs. 401), an unauthenticated network client can probe the `/sessions` endpoint with candidate emails and directly determine which correspond to valid, registered node API accounts.

### Impact Explanation
This endpoint is reachable by any unauthenticated network client with access to the node's API/UI port — no credentials or prior session are required. Successful enumeration of valid usernames on a Chainlink node's admin/API interface materially lowers the cost of subsequent credential-stuffing or brute-force attacks against the node operator's admin account, which controls job management, keys, and other sensitive node operations.

### Likelihood Explanation
The vulnerability is trivially and remotely exploitable with a single unauthenticated HTTP POST per probed email; no rate limiting or generic error message is enforced at this layer to mask the discrepancy.

### Recommendation
Return a single, generic, identically-worded/timed error (e.g., `"invalid credentials"`) for all login failure paths in `localauth.orm.CreateSession`, `oidcauth.localLoginFallback`, and `ldapauth.localLoginFallback`/`CreateSession`, regardless of whether the failure was due to unknown email or incorrect password, and ensure comparable response timing (the codebase already partially addresses timing via `constantTimeEmailCompare`, but this only runs after the email is confirmed to exist, so it does not protect the initial existence check).

### Proof of Concept
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"admin@example.com","password":"wrongpassword"}
```
Response body/text differs measurably from:
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"nonexistent-random-string@example.com","password":"wrongpassword"}
```
The first returns the JSON-API error `"Invalid password"` (HTTP 401), while the second returns the raw SQL "no rows" error text (also surfaced via `jsonAPIError`) — confirming that whether or not the email corresponds to a registered node user can be distinguished from the response alone, without any valid credentials.

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

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L580-594)
```go
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
```

**File:** core/sessions/ldapauth/ldap.go (L622-639)
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
```
