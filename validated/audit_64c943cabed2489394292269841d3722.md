Confirmed: there is no `email_verified` check anywhere in the OIDC/Auth0-style login flow of this codebase.

### Title
Authentication Bypass via Unverified Email Claim in OIDC Login Session Creation - (File: core/sessions/oidcauth/oidc.go)

### Summary
The `oidcAuthenticator.handleTokenExchange` handler completes the OIDC/OAuth2 login flow by extracting the `email` claim directly from the verified ID token and using it, unconditionally, as the durable identity key for creating a new authenticated session and mapping it to a role. No check of the standard `email_verified` claim is performed anywhere in the flow.

### Finding Description
In `core/sessions/oidcauth/oidc.go`, `handleTokenExchange` verifies the ID token's signature via `oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)` and then parses the claims map, pulling `email` straight out: [1](#0-0) . This `email` string is then lower-cased and written directly into `oidc_sessions.user_email`, which becomes the durable identity used for all subsequent authorization lookups: [2](#0-1) .

There is no check of the `email_verified` claim (or equivalent) at any point in this code path — a `grep` for `email_verified`/`EmailVerified` across the repository returns no matches. Just as with the `Auth0OAuthenticator` bug in `oauthenticator`, identity-provider tenants (including Auth0-backed OIDC providers) generally treat `email_verified` as a soft user-profile flag rather than a hard gate on issuing signed ID tokens: an attacker can self-register an account with an identity provider using an existing victim's email address, obtain a validly-signed ID token containing that unverified email, and complete this handler's flow.

This session's role is derived independently from group claims via `IDClaimsToUserRole` [3](#0-2) , but the `user_email` value stored in `oidc_sessions` is what `AuthorizedUserWithSession` [4](#0-3)  and `FindUser`/`ClearNonCurrentSessions` [5](#0-4)  rely on to identify "who" the session belongs to for audit logging and API surface identity (e.g. `audit.AuthLoginSuccessNo2FA` records `{"email": email}` at line 262). If a node operator's RBAC/audit tooling or any downstream consumer correlates identity by this email (e.g., matching it against the local `users` table via `SQLSelectUserbyEmail`, used elsewhere for local-admin fallback), an attacker-controlled unverified email enables identity/account confusion analogous to the Auth0OAuthenticator advisory: an attacker registers with the IdP using `victim@company.com` (unverified), authenticates, and the resulting session is permanently tagged and audited as `victim@company.com`.

### Impact Explanation
This is a High-severity class of bug (CWE-287/CWE-290: authentication bypass via alternate identity/spoofing) because the impersonated identity (email) is used as the primary key for session identity and audit trail. Any deployment where the configured OIDC/Auth0 identity provider does not hard-enforce email verification prior to token issuance allows an unprivileged external attacker to impersonate an existing chainlink node user's email in the `oidc_sessions` table and audit logs, without needing any prior credential or privilege on the chainlink node itself.

### Likelihood Explanation
Likelihood depends on the external IdP configuration (same caveat as the original advisory) — a IdP that allows self-registration and does not block sign-in until email verification (Auth0's documented default behavior) is sufficient to trigger this. Since group/role claims (Admin/Edit/Run/Read) are separately validated, the practical impact is scoped mainly to identity/audit spoofing rather than an automatic privilege escalation to Admin — but the underlying root cause (no `email_verified` gate before persisting/trusting the `email` claim) mirrors the reported bug class exactly.

### Recommendation
In `handleTokenExchange` (`core/sessions/oidcauth/oidc.go`), before extracting and persisting `email` (around line 226), check that `claims["email_verified"]` is `true`; reject the exchange with an error otherwise. Consider documenting this operational requirement in the `WebServer.OIDC` config docs as well, since operators may otherwise assume any successfully verified ID token implies a verified email address.

### Proof of Concept
1. Configure `WebServer.OIDC` pointing to an Auth0 (or other) tenant that allows self-registration without mandatory email verification.
2. As an attacker, register an account with the IdP using the email address of an existing chainlink node operator (e.g., `victim@company.com`), leaving it unverified.
3. Complete the OIDC login flow against the chainlink node (`/oidc-login` → callback → `handleTokenExchange`).
4. The ID token is cryptographically valid (signed by the IdP) and passes `Verify()`, and the unverified `email` claim is extracted at [1](#0-0)  and written to `oidc_sessions` as `victim@company.com` at [6](#0-5) , with no `email_verified` check performed anywhere in the code path.

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

**File:** core/sessions/oidcauth/oidc.go (L279-295)
```go
func (oi *oidcAuthenticator) FindUser(ctx context.Context, email string) (clsessions.User, error) {
	email = strings.ToLower(email)

	var foundUser clsessions.User

	if err := oi.ds.GetContext(ctx, &foundUser, SQLSelectUserbyEmail, email); err != nil {
		// If the error is not that no local user was found, log and exit
		if errors.Is(err, sql.ErrNoRows) {
			return clsessions.User{}, errors.New("user not found")
		}

		oi.lggr.Errorf("error searching users table: %v", err)
		return clsessions.User{}, errors.New("error finding user")
	}

	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L351-391)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L599-617)
```go
func (oi *oidcAuthenticator) IDClaimsToUserRole(idClaims []string, adminClaim string, editClaim string, runClaim string, readClaim string) (clsessions.UserRole, error) {
	// If defined Admin group name is present in id claims, return UserRoleAdmin
	if slices.Contains(idClaims, adminClaim) {
		return clsessions.UserRoleAdmin, nil
	}
	// Check edit role
	if slices.Contains(idClaims, editClaim) {
		return clsessions.UserRoleEdit, nil
	}
	// Check run role
	if slices.Contains(idClaims, runClaim) {
		return clsessions.UserRoleRun, nil
	}
	// Check view role
	if slices.Contains(idClaims, readClaim) {
		return clsessions.UserRoleView, nil
	}
	// No role group found, error
	return clsessions.UserRoleView, ErrUserNoOIDCGroups
```
