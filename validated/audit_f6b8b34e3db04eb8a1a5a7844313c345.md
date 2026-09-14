Confirmed: this codebase has no `sub`/subject-claim binding anywhere in the OIDC authenticator — identity is anchored solely to the bare `email` claim string extracted from the ID token.

### Title
Session Identity Confusion via Unvalidated Email Claim in OIDC Token Exchange - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The `handleTokenExchange` handler in `core/sessions/oidcauth/oidc.go` establishes an authenticated session by binding solely to the `email` string claim returned in the verified ID token, with no cross-check against a stable subject identifier (`sub`) or any binding between the claimed email and the actual account it is meant to represent. Any identity attested by the configured OIDC provider — including a claim value an end user can influence through provider-side self-service profile fields, or an admin-controlled claims-mapping/IdP configuration — is trusted implicitly as the account identity for the resulting session, mirroring the underlying flaw in CVE-2026-56223 (trusting IdP-asserted email for account resolution without validating that the assertion is authoritative for that identity).

### Finding Description
`handleTokenExchange` verifies the ID token signature via `oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)` [1](#0-0)  and then extracts group claims and the `email` claim directly from the token payload: [2](#0-1) 

The extracted `email` value — not a stable subject/user ID — is used as the sole identity key inserted into `oidc_sessions`, and this same table is later the sole source of truth for `AuthorizedUserWithSession`, which returns a `User{Email, Role}` for any request bearing the resulting session cookie: [3](#0-2) [4](#0-3) 

There is no verification anywhere in `ExtractIDClaimValues` or the surrounding handler that the `email` claim is authoritative, verified/immutable at the IdP, or scoped to a particular tenant/domain — role is derived independently from group claims via `IDClaimsToUserRole`, and email is trusted purely at face value [5](#0-4) . This is architecturally the same root cause as the reported bug class: an externally-controlled identity assertion (email) is used to establish/authorize a session for a specific identity without validating that the asserting party is authoritative for that identity value.

Additionally, the error-handling path on line 226-230 fails to `return` when the `email` claim cannot be extracted as a string, so execution continues past a write of an error status code and proceeds to create a session (with an empty-string email) and issue the success `c.JSON(http.StatusOK, ...)` response regardless, worsening the identity-confusion surface: [6](#0-5) [7](#0-6) 

### Impact Explanation
Since `AuthorizedUserWithSession` and downstream authorization/audit logic key entirely off the `email` string stored at session-creation time [8](#0-7) , any actor who can get the trusted OIDC provider to emit a token where the `email` claim matches a target victim's email (while independently satisfying a role-mapping group claim) is granted a session that the rest of the node treats as belonging to that victim identity — an authentication/identity confusion outcome consistent with the CVE's "merge arbitrary victim accounts based on email match" impact. This affects session-scoped authorization and audit trail integrity within a chainlink node's web server.

### Likelihood Explanation
Exploitability depends on the deployment's OIDC/IdP configuration (e.g., whether the configured IdP allows self-asserted or admin-editable `email` claims, or supports multiple upstream identity sources funneled through one `ProviderURL`/`ClientID`), so this requires some privileged control over IdP-side claims — comparable to the "enterprise org admin + malicious IdP" precondition in the original report, but the code path itself performs no defense-in-depth check (no `sub` pinning, no domain allowlist) that would otherwise mitigate a misconfigured or compromised IdP.

### Recommendation
Bind sessions to the immutable `sub` claim (and provider issuer) rather than the mutable `email` claim; store/compare a `(iss, sub)` tuple as the canonical session identity and treat `email` purely as a display attribute. Add explicit validation that the `email` claim domain is authorized for the configured tenant/provider before creating or updating any session or user record. Ensure the missing `return` after the email-extraction failure branch is added to prevent continued processing with an invalid claim.

### Proof of Concept
1. Configure a chainlink node with OIDC auth pointed at an IdP under attacker/admin control (or exploit an IdP misconfiguration allowing arbitrary claim values).
2. Log in as a low-privileged OIDC user, but have the IdP issue an ID token with `email` set to a victim's email address and group claims mapped to `AdminClaim`.
3. Complete `/oidc-exchange`; the resulting `oidc_sessions` row is created with `user_email = victim_email`, `user_role = admin` [3](#0-2) .
4. All subsequent authorized requests using the returned session cookie resolve via `AuthorizedUserWithSession` to the victim's email/admin role, producing session/identity confusion without any check that the asserting IdP/session-creator is authoritative for that email.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L206-212)
```go
	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L220-230)
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

**File:** core/sessions/oidcauth/oidc.go (L271-276)
```go
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
