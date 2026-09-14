### Title
Missing `return` on unchecked claim/error checks in `handleTokenExchange` lets OIDC login proceed after a failed check, writing/authenticating a session with unvalidated data - (File: core/sessions/oidcauth/oidc.go)

### Summary
`handleTokenExchange` in the OIDC authenticator writes an HTTP error response when a check fails (missing `email` claim, and failure to persist the `oidc_sessions` row) but does not `return` afterward, so execution falls through and continues to write to the gin response and complete session issuance using unvalidated/failed data — the same "unchecked failure signal is silently ignored and the state-changing operation proceeds anyway" bug class as the reported `invokeTransfer` issue (where a `false` return from `transfer()` is not checked and the call proceeds as if it succeeded).

### Finding Description
In `handleTokenExchange` [1](#0-0) , after the OIDC token exchange and claim verification, the email claim is extracted like this: [2](#0-1) 

Unlike every other failure branch in this function, this `if !ok { ... }` block calls `c.String(...)` to write an error response but has **no `return` statement**. Execution falls through to role mapping, session-row insertion, audit logging, and session cookie save using `email` in its zero value (`""`), because `email, ok := claims["email"].(string)` leaves `email == ""` when the type assertion fails.

The same fall-through pattern recurs at the session-insert failure check: [3](#0-2) 

Here, if the `INSERT INTO oidc_sessions ...` fails, the code logs the error and calls `c.String(http.StatusInternalServerError, "Error creating session")` but again does **not** `return`. Execution continues to: [4](#0-3) 

This means:
1. `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` fires and logs a successful login audit event even though the DB insert failed.
2. `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()` proceed, setting a session cookie with `clSession.ID` for a session ID that was never (or was incorrectly) persisted server-side, or that is tied to an empty/wrong email.
3. Because `gin` allows multiple writes to the response (the earlier `c.String` call does not abort the handler like `c.Abort()` would in middleware), the final `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` at line 273 is written after the error body, producing a malformed/ambiguous HTTP response body that a client may interpret as `Success: true` (many HTTP clients read the full body and the last/only fully-formed JSON often wins, or clients ignore headers already sent and parse the trailing JSON), effectively reporting login success to the caller despite the earlier failure.

This mirrors the report's root cause exactly: a failure signal from an operation (`ok` from `claims["email"].(string)`, or `err` from the DB `ExecContext`) is surfaced (logged/response written) but not acted upon by halting execution, so a state-changing operation (session issuance, audit log of "successful login") proceeds as if it had succeeded.

### Impact Explanation
- The role-to-session flow can complete and set an authenticated session cookie (`webauth.SessionIDKey`) even though the `oidc_sessions` DB row that session validation later depends on failed to be written, or was written with an empty `user_email`.
- An audit log entry falsely records `AuthLoginSuccessNo2FA` for a request that did not successfully complete claim/session processing, undermining audit-trail integrity used for security review.
- If the email claim assertion fails (`ok == false`), the session is created and inserted with `user_email = ""` (from `strings.ToLower(email)` where `email == ""`), associating an authenticated Chainlink node session/cookie with no identifiable email — a request-impersonation-adjacent condition where session state is created for an unidentified/unvalidated principal, yet the caller still receives a session cookie tied to a role derived from the ID token claims.
- Because subsequent authentication (`FindUser`/session validation) queries by `user_email`, downstream behavior for this malformed session record is unpredictable but represents a broken invariant that "AuthLoginSuccessNo2FA" audit events and issued sessions correspond to complete, successfully persisted state — exactly the "silent success on failure" fund/state-loss analog raised in the report (impact reduced from "High" to unprivileged-actor authentication/session-integrity/audit-integrity issue since no direct token/fund transfer exists in this Go codebase).

### Likelihood Explanation
This is reachable by any unauthenticated caller who can start the OIDC flow (`handleSignIn`) and reach `handleTokenExchange` (`/callback`-style endpoint), which is explicitly an unprivileged, internet-facing gateway/auth entry point (no prior session/role required to invoke it). Triggering the DB-insert-failure branch requires a transient DB error, but the missing-`email`-claim branch is triggerable purely by controlling/manipulating the OIDC identity provider's response the client receives (e.g., a malicious or rogue IdP endpoint, or crafted ID token claims lacking `email`), which is plausible in real misconfigurations or when an attacker controls a rogue IdP the code exchanges with.

### Recommendation
Add `return` immediately after both error-response blocks in `handleTokenExchange`:
1. After `c.String(http.StatusInternalServerError, "Failed to get email from claims")` at line 229 — add `return`.
2. After `c.String(http.StatusInternalServerError, "Error creating session")` at line 259 — add `return`.

This prevents the handler from falling through to audit-logging success events and session cookie issuance after a failed precondition, matching the pattern used correctly elsewhere in the same function (e.g., lines 195, 203, 211, 218, 224, 244, 270).

### Proof of Concept
1. Configure/point the OIDC provider (or intercept the discovery/token exchange in a test harness) so that the ID token's claims payload omits the `email` field but otherwise passes signature verification and includes valid RBAC group claims.
2. Call `POST /callback` (the route wired to `handleTokenExchange`) with a valid `code`/`state` pair from the crafted flow.
3. Observe:
   - `claims["email"].(string)` type-assertion fails (`ok == false`); the handler writes an HTTP 500 body ("Failed to get email from claims") but does not return.
   - Execution proceeds to `oi.IDClaimsToUserRole`, inserts a row into `oidc_sessions` with `user_email = ''`, calls `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)`, sets the session cookie via `ginSession.Save()`, and finally writes `c.JSON(http.StatusOK, {"success":true})` appended after the earlier 500 body.
   - Inspect the audit log: an `AuthLoginSuccessNo2FA` entry is recorded despite the missing email claim, and a session cookie is issued to the caller — confirming that the unchecked/ignored failure allowed the state-changing session-issuance flow to complete.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-163)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
```

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L250-260)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L262-276)
```go
	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})

	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}

	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
}
```
