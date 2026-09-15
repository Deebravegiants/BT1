Based on my investigation, I found a concrete code-flow defect in the OIDC sign-in callback handler that matches the CVE-2017-0926 bug class (improper authorization in the OAuth/OIDC sign-in component resulting in unauthorized session establishment).

### Title
Missing `return` after email-claim extraction failure allows session establishment to continue on error path in OIDC token exchange handler - ([File: core/sessions/oidcauth/oidc.go])

### Summary
`handleTokenExchange`, the OIDC (OAuth2/OpenID Connect) sign-in callback handler reachable by any unauthenticated client completing the `/oidc-login` redirect flow, fails to `return` after detecting that the identity provider's ID token claims are missing the `email` field. Execution falls through to role-mapping, database session insertion, and cookie-setting logic, resulting in an authenticated session being created and returned to the client despite the code's own error-handling branch indicating the flow should have aborted.

### Finding Description
In `handleTokenExchange`, after the ID token is verified and claims are parsed, the handler attempts to extract the `email` claim: [1](#0-0) 

If the type assertion fails (`ok == false`), the code logs an error and writes an HTTP 500 response body, but does **not** `return`. Execution continues into role mapping via `IDClaimsToUserRole`: [2](#0-1) 

and then into session creation, which inserts a new row into `oidc_sessions` (with an empty/garbage `user_email`) and sets the session cookie as if authentication succeeded: [3](#0-2) 

Because `AuthorizedUserWithSession` later trusts whatever `user_email`/`user_role` pair is stored in `oidc_sessions` for that session ID without re-validating against the original IdP claims: [4](#0-3) 

a session with a role derived from the attacker's own IdP group claims (Admin/Edit/Run/Read, controlled by `IDClaimsToUserRole`) gets persisted and honored by the middleware (`AuthenticateBySession` in `core/web/auth/auth.go`) even though the intended error/abort path was hit. This mirrors the GitLab CVE-2017-0926 bug class: an improperly guarded branch in the OAuth callback logic lets the login/session-creation code path complete despite a failed validation step, undermining the intended authorization gate.

### Impact Explanation
This is a control-flow/authorization defect in the internet-facing OIDC callback handler. While the role that ends up granted is still derived from the requester's own asserted IdP claims (not another specific victim's identity), the missing `return` means a validation failure that was clearly meant to abort the authentication flow instead silently proceeds to establish a fully authenticated, cookie-backed session with whatever role the claims map to (up to Admin, depending on IdP group configuration) — an unintended authorization bypass of the intended check.

### Likelihood Explanation
Exploitability depends on being able to complete the OIDC exchange with an ID token/claims payload lacking an `email` field (e.g., a misconfigured or permissive/self-service identity provider that omits the optional `email` claim while still supplying group/role claims). This is a plausible misconfiguration scenario for self-hosted OIDC deployments, but requires cooperation from (or misconfiguration of) the configured external IdP rather than a pure network-only attacker, which is a partial mitigating factor.

### Recommendation
Add a `return` statement immediately after the email-extraction failure branch in `handleTokenExchange` (mirroring the pattern used by every other error branch in the function) so that the handler aborts and no session row or cookie is created when the ID token doesn't contain the expected `email` claim.

### Proof of Concept
1. Configure OIDC with an identity provider that returns an ID token/claims set containing a valid group claim (e.g., matching `ReadClaim`) but no `email` field.
2. Complete the `/oidc-login` → `/oidc/callback` (token exchange) flow as an unprivileged, unauthenticated client.
3. Observe that despite the server logging "Failed to get email from claims" and writing a 500 status body, the handler continues, inserts a row into `oidc_sessions`, and calls `ginSession.Save()` — the response includes a valid session cookie (`SessionIDKey`), and subsequent authenticated requests using that cookie succeed via `AuthorizedUserWithSession`, confirming that a session was established despite the intended abort condition.

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

**File:** core/sessions/oidcauth/oidc.go (L233-245)
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
```

**File:** core/sessions/oidcauth/oidc.go (L247-276)
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
