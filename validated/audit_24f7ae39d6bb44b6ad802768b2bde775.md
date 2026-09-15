### Title
OIDC Authentication Provider Unconditionally Disables WebAuthn/2FA Enforcement for Both Local and SSO Login Paths - (File: core/sessions/oidcauth/oidc.go)

### Summary
When a chainlink node is configured to use the OIDC authentication provider, the local-admin login path (`/sessions`) can never enforce WebAuthn 2FA regardless of whether a user has actually enrolled a WebAuthn credential, and the OIDC SSO callback path (`/oidc-exchange`) issues a full session purely from IdP-attested claims with no reference to WebAuthn/2FA at all. This mirrors the reported Vikunja bug class: an SSO/OIDC login path that skips the second-factor check that the local password-login path otherwise enforces.

### Finding Description
`core/sessions/localauth/orm.go` (`orm.CreateSession`, lines 144-230) is the reference implementation of correct 2FA enforcement: it looks up `GetUserWebAuthn` for the user and, if credentials exist, forces a WebAuthn challenge/response before a session row is created [1](#0-0) .

`core/web/sessions_controller.go`'s `Create` handler for the `/sessions` endpoint is authenticator-agnostic: it calls `sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)` to decide whether to route the request through the WebAuthn challenge flow [2](#0-1) .

When the OIDC authenticator is the active `AuthenticationProvider`, `GetUserWebAuthn` is hard-coded to always return an empty slice, with the comment "MFA is delegated to SAML provider": [3](#0-2) 

Consequently, `sessions_controller.go`'s `Create` handler will *never* see any WebAuthn tokens for any user under the OIDC authenticator, so it never sets `sr.SessionStore`/`sr.WebAuthnConfig`, and the request goes straight into `oidcAuthenticator.CreateSession` → `localLoginFallback`, which checks only email + password and returns a session with zero MFA/2FA verification of any kind: [4](#0-3) [5](#0-4) 

Separately, the actual OIDC SSO callback (`handleTokenExchange`, registered at `/oidc-exchange`) issues a full authenticated session purely from IdP-attested email and group claims, again with no 2FA/WebAuthn check and no password verification: [6](#0-5) 

Both the `/sessions` endpoint (via `SessionsController`) and the `/oidc-login` / `/oidc-exchange` endpoints (via `oidcAuthenticator.ExtendRouter`, lines 658-664) are simultaneously reachable when OIDC is configured, per the comment in `CreateSession`: "CreateSession in the context of the OIDC driver handles only the local auth admin user... To initiate the SAML/OIDC flow, a separate /oidc-login route is defined" [7](#0-6) . `SaveWebAuthn` is also stubbed as unsupported for the OIDC driver, so there is no way to even register a credential through this authenticator, but the empty-stub `GetUserWebAuthn` guarantees the check is skipped structurally rather than merely being unused: any WebAuthn rows already present in the shared `web_authns` table (e.g., left over from a prior local-auth configuration, or if the deployment switches `AuthenticationMethod`) are silently ignored.

This is directly analogous to the Vikunja root cause: the OIDC login path issues a token/session without consulting the second-factor enrollment state that the local login path otherwise enforces (`user2.TOTPEnabledForUser` in Vikunja vs. `GetUserWebAuthn` in chainlink).

I was not able to fully confirm within the available tool budget how `AuthenticationMethod`/authenticator selection is wired in `core/services/chainlink/application.go` (the search only returned match counts, not the selection logic itself), so I cannot state with certainty whether a node can be reconfigured from local-auth (with WebAuthn already enrolled) to OIDC-auth without also clearing the `web_authns` table, or whether operators are expected to treat OIDC and local-WebAuthn as mutually exclusive by documentation. This affects the exact likelihood/severity of the "stale WebAuthn silently bypassed" sub-case, though the structural fact that `GetUserWebAuthn` is unconditionally stubbed to empty for the OIDC authenticator is confirmed by direct code inspection.

### Impact Explanation
If an operator enables the OIDC authenticator, both of its exposed login surfaces (`/sessions` local-admin fallback and `/oidc-exchange` SSO) provide full session/JWT-equivalent (cookie session with role) issuance with **no 2FA verification path at all** — not merely a bypassable one, but one that is structurally unreachable because `GetUserWebAuthn` never returns real data. Any attacker with valid password credentials for a local admin account (leaked/reused password, credential stuffing) can fully authenticate via `/sessions` without a WebAuthn challenge, even if that account is believed to be protected by 2FA. Successful login grants a full session with the account's role (potentially `UserRoleAdmin`), enabling job/bridge management, secret/API-token creation (`SetAuthToken`), and other admin actions — a concrete authentication/second-factor bypass with High severity, matching CWE-287.

### Likelihood Explanation
Likelihood is **conditional but concrete**: it requires the node to be configured to use the OIDC authentication provider (an intentional deployment choice, not default). Given that configuration, the bypass is unconditional and deterministic — every login through `/sessions` skips WebAuthn regardless of user configuration, since the check is hard-stubbed rather than data-driven. No race condition, timing attack, or malicious peer/node is required — a normal unprivileged client with valid credentials (or an unprivileged client relying on IdP group claims for `/oidc-exchange`) triggers it directly.

### Recommendation
1. `oidcAuthenticator.GetUserWebAuthn` should query the same `web_authns` table used by `localauth.orm` (keyed by lowercase email) instead of unconditionally returning an empty slice, so that any locally-enrolled WebAuthn credential is enforced for the `/sessions` fallback path.
2. If WebAuthn truly cannot be supported end-to-end for OIDC-driven accounts, the OIDC authenticator should hard-fail (or refuse to serve) local-fallback login for any account that has `web_authns` rows, rather than silently proceeding without a challenge — mirroring the recommended Vikunja fix of forbidding the alternate path outright when a second factor is enrolled.
3. For the `/oidc-exchange` SSO callback itself, if any local 2FA/step-up requirement is meant to also apply to SSO-authenticated identities matching a local user record, add an explicit check against `web_authns`/local user state before issuing the `oidc_sessions` row, analogous to Vikunja's recommended fix of checking `TOTPEnabledForUser` before calling `NewUserAuthTokenResponse`.

### Proof of Concept
Conceptual reproduction (not executed against a live instance):
1. Configure a chainlink node with `[WebServer.OIDC]` (or equivalent) as the active `AuthenticationProvider`, and ensure a local admin user exists in the `users` table with a WebAuthn credential present in `web_authns` (e.g., left from prior local-auth use, or inserted directly).
2. POST valid `email`/`password` for that admin to `/sessions`.
3. Observe that `SessionsController.Create` calls `oidcAuthenticator.GetUserWebAuthn`, which unconditionally returns `[]`, so no WebAuthn challenge (`options`/401 response) is ever returned [3](#0-2) .
4. `CreateSession` succeeds via `localLoginFallback` (password check only) and a valid session cookie/role is returned [4](#0-3) , despite the account having WebAuthn 2FA enrolled — the second factor was never requested.

### Citations

**File:** core/sessions/localauth/orm.go (L164-199)
```go
	// Load all valid MFA tokens associated with user's email
	uwas, err := o.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		// There was an error with the database query
		lggr.Errorf("Could not fetch user's MFA data: %v", err)
		return "", pkgerrors.New("MFA Error")
	}

	// No webauthn tokens registered for the current user, so normal authentication is now complete
	if len(uwas) == 0 {
		lggr.Infof("No MFA for user. Creating Session")
		session := sessions.NewSession()
		_, err = o.ds.ExecContext(ctx, "INSERT INTO sessions (id, email, last_used, created_at) VALUES ($1, $2, now(), now())", session.ID, user.Email)
		o.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})
		return session.ID, err
	}

	// Next check if this session request includes the required WebAuthn challenge data
	// if not, return a 401 error for the frontend to prompt the user to provide this
	// data in the next round trip request (tap key to include webauthn data on the login page)
	if sr.WebAuthnData == "" {
		lggr.Warnf("Attempted login to MFA user. Generating challenge for user.")
		options, webauthnError := sessions.BeginWebAuthnLogin(user, uwas, sr)
		if webauthnError != nil {
			lggr.Errorf("Could not begin WebAuthn verification: %v", webauthnError)
			return "", pkgerrors.New("MFA Error")
		}

		j, jsonError := json.Marshal(options)
		if jsonError != nil {
			lggr.Errorf("Could not serialize WebAuthn challenge: %v", jsonError)
			return "", pkgerrors.New("MFA Error")
		}

		return "", pkgerrors.New(string(j))
	}
```

**File:** core/web/sessions_controller.go (L41-54)
```go
	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}
```

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

**File:** core/sessions/oidcauth/oidc.go (L404-407)
```go
// GetUserWebAuthn returns an empty stub, MFA is delegated to SAML provider
func (oi *oidcAuthenticator) GetUserWebAuthn(ctx context.Context, email string) ([]clsessions.WebAuthn, error) {
	return []clsessions.WebAuthn{}, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L409-439)
```go
// CreateSession in the context of the OIDC driver handles only the local auth admin user, exposed by the default endpoint defined in the router. To initiate the SAML/OIDC
// flow, a separate /oidc-login route is defined which handles the redirect to the
// configured provider
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)

	// Save local admin session, user, and role to sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	session := clsessions.NewSession()
	_, err = oi.ds.ExecContext(ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		return "", fmt.Errorf("error creating local OIDC session: %w", err)
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
}
```
