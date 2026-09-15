### Title
Missing `return` after failed email-claim extraction in OIDC token exchange allows session creation to proceed despite unverified/missing email - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
`oidcAuthenticator.handleTokenExchange` extracts the authenticated user's email from OIDC claims via a type assertion. When the assertion fails, the handler logs an error and writes an HTTP 500 response body, but — unlike every other failure branch in the same function — it does **not** `return`. Execution falls through and continues to map the user's role, insert a new row into `oidc_sessions`, set the session cookie, and finally overwrite the response with an HTTP 200 success JSON body. This mirrors the root cause of the reported ERC20 issue: a "success/failure" signal (`ok`) is checked, logged, but not actually enforced, so the failure path is treated as if it succeeded.

### Finding Description
In `core/sessions/oidcauth/oidc.go`, `handleTokenExchange` is the internet-facing handler backing the OIDC login callback (`/oidc-login`/token-exchange endpoint), reachable by any client attempting SSO login: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

Every other error branch in this function returns immediately after writing an error response (see the `ShouldBindJSON`, state-mismatch, `Exchange`, `id_token` missing, `Verify`, `Claims`, and `ExtractIDClaimValues` checks), but this branch is missing the `return` statement. As a result, when the verified ID token's claims map lacks an `"email"` field — which is common for OIDC providers that don't include email by default, or for group/role-only claim configurations — execution proceeds with `email == ""` into role mapping and session persistence: [2](#0-1) 

The role is derived independently from `idClaims` (group claims), so a legitimate, successfully-authenticated OIDC user whose IdP response simply omits the `email` claim — but whose group claims map to `AdminClaim`/`EditClaim`/etc. — will still have `IDClaimsToUserRole` succeed. The code then inserts a row into `oidc_sessions` with `user_email = ""` and the resolved role, sets the session cookie via `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()`, and finally overwrites the earlier 500 status with a 200 success JSON response.

Downstream, `AuthorizedUserWithSession` will authenticate this session and return a `clsessions.User{Email: "", Role: <mapped role>}`, which is then set into the gin context and used to authorize subsequent API calls: [3](#0-2) 

### Impact Explanation
- A user completes a valid OIDC login handshake (real signed ID token from the configured provider) but the response has no `email` claim (very common for providers unless email scope/claim is deliberately requested or IdP is misconfigured). The handler still creates and activates a fully authenticated node API session for that user, with whatever role their OIDC groups map to (including Admin), rather than rejecting the login.
- Any node API endpoint gated by `AuthenticateBySession`/`AuthorizedUserWithSession` will accept this session as legitimate, i.e., role/permission checks for node API endpoints are satisfied despite the identity (email) verification step failing — an authentication logic bypass in the sense that a required validation is skipped without aborting the login flow.
- All users hitting this defect share `user_email = ""` in `oidc_sessions`, so `ClearNonCurrentSessions` (`DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2`) executed for one such user's session ID will delete *every other* user's empty-email session rows, causing unrelated users to be logged out — a cross-user session-management confusion caused by the same root defect.

### Likelihood Explanation
Any unprivileged party able to complete the standard OIDC redirect/exchange flow against the configured IdP can trigger this if the IdP's ID token claims omit `email` (default behavior for many providers unless the `email` scope/claim is explicitly requested and granted) — this does not require a malicious or compromised IdP, network-layer, or operator-only access. The bug is purely a missing `return`, so it is deterministic once the claims lack `email`.

### Recommendation
Add a `return` immediately after writing the error response in the `!ok` branch (matching every other error branch in the function):
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, consider rejecting logins where `email == ""` before creating/persisting the `oidc_sessions` row, to avoid multiple distinct users ever sharing the same session-table key.

### Proof of Concept
1. Configure Chainlink OIDC auth against an IdP/test provider that returns a validly-signed ID token whose claims include the configured group claim (e.g. satisfying `AdminClaim()`) but do **not** include an `"email"` key.
2. As an unprivileged client, initiate `/oidc-login`, complete the provider redirect, and call the token exchange endpoint (`handleTokenExchange`) with the resulting `code`/`state`.
3. Observe that despite `claims["email"].(string)` failing (`ok == false`) and a 500 body being written, execution continues: `IDClaimsToUserRole` succeeds (based on group claims only), a row is inserted into `oidc_sessions` with `user_email = ''` and the mapped role, `ginSession.Save()` persists a valid session cookie, and the final response is `200 OK` with `{"success": true}`.
4. Using the returned session cookie, call any node API endpoint gated by `AuthenticateBySession` — it will authorize as the mapped role (e.g., Admin) despite the missing/unverified email identity.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-231)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

**File:** core/sessions/oidcauth/oidc.go (L233-262)
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
