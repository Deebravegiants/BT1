Audit Report

## Title
OIDC Token Exchange Grants Authenticated Session Despite Missing Identity Claim, Bypassing Intended Rejection - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `handleTokenExchange`, when the OIDC ID token's `email` claim is missing or not a string, the handler logs the error and writes an HTTP 500 via `c.String(...)` but omits the `return` statement present in every other failure branch of this function. Execution falls through, computes an RBAC role from the `groups`/ID claims, inserts a new `oidc_sessions` row with `user_email = ""`, and sets a valid session cookie — producing a fully functional authenticated session with an assigned role but no identity.

## Finding Description
`handleTokenExchange` validates state, exchanges the code for a token, verifies the ID token, and extracts claims, each step correctly returning on failure. The email-claim check at [1](#0-0)  is the sole exception — it logs the error and calls `c.String(http.StatusInternalServerError, "Failed to get email from claims")` but does not `return`. Execution continues to map the role via `IDClaimsToUserRole` [2](#0-1) , insert an `oidc_sessions` row with a lowercased empty `user_email` and the resolved role [3](#0-2) , and persist the session cookie via `ginSession.Save()` [4](#0-3) .

Downstream, `AuthorizedUserWithSession` reconstructs `clsessions.User{Email, Role}` directly from the DB row with no check that `Email` is non-empty [5](#0-4) . RBAC gates in `core/web/auth/auth.go` (`RequiresRunRole`, `RequiresEditRole`, `RequiresAdminRole`) check only `user.Role`, never `user.Email` [6](#0-5) , so the resulting session functions with full privileges of whatever role was derived from group claims, despite lacking an identity.

## Impact Explanation
This is an authentication/fail-open defect: a session that should be rejected due to an incomplete claim set is instead persisted as valid and authorized, potentially with an Admin role, while carrying no email identity, also corrupting audit trail attribution since `audit.AuthLoginSuccessNo2FA` is logged with `email=""`. This maps to the in-scope "node API authentication or role bypass" impact category.

## Likelihood Explanation
Exploitation requires the operator to have `WebServer.AuthenticationMethod = 'oidc'` configured with an identity provider whose tokens can lack an `email` claim (or return it non-string) while still supplying a `groups`/ID claim mapping to a role. This is a provider/claims-configuration dependent scenario rather than something purely triggerable by an anonymous, credential-less external attacker; the "attacker" must be a user who can complete a valid OIDC login against the deployment's own configured IdP. That said, the defect itself is a genuine code-level fail-open bug, not merely a misconfiguration — the missing `return` is exploitable identically to any operator running an OIDC IdP that omits the email scope/claim for some users (a realistic and common IdP scope variation), so it is not purely a hypothetical/operator-error case.

## Recommendation
Add `return` immediately after `c.String(http.StatusInternalServerError, "Failed to get email from claims")` at `core/sessions/oidcauth/oidc.go:229` so the handler aborts when the `email` claim is missing or invalid. Additionally, reject empty-string `email` explicitly before persisting the `oidc_sessions` row, and add a defense-in-depth check in `AuthorizedUserWithSession` to reject sessions with an empty `UserEmail`.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'oidc'` with a provider whose ID tokens include a `groups` claim (e.g., `NodeAdmins`) but omit the `email` claim.
2. As a user authenticated by that provider, `POST /oidc-exchange` with a valid `code`/`state`.
3. In `handleTokenExchange`, `claims["email"].(string)` fails at lines 226-230; the missing `return` allows execution to continue.
4. `IDClaimsToUserRole` resolves role `UserRoleAdmin` from the `groups` claim (lines 233-245).
5. A row is inserted into `oidc_sessions` with `user_email = ''`, `user_role = 'admin'`, and the session cookie is set (lines 247-271).
6. Subsequent requests with that cookie pass `AuthenticateBySession` → `AuthorizedUserWithSession` → `RequiresAdminRole`, granting full admin API access with an empty identity.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
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

**File:** core/sessions/oidcauth/oidc.go (L264-271)
```go
	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
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

**File:** core/web/auth/auth.go (L198-252)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
```
