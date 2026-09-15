Confirmed: no `email_verified` claim check exists anywhere in the OIDC flow, and the session created in `handleTokenExchange` is bound purely to the raw `email` claim value from the ID token, with no cross-check against the local `users` table or any binding proof beyond the IdP's own claim.

### Title
OIDC Login Trusts Unverified `email` Claim to Establish User Session Identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The Chainlink node's OIDC authentication handler (`handleTokenExchange`) extracts the `email` claim from a verified ID token and uses it as the durable identity for the resulting session, without checking an `email_verified` claim or otherwise confirming the identity provider guarantees email ownership. Any user who can register/authenticate with an arbitrary (unverified) email address at the configured OIDC provider inherits a Chainlink node session tied to that email address.

### Finding Description
In `handleTokenExchange`, after a successful OAuth2 code exchange and ID token signature verification, the code pulls the `email` claim directly out of the token claims map and uses it, unmodified apart from lowercasing, as the durable user identity for the new session: [1](#0-0) 

This email is then persisted as `user_email` in the `oidc_sessions` table together with a role computed from group claims, and the session cookie is set to reference this session: [2](#0-1) 

At no point does the handler check `claims["email_verified"]`, nor does it consult the local `users` table to confirm the claimed email corresponds to a specific known/expected account before establishing the session identity — the ID token's `email` claim is trusted implicitly. `AuthorizedUserWithSession` subsequently returns whatever `user_email`/`user_role` was cached at login time for any request bearing that session cookie: [3](#0-2) 

This is the same bug class as the reported Coolify CVE-2026-86117: an authentication flow signs a caller into an identity based solely on an email string returned from an OAuth/OIDC provider, without verifying that the provider guarantees ownership of that email address. If the configured identity provider (as is common with self-service IdPs, e.g. some Okta/Keycloak/Auth0 tenants configured to allow self-registration with an unverified email field) does not itself enforce email verification before issuing ID tokens, an attacker can self-register at the IdP using a victim's or a privileged-sounding email address and obtain a Chainlink node session under that identity, with role determined only by whatever groups the attacker's own IdP account happens to have.

### Impact Explanation
Because role is derived from OIDC group claims (`AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim`) rather than from the trusted email itself, the most severe scenario (attacker email-squatting an existing admin's session identity to instantly get Admin role) requires the attacker to also hold matching group membership. However, the `user_email` value is still used as the durable identity in `oidc_sessions`, in audit logs (`audit.AuthLoginSuccessNo2FA`), and would be relied upon anywhere the application treats OIDC session email as an authoritative user identifier (e.g., API tokens via `SetAuthToken`/`oidc_user_api_tokens`, keyed by `user_email`). An attacker with any group-claim overlap and a victim's spoofed unverified email can create authenticated sessions and API tokens that are audit-logged and administratively tracked as belonging to the victim's email, enabling identity/audit-trail confusion and any privilege the attacker's own group membership provides while impersonating another user's recorded identity.

### Likelihood Explanation
Exploitability depends entirely on operator's OIDC IdP configuration: this is only reachable if the configured identity provider issues valid signed ID tokens for self-registered/unverified emails (a real-world, non-default but not uncommon IdP misconfiguration, matching the same trust assumption abused in the Coolify CVE). Given that likelihood, no additional application-side defense exists in this code path to prevent it — there's no `email_verified` check as a compensating control.

### Recommendation
In `handleTokenExchange`, require and validate `claims["email_verified"] == true` before accepting the `email` claim as an identity anchor, and reject the login (or force a fallback/registration flow) if the claim is missing or false. Additionally, avoid overloading the raw IdP-asserted email as the sole identity key for session and API-token storage without any secondary binding (e.g., subject `sub` claim) to guard against IdP tenants that reuse or don't guarantee uniqueness/verification of email addresses.

### Proof of Concept
1. Configure Chainlink node with `WebServer.AuthenticationMethod = 'oidc'` pointed at a self-service OIDC provider that allows account self-registration without enforcing email verification (or an IdP tenant where `email_verified` is `false`/absent in issued ID tokens).
2. Attacker registers an account at the IdP using a target email address (e.g., `admin@company.com`) and satisfies at least one of the configured `RunClaim`/`ReadClaim` group memberships.
3. Attacker completes the OAuth2 authorization code flow against the node's `/oidc-login` and `/oidc-exchange` endpoints: [4](#0-3) 
4. The node verifies the ID token signature (valid, since it's genuinely signed by the configured IdP) and extracts `email = "admin@company.com"` from the claims without checking `email_verified`, creating a session and audit log entry under that identity. [5](#0-4)

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

**File:** core/sessions/oidcauth/oidc.go (L658-664)
```go
func (oi *oidcAuthenticator) ExtendRouter(api *gin.RouterGroup) error {
	api.GET("/oidc-enabled", oi.handleCheckEnabled)
	api.GET("/oidc-login", oi.handleSignIn)
	api.POST("/oidc-exchange", oi.handleTokenExchange)

	return nil
}
```
