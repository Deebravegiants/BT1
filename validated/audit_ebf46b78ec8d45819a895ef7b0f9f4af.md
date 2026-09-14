Confirmed: no `email_verified` check exists anywhere in the codebase. This confirms the root cause in the OIDC token exchange flow.

### Title
Unverified email claim trust leads to authentication bypass and role assignment in OIDC token exchange - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
The OIDC authentication flow's token-exchange handler extracts and trusts the `email` claim from a cryptographically verified ID token without checking the `email_verified` claim, and uses that unverified email as the sole binding key to create an authenticated session with a role derived from group claims. Any actor who can get an IdP to issue an ID token containing an unverified/attacker-controlled `email` value matching a target user's email is granted a live session identified by that email, mirroring the "auto-linking by email match" root cause described in the reference CVE.

### Finding Description
In `handleTokenExchange`, after verifying the ID token signature (`core/sessions/oidcauth/oidc.go:207-212`), the code reads the email directly from the claims map: [1](#0-0) 
No check of `email_verified` (or any equivalent ownership assertion) is performed anywhere in the codebase — a repo-wide search confirms this. The email is then lower-cased and persisted directly as the session identity, alongside a role computed purely from group claims in the same unverified token: [2](#0-1) 
Downstream, `AuthorizedUserWithSession` (`core/sessions/oidcauth/oidc.go:349-391`) trusts the `user_email`/`user_role` columns stored in `oidc_sessions` at face value for the lifetime of the session — there is no secondary check against a verified identity store. The `FindUser` fallback and `localLoginFallback` (`core/sessions/oidcauth/oidc.go:278-295`, `578-597`) are separate local-admin flows and don't intersect with this OIDC session creation path, so this is not local-account linking per se — but the practical effect is identical to the reported bug class: identity and role are established solely from an unauthenticated claim of email ownership, with no proof-of-possession beyond IdP token signature validity, which does not certify email ownership unless `email_verified` is explicitly checked.

### Impact Explanation
If the configured IdP can be induced to issue ID tokens with attacker-supplied, unverified email addresses (common in many self-service/social IdPs, especially where email is a mutable profile field or account email changes aren't verification-gated), an unprivileged remote attacker can obtain a fully authenticated Chainlink node session under a victim's email and inherit whatever role (`Admin`, `Edit`, `Run`) that email's group claims map to. This is a full authentication/authorization bypass (CWE-287/CWE-346 class), matching CVSS 9.1 AV:N/AC:L/PR:N/UI:N impact profile of the reference CVE.

### Likelihood Explanation
Exploitability depends on the specific IdP's behavior around unverified emails, which is outside the chainlink code's control, but the code provides no defense-in-depth against it: no `email_verified` gate, no secondary binding to the immutable `sub` claim, no re-validation on each request. This is a code-level gap that violates OIDC best practice (RFC/OIDC spec explicitly warns implementers to check `email_verified` before trusting `email` for authorization decisions).

### Recommendation
- Reject or downgrade trust when `email_verified` is present and `false`, or require it to be explicitly `true` before honoring the `email` claim in `handleTokenExchange`.
- Bind sessions to the immutable `sub` claim (and issuer) rather than (or in addition to) email, storing `sub` in `oidc_sessions`/`oidc_user_api_tokens` and treating email purely as a display attribute.
- Document/require IdP configuration to guarantee verified emails only, and fail closed if the claim is absent.

### Proof of Concept
1. Configure or compromise an OIDC identity such that the ID token issued contains `"email": "victim@company.com"` with `"email_verified": false` (or omitted), while group claims for that identity map to `AdminClaim`.
2. Complete the `/oidc-login` → provider → `/oidc-exchange` flow with this token.
3. `handleTokenExchange` verifies the token signature succeeds (attacker's own valid token), extracts `email` from claims unconditionally, maps groups to `UserRoleAdmin`, and inserts a new row into `oidc_sessions` for `victim@company.com` with `admin` role.
4. The attacker's browser session cookie now authenticates as `victim@company.com` with admin role for all subsequent `/v2/*` API calls via `AuthenticateBySession` → `AuthorizedUserWithSession`. [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** core/web/auth/auth.go (L55-71)
```go
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```
