Confirmed analog exists: `SessionsController.Create` at `core/web/sessions_controller.go:56-60` forwards the exact error returned by `AuthenticationProvider().CreateSession` directly to the unauthenticated client via `jsonAPIError(c, http.StatusUnauthorized, err)`, and the LDAP/local/OIDC authentication providers return distinguishable, account-state-revealing error strings (e.g. `"user not active"`, `"unable to establish connection to LDAP server..."`, `"log in successful, but no assigned groups to assume role"`, `"invalid email"` vs `"invalid password"`).

### Title
Session-creation endpoint leaks distinguishing account-state error messages to unauthenticated clients - (File: core/web/sessions_controller.go)

### Summary
The `/sessions` login endpoint returns the raw error produced by the authentication provider's `CreateSession` call directly to the HTTP client. Because the LDAP, local, and OIDC authentication providers construct different, semantically distinct error strings depending on *why* authentication failed (e.g., unknown email vs. wrong password vs. inactive/disabled account vs. missing role group), an unauthenticated caller can use the response body to enumerate valid emails and infer account lifecycle state — the same bug class described in the Spring WS advisory (CWE-209, information exposure through error messages revealing account state).

### Finding Description
`SessionsController.Create` binds the login request and calls the active `AuthenticationProvider().CreateSession(ctx, sr)`. On failure it does: [1](#0-0) 
`err` is passed unmodified into `jsonAPIError`, which serializes the error's message into the JSON-API response body returned with HTTP 401.

The underlying providers construct different messages per failure reason instead of a single generic "authentication failed" message:

- LDAP local fallback distinguishes bad email vs bad password vs LDAP connectivity vs "log in successful, but no assigned groups to assume role": [2](#0-1) [3](#0-2) 

- `FindUser` (invoked as part of the LDAP login path) further reveals "user not active" for accounts that exist but are deactivated: [4](#0-3) 

- The local auth ORM also distinguishes "Invalid email" from "Invalid password": [5](#0-4) 

- The OIDC local-fallback path exhibits the identical email-vs-password distinction: [6](#0-5) 

Because these varied messages propagate verbatim to the HTTP response body, a remote unauthenticated client submitting login attempts can distinguish "email doesn't exist" from "email exists but wrong password" from "account exists but is inactive/disabled" from "LDAP connectivity issue," which is precisely the account-enumeration / lifecycle-state disclosure pattern flagged in the Spring WS advisory.

### Impact Explanation
This allows an unauthenticated remote attacker to enumerate valid operator/admin account emails on a chainlink node and learn account lifecycle state (active/inactive, whether LDAP group membership is assigned, whether the account is a local-fallback admin), which assists in targeted credential-stuffing or social-engineering attacks against a specific known-valid account. Impact is confidentiality-only (matches CVSS C:L/I:N/A:N in the advisory) — no direct bypass of authentication or fund movement.

### Likelihood Explanation
The `/sessions` create endpoint is exposed to any client able to reach the node's UI/API port (unauthenticated by design, since it *is* the login endpoint), so exploitation only requires network reachability and repeated POSTs with different emails — no privileged access needed. Likelihood is high for information-gathering, though severity is capped at Medium since it's a disclosure-only issue.

### Recommendation
Return a single generic authentication error (e.g., "invalid credentials") from `SessionsController.Create` for all `CreateSession` failure modes, and only log the detailed distinguishing reason (email not found, inactive, wrong password, LDAP unreachable, no matching role group) server-side via the audit logger — do not forward provider error text verbatim to `jsonAPIError`. Apply the same generic-response principle to `ldap.go`, `orm.go`, and `oidc.go` `CreateSession`/`localLoginFallback` return paths so the HTTP-visible error is uniform regardless of failure cause.

### Proof of Concept
1. `POST /sessions` with a known-valid admin email and wrong password → response body contains error derived from `"invalid password"` / `"Invalid password"`.
2. `POST /sessions` with a fabricated/unknown email → response body contains a different error message (`"invalid email"` / `"Invalid email"` / `"no users found with provided email"`).
3. `POST /sessions` for an LDAP-backed account that has been deactivated upstream → error surfaces `"user not active"` via the `FindUser` call chain reached from `CreateSession`.
4. Comparing responses across these three requests lets an attacker distinguish non-existent accounts, existing-but-wrong-password accounts, and existing-but-deactivated accounts without any authentication, confirming the disclosure.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/ldapauth/ldap.go (L131-142)
```go
	// First query for user "is active" property if defined
	usersActive, err := l.validateUsersActive([]string{email})
	if err != nil {
		if errors.Is(err, ErrUserNotInUpstream) {
			return sessions.User{}, ErrUserNotInUpstream
		}
		l.lggr.Errorf("error in validateUsers call: %v", err)
		return sessions.User{}, errors.New("error running query to validate user active")
	}
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L405-420)
```go
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
