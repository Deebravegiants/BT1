### Title
Missing `return` After Failed Email-Claim Extraction Lets OIDC Token Exchange Silently Continue and Issue an Authenticated Session - ([File: core/sessions/oidcauth/oidc.go])

### Summary
`handleTokenExchange` in the OIDC authenticator implements the login-callback flow that is reachable by any unauthenticated client hitting the OIDC exchange endpoint with an authorization code. Similar to the reported `WETHRouter.redeem()` bug — where a failing sub-operation (`mToken.redeem()`) is checked in form but the failure is not acted upon, letting later "success" logic run regardless — this handler checks whether the `email` claim exists, logs an error and writes an HTTP response on failure, but **does not `return`**, so the rest of the "successful login" logic (session persistence, audit log, `200 OK` response) executes unconditionally afterward.

### Finding Description
In `core/sessions/oidcauth/oidc.go`, `handleTokenExchange` extracts the OIDC ID-token claims and then reads the `email` claim: [1](#0-0) 

Unlike every other error branch in this same function (token exchange, ID-token verification, claims parsing, role mapping, session-save — each of which properly `return`s after writing an error response), this branch omits the `return` statement. Execution falls through to: [2](#0-1) 

and finally: [3](#0-2) 

so a persistent `oidc_sessions` row is inserted with `user_email = ""` (or whatever non-string `claims["email"]` produced), an audit log entry `AuthLoginSuccessNo2FA` is recorded, a valid session cookie (`SessionIDKey`) is set on the client, and the handler finally emits `ExchangeTokenResponse{Success: true}` with `http.StatusOK` — even though an error page (`c.String(http.StatusInternalServerError, ...)`) had already been written moments earlier in the same request. Gin allows multiple writes (with only a warning for the first “superfluous” header set), so the client-visible/observable result is the final write: a 200 OK success response carrying a working authenticated session tied to an empty-string identity, exactly like `WETHRouter.redeem()` completing the ETH transfer despite the earlier `mToken.redeem()` failure.

Note also that the same pattern (write error, no `return`) recurs for the DB insert error at lines 257-260, compounding the issue: a session that fails to persist is still handed to the client as if it succeeded. [4](#0-3) 

### Impact Explanation
This creates a real authentication/session-integrity defect reachable from an unprivileged, unauthenticated client performing the standard OIDC login callback:
- Any OIDC provider response (or attacker-controlled/misconfigured provider, or a race/edge case where the `email` claim is absent or non-string) results in the server minting and returning a *valid, cookie-backed* Chainlink node session under the empty-string user identity, while the caller receives an apparent HTTP 200 success.
- Because `user_email` in `oidc_sessions` collapses to the same empty string for every such failure, repeated occurrences produce colliding session rows under one identity, and any later `FindUser`/`AuthorizedUserWithSession` lookups keyed on that empty email create cross-request identity confusion.
- The role assigned to this bogus session is still derived from `IDClaimsToUserRole`, meaning if the mapped claims otherwise satisfy an admin/edit group check, an operator-facing authenticated session with elevated role could be granted without a bound, verifiable user identity — a session/identity confusion analogous to the token-redemption discrepancy in the original report (perceived success masking an inconsistent/incomplete state).

### Likelihood Explanation
The vulnerable code path is the primary OIDC login callback, executed on every login attempt through this authentication provider; it is not gated by any privileged role and is directly reachable by any client that can reach the gateway/web UI login flow. The probability of triggering the missing-claim branch depends on the OIDC IdP's claim configuration (some providers omit `email` unless a specific scope such as `email` or `profile` is requested), making this realistically triggerable through configuration edge cases or a malicious/compromised IdP response, without requiring any special privilege.

### Recommendation
Add the missing `return` statement immediately after writing the error response in the `email` claim check (mirroring every other error branch in the same function):
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, add a `return` after the DB-insert error at lines 257-260 so a failed session-creation is never followed by `ginSession.Save()` and a `200 OK` success response.

### Proof of Concept
1. Configure (or compromise) an OIDC identity provider such that the ID token/UserInfo claims returned during token exchange omit the `email` claim (e.g., the IdP scope configuration does not include `email`, or returns `email` as a non-string/null value).
2. An unauthenticated client completes the standard OIDC redirect flow and calls the token-exchange endpoint backing `handleTokenExchange` with a valid `code`/`state`.
3. Claim parsing (`idToken.Claims`, `ExtractIDClaimValues`) succeeds, but `claims["email"].(string)` fails the type assertion; the handler logs the error and writes an interim `500` body but does not `return`.
4. Execution proceeds to `IDClaimsToUserRole`, inserts a row into `oidc_sessions` with `user_email = ""`, sets the session cookie via `ginSession.Save()`, and finally overwrites the response with `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.
5. The client ends up holding a valid, cookie-authenticated session (verifiable via a subsequent authenticated request) despite the server having detected and logged a claim-validation failure — mirroring the "perceived success, actual failure" state divergence described in the original `redeem()` report.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-231)
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
```

**File:** core/sessions/oidcauth/oidc.go (L247-262)
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
```

**File:** core/sessions/oidcauth/oidc.go (L264-276)
```go
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
