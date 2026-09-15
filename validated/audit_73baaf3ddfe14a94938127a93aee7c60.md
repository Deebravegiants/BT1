The code confirms the claim exactly: `handleTokenExchange` requests the `email` scope statically in server config (`Scopes: []string{oidc.ScopeOpenID, "profile", "email", oidcCfg.ClaimName()}`), and the email-claim check at lines 226-230 lacks a `return` statement, unlike every other error branch in the function. [1](#0-0) 

Audit Report

## Title
Missing `return` after failed email-claim extraction in OIDC token exchange creates an authenticated session with an empty/unattributed identity - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, every other validation failure branch (state mismatch, token exchange failure, missing `id_token`, verification failure, claims parsing failure, ID-claim extraction failure) correctly `return`s, but the `email` claim extraction check at lines 226-230 does not, so execution falls through to role mapping, session persistence, audit logging, and a final `200 OK` success response even when email extraction fails.

## Finding Description
`handleTokenExchange` consistently returns immediately on every failure condition except one: [2](#0-1)  The email extraction at lines 226-230 logs and writes a `500` body but omits `return`, letting control flow continue into `IDClaimsToUserRole` (lines 233-245), the `INSERT INTO oidc_sessions` (lines 247-260, keyed by `strings.ToLower(email)` which is empty), an audit log call with the empty email (line 262), session cookie persistence (lines 264-271), and finally an unconditional `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` (lines 273-275) that overwrites the earlier `500` write on the same response writer. `AuthorizedUserWithSession` later trusts whatever `user_email`/`user_role` is stored for the session ID with no re-validation against the IdP. [3](#0-2)  The role is derived solely from group claims via `IDClaimsToUserRole`, independent of `email`, so a session with a legitimate elevated role but empty email can be created and later authenticate as a valid, if unattributed, user.

## Impact Explanation
This creates a persisted, cookie-backed session with an empty `user_email` but a real RBAC role from the ID token's group claims, allowing subsequent authorization checks to succeed based on role alone while corrupting audit attribution (`audit.AuthLoginSuccessNo2FA` logged with an empty email) and masking the underlying failure from the caller via the overwritten `200 OK` response. This is an in-scope authentication/audit-integrity defect in the node's session management logic, not merely a cosmetic bug.

## Likelihood Explanation
The path is reached via the standard, unprivileged OIDC authorization-code flow that every login uses; it requires only that the IdP-issued ID token lack a usable `email` claim while still satisfying group-claim-based role mapping. The server statically requests the `email` scope (`oidcCfg` scopes include `"email"`), so this is not attacker-controlled scope selection, but IdPs can still omit or malform the `email` claim in valid tokens (e.g., unverified/null email, non-standard claim type) independent of node operator misconfiguration, keeping this within reach of a standard external OIDC login flow rather than requiring privileged or host access.

## Recommendation
Add a `return` immediately after writing the error response in the email-claim check, mirroring every other branch in the function, and also add `return` after the `oi.ds.ExecContext` failure branch (lines 257-260) so a failed session insert never proceeds to the audit-success call and `200 OK` response.

## Proof of Concept
1. Configure/attest an OIDC identity provider whose ID token satisfies group-claim role mapping (`IDClaimsToUserRole`) but returns an `email` claim that is missing or non-string typed.
2. As an unauthenticated client, complete `/oidc-login` → provider redirect → `/oidc-login/callback` token exchange.
3. Observe server logs `"Failed to get email from claims"` with a `500` body write, but the final HTTP response is `200 OK` with `{"success":true}`; a new `oidc_sessions` row is inserted with `user_email = ''` and a valid mapped `user_role`; the `Set-Cookie` session ID authenticates successfully against `AuthorizedUserWithSession` for subsequent authenticated requests.

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
