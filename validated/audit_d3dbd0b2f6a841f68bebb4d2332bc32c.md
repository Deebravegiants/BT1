Nothing in scope exclusions rules out this finding. The code confirms the claim exactly as described: both missing `return` statements exist and cause fall-through execution with unvalidated/failed state.

Audit Report

## Title
Missing `return` on unchecked claim/error checks in `handleTokenExchange` lets OIDC login proceed after a failed check, writing/authenticating a session with unvalidated data - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `handleTokenExchange`, the `email, ok := claims["email"].(string)` failure branch and the `oidc_sessions` DB insert failure branch both write an HTTP error response via `c.String(...)` but omit the `return` statement present in every other error branch of this function. As a result, execution falls through to role-based session issuance, a false "successful login" audit entry, and a saved authenticated session cookie, even though the email claim was missing or the session row failed to persist.

## Finding Description
`handleTokenExchange` correctly returns after every other failure check (state mismatch, token exchange failure, missing `id_token`, ID token verification failure, claims parsing failure, `ExtractIDClaimValues` failure, role mapping failure, and session save failure) [1](#0-0) . However, two branches break this pattern:

1. The email-claim extraction check writes an error string but does not `return`: [2](#0-1) 

2. The `oidc_sessions` insert failure check writes an error string but does not `return`: [3](#0-2) 

Because `email, ok := claims["email"].(string)` leaves `email == ""` when the assertion fails, and because the DB insert error doesn't halt execution, the handler proceeds to fire an `AuthLoginSuccessNo2FA` audit event, set the session cookie, and return `Success: true`, regardless of whether the email claim was present or the DB write succeeded: [4](#0-3) 

## Impact Explanation
This breaks the invariant that a `AuthLoginSuccessNo2FA` audit event and an issued session cookie correspond to a fully-validated, successfully-persisted authentication state. A caller can receive `{"success": true}` and a valid session cookie (`webauth.SessionIDKey`) tied to a `clSession.ID` that either was never persisted in `oidc_sessions` (on DB insert failure) or was persisted with `user_email = ''` (on missing email claim), and an audit trail falsely records login success. This is a genuine authentication/session-integrity and audit-integrity defect in the node's auth flow, matching the in-scope "node API authentication/role bypass"-adjacent impact category.

## Likelihood Explanation
The missing-email-claim branch is reachable by controlling/misconfiguring the ID token claims returned during the OIDC exchange (e.g., a rogue or misconfigured IdP whose ID token omits `email` while still passing signature verification), and is triggered purely through the normal, unauthenticated `handleSignIn` → `/callback` flow with no operator or admin privileges required. The DB-insert-failure branch requires a transient datastore error, which is less attacker-controlled but still a legitimate defect that leads to a false success response and audit event on any transient DB error during login.

## Recommendation
Add `return` immediately after both error-response calls:
- After `c.String(http.StatusInternalServerError, "Failed to get email from claims")` (line 229).
- After `c.String(http.StatusInternalServerError, "Error creating session")` (line 259).

This aligns these two branches with the `return`-after-error pattern used consistently everywhere else in `handleTokenExchange`.

## Proof of Concept
1. Stand up/point the OIDC provider configuration at a test IdP (or intercept token exchange in an integration test) that returns a valid, signature-verifiable ID token whose claims omit `email` but include valid RBAC group claims for `ClaimName()`.
2. Complete the OIDC flow: `GET` the sign-in redirect endpoint, then `POST /callback` (routed to `handleTokenExchange`) with the resulting `code`/`state`.
3. Observe that `claims["email"].(string)` assertion fails, an HTTP 500 body ("Failed to get email from claims") is written, but execution continues: `oi.IDClaimsToUserRole` runs, the `oidc_sessions` row is inserted with `user_email = ''`, `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)` fires, `ginSession.Save()` sets an authenticated session cookie, and a trailing `c.JSON(http.StatusOK, {"success":true})` is appended after the earlier error body.
4. A Go handler-level test invoking `handleTokenExchange` with a mocked `oi.provider`/`idToken.Claims` that omits `email` and asserting on the response writer's body/status and on the resulting session cookie/audit log call would confirm this fall-through behavior directly.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L177-224)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L250-260)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L262-276)
```go
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
