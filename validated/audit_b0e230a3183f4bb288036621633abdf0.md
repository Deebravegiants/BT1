## Title
OIDC Login Trusts Unverified Email Claims and Creates Sessions Without Validating the `email` Assertion - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
`handleTokenExchange` in the OIDC authentication provider accepts the `email` claim returned by the identity provider's ID token and binds it directly to a newly created, fully-privileged Chainlink session — with no verification that the identity provider actually confirmed ownership of that email address (no `email_verified` check anywhere in the codebase), and with a missing early-`return` on the one guard that does exist. This mirrors the root cause of CVE-2019-5486: GitLab trusted an SSO provider's identity assertion without enforcing the same verification/domain restrictions applied to other login paths, letting an attacker assume an account identity that bypassed intended checks.

### Finding Description
In `handleTokenExchange`, after verifying the ID token signature, the code extracts the `email` claim with a bare type assertion and does **not** return on failure: [1](#0-0) 

If `claims["email"]` is missing or not a string, the handler logs an error and writes an HTTP 500 body via `c.String(...)`, but execution **continues** (no `return`) — the empty `email` value is then used to create a real, valid `oidc_sessions` row and set the session cookie: [2](#0-1) 

Separately — and more fundamentally — the role granted to the session (`IDClaimsToUserRole`) is derived purely from group claims, and the `email` value used to identify/attribute the session is taken from the IdP's `email` claim with **no verification** that the IdP confirmed the address (no `email_verified` check exists anywhere in the repository). Any OIDC provider or account that can present an arbitrary `email` field (self-asserted profile field, unverified secondary/alias email, or app-defined claim source) is accepted as the authoritative account identity: [3](#0-2) 

This identity is not cosmetic — several privileged REST/GraphQL mutations resolve the *local* admin user by trusting `session.User.Email` from the authenticated session and use it for audit attribution and lookups: [4](#0-3) [5](#0-4) 

Because the email binding step has no ownership/verification guard (and can even be left blank due to the missing `return`), the OIDC flow can produce an authenticated session whose `user_email` field does not truthfully represent a verified identity — the same class of bypass as GitLab's Salesforce SSO flaw, where an unprivileged actor could complete SSO login while skipping the verification checks other paths enforced.

### Impact Explanation
An attacker who can complete the OIDC handshake (i.e., an account on the configured identity provider, which need not be privileged in Chainlink) can obtain a valid, role-bearing `oidc_sessions` entry keyed to an email value that was never verified as belonging to them — including an empty string in the missing-claim case. Downstream code trusts this email for audit-log attribution (`audit.AuthLoginSuccessNo2FA`) and as the lookup key in sensitive mutations (`UpdateUserPassword`, `CreateAPIToken`, `NewAPIToken`, `DeleteAPIToken`), creating cross-user identity/audit confusion and a foothold for account-identity spoofing consistent with an authentication-bypass class vulnerability.

### Likelihood Explanation
Exploitability depends on the configured OIDC provider's behavior (whether it will emit an `email` claim that isn't verified, or omit it), but the Chainlink code itself provides no defense-in-depth: there is no `email_verified` check, no server-side canonicalization/whitelist, and a genuine control-flow bug (missing `return`) that lets processing continue past a claim-extraction failure. This makes the issue reachable with a misconfigured or permissive upstream IdP, or in provider integrations where the `email` claim is user-editable.

### Recommendation
1. Require and check the `email_verified` claim (must be `true`) from the OIDC token before trusting `email` for session binding.
2. Add the missing `return` after the failed `email` claim assertion in `handleTokenExchange` (`core/sessions/oidcauth/oidc.go:226-230`) so an unverifiable identity never proceeds to session creation.
3. Reject session creation entirely if `email` is empty or unverified, rather than logging and continuing.

### Proof of Concept
1. Configure (or compromise) an OIDC identity provider that returns an ID token containing a group claim mapping to `AdminClaim`/`EditClaim` and an `email` claim equal to an existing local Chainlink admin's email address, without `email_verified: true`.
2. Complete `/oidc-login` → `/oidc-exchange` as this account.
3. `handleTokenExchange` inserts a row into `oidc_sessions` with `user_email = <target's email>` and the role derived from group claims, and sets `SessionIDKey` on the cookie — with no check that the IdP actually verified the email.
4. Subsequent GraphQL calls (e.g., `updateUserPassword`) resolve `FindUser(ctx, session.User.Email)` using this attacker-controlled email, producing audit log entries and behaviors attributed to the victim's account identity.

### Citations

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

**File:** core/web/resolver/mutation.go (L990-1005)
```go
func (r *Resolver) CreateAPIToken(ctx context.Context, args struct {
	Input struct{ Password string }
}) (*CreateAPITokenPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	session, ok := webauth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return nil, errors.New("Failed to obtain current user from context")
	}
	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

```

**File:** core/web/user_controller.go (L122-131)
```go
	// Don't allow current admin user to edit self
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	if strings.EqualFold(sessionUser.Email, request.Email) {
		jsonAPIError(c, http.StatusBadRequest, errors.New("can not change state or permissions of current admin user"))
		return
	}
```
