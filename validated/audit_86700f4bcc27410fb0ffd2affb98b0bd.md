### Title
Missing `return` after email-claim validation failure lets OIDC callback create a fully authenticated, privileged session with an unverified/empty identity - (File: core/sessions/oidcauth/oidc.go)

### Summary
`oidcAuthenticator.handleTokenExchange` fails to check/short-circuit on a fundamental validation error the same way `PerpDepository.withdrawInsurance` failed to check the result of `transfer`: an "operation" (extracting the identity claim) can silently fail, yet the state-mutating steps that follow (role mapping, session row insert, session cookie issuance) are executed anyway, producing a persisted, unprivileged-actor-controllable authenticated session built on invalid data.

### Finding Description
In the OIDC callback handler, after verifying the ID token and extracting group claims, the code attempts to read the `email` claim: [1](#0-0) 

If the assertion fails, an error is logged and an HTTP body is written with `c.String(http.StatusInternalServerError, ...)`, but **there is no `return` statement**. Execution falls through to role mapping and session creation using the now-empty `email` variable: [2](#0-1) 

The session is persisted with `user_email = ""` and the role computed from the IdP's group claims, then the gin session cookie is saved and (in the normal flow) a success response is written. This mirrors the reported bug class: a failure signal from a critical operation (claim extraction, analogous to `transfer`'s boolean return) is observed but not acted upon, and the subsequent accounting/state (session row, cookie) proceeds as if the operation had succeeded.

The resulting session is fully valid for authorization purposes — `AuthorizedUserWithSession` simply reads back whatever was stored, with no re-validation of email presence: [3](#0-2) 

Because the role (`Admin`/`Edit`/`Run`/`Read`) is derived purely from IdP group claims and not tied to a validated, unique email, any IdP response lacking (or manipulated to lack) an `email` claim but containing the configured admin/edit/run group claim still yields a working, privileged session. Additionally, since every such session shares the same `user_email = ""`, `ClearNonCurrentSessions` (`DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2`) would treat all such "identity-less" sessions as belonging to the same user, letting one such session terminate another's — a cross-user session confusion/interference distinct from ordinary per-user session isolation.

### Impact Explanation
An unprivileged client that can influence or exploit the OIDC token-exchange response (e.g., a malicious or misconfigured OIDC provider, or any code path where the `email` claim is absent while group claims are present) can obtain a persisted, cookie-backed session with an elevated role (up to Admin, depending on `AdminClaim()` group membership) without a validated unique identity. This breaks the node's authentication/audit invariant that every session maps to a real, attributable user identity, and enables session interference between different "email-less" principals via `ClearNonCurrentSessions`.

### Likelihood Explanation
This requires the connected OIDC identity provider's ID token to omit the `email` claim while still presenting one of the configured RBAC group claims — a condition entirely under the control of the IdP response the node trusts during callback handling, not a hypothetical or purely operator-controlled scenario. Given OIDC providers vary in which claims they include by default/scope configuration, this is a realistically reachable, unprivileged-facing code path (the `/oidc/exchange` HTTP endpoint) rather than an internal/administrative one.

### Recommendation
Add a `return` immediately after writing the error response when the `email` claim assertion fails, so no session or role is created for an unvalidated identity:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, consider rejecting/erroring the whole token exchange if `email` is empty rather than persisting an empty-string identity, to avoid cross-user session collisions in `ClearNonCurrentSessions` and audit-log corruption.

### Proof of Concept
1. Configure the node with OIDC using group-based `AdminClaim`/`EditClaim`/etc. mappings.
2. Have the (attacker-influenced or misconfigured) IdP return an ID token / userinfo response that includes the configured admin group claim but omits the `email` field (or the `id_token` claims lack `email` while `claims` map used for role mapping is populated from group claims independently).
3. `handleTokenExchange` logs the missing-email error, writes a `500` body, but does **not** return; execution continues.
4. `IDClaimsToUserRole` returns the mapped role (e.g., Admin) based on group claims (unaffected by empty email).
5. A row is inserted into `oidc_sessions` with `user_email = ''` and the elevated role; `ginSession.Set(...)` / `ginSession.Save()` persist a valid session cookie to the response.
6. The caller now holds a cookie that `AuthorizedUserWithSession` will resolve to a fully privileged user with an empty/unverifiable identity, usable against all `Authenticate`-protected `/v2/*` endpoints.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L233-276)
```go
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
