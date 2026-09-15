I found a strong analog: in the OIDC authentication handler, the session-creation database write's error is checked but not acted upon before the code proceeds to log an audit "success" event and returns a success response to the client — the exact same "unchecked return value causing downstream inconsistency / false success emission" bug class as the report.This confirms the bug. At `core/sessions/oidcauth/oidc.go` line 226-230, the same missing-`return` pattern also occurs when the `email` claim is missing, and it happens again at lines 257-260 for the DB write. Let me verify the `AuthorizedUserWithSession` consumer path and the `ginSession.Set`/`Save` to confirm the ID-cookie-with-no-DB-row consequence.### Title
Missing `return` after failed OIDC session persistence causes false "login success" audit event and issuance of a session cookie for a non-existent session record - (File: core/sessions/oidcauth/oidc.go)

### Summary
In `oidcAuthenticator.handleTokenExchange`, the error returned by the database write that persists a new OIDC-authenticated session is checked and logged, but the handler does not `return` on failure, mirroring the reported bug class where an unchecked/mishandled failure return value is followed by code that behaves as if the operation succeeded (there, an ERC20 event emission; here, an audit-success event and a valid-looking session response).

### Finding Description
`handleTokenExchange` inserts the newly created session into the `oidc_sessions` table: [1](#0-0) 

If `ExecContext` fails, the code logs the error and writes an HTTP 500 body via `c.String(...)`, but execution is **not** stopped — there is no `return` statement, unlike every other error branch in the same function (e.g. lines 166-171, 189-196, 209-211, 216-218, 222-224, 241-244, 267-270 all `return` after handling their error). As a result, control falls through to: [2](#0-1) 

This means that after a failed DB insert:
1. `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` still records a **successful login audit event**, even though the session was never persisted.
2. `ginSession.Set(webauth.SessionIDKey, clSession.ID)` followed by `ginSession.Save()` still sets and saves a gin session cookie referencing `clSession.ID` — an ID that does not exist in the `oidc_sessions` table.
3. If `ginSession.Save()` succeeds, the handler falls through to `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`, sending (or attempting to send, on top of the already-written 500 body) a success response to the client, even though authentication/session-creation failed.

The same missing-`return` pattern also exists a few lines earlier when the `email` claim extraction fails: [3](#0-2) 

Downstream, the session cookie value is consumed by `AuthenticateGQL`, which calls `AuthorizedUserWithSession` against the `oidc_sessions` table: [4](#0-3) 

Since the row was never inserted, a subsequent request with this cookie will fail lookup (`sql.ErrNoRows` → `ErrUserSessionExpired`), so this specific instance does not directly grant privileged access. However, it directly reproduces the reported bug class: **a failure path that does not halt execution, causing a "success" signal (audit log entry, and potentially an HTTP success response) to be emitted for an operation that actually failed**, producing state/log inconsistency that downstream consumers (SIEM/audit tooling, or the frontend) will misinterpret as a successful, persisted login.

### Impact Explanation
- The audit log (`AuthLoginSuccessNo2FA`) becomes an unreliable source of truth: security monitoring/alerting built on audit logs will record successful logins that never actually completed, undermining incident investigation and compliance evidence — directly analogous to the report's "downstream applications capturing wrong transaction/state of the protocol."
- The client may receive a `Success: true` JSON body (or a malformed/garbled double response, since `c.String` was already invoked) despite the backend failing to create the session, causing user-facing state confusion.
- Because this affects the **unprivileged, internet-facing OIDC login callback endpoint** (an unauthenticated user completing OAuth2/OIDC exchange), it is reachable pre-authentication by any client attempting to log in when the DB is transiently unavailable/erroring.

Severity is lower than a true auth bypass because the stale session ID cannot itself be used to authenticate (the lookup will fail), so this is best characterized as a logging/state-integrity issue rather than a privilege escalation.

### Likelihood Explanation
Requires the `oidc_sessions` INSERT to fail (e.g., transient DB error, constraint violation) while the rest of the OIDC flow (token exchange, claims verification) succeeds. This is a realistic operational condition (DB contention, connection issues) and does not require attacker-controlled input beyond a normal OIDC login attempt, but it is not attacker-triggerable at will (it depends on infrastructure conditions), so likelihood is low-to-moderate.

### Recommendation
Add `return` immediately after handling the `ExecContext` error (mirroring the `ginSession.Save()` error handling directly below it), and likewise `return` after the `email` claim extraction failure:

```go
_, err = oi.ds.ExecContext(ctx, ...)
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```
and
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Only emit `audit.AuthLoginSuccessNo2FA` and set the session cookie after confirming the session row was successfully persisted.

### Proof of Concept
1. Force the `oidc_sessions` INSERT executed at `core/sessions/oidcauth/oidc.go:250-256` to fail (e.g., temporarily break DB connectivity, or add a unique-constraint violation via a colliding session ID).
2. Trigger a normal OIDC login flow via `POST` to the token-exchange endpoint that invokes `handleTokenExchange`.
3. Observe that despite the logged `ExecContext` error, execution continues to line 262, `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` is called, and `ginSession.Set/Save` still run, followed by `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` — inconsistent with the actual DB failure, and appended after the already-written 500 response body.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L249-260)
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

**File:** core/sessions/oidcauth/oidc.go (L349-373)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
```
