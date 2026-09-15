### Title
Missing `return` after failed OIDC email-claim extraction allows session creation with unverified/mismatched identity - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
In `handleTokenExchange`, the handler that completes the OIDC/OAuth2 SSO login flow, the code extracts the `email` claim from the ID token but fails to `return` when that extraction fails, allowing execution to continue and a fully authenticated session to be created and returned to the client despite the email value being empty/invalid.

### Finding Description
`handleTokenExchange` in `core/sessions/oidcauth/oidc.go` verifies the ID token, extracts role-mapping claims via `ExtractIDClaimValues`, then attempts to read the `email` claim: [1](#0-0) 

Unlike every other error-handling branch in this same function (id_token missing, ID-token verification failure, claims parsing failure, role-mapping failure — all of which call `return` after writing an error response), this branch writes an HTTP 500 body via `c.String` but does **not** `return`. Execution falls through with `email` left as the zero value `""`.

The function then proceeds to:
1. Map the (independently-extracted) group claims to an RBAC role via `IDClaimsToUserRole`.
2. Insert a new row into `oidc_sessions` with `user_email = strings.ToLower(email)` (i.e. an empty string) and the resolved `role`: [2](#0-1) 
3. Audit-log a successful login with the (empty) email.
4. Set the session cookie (`webauth.SessionIDKey`) and return `ExchangeTokenResponse{Success: true}` with HTTP 200: [3](#0-2) 

Because Gin's `c.String` call earlier only sets the status/body for that write — it does not abort the handler — the response actually delivered to the browser is the final `c.JSON(http.StatusOK, ...)` success payload with a valid, cookie-backed session, even though the identity provider's response failed to yield a usable email identity. Role assignment (`AuthorizedUserWithSession` reads `user_email`/`user_role` straight out of `oidc_sessions`) is decoupled from any verified email, so a session is minted and authenticated purely on the strength of whatever group/role claims were present, with the `user_email` column silently defaulting to `""`.

This mirrors the class of bug in CVE-2017-18906: an SSO/OAuth2 callback path that doesn't correctly halt processing on an identity-verification failure ends up completing authentication and issuing a valid session anyway, producing an authenticated identity/session that is not properly bound to a verified user identity (empty/mismatched email vs. asserted role).

### Impact Explanation
An attacker who can influence or exploit an IdP response that omits/malforms the `email` claim (e.g., a federated/enterprise IdP misconfiguration, a claims-mapping edge case, or an IdP that doesn't always populate `email` for every account type) ends up with a fully valid, cookie-authenticated `oidc_sessions` row and an RBAC role taken directly from the `groups`/claim-name mapping — while `user_email` is stored as `""`. Since `AuthorizedUserWithSession` trusts the stored `user_role` without re-validating the email, this results in an authenticated session whose identity binding is broken, and (depending on `ClaimName`/role config) can grant elevated roles (e.g., `Admin`) without a legitimate, attributable user identity — a session/identity confusion and potential unauthorized privilege grant in the node's user-authentication path.

### Likelihood Explanation
Requires the OIDC/OAuth2 SSO WebServer authenticator to be enabled (`WebServer.OIDC` configured) and requires the IdP's ID token response to lack an `email` claim (or return the wrong type) for a given authentication flow — a scenario reachable by any user completing the standard `/oidc-login` → `/signin` exchange, not requiring any special privilege beyond initiating a normal SSO login. This makes it a plausible, unprivileged-actor-reachable defect in a code path that is directly exposed to the internet-facing gateway (gin `handleTokenExchange` route), though it is contingent on IdP claim content.

### Recommendation
Add a `return` immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call in `handleTokenExchange`, matching the pattern used by every other failure branch in the function, so that no session is created or returned when the email claim cannot be extracted:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```

Additionally, consider making `email` a mandatory, validated field before any `oidc_sessions` row is inserted, to prevent any authenticated session from ever being created with an empty/unverified `user_email`.

### Proof of Concept
1. Configure `WebServer.OIDC` and complete the `/oidc-login` redirect to reach `handleTokenExchange`.
2. Return (or induce, via a claims-mapping/IdP misconfiguration) an ID token whose payload contains valid `groups`/role claims but no `email` field (or a non-string `email`).
3. Observe that `handleTokenExchange` logs an error and writes an HTTP 500 body for the missing email, but execution continues: `IDClaimsToUserRole` resolves a role, a row is inserted into `oidc_sessions` with `user_email = ''`, the session cookie is set, and the final response is HTTP 200 `{"success":true}`.
4. The resulting session cookie is valid and, per `AuthorizedUserWithSession` (`core/sessions/oidcauth/oidc.go:351-391`), authorizes the caller with the role stored for the empty-email session — i.e., an authenticated session bound to no verifiable identity. [4](#0-3)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-256)
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
