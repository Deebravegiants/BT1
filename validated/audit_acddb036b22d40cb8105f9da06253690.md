## Analysis

I found a concrete analog: in `CreateSession`, when credentials are invalid, the local auth provider returns different error strings depending on whether the account exists or not, and that error text is passed directly back to the HTTP client.

### Title
Login response leaks account existence via distinct "Invalid email" vs "Invalid password" errors - (File: core/sessions/localauth/orm.go)

### Summary
The `CreateSession` flow first looks up the user by email, and — if found — separately validates the email match and then the password, returning a different error message for each failure case. This error is passed unmodified to the HTTP response, letting an unauthenticated caller distinguish "no such account" from "wrong password."

### Finding Description
`orm.CreateSession` calls `FindUser` and then explicitly checks email vs. password in two independent steps, returning `"Invalid email"` if the account is not found (or `err` from `FindUser` if the SQL lookup errors), and `"Invalid password"` if the account exists but the password is wrong: [1](#0-0) 

The same pattern exists in the LDAP and OIDC local-fallback authenticators, which explicitly audit and return `"invalid email"` vs `"invalid password"`: [2](#0-1) [3](#0-2) 

This error is forwarded to `SessionsController.Create`, which returns it verbatim as the HTTP response body via `jsonAPIError`: [4](#0-3) [5](#0-4) 

This is structurally the same bug class as CVE-2020-35518: the server gives a differing, distinguishable response (here, differing error text/message content rather than an LDAP bind timing/response difference) depending on whether the identity (email/DN) exists, allowing enumeration without valid credentials.

### Impact Explanation
An unauthenticated attacker hitting `POST /sessions` can enumerate valid admin/API user emails on a chainlink node by observing whether the response body says "Invalid email" or "Invalid password." This does not itself grant access, but user/account enumeration is a meaningful precursor to credential stuffing, phishing, and targeted brute-force against the node's admin API, which controls job/fund-affecting operations.

### Likelihood Explanation
Low-to-medium: the endpoint (`/sessions`) is unauthenticated by design (login endpoint) and reachable from any client that can reach the node's API. No special access or timing side channel is required — the difference is directly present in the JSON error text returned in the 401 response body, as shown in the existing test cases exercising "incorrect pwd" vs "incorrect email": [6](#0-5) 

### Recommendation
Return a single generic error (e.g., "Invalid email or password") for both the "user not found" and "wrong password" branches in `orm.CreateSession` (`core/sessions/localauth/orm.go`), `ldapAuthenticator.localLoginFallback` (`core/sessions/ldapauth/ldap.go`), and `oidcAuthenticator.localLoginFallback` (`core/sessions/oidcauth/oidc.go`), while still logging/auditing the specific reason server-side only. Ensure `SessionsController.Create` surfaces only this generic message to the client on any authentication failure.

### Proof of Concept
1. `POST /sessions` with `{"email":"admin@knownvalid.com","password":"wrong"}` → response body contains `"Invalid password"`.
2. `POST /sessions` with `{"email":"doesnotexist@random.com","password":"wrong"}` → response body contains `"Invalid email"` (or a different `FindUser` error).
3. Comparing the two response bodies allows an attacker to determine which emails are registered accounts on the node, as demonstrated by the differing test cases in `sessions_controller_test.go` lines 39–40 (`{"incorrect pwd", ...}` vs `{"incorrect email", ...}`).

### Citations

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

**File:** core/web/sessions_controller_test.go (L33-42)
```go
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
```
