### Title
Missing `return` after failed OIDC email-claim extraction lets `handleTokenExchange` create an authenticated session with an unverified/empty email — (File: `core/sessions/oidcauth/oidc.go`)

### Summary
The reported JoJo issue is about an ignored `IERC20.approve` return value, i.e. a check whose result is silently discarded so execution proceeds as if it had succeeded. The closest reachable analog in this chainlink repo is not a `bool`-return-ignored call, but the same root-cause pattern of "check performed, failure logged, but execution is NOT halted": in `oidcAuthenticator.handleTokenExchange`, the `ok` result of extracting `email` from the OIDC ID-token claims is checked, an error is logged and an HTTP 500 body is written, but the handler does not `return`, so it falls through and creates/persists an authenticated session anyway.

### Finding Description
`handleTokenExchange` is the public callback endpoint used by an unauthenticated client to complete the OIDC login flow (`/oidc-token-exchange` style route, reachable pre-authentication) [1](#0-0) .

After exchanging the authorization code and verifying the ID token, the handler extracts the `email` claim:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
``` [2](#0-1) 

There is no `return` statement after the `c.String(...)` call in the `!ok` branch. Execution therefore continues into the role-mapping and session-creation logic using the zero-value `email` (an empty string):
```go
role, err := oi.IDClaimsToUserRole(...)
...
clSession := clsessions.NewSession()
_, err = oi.ds.ExecContext(ctx,
    "INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
    clSession.ID, strings.ToLower(email), role,
)
...
ginSession.Set(webauth.SessionIDKey, clSession.ID)
err = ginSession.Save()
...
c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})
``` [3](#0-2) 

This means a token exchange whose ID token lacks a valid/string `email` claim (but otherwise passes group/role claim checks) still results in a valid, cookie-backed session being stored in `oidc_sessions` with `user_email = ''`, and a `200 {"success": true}` response even though the handler already wrote a `500` body to the client moments earlier (double-write to the `gin.Context`, undefined behavior on the wire, but the session row and cookie are real).

Downstream, `AuthorizedUserWithSession` trusts whatever `user_email`/`user_role` was stored in `oidc_sessions` at creation time and does not re-derive the email from the identity provider on each request: [4](#0-3) 

So an authenticated session tied to an empty-string email but with a role derived from group claims persists and is usable for subsequent authenticated API calls.

### Impact Explanation
An unprivileged actor who can influence or control an OIDC-compatible identity provider response (e.g., a misconfigured/compromised IdP, or a token whose `email` claim is missing/non-string but which still carries valid role-mapping group claims) can obtain a live, cookie-authenticated Chainlink node session with an empty-string identity. This breaks the invariant that every session row maps to a real user email, and downstream code that logs, audits, or looks up users by `user_email` (e.g., `ClearNonCurrentSessions`, `FindUser`) will silently operate on/collide across an empty-email "ghost" identity — a form of cross-user response confusion / audit-trail corruption in the authentication layer of the node's HTTP API.

### Likelihood Explanation
Reaching this path requires control over the ID token's claims (an untrusted/attacker-influenced OIDC provider or a token replay/crafting scenario), which is a more constrained precondition than a straightforward unauthenticated-attacker bug. Still, the bug is directly reachable via the public token-exchange HTTP endpoint with no prior authentication, and the missing `return` is a clear, deterministic code defect (not test-only, not operator-only).

### Recommendation
Add a `return` immediately after writing the error response in the `!ok` branch:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Audit the rest of `handleTokenExchange` for the same pattern (e.g. any other `c.String`/`c.JSON` calls not immediately followed by `return`) and ensure all failure branches halt execution before any session/DB write occurs.

### Proof of Concept
1. Configure the node with OIDC auth enabled and role-mapping claims (`AdminClaim`, `EditClaim`, etc.) that can be satisfied.
2. Have the identity provider (or a proxy/MITM in a test harness) return an ID token whose `email` claim is absent or a non-string type, but whose group claims satisfy `IDClaimsToUserRole`.
3. Complete the OAuth2 code exchange against `POST /.../token-exchange` (the route wired to `handleTokenExchange`).
4. Observe: the handler logs "Failed to get email from claims" and writes a 500 body, but still executes `INSERT INTO oidc_sessions (... user_email='' ...)`, calls `ginSession.Save()`, and returns `200 {"success":true}` with a valid session cookie set.
5. Use the returned session cookie against authenticated API routes — it authenticates successfully with `user_email = ""` and the mapped role.

*Note: I was unable to fully verify the exact router path/route name that wires `handleTokenExchange` (index limits may exclude the router registration file); a Devin session with full repo access could confirm the exact route and add an integration test.*

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-172)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L233-276)
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
