### Title
Local password login bypasses OIDC group-claim role authority, allowing stale/unauthorized RBAC role grants - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The `neptune-mutual` finding describes two independent mechanisms that grant the same privilege (`AccessControl` roles) with inconsistent enforcement: an intended, checked path and an unchecked "bypass" path. Chainlink's OIDC authentication provider exhibits the same class of bug: when `AuthenticationMethod = 'oidc'` is configured, the intended, sole mechanism for computing a user's RBAC role is meant to be the identity provider's group claims (`AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim`), verified on every login via `handleTokenExchange`/`IDClaimsToUserRole`. However, `CreateSession` provides a parallel path — `localLoginFallback` — that authenticates against the local `users` table password hash and assigns whatever role is stored in that row, entirely bypassing the OIDC group-claim verification that the deployment is relying on for access control.

### Finding Description
`oidcAuthenticator.CreateSession` is the entrypoint used by the standard `/sessions` login endpoint (unauthenticated, credential-based) when `AuthenticationMethod` is `oidc`: [1](#0-0) 

It unconditionally calls `localLoginFallback`, which checks the request's email/password against the local `users` table and returns that row's stored `Role` verbatim: [2](#0-1) 

This is architecturally parallel to — and inconsistent with — the "real" OIDC-driven role assignment path, `handleTokenExchange`, which derives the role strictly from IdP-attested group claims via `IDClaimsToUserRole`: [3](#0-2) [4](#0-3) 

Both paths write to the same `oidc_sessions` table and produce equally-privileged sessions, but only one of them is gated by the deployment's actual RBAC source of truth (the IdP). The local `users.role` column is not kept in sync with (nor derived from) IdP group membership — it is a separate, independently-writable value (e.g., set at initial node bootstrap, or left over from before OIDC was enabled). Because `oidcAuthenticator.UpdateRole` explicitly returns `ErrNotSupported` for OIDC deployments, operators have no first-class way to manage or audit this local role field once OIDC is the configured provider, yet it remains fully authoritative for anyone who can present valid local credentials: [5](#0-4) 

This mirrors the audit finding precisely: a "new" access-control mechanism (IdP group-claim based RBAC) was layered on top of an existing one (local password/role authentication) without reconciling them, so the old mechanism can be used to obtain access/roles that the new mechanism's constraints (current IdP group membership) would deny.

### Impact Explanation
If IdP group membership for a user is revoked or downgraded (the expected control point for an OIDC-governed deployment — e.g., offboarding, role demotion), that user's local `users` table row is unaffected. As long as their local password remains valid (it is never invalidated by IdP changes), they can continue to authenticate via `localLoginFallback` and be granted their old (possibly `admin`) role, completely bypassing the IdP-side revocation the operator believed was authoritative. This is a role/authentication-bypass matching the "concrete authentication or role bypass" acceptance criterion: an actor who should no longer hold a privileged role (per the intended RBAC control) can still obtain a fully privileged session and admin-only API access (`RequiresAdminRole`-gated routes such as user management, ETH key export, transfers, etc.).

### Likelihood Explanation
Likelihood depends on operational conditions rather than a network-based exploit: it requires that (a) OIDC is configured as `AuthenticationMethod`, and (b) a local `users` row with a stale/undesired role and a still-valid password exists (e.g., the bootstrap admin created before OIDC rollout, or a user whose local password was never rotated when moved to IdP-only access). This is a realistic operational scenario for node operators who adopt OIDC to centralize access revocation, since the code gives them no visibility or built-in mechanism (`UpdateRole` is disabled) to manage the local table once OIDC is enabled.

### Recommendation
- Disable or explicitly gate `localLoginFallback` when `AuthenticationMethod = 'oidc'`, e.g., only allow it for a single, clearly documented bootstrap/break-glass account, not any row in `users`.
- If local login must remain supported, derive the session role from the same authority (or explicitly mark local-fallback sessions with a maximally-restricted role) rather than trusting the stored `users.role` column, and provide an admin-visible/audited way to manage or disable local credentials while OIDC is active.
- Ensure `UpdateRole`/user management surfaces this dual-authority risk instead of silently returning `ErrNotSupported`, so operators are not misled into believing IdP group management is the sole control.

### Proof of Concept
1. Deploy a Chainlink node with `WebServer.AuthenticationMethod = 'oidc'` and a local admin user created during initial setup (`users` table row, `role='admin'`).
2. Configure the OIDC IdP and later remove the operator from the `NodeAdmins` (or equivalent) IdP group to revoke admin access, per the intended access-control model.
3. The operator's local password (in the `users` table) is untouched by this IdP change.
4. POST to the standard `/sessions` login endpoint with the operator's email/password; `oidcAuthenticator.CreateSession` → `localLoginFallback` succeeds and issues a new `oidc_sessions` row with `role = 'admin'` sourced from the stale local `users` row, granting a fully privileged session despite the IdP-side revocation. [6](#0-5)

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L409-439)
```go
// CreateSession in the context of the OIDC driver handles only the local auth admin user, exposed by the default endpoint defined in the router. To initiate the SAML/OIDC
// flow, a separate /oidc-login route is defined which handles the redirect to the
// configured provider
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)

	// Save local admin session, user, and role to sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	session := clsessions.NewSession()
	_, err = oi.ds.ExecContext(ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		return "", fmt.Errorf("error creating local OIDC session: %w", err)
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L456-459)
```go
// UpdateRole is not supported for read only OIDC
func (oi *oidcAuthenticator) UpdateRole(ctx context.Context, email string, newRole string) (clsessions.User, error) {
	return clsessions.User{}, clsessions.ErrNotSupported
}
```

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L599-618)
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
}
```
