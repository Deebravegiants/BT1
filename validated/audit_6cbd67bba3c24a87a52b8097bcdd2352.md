### Title
Missing `return` after failed email-claim extraction lets OIDC login succeed and create an authenticated session with an empty/attacker-influenced email - (File: core/sessions/oidcauth/oidc.go)

### Summary
`handleTokenExchange` in `core/sessions/oidcauth/oidc.go` mirrors the reported bug class: a validation check that is supposed to abort the request on failure is missing the control-flow keyword needed to actually stop execution (`revert` in the Solidity report, `return` here). This lets execution continue past a failed check and complete the privileged action (creating an authenticated user session) anyway.

### Finding Description
In `handleTokenExchange`, after the OIDC ID token is verified and claims are parsed, the code extracts the `email` claim: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```

Every other failure branch in this function (`ShouldBindJSON`, state mismatch, `Exchange`, `id_token` extraction, `Verify`, `idToken.Claims`, `ExtractIDClaimValues`, role mapping, `ginSession.Save`) writes an error response **and returns**, e.g.: [2](#0-1) 

But the `email` claim check at line 226-230 writes `c.String(http.StatusInternalServerError, ...)` and falls through — there is no `return`. `c.String` in gin does not abort the handler (only `c.Abort()` does), so execution continues to compute the role from `idClaims`, insert a new row into `oidc_sessions` with `email` set to whatever `claims["email"]` produced (empty string `""` when the assertion fails), and set the session cookie: [3](#0-2) 

Finally it writes a second response, `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`, which overwrites/appends to the earlier error write: [4](#0-3) 

The net effect: a valid IdP-issued token whose ID-claim response happens to omit/mistype the `email` field (or where `claims["email"]` is not a string) still results in a *valid session cookie* being issued and stored (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`), tied to a session row where `user_email = ""` and `user_role` = whatever role was derived from group claims. That cookie is subsequently accepted as authenticated by `AuthorizedUserWithSession`, which trusts the DB row without re-validating the email: [5](#0-4) 

### Impact Explanation
This is the internet-facing OIDC login callback (`/sessions/exchange`-type endpoint reachable by any unauthenticated client attempting to log in). A missing abort here means:
- A caller can obtain a fully authenticated session cookie (mapped to a real RBAC role derived from group/ID claims) even though the identity attribute (`email`) used for auditing, `FindUser`, and session bookkeeping is empty/garbage.
- Multiple such logins collide on the same empty-string `user_email` key, which is used by `ClearNonCurrentSessions` (`DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2`) — any user whose email extraction fails would delete/collide with every other empty-email session, creating a session-management/cross-user confusion condition.
- The audit log records `email` as empty for a login event that otherwise proceeds as a success, undermining traceability of privileged authentication events.

This satisfies "concrete authentication/role bypass ... cross-user response confusion" from the validation rules — the check that should stop unauthenticated/invalid identity assertions from producing a session silently fails to stop it.

### Likelihood Explanation
Likelihood depends on the IdP/OIDC provider configuration returning ID token claims without a well-formed `email` field (e.g., IdP configured without the `email` scope claim populated, or an email claim of non-string type). This is a real-world misconfiguration/edge case rather than a routine happy path, but it is directly reachable by any client completing the standard, unauthenticated `/oidc-login` → `/exchange` flow with a validly signed ID token that simply omits or mistypes the email claim — no privileged access is required to trigger it.

### Recommendation
Add the missing `return` (matching every other error branch in this function) so the handler aborts when the email claim cannot be extracted, and this session is never created:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```

The similar fall-through at the `oidc_sessions` insert error branch (lines 257-260) should also be given a `return` for consistency, since it currently also continues to set the session cookie and return `200 OK` on a DB write failure: [6](#0-5) 

### Proof of Concept
1. Configure the node with `OIDCAuth` and a real/mock OIDC provider.
2. Have the provider return a validly-signed ID token whose claims map does not include an `email` key as a string (e.g., omit it or supply it as a non-string type), while still including group claims that map to a valid RBAC role (admin/edit/run/read).
3. Complete the standard `/oidc-login` redirect flow and POST the resulting `code`/`state` to the token-exchange endpoint (`handleTokenExchange`).
4. Observe: despite the internal server error write attempt at line 229, execution continues; `role` is derived successfully from `idClaims`, a row is inserted into `oidc_sessions` with `user_email = ''`, the session cookie is set via `ginSession.Save()`, and the client receives (a mangled/overwritten) `200 OK` `{"success":true}` body along with a valid, authenticated session cookie — usable for subsequent authenticated API calls per role.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L199-204)
```go
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}
```

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

**File:** core/sessions/oidcauth/oidc.go (L273-275)
```go
	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
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
