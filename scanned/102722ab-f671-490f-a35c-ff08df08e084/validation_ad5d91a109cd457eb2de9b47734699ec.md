This confirms the vulnerability pattern. The Chainlink OIDC authenticator binds the entire authorization/session lifecycle to the `email` claim extracted from the ID token rather than the stable `sub` claim — exactly the bug class described in the django-allauth advisory (using a mutable identifier for authorization decisions instead of `sub`).

### Title
OIDC authenticator binds session identity and role solely to the mutable `email` claim instead of the immutable `sub` claim - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
The `oidcAuthenticator.handleTokenExchange` handler extracts the `email` claim from the verified ID token and uses it as the sole identity key to create and persist the user's session, role, and later API-token bindings. It never reads or pins the OIDC `sub` claim (the provider-guaranteed immutable subject identifier). This mirrors CVE-2025-65431/GHSA-8m3c-c723-h4p4, where Okta/NetIQ allauth providers used `preferred_username` (mutable) instead of `sub` for authorization decisions.

### Finding Description
In `handleTokenExchange`, after verifying the ID token signature, the code reads `email` directly out of the claims map and uses it, unqualified by `sub`, as the durable identity key for the whole authorization/session subsystem: [1](#0-0) 

That `email` is then persisted as the primary key of the new session row, tying the session's role directly to whatever `email` value the IdP returned this time: [2](#0-1) 

Session validation (`AuthorizedUserWithSession`) subsequently looks up `user_email`/`user_role` purely by session ID with no secondary binding to `sub`: [3](#0-2) 

The same `email`-only identity is reused for API token issuance/deletion (`SetAuthToken`, `DeleteAuthToken`) and for clearing "other" sessions belonging to the same identity (`ClearNonCurrentSessions`): [4](#0-3) [5](#0-4) 

`email` is a self-service, provider-mutable attribute at most IdPs (including Okta, NetIQ/eDirectory-backed IdPs, Azure AD, Google Workspace, etc.) — a user (or an admin under delegated self-service email change) can change it. The OIDC `sub` claim is defined by the OIDC spec to be a stable, non-reassignable identifier scoped to the issuer/client, and is exactly the field the referenced advisory says providers should use for authorization decisions instead of mutable attributes. Chainlink's OIDC module never validates or persists `sub` at all — there is no code path in `core/sessions/oidcauth/oidc.go` that reads `claims["sub"]`.

### Impact Explanation
Because `email` is treated as the durable authorization key end-to-end (session table, API-token table, "clear other sessions" logic, audit logging), any user who can get their IdP-registered `email` claim changed to match another user's email (even temporarily, or through an IdP account recycling/rename flow) will be issued a Chainlink session/API token keyed to that email string. Combined with `oidcAuth`'s own `ClearNonCurrentSessions`/`DeleteAuthToken`/`SetAuthToken` queries which act on all rows matching that `user_email`, this creates cross-user session and API-token confusion/takeover potential and disrupts audit-log integrity (the audit trail records only the `email` string, not a stable subject). This is an authentication/identity-binding weakness reachable by any unprivileged user who authenticates through the OIDC login flow — it does not require insider or operator privileges.

### Likelihood Explanation
Exploitability depends on an external factor (the ability to change one's own or another account's `email` attribute at the configured upstream IdP), which is plausible for many enterprise IdP configurations (self-service profile email updates, employee rehire/email-reuse policies, or admin-driven email reassignment) — the exact real-world scenario the referenced advisory addresses. The vulnerable code path (`handleTokenExchange`) is reachable directly from the unauthenticated `/signin` OIDC callback with no additional privilege required.

### Recommendation
Extract and persist the OIDC `sub` claim (scoped by issuer/client) as the primary, immutable identity key for `oidc_sessions` and `oidc_user_api_tokens`, using `email` only as a display/audit attribute, not as an authorization key. Update `handleTokenExchange`, `AuthorizedUserWithSession`, `SetAuthToken`, `DeleteAuthToken`, and `ClearNonCurrentSessions` to key off `sub` (or a `(issuer, sub)` composite) instead of `user_email`.

### Proof of Concept
1. Configure Chainlink with `WebServer.AuthenticationMethod = "oidc"` pointing at an IdP that permits a user to change their own registered email (e.g., self-service profile update), per `core/config/docs/core.toml` OIDC settings.
2. As User A (attacker, low-privileged OIDC group membership), log in via `/signin` → `oi.handleSignIn` → callback → `oi.handleTokenExchange`, which creates an `oidc_sessions` row keyed on `user_email = attacker@example.com` at [6](#0-5) .
3. At the IdP, change User A's `email` attribute to `victim-admin@example.com` (the address of a genuine local admin/target user known from the `users` table or a previous higher-privileged session).
4. Log in again through `/signin`; `handleTokenExchange` again reads `claims["email"]` (now `victim-admin@example.com`) and inserts/updates records in `oidc_sessions`/`oidc_user_api_tokens` under that email, with the role derived from Attacker's own current OIDC group claims via `IDClaimsToUserRole`.
5. Because `ClearNonCurrentSessions`, `SetAuthToken`, and `DeleteAuthToken` all operate purely on `user_email` matches, the attacker's new session/API token now collides with, invalidates, or is indistinguishable from the real victim's identity records — with no `sub`-based check ever performed to detect the identity swap.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-262)
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

**File:** core/sessions/oidcauth/oidc.go (L510-547)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (oi *oidcAuthenticator) SetAuthToken(ctx context.Context, user *clsessions.User, token *auth.Token) error {
	if !oi.config.UserAPITokenEnabled() {
		return errors.New("API token is not enabled ")
	}

	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return fmt.Errorf("OIDCAuth SetAuthToken hashed secret error: %w", err)
	}

	err = sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Remove any existing API tokens
		if _, err = oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE user_email = $1", user.Email); err != nil {
			return fmt.Errorf("error executing DELETE FROM oidc_user_api_tokens: %w", err)
		}
		// Create new API token for user
		_, err = oi.ds.ExecContext(ctx,
			"INSERT INTO oidc_user_api_tokens (user_email, user_role, token_key, token_salt, token_hashed_secret, created_at) VALUES ($1, $2, $3, $4, $5, $6, now())",
			user.Email,
			user.Role,
			token.AccessKey,
			salt,
			hashedSecret,
		)
		if err != nil {
			return fmt.Errorf("failed insert into oidc_user_api_tokens: %w", err)
		}
		return nil
	})
	if err != nil {
		oi.lggr.Errorf("error creating API token: %v", err)
		return errors.New("error creating API token")
	}

	oi.auditLogger.Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	return nil
```
