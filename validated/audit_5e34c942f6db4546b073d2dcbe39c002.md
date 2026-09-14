### Title
Missing `return` after failed OIDC email-claim extraction allows session creation with empty `user_email` - (File: core/sessions/oidcauth/oidc.go)

### Summary
In `handleTokenExchange`, after a successful OIDC token exchange and ID-token verification, the handler attempts to read the `email` claim. If that claim is missing or not a string, an error is logged and an HTTP 500 body is written, but execution is **not stopped** (`return` is missing). This is the same bug class as the reported "unchecked return value" issue: a failure indicator (`ok`) is observed but not acted upon, so the code proceeds as if the operation had succeeded.

### Finding Description
`handleTokenExchange` performs this sequence: exchange code → verify ID token → parse claims → extract role claims → extract `email` claim: [1](#0-0) 

Unlike every other failure branch in this function (state mismatch, exchange failure, missing `id_token`, verification failure, claims parse failure, role-mapping failure — all of which call `return` immediately after writing the error response), this branch omits the `return`: [2](#0-1) 

Because `return` is missing, execution falls through to role mapping and session persistence using the now-empty `email` variable (Go zero-value for the failed type assertion): [3](#0-2) 

The code inserts a row into `oidc_sessions` with `user_email = ""` (lower-cased empty string), sets the audit log entry with `email: ""`, and — critically — still calls `ginSession.Save()` and returns `ExchangeTokenResponse{Success: true}` to the client on line 273-275, i.e., the HTTP response indicates the login succeeded and a valid session cookie is issued, even though the server-side error page was written moments earlier (writing two response bodies to the same `gin.Context` is itself indicative that the control flow was not intended to continue).

This exactly mirrors the reported bug class: a failure signal (`ok == false` / `transferFrom` returning `false`) is checked but the code does not halt or roll back on that failure, and later logic proceeds as though the operation succeeded — leading to an inconsistent/invalid state being persisted and treated as valid.

### Impact Explanation
A valid, cookie-backed session is created and returned to the client with `success: true` even though the server failed to determine the user's email. The session's `user_role` is still derived correctly from the IdP's group claims, but the identity (`user_email`) tied to the session is empty. Downstream, `FindUser`/session lookups rely on `user_email`, so:
- Session records that cannot be tied to a real email undermine the audit trail (`AuthLoginSuccessNo2FA` is logged with `email: ""`), weakening accountability for privileged (e.g., admin-mapped) OIDC sessions.
- A HTTP 200 success response is served to the client despite an internal error having occurred, which is confusing/incorrect API behavior and could mask a real authentication failure while still leaving the client with an active cookie/session that the server considers valid via `AuthorizedUserWithSession`.

This is a correctness/authentication trust-boundary bug reachable directly by any client completing the OIDC front-channel flow, but the severity is bounded by the fact that reaching the `email` claim missing branch typically requires the IdP not to return an `email` claim (e.g., misconfigured scopes) — it is not fully attacker-controlled input in a standard, correctly configured deployment.

### Likelihood Explanation
Likelihood is moderate-to-low in a correctly configured environment because the OIDC scope list explicitly requests `"email"`, so a compliant IdP will normally return the claim. However, it is trivially reachable in any misconfiguration, and more importantly it is a code-flow defect (missing `return`) that is orthogonal to any specific IdP behavior — the same pattern class ("check but don't enforce") as the external report, making it a legitimate, low-effort-to-trigger, unprivileged-actor-reachable defect (the OIDC callback endpoint is hit by any unauthenticated client completing the redirect flow).

### Recommendation
Add the missing `return` statement immediately after writing the error response in the `email` claim extraction failure branch, consistent with every other error branch in `handleTokenExchange`:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```

Additionally, consider auditing the rest of the function for double-response risks, and add a linter rule (e.g., `bodyclose`/custom check or gin response-then-return pattern check) to catch missing `return` after error responses in HTTP handlers.

### Proof of Concept
1. Configure the Chainlink node with OIDC authentication where the IdP's ID token/claims response omits the `email` field (e.g., an IdP that only returns `email` conditionally, or a proxy/mock IdP under attacker influence returning claims without `email`).
2. Complete a normal OIDC front-channel login flow up to `POST /../token-exchange` (the endpoint served by `handleTokenExchange`), with a valid `code`/`state`, valid token exchange, valid ID token signature, and valid group claims mapping to a role (e.g., "Read").
3. Observe that the server:
   - Writes `c.String(http.StatusInternalServerError, "Failed to get email from claims")` internally (visible via logs, though this string response is overwritten by the code path continuing).
   - Continues to `INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, '', $3, now())`.
   - Calls `ginSession.Save()` and returns `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.
4. The client receives an HTTP 200 `{"success":true}` and a valid session cookie, and can subsequently make authenticated requests using that session (role-gated per the mapped claim), despite the server having encountered — and logged — an internal error extracting the identity email.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-230)
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
```

**File:** core/sessions/oidcauth/oidc.go (L233-262)
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
```
