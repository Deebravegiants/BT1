Based on my analysis of the login/session-creation code paths, I found a genuine analog to the Symfony "Prevent user enumeration" issue (GHSA-5pv8-ppvj-4h68 / CVE-2021-21424) in this chainlink repository's authentication flow.

### Title
User enumeration via distinguishable error messages/timing in `/sessions` login endpoint - (File: `core/sessions/localauth/orm.go`, `core/web/sessions_controller.go`)

### Summary
The unprivileged, internet-facing `POST /sessions` endpoint returns different error content (and takes a different code path/timing) depending on whether the submitted email corresponds to an existing user, allowing an attacker to enumerate valid Chainlink node operator accounts without credentials.

### Finding Description
`SessionsController.Create` accepts an unauthenticated `SessionRequest{Email, Password}` and forwards it to `AuthenticationProvider().CreateSession`, returning any error verbatim to the client via `jsonAPIError(c, http.StatusUnauthorized, err)`: [1](#0-0) . `jsonAPIError` serializes `err.Error()` directly into the JSON response body: [2](#0-1) .

In the local auth implementation, `CreateSession` first performs `FindUser` (a raw SQL lookup) and returns immediately with the raw error (e.g., `sql.ErrNoRows`-derived text) if the email doesn't exist — before ever touching password comparison logic. Only if the user is found does it proceed to compare email/password and return distinct `"Invalid email"` / `"Invalid password"` errors: [3](#0-2) .

The same pattern repeats in the LDAP and OIDC authenticators' `localLoginFallback`, which return `"invalid email"` vs `"invalid password"` depending on which check fails after the user record lookup: [4](#0-3) [5](#0-4) . The LDAP `CreateSession` also takes a materially different code path (LDAP bind attempt + directory search) for existing vs. non-existing users, introducing a timing side-channel similar to the one described in the advisory: [6](#0-5) .

While a `constantTimeEmailCompare` is used for the email string comparison itself (to avoid a substring/prefix timing leak on the email match) [7](#0-6) , this only protects the comparison after the user is already found — it does nothing to prevent the enumeration signal from the earlier `FindUser` short-circuit (different error text and no password-hash computation performed at all for unknown emails).

### Impact Explanation
An unauthenticated remote attacker hitting `/sessions` can distinguish "email does not exist" from "email exists but wrong password" by inspecting the JSON error body text and/or response timing (since password hashing via `utils.CheckPasswordHash` is skipped entirely for unknown emails). This discloses which email addresses are registered node-operator accounts, aiding targeted credential-stuffing/phishing/brute-force campaigns against the Chainlink node's admin API. Impact is confidentiality-only (CWE-200/203), matching the CVSS profile of the reference advisory (C:L/I:N/A:N).

### Likelihood Explanation
High likelihood of exploitability: the endpoint requires no authentication, no rate-limiting is evident in this code path, and the differing error strings are returned as plain JSON to any caller, making automated enumeration trivial to script.

### Recommendation
- Always execute a dummy password-hash comparison (or run `CheckPasswordHash` against a fixed/dummy hash) when `FindUser` fails, so the code path timing is equalized between "user not found" and "user found, bad password."
- Normalize all authentication failure responses in `CreateSession` (local, LDAP, OIDC) to a single generic error (e.g., `"invalid credentials"`) and a single HTTP status (401), removing the `"Invalid email"` vs `"Invalid password"` vs raw SQL error distinctions before they reach `jsonAPIError`.
- Apply the same normalization to `TestPassword` implementations, which currently also leak whether a user record exists via differing error paths: [8](#0-7) .

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@x.com","password":"anything"}` → immediate response with SQL-lookup-derived error text, fast response time (no password hashing performed).
2. `POST /sessions` with `{"email":"<known-existing-email>","password":"wrongpassword"}` → response body reads `"Invalid password"`, measurably slower due to bcrypt/hash comparison in `utils.CheckPasswordHash`.
3. Comparing response content and timing across steps 1 and 2 for a list of candidate emails allows an attacker to enumerate valid accounts on the node's admin API.

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

**File:** core/sessions/localauth/orm.go (L309-318)
```go
func (o *orm) TestPassword(ctx context.Context, email string, password string) error {
	var hashedPassword string
	if err := o.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return pkgerrors.New("no matching user for provided email")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return pkgerrors.New("passwords don't match")
	}
	return nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L396-428)
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

**File:** core/sessions/oidcauth/oidc.go (L580-597)
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

	return user, nil
}
```
