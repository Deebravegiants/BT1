The claim's code citation is accurate — I've confirmed both bugs exist exactly as described in the actual repository code.Audit Report

## Title
Missing `return` Statements in `handleTokenExchange` Allow Session Creation and Audit Logging to Proceed Despite Detected Errors - (File: core/sessions/oidcauth/oidc.go)

## Summary
`handleTokenExchange` in `core/sessions/oidcauth/oidc.go`, the handler for the public/unauthenticated `POST /oidc-exchange` endpoint, detects two distinct failure conditions — a missing/invalid `email` claim and a failed `INSERT INTO oidc_sessions` — logs the error and writes an error response via `c.String(...)`, but omits the `return` statement in both cases. Execution falls through to session-cookie establishment and audit logging as if the request had succeeded.

## Finding Description
Two specific spots in `handleTokenExchange` lack the `return` after error handling:

1. When `claims["email"]` is not a string: [1](#0-0) . Execution continues into role mapping and the `oidc_sessions` INSERT with an empty `email`.
2. When the `INSERT INTO oidc_sessions` fails: [2](#0-1) . Execution continues into the audit call and session cookie save regardless of the insert outcome.

In both cases, control flow proceeds to: [3](#0-2) , which unconditionally fires `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)`, sets `ginSession.Set(webauth.SessionIDKey, clSession.ID)`, calls `ginSession.Save()`, and finally writes `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.

This is a genuine logic defect: the intended security gate ("reject login flow if the email claim can't be extracted, or if the session row can't be persisted") is not enforced because the code never halts after detecting the fault. No other check in the function (state validation, token exchange, ID-token verification, `ExtractIDClaimValues`, `IDClaimsToUserRole`) compensates for this, since those all correctly `return` on error — only these two spots are missing it.

Note that in Go's `net/http`, only the first `WriteHeader` call from `c.String(http.StatusInternalServerError, ...)` sets the actual response status code (subsequent `c.JSON` calls after headers are already written do not change the status the client ultimately receives); regardless, the session cookie is genuinely set/saved and the audit event genuinely fires despite the detected failure, which is the core security-relevant defect.

## Impact Explanation
- Missing-email case: a session row is actually inserted into `oidc_sessions` with `user_email = ''`, a session cookie referencing that valid, persisted session ID is set on the client, and an `AuthLoginSuccessNo2FA` audit entry is recorded with an empty email — even though the handler detected and intended to reject this login. The role assigned is still derived correctly from `idClaims`/group claims (unaffected by this bug), so this does not directly grant privilege escalation, but it bypasses an intended validation gate, corrupts the audit trail, and creates a persisted, usable session that the code explicitly tried to prevent from being created.
- INSERT-failure case: the cookie references a session ID that was never persisted, so subsequent authenticated requests using it will fail lookup in `AuthorizedUserWithSession` (which queries `oidc_sessions` by ID) — limiting this branch's practical impact primarily to a spurious success audit log entry and misleading client-side response state, rather than a usable bypass.

The core validated impact is an audit-logging/session-establishment integrity flaw: a security check is not enforced end-to-end (fail-early principle broken), which is a real defect in the authentication flow.

## Likelihood Explanation
`/oidc-exchange` is intentionally public/unauthenticated as the OIDC callback endpoint, reachable once OIDC is enabled (`OIDC.Enabled=true`). The missing-email path can be triggered by any legitimately-completed OIDC exchange where the ID token/claims lack an `email` field (e.g., IdP not configured to return an `email` claim, or `email` scope not requested) — a plausible, non-adversarial condition in real deployments. This does not require attacker privilege beyond completing the standard front-channel OIDC flow with a valid IdP.

## Recommendation
Add `return` immediately after each error-handling block in `handleTokenExchange`:
- After `c.String(http.StatusInternalServerError, "Failed to get email from claims")`.
- After `c.String(http.StatusInternalServerError, "Error creating session")`.

More generally, audit all handlers in `core/sessions/oidcauth/oidc.go` for the "log error → write HTTP response → fall through" pattern and ensure every error branch explicitly returns.

## Proof of Concept
1. Enable OIDC (`OIDC.Enabled=true`) against a test/mock provider configured (or misconfigured) to omit the `email` claim from the ID token while still supplying valid group claims for `IDClaimsToUserRole`.
2. Complete `/oidc-login` and call `POST /oidc-exchange` with the resulting code/state.
3. Observe server logs showing `"Failed to get email from claims"`, yet a new row is written to `oidc_sessions` with `user_email = ''`, a session cookie is set via `ginSession.Save()`, and the audit log records `AuthLoginSuccessNo2FA` with `email: ""` — confirming the code proceeded past the detected error instead of returning.
4. A Go unit/integration test invoking `handleTokenExchange` with a mocked provider/token whose claims lack `email` can assert directly that `oidc_sessions` receives a row and `ginSession.Save()` is called despite the error condition, proving the missing-`return` defect.

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L262-275)
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
```
