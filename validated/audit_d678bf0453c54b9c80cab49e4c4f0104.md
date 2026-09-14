### Title
Missing `return` after failed email-claim extraction lets OIDC login proceed with an empty user identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
This is an authentication-flow analog of the Spring Security OAuth "authorization endpoint → approval endpoint" flaw: the OIDC login/authorization callback handler in Chainlink's node webserver does not properly halt processing when a required field cannot be safely extracted from the identity provider's response, allowing an authenticated session to be created with corrupted/missing identity data.

### Finding Description
In `handleTokenExchange` (`core/sessions/oidcauth/oidc.go`), after the ID token is verified and claims are parsed, the code extracts the `email` claim: [1](#0-0) 

If `claims["email"]` is not a string (missing, null, or wrong type), the branch logs an error and writes an HTTP 500 body via `c.String(...)`, but **does not `return`**. Execution falls through to role mapping, session creation, and the audit log/session save, all using the zero-value `email` variable: [2](#0-1) 

Because `c.String` does not abort Gin's handler chain, the function continues to:
1. Map claims to a role via `IDClaimsToUserRole` (independent of email) — still succeeds using valid group claims from the verified ID token.
2. Insert a row into `oidc_sessions` with `user_email = ""` (lower-cased empty string) and the mapped role.
3. Set the session cookie (`clsession_id`) and return `HTTP 200 {"success": true}` to the client — even though the body already wrote a 500 status/message earlier, Gin allows the subsequent `c.JSON` to override the response, so the client legitimately receives a "success" authenticated session despite the corrupted identity.

This mirrors the root cause pattern in CVE-2018-1260 (GHSA-rrpm-pj7p-7j9q): a request in the authorization/token-exchange flow is forwarded past a validation step that should have terminated processing, resulting in an authenticated result being produced from unvalidated/incomplete data.

### Impact Explanation
An OIDC login can complete and mint a valid authenticated session tied to an **empty-string email identity** and a role derived purely from the verified group claims. Any other logic in the system that keys off `user_email` (e.g., audit trail attribution, per-user API token issuance, or future lookups by email) could confuse or collide with this empty-email session. At minimum this is a request/response integrity bug in the authentication path: the handler returns "Success: true" to the client while having already attempted to signal a 500 failure, and persists a session with a corrupted identity field rather than rejecting the login. This weakens the authentication guarantee that every session in `oidc_sessions` is tied to a valid, attested user identity.

### Likelihood Explanation
Triggering this requires an unprivileged actor who controls (or can influence) the OIDC identity provider's token response — e.g., a provider misconfiguration, a malicious/compromised IdP, or an ID token missing the `email` claim while still containing valid group claims. Since the state (`CSRF`) check and ID token signature verification still occur beforehand, this is not exploitable by a purely external unauthenticated attacker without IdP-side influence, but it is a genuine defect in production authentication code reachable through the standard `/signin` OIDC callback flow.

### Recommendation
Add a `return` (and reject the login with an error response) immediately after the failed `email` claim type assertion in `handleTokenExchange`:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally audit other early-return branches in this handler for the same `c.String(...)` without `return` anti-pattern (e.g., line 258-260 after the `oidc_sessions` insert failure also lacks a `return`).

### Proof of Concept
1. Configure `WebServer.OIDC` per `core/config/docs/core.toml` (lines 210-233) against an identity provider that returns a valid, signed ID token containing the configured group claim (e.g., matching `ReadClaim`) but omitting the `email` claim.
2. Complete the standard flow: `GET /signin` (sets state) → provider redirect → `POST` to the token-exchange endpoint with the valid `code`/`state`.
3. Observe: token exchange and signature verification succeed; the `email` type assertion fails and logs an error but the handler does not return.
4. Execution continues, `IDClaimsToUserRole` succeeds using the group claim, a row is inserted into `oidc_sessions` with `user_email=''`, the session cookie is set, and the response is `200 {"success": true}` — a working authenticated session is granted despite the failed identity extraction. [3](#0-2)

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
