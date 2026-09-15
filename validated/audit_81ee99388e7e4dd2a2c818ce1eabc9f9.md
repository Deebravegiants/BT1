Audit Report

## Title
Missing `return` after failed email-claim extraction in `handleTokenExchange` allows OIDC session creation with an unverified empty-string identity - (File: `core/sessions/oidcauth/oidc.go`)

## Summary
In `oidcAuthenticator.handleTokenExchange`, when the verified ID token's `email` claim is missing or not a string, the handler logs the error and writes an HTTP 500 body via `c.String(...)` but fails to `return`, unlike every other error branch in the function. Execution falls through to role mapping and session persistence, resulting in a valid, cookie-backed session inserted into `oidc_sessions` with `user_email = ''` and whatever `user_role` the group claims map to, and a final `200 {"Success": true}` response is sent to the client.

## Finding Description
The code at [1](#0-0)  is the only error branch in `handleTokenExchange` that omits `return` after writing an error response:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```

Every other failure path in the same function (invalid request, bad state, exchange failure, missing `id_token`, verify failure, claims parse failure, role mapping failure, session-save failure) correctly returns immediately, as seen at [2](#0-1)  and [3](#0-2) . Because this one branch is missing `return`, execution proceeds to role mapping via `IDClaimsToUserRole` ( [4](#0-3) ) and then inserts a new row into `oidc_sessions` keyed by the zero-value `email` (`""`), sets the session cookie, and returns HTTP 200 success, as shown at [5](#0-4) .

The resulting session is later trusted verbatim by `AuthorizedUserWithSession`, which reads `user_email`/`user_role` directly from `oidc_sessions` with no cross-check against the local `users` table: [6](#0-5) . This confirms the claim's description of the broken security assumption — a session is materialized and trusted without a verified, non-empty user identity, and its authority (role) is still fully attacker/IdP-claim-derived.

## Impact Explanation
This is a genuine control-flow/logic defect in the node's authentication code, not a misconfiguration or third-party issue: the node's own handler fails to abort on an authentication data error it explicitly detected and logged. The consequences are:
- A session with an empty-string user identity can be granted a legitimate role (`admin`/`edit`/`run`/`view`) purely from group claims, breaking the intended per-user identity binding of sessions.
- All such sessions collapse to the same `""` email, which undermines identity-scoped operations like `ClearNonCurrentSessions` (session/user-identity confusion).
- The client-visible outcome is a successful `200 {"Success": true}` login response and a working session cookie despite the server having detected and attempted to signal an authentication failure — an intended-block bypass in the login flow.

This maps to the in-scope "node API authentication or role bypass" / "cross-user response corruption" impact classes.

## Likelihood Explanation
This path is reachable by any client that can complete the standard `/oidc-login` → `/oidc/token-exchange` flow once OIDC auth is enabled — no operator, admin, or host access is required to exercise the flow itself. The idToken's signature/expiry is still cryptographically verified via `oi.provider.Verifier(...).Verify(...)`, so exploitation is not a full unauthenticated bypass; it requires the resulting verified token to lack an `email` claim while still carrying qualifying group claims (e.g., an IdP that omits `email` for certain account/scope configurations, or a client able to influence the requested scopes). This is a real, code-level defect reachable through the normal login flow, not one requiring database, host, or leaked-credential access, so it is properly in-scope and not excluded as "misconfiguration-only," since the root cause is the missing `return` in the node's own code rather than any operator error.

## Recommendation
Add `return` immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call at [1](#0-0)  so that a missing/invalid `email` claim aborts the request before role mapping and session persistence occur. Additionally, the identical missing-`return` pattern after `c.String(http.StatusInternalServerError, "Error creating session")` at [7](#0-6)  should be fixed for the same reason.

## Proof of Concept
1. Configure `WebServer.OIDC` and complete the `/oidc-login` redirect flow to obtain a valid authorization `code`.
2. Arrange for the ID token returned during code exchange to include valid group claims matching `AdminClaim`/`EditClaim`/etc. but omit the `email` claim.
3. Send `POST /oidc/token-exchange` with the valid `code`/`state` to trigger `handleTokenExchange`.
4. Observe: despite the logged "Failed to get email from claims" error and initial 500 status write, the handler proceeds to insert a row into `oidc_sessions` with `user_email = ''` and the mapped role, sets the session cookie, and returns `{"Success": true}` — a Go handler/integration test asserting a row is inserted into `oidc_sessions` and a 200 response is returned in this scenario would confirm the defect.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L200-204)
```go
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
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

**File:** core/sessions/oidcauth/oidc.go (L241-245)
```go
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-275)
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

	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
```

**File:** core/sessions/oidcauth/oidc.go (L349-381)
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
