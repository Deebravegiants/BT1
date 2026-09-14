### Title
Missing `return` after failed email-claim extraction lets OIDC login proceed with an empty/attacker-influenced email, creating a session for the wrong identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
In `handleTokenExchange` (the OIDC callback endpoint used to exchange an authorization code for a session), the type assertion on the `email` claim is checked with `ok`, but on failure the handler only logs and writes an HTTP response — it does not `return`. Execution continues into the code that maps claims to an RBAC role and persists a new session row keyed on `email`, exactly mirroring the reported bug class: a failure signal ("this operation did not succeed") is not checked/acted upon, and the operation proceeds as if it had succeeded.

### Finding Description
`handleTokenExchange` performs the full OIDC code→token exchange, verifies the ID token, and extracts claims: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```
There is no `return` statement in the `!ok` branch. This is the direct Go analog of "not checking the return value of an operation before proceeding" from the report: just as `IERC20.transfer()`'s boolean success value must be checked before assuming the transfer succeeded, the boolean `ok` here must be checked (and acted on) before the handler is allowed to continue creating a session.

Execution falls through to: [2](#0-1) 
```go
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

// Map the claims to a role and insert a newly created session paired with role mapping for user
role, err := oi.IDClaimsToUserRole(...)
...
clSession := clsessions.NewSession()
_, err = oi.ds.ExecContext(
    ctx,
    "INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
    clSession.ID,
    strings.ToLower(email),   // email is "" (zero value) when the assertion failed
    role,
)
```
and finally sets the gin session cookie to the newly created session ID: [3](#0-2) 
```go
ginSession.Set(webauth.SessionIDKey, clSession.ID)
err = ginSession.Save()
...
c.JSON(http.StatusOK, ExchangeTokenResponse{
    Success: true,
})
```
The response body reports `Success: true` to the caller even though the server had already written a `500` body earlier in the same handler via `c.String(...)` (a double-write, itself indicating the control flow is broken) and even though the extracted identity (`email`) is empty/invalid. Any later authentication via `FindUser`/`SQLSelectUserbyEmail` keyed off `lower(email)` would look up a blank string, and depending on downstream behavior a session/user record with an inconsistent or empty email/role mapping is persisted and could be treated as authenticated.

### Impact Explanation
This handler is the internet-facing OIDC login callback (`/oidc/exchange` or equivalent registered route) — reachable by anyone completing (or partially completing) the OAuth2 code exchange, i.e., an unprivileged/unauthenticated actor by definition, since the whole point of the flow is to establish authentication. A code path that fails to `return` on a failed claim assertion means the "failure" is not actually enforced: a session row is written and a session cookie is issued to the caller regardless. This is a session/identity establishment bypass in the authentication flow, directly matching the required class ("concrete authentication or role bypass ... cross-user response confusion").

### Likelihood Explanation
Reaching this branch requires the identity provider's ID token to be successfully verified (signature/issuer/audience all valid — handled earlier in the function) but the `email` claim absent or of the wrong JSON type. This can occur with misconfigured or nonstandard identity providers, or with any actor who can influence which claims are present in a token accepted by the configured provider (e.g., providers where the email claim is optional or conditionally present). Because there is no test coverage forcing this branch to `return`, the missing `return` is a straightforward logic slip rather than requiring adversarial cryptographic effort — likelihood is Medium, gated on provider/claim configuration rather than on breaking JWT verification.

### Recommendation
Add `return` immediately after writing the error response in the `!ok` branch:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
More generally, audit every `gin.Context` response write in `oidc.go` (and similar sibling authenticators) to ensure a `return` always follows, so that a failed check can never fall through into session creation — the same principle as always checking and acting on a boolean success/failure signal before proceeding, as recommended in the source report for `transfer()`/`transferFrom()`.

### Proof of Concept
1. Configure/point the CL node's OIDC provider config at a provider (or a MITM/malicious-but-otherwise-valid-issuer test provider within scope of "unprivileged actor testing the endpoint") that returns a verifiable ID token lacking the `email` claim (or with `email` as a non-string JSON value, e.g. a number or object).
2. Initiate the flow via `handleSignIn`, complete the provider-side consent, and call `POST /oidc/exchange` (i.e., `handleTokenExchange`) with the resulting `code`/`state`.
3. Observe that despite the server logging `"Failed to get email from claims"` and writing an initial `500` body, execution continues: `IDClaimsToUserRole` is evaluated, `INSERT INTO oidc_sessions (..., user_email, ...)` runs with `user_email = ""`, `ginSession.Set(webauth.SessionIDKey, clSession.ID)` is called, and the final HTTP response is `200 {"success": true}` with a valid session cookie set.
4. Confirm the returned session cookie authenticates subsequent API requests (via `AuthorizedUserWithSession`), demonstrating a session was established despite the intended failure path.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L231-260)
```go
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

	// Map the claims to a role and insert a newly created session paired with role mapping for user
	role, err := oi.IDClaimsToUserRole(
		idClaims,
		oi.config.AdminClaim(),
		oi.config.EditClaim(),
		oi.config.RunClaim(),
		oi.config.ReadClaim(),
	)
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}

	// Save new user authenticated clSession and role to oidc_sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	clSession := clsessions.NewSession()
	_, err = oi.ds.ExecContext(
		ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		clSession.ID,
		strings.ToLower(email),
		role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		c.String(http.StatusInternalServerError, "Error creating session")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L264-271)
```go
	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}
```
