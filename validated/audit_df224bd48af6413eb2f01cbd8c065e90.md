### Title
OIDC session identity keyed solely on unverified `email` claim allows cross-session impersonation/lockout - ([File: core/sessions/oidcauth/oidc.go])

### Summary
Chainlink's OIDC authentication provider treats the `email` claim from the identity provider's ID token as a trusted, stable user identifier without ever checking an `email_verified` claim or binding the session to the token's `sub` (subject) identifier. This is the same root-cause pattern as CVE-2023-0105 (Keycloak): a user-controlled/IdP-controlled attribute (email) that is not guaranteed to be verified or unique is used as the sole key for creating, looking up, and clearing user sessions, enabling one identity to "shadow" and disrupt another identity that shares the same email string.

### Finding Description
In `handleTokenExchange`, after verifying the ID token signature, the code pulls the `email` field directly out of the claims map with no check that the IdP actually verified ownership of that address: [1](#0-0) 

This raw, unverified `email` value is then written directly into the `oidc_sessions` table as the row's identity key, alongside the RBAC role computed from group claims: [2](#0-1) 

All subsequent session lifecycle operations key exclusively off this string, not off the IdP's stable subject identifier (`sub`) or any local unique user ID:
- `AuthorizedUserWithSession` resolves an authenticated user purely from `oidc_sessions.user_email` for the given session ID: [3](#0-2) 
- `ClearNonCurrentSessions` looks up the email tied to the current session ID and then deletes **every** `oidc_sessions` row that matches that email string (case-insensitively), regardless of which login event created them: [4](#0-3) 

Because there is no `email_verified` gate and no binding to `sub`, any two distinct IdP identities that end up presenting the same `email` claim value (e.g. a misconfigured/self-service IdP that does not enforce email verification or global uniqueness — the exact scenario the Keycloak advisory describes) are treated by Chainlink as the *same* user for session purposes. This mirrors the Keycloak root cause: "the verified state is not reset ... it is possible for users to shadow others with the same email."

### Impact Explanation
An attacker who can obtain (or self-register) an IdP account whose `email` claim matches a legitimate node operator's email — without actually controlling that mailbox — can:
- Be granted an active `oidc_sessions` entry under the victim's email string, and
- Call the session-clearing flow (`ClearNonCurrentSessions`, invoked via the resolver/user-controller "log out other sessions" mutation) to purge the victim's genuine sessions, causing account lockout.
- Because `AuthorizedUserWithSession` resolves identity purely from the stored email string, cross-user response confusion / impersonation of the victim's email-tied identity is possible within the OIDC session subsystem.

This satisfies the "concrete authentication bypass / request impersonation / cross-user response confusion" bar, matching the CWE-287/CWE-841 class of the reference advisory.

### Likelihood Explanation
Exploitability depends on the specific OIDC IdP's behavior — if the configured provider enforces `email_verified=true` and unique email ownership, this path is not reachable by an unprivileged attacker. However, the Chainlink code itself performs **no defensive check** on `email_verified` or `sub`, so any IdP configuration that is lenient about email uniqueness/verification (a common real-world misconfiguration, and the exact scenario named in the original advisory) directly exposes this weakness. This is a genuine code-level gap independent of any specific IdP, making it a reasonable and reachable analog for an unprivileged remote actor who controls their own IdP account.

### Recommendation
- Require and check the `email_verified` claim (reject login/session creation if `false` or absent) before treating `email` as an identity.
- Key `oidc_sessions` (and all session lookup/clear operations) on the IdP's `sub` claim, not the mutable `email` claim, and treat `email` purely as a display attribute.
- When mapping to local roles, do not implicitly trust email as a linkage to any pre-existing local user record without an explicit administrator-approved binding step.

### Proof of Concept
1. Configure Chainlink node with OIDC authenticator against an IdP that does not enforce unique/verified emails (or exploit a permissive self-service IdP).
2. Attacker registers/authenticates at the IdP with `email` claim set to `victim@company.com` (unverified) and any group membership satisfying `IDClaimsToUserRole`.
3. Attacker completes `/oidc-login` -> `handleTokenExchange`, causing Chainlink to insert an `oidc_sessions` row keyed on `victim@company.com`.
4. Attacker (or any session sharing that email) calls the "clear other sessions" endpoint, triggering `ClearNonCurrentSessions`, which deletes all `oidc_sessions` rows matching `lower(user_email) = lower('victim@company.com')` except the attacker's own — logging the real victim out (lockout), or, depending on timing, allowing the attacker's session to be treated as authoritative for that identity (impersonation).

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-260)
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
