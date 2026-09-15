### Title
User existence disclosure via distinguishable login error messages on unauthenticated session creation endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The Statamic advisory describes an authenticated-but-underprivileged actor abusing an endpoint to learn whether an email belongs to an existing user, without any data disclosure beyond existence. The analogous, and actually more severe, pattern in this codebase is in the local-auth login flow, where the `CreateSession` API returns distinct, unredacted error text ("Invalid email" vs "Invalid password") that is propagated verbatim to a fully unauthenticated HTTP caller.

### Finding Description
`orm.CreateSession` performs email lookup and comparison before checking the password, returning a distinguishable error for each failure case: [1](#0-0) 

This function is invoked directly from the public session-creation endpoint `SessionsController.Create`, which forwards the raw error from `CreateSession` straight into the HTTP response body as a 401 JSON:API error, with no message normalization: [2](#0-1) 

The `/sessions` POST route that dispatches to this handler sits outside any `auth.Authenticate` middleware group (unlike `/v2/users` and other admin routes), so it is reachable by any unauthenticated network client attempting to log in. By submitting a login attempt and inspecting whether the returned error is "Invalid email" or "Invalid password", a caller with zero credentials can enumerate valid Control Panel/API user emails on the node — a strictly weaker starting privilege than the Statamic report's "authenticated CP user without user-view permission."

The same email/password-first branching and message pattern is duplicated in the LDAP and OIDC local-fallback authenticators: [3](#0-2) [4](#0-3) 

### Impact Explanation
An attacker with network access to the node's HTTP API (no valid credentials required) can determine which email addresses are registered as Chainlink node API/CP users by observing the distinguishable "Invalid email" vs "Invalid password" response. This is a CWE-200/CWE-862-class information disclosure that directly maps to the "confirm user existence" impact of the referenced advisory, and additionally lowers the attacker's required privilege from "authenticated, low-permission" to "completely unauthenticated," making brute-force targeting of specific admin accounts (e.g., credential stuffing, password guessing) easier because valid targets can be pre-filtered.

### Likelihood Explanation
High. The session creation endpoint is intentionally internet/network reachable pre-authentication (it is how legitimate users log in), requires no special conditions, and the difference in error strings is a direct, deterministic behavior of the code — no timing side channel or race condition is needed.

### Recommendation
Return a single generic error (e.g., "invalid credentials") for both the email-not-found and password-mismatch branches in `orm.CreateSession` (and the equivalent LDAP/OIDC `localLoginFallback` functions), and ensure `SessionsController.Create` does not forward provider-internal error text verbatim to the client. Perform the password/webauthn lookup work in constant time regardless of whether the email exists, to avoid reintroducing the same disclosure via timing.

### Proof of Concept
1. `POST /sessions` with `{"email": "known-admin@example.com", "password": "wrongpassword"}` → observe HTTP 401 body containing `"Invalid password"`.
2. `POST /sessions` with `{"email": "doesnotexist@example.com", "password": "wrongpassword"}` → observe HTTP 401 body containing `"Invalid email"`.
3. The difference in returned error text confirms whether `known-admin@example.com` is a registered user, without any authentication or prior access.

### Citations

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

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
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
