## Analysis

This is a genuine control-flow analog of the reported bug class: the report's root cause is missing an early return / mis-ordering flow control so that a security-relevant action (event emission) proceeds/aborts incorrectly for a specific input case. The Chainlink codebase has the same defect pattern in the internet-facing OIDC login callback, where a missing `return` after an error response lets execution fall through and complete a privileged action (session creation + success response) despite an unhandled failure condition.

### Title
Missing `return` after failed email-claim extraction in OIDC token exchange creates an authenticated session with an empty/unattributed identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
In `handleTokenExchange`, the handler for the unauthenticated `/oidc-login` callback endpoint, the code that extracts the `email` claim from the verified ID token does not `return` when the claim is missing or of the wrong type. Execution falls through, computes an RBAC role from group claims, inserts a new row into `oidc_sessions` with an empty `user_email`, sets the session cookie, and returns HTTP 200 with `Success: true` to the caller.

### Finding Description
`handleTokenExchange` validates several preconditions and correctly `return`s on failure for state mismatch, token exchange failure, missing `id_token`, and token verification/claims-parsing failures. [1](#0-0) 

However, the email extraction check omits the `return`:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
``` [2](#0-1) 

Because there is no `return`, execution continues into role mapping and session persistence: [3](#0-2) 

...and then inserts a new `oidc_sessions` row keyed by the (empty) `email`, sets the session cookie, and finally responds with `http.StatusOK` / `Success: true`, overwriting the earlier `500` write on the same `gin.Context` response writer: [4](#0-3) 

The role assigned to this session is derived purely from `idClaims` (OIDC group claims), independent of the `email` field, via `IDClaimsToUserRole`, so a session with an elevated role (e.g. admin/edit/run) but an empty `user_email` can legitimately be created: [3](#0-2) 

Later requests carrying this session cookie are authenticated via `AuthorizedUserWithSession`, which trusts whatever `user_email`/`user_role` is stored in `oidc_sessions` for the session ID, with no re-validation against the identity provider: [5](#0-4) 

This is the same class of bug as the reported issue: a control-flow gap (missing early return / event only emitted on some code paths) that lets subsequent security-relevant logic (an event emission in the report; here, session persistence, an audit log, and a success response) execute in a state where it should have been aborted.

### Impact Explanation
- A persisted, cookie-backed authenticated session is created with an **empty `user_email`** but a **real RBAC role** taken from the ID token's group claims. All subsequent authorization checks (`RequiresRunRole`, admin/edit checks) succeed for this session based on the role field alone.
- The audit trail for this session is corrupted: `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` is called with `email` (empty), meaning privileged actions performed under this session cannot be attributed to a real user identity in the audit log — undermining the accountability guarantees the audit logging subsystem is meant to provide.
- The caller-visible response is unconditionally success (`200 OK`, `Success: true`), masking the underlying claim-extraction failure from the client and from server-side monitoring that might otherwise flag the anomaly from the `500` log line alone (since the final response overwrites it).

### Likelihood Explanation
This path is reachable by any client completing the standard, unprivileged OIDC authorization-code flow against the configured IdP — the same flow used by every login. It requires the IdP-issued ID token to lack a usable `email` claim (e.g., IdP/config mismatch, restricted `email` scope grant, a non-standard/misconfigured or attacker-influenced identity source, or a client controlling which scopes are granted during consent) while still satisfying the group-claim-based role mapping. It does not require any elevated privilege or node-operator access — only completion of the login redirect flow — so it is reachable purely from an unprivileged external HTTP client.

### Recommendation
Add a `return` immediately after writing the error response when the `email` claim cannot be extracted, mirroring the pattern used for every other failure branch in `handleTokenExchange`:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, treat the session-insert error path the same way — `return` after logging the `oi.ds.ExecContext` failure at lines 257-260 instead of falling through to the audit-success call and the `200 OK` response — so a failed session write never produces a "success" audit record or response.

### Proof of Concept
1. Configure the node's OIDC provider such that the ID token returned for a legitimate authorization-code exchange does not include an `email` claim (e.g., IdP configuration granting only the group/role scope, or an IdP token endpoint response omitting `email`), while the token still satisfies `IDClaimsToUserRole` via group claims (e.g., membership in the configured Admin/Edit/Run group).
2. Complete the standard `/oidc-login` → provider redirect → `/oidc-login/callback` (token exchange) flow as an unauthenticated client.
3. Observe:
   - Server logs `"Failed to get email from claims"` and writes a `500` body, but the HTTP response ultimately returned is `200 OK` with `{"success":true}`.
   - A new row is inserted into `oidc_sessions` with `user_email = ''` and `user_role` set to the mapped role.
   - The response `Set-Cookie` contains a valid session ID for this row.
4. Use the returned session cookie against any authenticated endpoint (e.g., an admin-only route) — it authenticates successfully via `AuthorizedUserWithSession`, returning `User{Email: "", Role: <mapped role>}`, granting access without any attributable user identity in the audit trail.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-225)
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

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}

	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}

	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}

	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
		return
	}
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
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

**File:** core/sessions/oidcauth/oidc.go (L247-276)
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
