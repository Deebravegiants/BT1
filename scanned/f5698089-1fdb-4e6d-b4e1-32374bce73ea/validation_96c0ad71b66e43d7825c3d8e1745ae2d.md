### Title
Unchecked session-persistence failure lets `handleTokenExchange` continue and issue a session cookie for a non-persisted OIDC session - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
`oidcAuthenticator.handleTokenExchange` inserts a new row into `oidc_sessions` and, on failure, writes an HTTP 500 response but does **not** `return`. Execution falls through and continues to audit-log a successful login, set the session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`), save the session, and finally write a second (`200 OK`) response body. This mirrors the reported bug class: an unchecked/mishandled failure of a critical persistence operation (`_token.transfer` in the original report ↔ `oi.ds.ExecContext(... INSERT INTO oidc_sessions ...)` here) is followed by code that behaves as if the operation succeeded, producing an inconsistent state and a malformed dual response.

### Finding Description
In `core/sessions/oidcauth/oidc.go`, `handleTokenExchange` performs the OIDC token exchange, validates claims/roles, and then persists the session: [1](#0-0) 

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

The `if err != nil` block writes an error response but is missing a `return` statement. As a result, even when the DB insert fails:
- An audit log entry `AuthLoginSuccessNo2FA` is recorded, falsely indicating a completed login.
- `clSession.ID` (a session ID that was never actually persisted to `oidc_sessions`) is placed into the Gin session store and `ginSession.Save()` is invoked, attempting to set the session cookie.
- The handler proceeds to `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`, writing a second response payload after already writing a `500` response body — an invalid/ambiguous HTTP response (Gin does not prevent multiple writes on the same `*gin.Context`, though only the first `WriteHeader` call determines the status actually sent).

This directly parallels the reported vulnerability’s pattern: a critical state-mutating operation (`_token.transfer` / `INSERT INTO oidc_sessions`) is not gated by a success check before the surrounding code commits to "the operation succeeded" — updating `totalERC20Claimed` unconditionally in the original report, and here setting/persisting a session cookie referencing a session ID that does not exist in the backing table.

### Impact Explanation
If the `oidc_sessions` INSERT fails (DB error, connection issue, disk/quota problem, replica lag, etc.) during an OTherwise-successful OIDC login:
- The session/token bookkeeping is left inconsistent: a cookie referencing `clSession.ID` may be set on the client even though no corresponding row exists server-side (since `AuthorizedUserWithSession`/`FindUserByAPIToken`-style lookups depend on that table for OIDC-backed sessions). This is analogous to the "locked tokens"/"accounting error" impact of the original report — the client is left holding a credential that cannot actually be used to authenticate.
- A successful-looking audit log entry (`AuthLoginSuccessNo2FA`) is emitted for a login that did not actually establish a durable, valid session, which can mislead operators/incident responders reviewing audit trails for authentication events.
- The HTTP response itself becomes malformed (writing both a `500` error body and then a `200 JSON` body), which can produce confusing/undefined client-side behavior depending on how downstream HTTP clients parse the response.

This qualifies as a request/response and session-bookkeeping integrity defect reachable directly by an unprivileged client performing a normal OIDC login flow, without any privileged/operator/node-level access, malicious peer, or mocked path.

### Likelihood Explanation
The triggering condition is any transient failure of the `oi.ds.ExecContext` INSERT (e.g., DB unavailability, timeout, constraint violation, connection pool exhaustion) during `handleTokenExchange`. This does not require attacker-controlled input beyond a normal login attempt; it can occur under ordinary operational conditions (DB hiccups, high load) and does not require compromising any other node or peer. Because the flawed code path is only exercised on a DB error, it is likely low-frequency in normal operation but will occur whenever the underlying datastore experiences any write failure during login, which is a realistic operational scenario, not a purely theoretical one.

### Recommendation
Add a `return` immediately after writing the error response in the `if err != nil` block following the `oi.ds.ExecContext` INSERT call, so that a failed session-persistence attempt does not fall through to:
1. Audit-logging a successful login.
2. Setting/saving the session cookie for a session ID that was never persisted.
3. Writing a second, conflicting HTTP response.

Additionally, consider wrapping the audit log emission, cookie assignment, and final JSON response in the success path only, guarded by successful completion of the persistence step, to keep the audit trail and session state consistent with the actual outcome of the database write.

### Proof of Concept
1. Configure the Chainlink node with OIDC authentication enabled (`UserAPITokenEnabled`/OIDC auth provider) as in `core/sessions/oidcauth/oidc.go`.
2. Simulate a transient failure on the `oidc_sessions` table INSERT (e.g., via a DB proxy that intermittently rejects writes, or a full disk/connection-pool exhaustion condition) while a legitimate user completes the OIDC redirect flow and hits `POST /.../token-exchange` (handled by `handleTokenExchange`).
3. Observe that:
   - The audit log records `AuthLoginSuccessNo2FA` for the attempt.
   - The Gin session store is set with `webauth.SessionIDKey = clSession.ID`, and `ginSession.Save()` is invoked, despite no row existing in `oidc_sessions` for `clSession.ID`.
   - The final HTTP response body is a concatenation of `"Error creating session"` (from the first `c.String` call) followed by the JSON payload from the second `c.JSON` call, evidencing the double-write bug.
4. A subsequent request using the cookie set in step 3 is expected to fail `FindUserByAPIToken`/`AuthorizedUserWithSession`-equivalent lookups against `oidc_sessions`, confirming the client was issued state referencing a session that was never durably created — the “locked/inconsistent state” analog to the reported unchecked-transfer defect.

Note: I was unable to fully trace how `oidc_sessions` lookups (e.g., the OIDC equivalent of `AuthorizedUserWithSession`) behave when the cookie references a missing row, since that lookup path wasn't directly retrieved in this session; the described impact (broken login state, malformed response, misleading audit entry) is established directly from the code shown above, but the exact downstream authentication-check behavior on the next request should be verified against the OIDC session-lookup implementation before finalizing severity.

### Citations

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
