### Title
OIDC token exchange proceeds with an empty/invalid email claim, creating an authenticated session decoupled from any real user identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
Dovecot's CVE-2019-3814 allowed a valid but malformed identity assertion (a client certificate with an empty username field) to be accepted, letting an attacker impersonate another party because the empty-field case wasn't treated as a hard failure. The chainlink OIDC authenticator has the same class of defect: when the identity provider's ID token claims are missing the `email` field (or it isn't a string), the handler logs an error and writes an HTTP error body, but **does not `return`**, so execution continues and a session row is still created using the empty string as the user's email.

### Finding Description
In `handleTokenExchange`, after the ID token is cryptographically verified and role claims are extracted, the code retrieves the email: [1](#0-0) 

If `claims["email"]` is absent or not a string, `ok` is `false` and `email` is `""`. The function logs the failure and calls `c.String(http.StatusInternalServerError, ...)`, but there is no `return` statement, so control falls through to the session-creation logic just a few lines later, which inserts a new `oidc_sessions` row keyed to the (now empty) email and the previously-computed role: [2](#0-1) 

Because the OIDC role mapping (`IDClaimsToUserRole`) is derived from a *separate* claim (the configured group claim, not `email`), an attacker who controls or influences their own IdP-issued token payload (e.g., a token from a provider that omits `email` for certain accounts, or a token whose `email` claim is non-string/null) can still be assigned a valid RBAC role while the `user_email` column is left as `""`. The gin session cookie is still saved with the created session ID: [3](#0-2) 

Any subsequent request authenticated via `AuthenticateBySession`/`AuthenticateGQL` will resolve this session through `AuthorizedUserWithSession`, returning a `sessions.User{Email: "", Role: <role>}`: [4](#0-3) [5](#0-4) 

This is the same root-cause pattern as Dovecot's bug: an empty/invalid identity field is not rejected outright, so the authentication layer produces a session bound to an ill-defined ("nobody") identity but with a real, usable role. Since downstream authorization only checks the `Role` field on the session-stored user (RBAC gating), the empty-email session is nonetheless treated as authenticated and role-authorized. If any local/legacy row in the `users` table ever has an empty `email` (e.g., a broken import or seed data), subsequent calls like `FindUser(ctx, sessionUser.Email)` in `UserController.UpdatePassword` could resolve to that row, causing cross-identity confusion: [6](#0-5) 

### Impact Explanation
An unprivileged actor with any account on the configured OIDC provider that yields role-qualifying group claims but no (or a non-string) `email` claim ends up with a fully functional, role-scoped chainlink session that is not tied to any accountable identity. This breaks the assumption that every authenticated session maps to a specific email/user, undermining audit logging (the audit log call in this same function uses the same empty `email` value), and creates a path to unauthorized-role access / session anomaly consistent with the "authentication or role bypass" and "cross-user response confusion" categories in scope.

### Likelihood Explanation
Exploitability depends on how easily an attacker can obtain an OIDC ID token lacking the `email` claim from the configured IdP while still belonging to one of the configured role groups — this is plausible for many OIDC providers where `email` is an optional/omittable scope claim or where a service/robot account has no email attribute, so the likelihood is moderate rather than purely theoretical. The missing `return` is a clear, unconditional code-path bug, not a network- or operator-only condition.

### Recommendation
Add an explicit `return` (or otherwise abort request processing) immediately after detecting a missing/invalid `email` claim in `handleTokenExchange`, and reject the token exchange outright rather than continuing to create a session:
```go
email, ok := claims["email"].(string)
if !ok || email == "" {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, consider validating that `email` is non-empty before performing the `INSERT INTO oidc_sessions` and audit-log calls, and add a defense-in-depth check in `AuthorizedUserWithSession`/`FindUser` to refuse empty-email lookups.

### Proof of Concept
1. Configure OIDC auth with a provider/account whose ID token has valid group claims (satisfying `AdminClaim`/`EditClaim`/etc.) but no `email` claim (or `email: null`).
2. Complete the OAuth2 code exchange via `POST /sessions/oidc/exchange` (routes to `handleTokenExchange`).
3. Observe: `claims["email"].(string)` assertion fails (`ok == false`), an error response is written, but execution is not halted.
4. The code proceeds to `IDClaimsToUserRole` (succeeds, using group claims) and inserts a new `oidc_sessions` row with `user_email = ''` and the derived role, then saves the session cookie and returns HTTP 200 with `{"success": true}` (the earlier `c.String` call does not prevent the later `c.JSON` call from also writing to the response).
5. Subsequent authenticated requests using this session cookie succeed via `AuthenticateBySession`, returning a `User{Email: "", Role: <derived role>}` object usable for role-gated API/GraphQL operations. [7](#0-6)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L220-276)
```go
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
		return
	}
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

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

**File:** core/web/auth/auth.go (L52-71)
```go
// AuthenticateBySession authenticates the request by the session cookie.
//
// Implements authMethod
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/web/user_controller.go (L210-224)
```go
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to update password"))
		return
	}
```
