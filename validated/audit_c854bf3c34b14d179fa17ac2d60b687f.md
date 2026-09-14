## Finding

The `anyone-can-pay` bug class is "logic that should be gated by a validity/condition check executes anyway, operating on data that failed to be properly established." The closest reachable analog is in the OIDC callback handler `handleTokenExchange`.

### Title
Missing `return` after failed email-claim extraction lets an OIDC login succeed and create a session with an empty/invalid user identity - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
In `handleTokenExchange`, after the ID token is verified and the RBAC role is derived from group claims, the code attempts a type assertion to pull the `email` field out of the claims map. If the assertion fails, the handler logs an error and writes a `500` response body, but — unlike every other failure branch in the same function — it does **not** `return`. Execution falls through and continues to create/persist a session using the unset `email` variable. [1](#0-0) 

### Finding Description
Every other error path in `handleTokenExchange` (state mismatch, token exchange failure, missing `id_token`, ID token verification failure, claim parsing failure, claim extraction failure, role mapping failure) calls `return` immediately after writing the error response: [2](#0-1) 

The one exception is the `email` extraction block:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
``` [1](#0-0) 

Because there is no `return`, `c.String` merely appends a response body/status — Gin doesn't abort the handler — and the function proceeds to:
1. compute `role` from `idClaims` via `oi.IDClaimsToUserRole(...)`,
2. insert a new row into `oidc_sessions` keyed by the (empty) `email` and the derived `role`,
3. set the session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`), and
4. return `ExchangeTokenResponse{Success: true}` to the caller. [3](#0-2) 

This mirrors the CKB pattern precisely: a gating condition (`is_ckb_only`/here, "did we get a valid claim value") is checked but the code that should be conditioned on it (writing to `input_wallets[j].udt_amount` / here, persisting a session with a validated identity) runs unconditionally afterward. Downstream, `AuthorizedUserWithSession` for the OIDC provider trusts whatever `user_email`/`user_role` is stored in `oidc_sessions` without any secondary check against the `users` table: [4](#0-3) 

### Impact Explanation
An authenticated session cookie is issued and treated as valid by `AuthenticateBySession`/`AuthorizedUserWithSession` even though the identity (`email`) was never successfully established, and the client-visible response reports `Success: true` instead of surfacing the failure. Since role is derived purely from group claims independent of the (failed) email extraction, any caller who completes the OAuth2 code exchange and satisfies a claim/group-name mapping (`AdminClaim`, `EditClaim`, etc.) but omits/misshapes the `email` claim still receives a fully functional session with `SessionUserKey`/role set, backed by a DB row with `user_email = ""`. This is a request-flow logic bypass that produces a valid authenticated session despite an explicit, intended failure branch — a session/authentication integrity bug in the internet-facing OIDC callback endpoint. [5](#0-4) 

### Likelihood Explanation
Reaching this code path only requires completing a normal OIDC authorization-code exchange against the configured identity provider and having (or crafting, if the IDP is self-service/attacker-influenced) an ID token whose claims lack a usable `email` field while still satisfying one of the configured group-claim mappings. No malicious node/peer or network-layer manipulation is needed — this is purely an unprivileged client hitting `handleTokenExchange`, i.e. the "session/token/external-initiator handling" surface explicitly in scope.

### Recommendation
Add an explicit `return` immediately after writing the `500` response in the `email` extraction failure branch, exactly like all sibling error branches in this function, so that session creation and cookie issuance cannot occur when the email claim could not be extracted:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, treat an empty `email` as invalid before the `INSERT INTO oidc_sessions` call, and add a regression test asserting that a token exchange with a missing/invalid `email` claim never results in `Success: true` or a persisted session row.

### Proof of Concept
1. Stand up (or control) an OIDC identity provider that issues an ID token containing group claims matching one of the configured `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim` values but omitting the `email` claim (or setting it to a non-string type).
2. Complete the standard `/sessions/oidc` → `handleSignIn` → provider login → callback flow, POSTing the resulting `code`/`state` to the token-exchange endpoint handled by `handleTokenExchange`.
3. Observe that despite the `500` status written into the response body for the email-extraction failure, the handler continues, inserts a row into `oidc_sessions` with `user_email = ''`, sets the session cookie, and ultimately returns HTTP 200 with `ExchangeTokenResponse{Success: true}`.
4. Use the returned session cookie against any authenticated endpoint (e.g. GraphQL mutations gated by `authenticateUserIsAdmin`) — the request succeeds because `AuthorizedUserWithSession` trusts the `oidc_sessions` row's `user_role` without any relation to a legitimate `users` record.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-276)
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
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

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
