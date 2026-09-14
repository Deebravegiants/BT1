### Title
Missing `return` Statements in OIDC Token Exchange Allow Authentication to Complete Despite Detected Errors - (File: core/sessions/oidcauth/oidc.go)

### Summary
`handleTokenExchange` in the OIDC authentication provider detects two distinct failure conditions — a missing `email` claim and a failed session-row INSERT — logs them and writes an HTTP error response, but does **not** `return` afterwards. Execution falls through and completes the login flow: it sets the session cookie (`ginSession.Set` + `Save()`), emits an `AuthLoginSuccessNo2FA` audit event, and finally overwrites the earlier error response with `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`. This is a direct analog to the audit's "Error Propagation" finding: an error is detected but the code does not "fail early and loudly" — it silently defaults to the success path.

### Finding Description
In `core/sessions/oidcauth/oidc.go`, `handleTokenExchange` (the handler for the public, unauthenticated `POST /oidc-exchange` endpoint registered in `ExtendRouter`) processes an OIDC provider callback: [1](#0-0) 

If `claims["email"]` is not a string, the code logs the error and writes a 500 response via `c.String(...)`, but there is no `return`. The function continues to compute the role from `idClaims` and proceeds with an empty `email` value. [2](#0-1) 

Similarly, if the `INSERT INTO oidc_sessions` call fails, the error is logged and a 500 body is written, but again there is no `return`. Execution falls through to `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)`, sets the session cookie via `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()`, and finally responds with `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` — overwriting/following the previously-written error response with a success one.

This mirrors the report's core complaint about the Compound error-propagation pattern: errors are checked (`if err != nil`) but the calling code fails to halt on error, so the "default" behavior after a detected failure is to continue as if nothing went wrong (`Error.NO_ERROR`-style assumption of success). Here the Go equivalent is neglecting the `return` statement after handling `err`/`!ok`, so a detected fault does not prevent the login/session-establishment code path from executing.

### Impact Explanation
The immediate observable impact is that the login flow does not correctly abort on failure:
- A malformed or unexpected ID-token claims response (missing/invalid `email`) results in a session being created and a cookie issued to the client, associated with a session row whose `user_email` column is an empty string, and an audit log entry (`AuthLoginSuccessNo2FA`) recording a successful login with an empty email — all while the server itself logged and attempted to signal a failure.
- If the `oidc_sessions` INSERT fails, the client still receives an `HTTP 200 {"success": true}` and a session cookie referencing a session ID that was never persisted, along with a spurious `AuthLoginSuccessNo2FA` audit entry, even though authentication state on the server is inconsistent.

Because the role assigned to the session is still derived from `idClaims`/group membership (a separate mapping unaffected by the missing-return bugs), this specific code path may not on its own grant elevated privileges, but it directly violates the audit's "Fail Early and Loudly" principle and produces incorrect audit trail entries and inconsistent session state for callers of the unauthenticated `/oidc-exchange` endpoint — a genuine authentication-flow correctness/logging integrity issue reachable by any client that can reach the endpoint (including malformed or compromised IdP responses).

### Likelihood Explanation
The `/oidc-exchange` endpoint is public and unauthenticated by design (it's the callback endpoint completing the OIDC login). Triggering the missing-`email`-claim path only requires an ID token whose claims map lacks (or has a non-string) `email` field — a condition that can arise from IdP misconfiguration, a non-standard OIDC provider, or claim-shape assumptions being violated, all of which are plausible in production deployments where OIDC is enabled (`OIDC.Enabled=true`). The INSERT-failure path can be triggered by any transient database failure during login. Both are reachable without any special privilege, matching the "unprivileged actor" scope of this analysis.

### Recommendation
Add `return` immediately after both error-handling blocks in `handleTokenExchange`:
- After `c.String(http.StatusInternalServerError, "Failed to get email from claims")` (line 229/230).
- After `c.String(http.StatusInternalServerError, "Error creating session")` (line 259/260).

More generally, audit all `gin` handlers in `core/sessions/oidcauth/oidc.go` and related authentication code for the pattern "log error → write HTTP error response → fall through" instead of "log error → write HTTP error response → `return`", since this is exactly the class of bug the cited audit warns about (errors detected but not enforced, defaulting silently to the success path).

### Proof of Concept
1. Configure Chainlink node with OIDC authentication enabled (`OIDC.Enabled=true`) pointing at a test/mock OIDC provider.
2. Initiate `/oidc-login`, complete the provider's authorization step, and have the mock provider return an ID token whose claims omit the `email` field (or set `email` to a non-string value) while still including valid group claims for `IDClaimsToUserRole`.
3. Client calls `POST /oidc-exchange` with the resulting `code`/`state`.
4. Observe server logs show `"Failed to get email from claims"` (500 written), yet the HTTP response ultimately returned is `200 {"success": true}` along with a `Set-Cookie` for the session, and a new row is written to `oidc_sessions` with `user_email = ''`; the audit log records `AuthLoginSuccessNo2FA` with `email: ""`.
5. Separately, simulate a failing `INSERT INTO oidc_sessions` (e.g., temporarily break DB connectivity for that statement) and observe the same result: 500 is logged/written, but the handler still proceeds to set the cookie and finally return `200 {"success": true}`. [3](#0-2)

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
