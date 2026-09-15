## Title
OIDC callback `state` parameter is not reliably invalidated on failure paths, permitting replay of the sign-in callback - (File: `core/sessions/oidcauth/oidc.go`)

## Summary
The `handleTokenExchange` handler in the Chainlink node's OIDC authentication module checks the OAuth2 `state` value against the value stored in the session and calls `ginSession.Delete("state")` immediately after a successful comparison, but the deletion is never persisted unless the handler reaches the very end of the function and calls `ginSession.Save()`. Every error branch in between (token exchange failure, missing `id_token`, ID token verification failure, claims-parsing failure, or role-mapping failure) returns without calling `Save()`, so the cookie-backed session on the client is never rewritten to drop the `state` value. This mirrors the class of bug in CVE-2020-14302, where a Keycloak endpoint kept accepting multiple invocations of the same `state` parameter after an external IdP redirect, enabling replay of the authentication callback.

## Finding Description
`handleSignIn` generates a random `state`, stores it in the gin session, and persists it with `session.Save()`: [1](#0-0) 

`handleTokenExchange` then validates the returned `state` against the stored value and calls `ginSession.Delete("state")`: [2](#0-1) 

However, that deletion is only made durable if execution reaches the final `ginSession.Save()` call at the very end of the success path: [3](#0-2) 

Between those two points, there are multiple early `return` statements on error that never call `Save()`:
- token exchange failure [4](#0-3) 
- missing `id_token` field [5](#0-4) 
- ID token verification failure [6](#0-5) 
- claims parsing / role-mapping failure [7](#0-6) 

Because the gin session used here is cookie-backed and mutations are only written back to the client via `Save()`, any of these failure paths leaves the client's session cookie unchanged — i.e., the original `state` value is still present and valid in the cookie. This means the same `state` value can be presented again to `/oidc-exchange` in a subsequent request (e.g., with a different `code` from a new authorization attempt), and the server will accept it as valid because the "used" state was never actually invalidated on the client-visible session.

## Impact Explanation
This weakens the intended CSRF/replay protection that the OAuth2 `state` parameter is supposed to provide for the sign-in callback endpoint exposed at `/oidc-login` and `/oidc-exchange`: [8](#0-7)  Rather than being strictly single-use, the same `state` value can be replayed across multiple callback invocations whenever an earlier attempt failed prior to the final session save, directly matching the bug class described in CVE-2020-14302 (a "state" parameter accepting multiple invocations after authentication).

## Likelihood Explanation
Exploitation still requires the attacker to obtain a valid authorization `code` from the real IdP for the exchange to actually succeed (Exchange() calls the IdP's token endpoint, which independently enforces code single-use), so this does not by itself grant a full authentication bypass. The practical effect is a robustness/defense-in-depth gap in the CSRF-state protection rather than a directly exploitable session-hijack primitive, since the `state` value has 256 bits of entropy and is not otherwise disclosed to third parties.

## Recommendation
Persist the `state` invalidation (`ginSession.Save()`) immediately after `ginSession.Delete("state")`, before proceeding with the token exchange, so that the state can never be presented again regardless of what happens later in the handler. Consider also binding `state` to a short expiry and clearing it via a dedicated `Save()` call at each early-return branch, rather than relying on a single terminal `Save()`.

## Proof of Concept
1. Initiate `/oidc-login`; the response cookie contains a session with `state = S`.
2. Send `/oidc-exchange` with `{state: S, code: bad_code}` — this passes the state check, calls `Delete("state")` in memory, then fails at `Exchange()` and returns without `Save()`. The response cookie remains unchanged and still contains `state = S`.
3. Complete a new authorization flow with the IdP that yields a fresh, valid `code2`, but reuse the still-valid browser cookie from step 1/2.
4. Send `/oidc-exchange` with `{state: S, code: code2}` — the server still finds `state = S` in the (unmodified) session cookie and accepts it, despite this being the second logical invocation of the same `state` value.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L147-161)
```go
func (oi *oidcAuthenticator) handleSignIn(c *gin.Context) {
	// generate state and store on session
	state := oi.generateState()
	session := sessions.Default(c)
	session.Set("state", state)
	err := session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save session"})
		return
	}

	// redirect to provider
	url := oi.oauth2Config.AuthCodeURL(state, oauth2.AccessTypeOffline)
	c.Redirect(http.StatusFound, url)
}
```

**File:** core/sessions/oidcauth/oidc.go (L174-184)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L187-196)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L198-204)
```go
	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L206-212)
```go
	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L214-245)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L658-664)
```go
func (oi *oidcAuthenticator) ExtendRouter(api *gin.RouterGroup) error {
	api.GET("/oidc-enabled", oi.handleCheckEnabled)
	api.GET("/oidc-login", oi.handleSignIn)
	api.POST("/oidc-exchange", oi.handleTokenExchange)

	return nil
}
```
