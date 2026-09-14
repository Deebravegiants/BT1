### Title
Missing Error-Path `return` in OIDC Token Exchange Grants Authenticated Session Despite Failed DB Write / Missing Email Claim - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
`handleTokenExchange` in `core/sessions/oidcauth/oidc.go` fails to `return` after two critical error checks, mirroring the report's root cause: a critical operation's success is not verified before the code proceeds to assume it succeeded. First, when the `email` claim cannot be extracted, the handler logs/writes an error response but falls through and continues execution. Second, when the `INSERT INTO oidc_sessions` write fails, the handler again writes an error response but falls through, and unconditionally grants the client an authenticated session cookie for a session ID that was never persisted to the database.

### Finding Description
In `handleTokenExchange`: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```
There is no `return` after the `c.String(...)` call, so `email` ("" on failure) flows into the rest of the function.

Second occurrence at the session-persistence step: [2](#0-1) 

```go
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
```
Again, no `return` after the error branch. The function proceeds to audit-log a "login success" event and, more importantly, sets the gin session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)` then `ginSession.Save()`), handing the caller a cookie referencing a `clSession.ID` that was never inserted into `oidc_sessions`. Because Gin allows multiple writes to the response (the last `c.JSON(http.StatusOK, ...)` at the end overwrites the earlier `c.String(http.StatusInternalServerError, ...)` in the response body/status unless the connection was already flushed), the final HTTP response returned to the browser is `200 OK` with `Success: true`, even though the DB write failed. The subsequent `AuthorizedUserWithSession` lookup (`SELECT ... FROM oidc_sessions WHERE id = $1`) would then fail for that session ID, but the fact remains that the code path treats a failed persistence operation as if it succeeded, exactly analogous to the reported bug class of "assumes success without verifying it."

This matches the requested unprivileged-actor analog: it sits in node API authentication / session handling reachable by any client performing the OIDC login flow (`/oidc/callback` type token-exchange endpoint), not requiring privileged access.

### Impact Explanation
- If the `email` claim type assertion fails, the handler still proceeds to map the OIDC group claims to an RBAC `role` and would attempt session creation using an empty-string email, silently degrading identity binding for the created session instead of aborting the login flow.
- If the DB insert of the session record fails, the client still receives a session cookie (`SessionIDKey`) for a session that does not exist in `oidc_sessions`. While the immediate practical effect is that later authenticated requests using that cookie will fail lookups (`AuthorizedUserWithSession`) and thus not directly grant unauthorized access, the code's failure to check/act on the write's success is a clear violation of the "verify critical operation before proceeding" invariant that the reported bug is about, and creates an inconsistent server state (audit log records a successful login with no backing session row), undermining audit-log integrity and creating latent risk if the surrounding code (e.g., caching layers, session store behavior) is later changed to assume the row exists.

### Likelihood Explanation
Both code paths are reachable by any client hitting the OIDC token exchange callback endpoint with a slightly malformed IdP response (missing/non-string `email` claim) or during any transient DB error (deadlock, connection issue) on the `INSERT` — DB write failures are not attacker-controlled but not rare either, and the missing-email-claim path can be influenced by a malicious/misconfigured upstream response depending on OIDC provider behavior. The bug is a straightforward missing `return` — an unconditional structural coding error, not dependent on privileged access.

### Recommendation
Add `return` immediately after both error branches:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
and
```go
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```
This ensures the session cookie and audit "login success" event are only emitted once the DB write and claim extraction are confirmed to have succeeded.

### Proof of Concept
1. Configure the OIDC provider mock/test double so `idToken.Claims(&claims)` returns a claims map without an `email` key (or with a non-string value).
2. Drive `handleTokenExchange` via the exchange endpoint with a valid `code`/`state`.
3. Observe that execution does not stop after the `!ok` branch: `IDClaimsToUserRole` is still called, the `INSERT INTO oidc_sessions` still executes with `email=""`, and (assuming role mapping and DB insert succeed) the handler ultimately returns `200 OK` with `{"success":true}` — overwriting the earlier `500` write — despite the missing email claim.
4. Separately, force `oi.ds.ExecContext` to return an error (e.g., point at a broken DB connection or unique-constraint violation on `clSession.ID`). Observe the handler still proceeds to `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()`, issuing the client a session cookie for a nonexistent `oidc_sessions` row, while also invoking `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` recording a false "success" audit event.

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
