## Finding

The Chainlink OIDC authentication handler contains the same "unchecked return value" bug class as the reported Augur `Ownable.transferOwnership` issue: a boolean/error check is performed, an error response is written, but execution is **not halted**, so the code proceeds as if the check had succeeded. [1](#0-0) [2](#0-1) 

### Title
Missing `return` after failed claim/session checks in OIDC token exchange allows session establishment on unchecked failure paths - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
In `oidcAuthenticator.handleTokenExchange` (the handler backing the OIDC callback/token-exchange endpoint), two checks are performed whose failure is only logged/reported via `c.String(...)` but the function does **not** `return` afterwards, exactly mirroring the `onTransferOwnership` unchecked-boolean pattern in the report: the failure signal is generated but ignored by the control flow, and execution proceeds down the "success" path.

### Finding Description
`handleTokenExchange` is reachable by an unprivileged client hitting the OIDC callback route, which drives the node's web session/role authentication provider (`clsessions.AuthenticationProvider`). Two spots break the "check-then-abort" pattern used everywhere else in this function:

1. Email claim extraction:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
``` [1](#0-0) 
There is no `return` on the `!ok` branch, unlike every other error-handling block in the same function (e.g. lines 166-172, 177-183, 189-196, 200-204, 208-212, 215-219, 221-225, 241-245, 267-271), which all `return` immediately after writing an error response.

2. Session row insertion:
```go
_, err = oi.ds.ExecContext(ctx, "INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())", clSession.ID, strings.ToLower(email), role)
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
}
oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})
ginSession.Set(webauth.SessionIDKey, clSession.ID)
err = ginSession.Save()
``` [3](#0-2) 
Again there is no `return` when the `INSERT` fails. Execution continues to audit-log a login success, sets the session cookie (`webauth.SessionIDKey`) to `clSession.ID` in the gin session store, saves it, and ultimately responds `HTTP 200 {"Success": true}` — even though the corresponding row was never persisted to `oidc_sessions`, and even though an `http.StatusInternalServerError` body was already written earlier in the same response (a double-write, itself indicating the control flow was not intended to continue).

This is analytically identical to the reported bug class: a boolean/error check exists, its `false`/non-nil result is observed and reported, but the calling code never gates subsequent security-relevant actions (session cookie issuance, audit log, HTTP success response) on that result.

### Impact Explanation
If the `email` claim is absent/wrong-typed (attacker/IdP-controlled response shape) or the DB insert transiently fails, the handler still: sets a session cookie tied to `clSession.ID`, marks the login as a successful audit event, and returns `Success: true` to the client. Depending on downstream behavior of `AuthorizedUserWithSession` (which looks the session up strictly by ID and returns whatever `user_role`/`user_email` was — or wasn't — stored), this can produce sessions with an empty email but a role derived purely from OIDC group claims, or a client holding a cookie referencing a session row that doesn't exist. Both outcomes are exactly the class of "role bypass / cross-user response confusion" called out as acceptable analog impact.

### Likelihood Explanation
Reaching this code only requires completing the standard OIDC redirect/callback flow to `handleTokenExchange`, which is the node's normal unprivileged sign-in path when OIDC auth is configured, so likelihood of triggering the missing-claim branch is realistic in real-world IdP misconfigurations, and the missing-`return` after the DB insert failure branch can be hit under any transient DB error during login.

### Recommendation
Add `return` immediately after both error-reporting blocks, matching the pattern used elsewhere in `handleTokenExchange`:
- After `c.String(http.StatusInternalServerError, "Failed to get email from claims")` at line 229.
- After `c.String(http.StatusInternalServerError, "Error creating session")` at line 259.

This ensures the session cookie is never set and no "success" response is returned unless the email claim was validly extracted and the session row was actually persisted.

### Proof of Concept
1. Configure OIDC auth with an identity provider (or a proxy standing in for one) that omits the `email` claim, or intentionally returns a non-string `email` field, in the ID token claims.
2. Drive the standard `/sign-in` → provider → `/session/exchange` (token exchange) flow as an unprivileged client.
3. Observe that `handleTokenExchange` logs `"Failed to get email from claims"` and writes a `500` body, but execution continues: `IDClaimsToUserRole` still runs, `oi.ds.ExecContext` still inserts an `oidc_sessions` row (with `user_email = ""`), the audit logger records `AuthLoginSuccessNo2FA`, `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()` still execute, and the final response is `HTTP 200 {"Success": true}` with a working session cookie — despite the earlier claim-validation failure.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-231)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

**File:** core/sessions/oidcauth/oidc.go (L247-271)
```go
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

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})

	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}
```
