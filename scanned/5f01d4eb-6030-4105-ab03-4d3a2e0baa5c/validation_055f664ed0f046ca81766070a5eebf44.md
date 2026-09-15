## Analysis

The reported CVE-2016-2336 is a type-confusion bug where a failed/incorrect type assumption on an attacker-influenced object is not properly validated before use, leading to unsafe continued execution. The closest concrete analog in this codebase is in the OIDC token-exchange handler, where a failed type assertion on an identity-provider-controlled claim value does not abort request processing, allowing an authenticated session to be established using invalid/empty identity data. [1](#0-0) 

### Title
Missing `return` after failed type assertion on OIDC `email` claim allows session creation with invalid identity data - (File: core/sessions/oidcauth/oidc.go)

### Summary
In `handleTokenExchange`, the `email` claim extracted from the verified OIDC ID token is type-asserted to a `string`. When the identity provider's `email` claim is absent or of an unexpected type (nil, number, object, array), the type assertion fails (`ok == false`). The handler logs the error and writes an HTTP 500 response body via `c.String(...)`, but does **not** `return`, so execution continues down the normal success path using the zero-value empty string for `email`. [1](#0-0) 

### Finding Description
This mirrors the root cause of CVE-2016-2336: a type mismatch on externally supplied data is detected, but the failure isn't used to halt processing before the malformed value is used downstream. Here, after the failed assertion, the code proceeds to:
1. Derive the user's `role` from group claims (independent of `email`).
2. Insert a new row into `oidc_sessions` with `user_email` set to the empty string.
3. Emit an audit log entry `AuthLoginSuccessNo2FA` with `email: ""`.
4. Set the session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`) and save it.
5. Return `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` — a 200 success — even though a 500 error body was already written earlier in the same handler. [2](#0-1) 

The resulting session is fully functional: `AuthorizedUserWithSession` looks sessions up strictly by the random `sessionID` (not by email), so the empty-string email doesn't grant access to another specific account, but it does mean the server establishes and honors an authenticated session — with a real RBAC role sourced from IdP group claims — despite failing to validate a core identity attribute. [3](#0-2) 

This also corrupts identity-management operations that key off `user_email`: `ClearNonCurrentSessions` deletes all `oidc_sessions` rows matching `lower(user_email) = lower($1)`, so if more than one such malformed session exists, one user's password-change flow will indiscriminately purge other users' empty-email sessions, causing cross-user session interference. [4](#0-3) 

### Impact Explanation
An authenticated OIDC session (with a legitimately mapped RBAC role, potentially Admin/Edit/Run depending on IdP group claims) can be created and persisted even though the server explicitly detected and logged that the identity extraction failed. Audit logs record a blank/incorrect identity for what is treated as a successful login, undermining accountability for privileged actions taken under that session. Session bookkeeping (`ClearNonCurrentSessions`) can also cross-affect unrelated sessions sharing the empty-email marker.

### Likelihood Explanation
Reaching this path only requires an OIDC identity provider response whose ID token claims omit `email` or return it as a non-string type — a state reachable by any OIDC-authenticated user if the provider/scope configuration doesn't reliably return an email claim (a common real-world OIDC configuration edge case, not an exotic attack). No privileged access is required to trigger it; a standard OIDC login flow through `/oidc-exchange` is sufficient.

### Recommendation
Add a `return` immediately after the `c.String(http.StatusInternalServerError, ...)` call at line 229 so the handler aborts before creating a session, inserting the `oidc_sessions` row, or writing the success JSON response. Additionally, avoid writing multiple HTTP status/response bodies within a single handler invocation, and reject/require a well-formed `email` claim before proceeding to session creation and audit logging.

### Proof of Concept
1. Configure/point the OIDC provider (or intercept its response in a test/staging environment) such that the ID token's claims omit the `email` field (or set it to a non-string, e.g. `null` or a number), while still including valid group claims mapping to a role (e.g., admin).
2. Complete the OAuth2 authorization flow and POST the resulting `code`/`state` to `/oidc-exchange`.
3. Observe that `claims["email"].(string)` fails (`ok == false`); the handler logs an error and writes a 500 body, but does not return.
4. Execution continues: a role is derived from the group claims, a new row is inserted into `oidc_sessions` with `user_email = ''`, the session cookie is set, and the handler ultimately returns `200 {"success": true}`.
5. The response cookie corresponds to a valid, working session with the mapped role, confirming a functioning authenticated session was created despite the earlier detected and logged identity-extraction failure.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
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

**File:** core/sessions/oidcauth/oidc.go (L349-391)
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
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L441-449)
```go
// ClearNonCurrentSessions removes other oidc_sessions for the user tied to sessionID.
func (oi *oidcAuthenticator) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := oi.ds.GetContext(ctx, &email, "SELECT user_email FROM oidc_sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2", email, sessionID)
	return err
}
```
