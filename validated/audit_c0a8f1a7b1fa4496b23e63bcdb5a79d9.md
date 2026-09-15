Confirmed: the code exactly matches the report. The `email, ok := claims["email"].(string)` block at `core/sessions/oidcauth/oidc.go` lines 226-230 writes an error response via `c.String` but has no `return` statement, while every sibling error branch in `handleTokenExchange` (lines 199-204, 207-212, 214-219, 220-225, 241-245, 266-271) does return. Execution falls through and uses the empty `email` string to build the RBAC role, insert an `oidc_sessions` row, audit-log a "successful" login, save the session cookie, and respond `200 {"success": true}` — exactly as described.

This is a genuine, reachable authentication-flow bug: it requires that OIDC auth is configured (an operator-enabled feature, not default-on), and that the identity provider's ID token lacks an `email` claim while other claims used for RBAC role mapping are present — a plausible edge case for many enterprise IdPs where `email` scope/claim is optional. The flaw is entirely in Chainlink's own control-flow handling (missing `return`), not in a malicious node/peer/dependency, and it results in a concrete in-scope impact: minting of a valid authenticated session (with a mapped RBAC role) tied to an empty/invalid identity, i.e., a node authentication/session-integrity bypass. This is not an operator/host-privileged bypass — it's triggerable by whoever completes the OAuth2 code exchange against the configured IdP, satisfying the "unprivileged client to node API" requirement once the feature is enabled.

Audit Report

## Title
Missing `return` after email-extraction failure allows OIDC session creation to proceed with an empty identity - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, after verifying the ID token, the handler type-asserts the `email` claim at `claims["email"].(string)`. If the assertion fails, the code logs an error and writes an HTTP 500 body via `c.String(...)` but does not `return`, unlike every other error branch in the same function, so execution continues and creates an authenticated session using the empty `email` value.

## Finding Description
At `core/sessions/oidcauth/oidc.go` lines 226-230, the `ok` check for the `email` claim omits the `return` that appears after all other error checks in `handleTokenExchange` (e.g., lines 199-204, 207-212, 214-219, 220-225, 241-245, 266-271). Because `ok` is false, `email` remains `""`, yet the code proceeds to: map RBAC role via `IDClaimsToUserRole` (lines 234-245), insert into `oidc_sessions` with `user_email=''` (lines 249-260), audit-log `AuthLoginSuccessNo2FA` with the empty email (line 262), set the session cookie (lines 264-271), and finally return `c.JSON(http.StatusOK, {"success": true})` (lines 273-275). None of the existing checks catch this because the function's control flow assumes every error branch returns, and this one silently doesn't.

## Impact Explanation
This produces a genuine authenticated session with a mapped RBAC role (Admin/Edit/Run/Read per `IDClaimsToUserRole`) tied to an empty `user_email`, with the client receiving a valid session cookie and `success: true`, despite an internal failure condition. This corrupts the node's session/identity integrity model and is an in-scope node authentication/session-handling defect (an error path fails to abort, letting an incomplete/invalid authentication proceed as if successful) — the same bug class as the referenced `SendDataWithRetry` analog.

## Likelihood Explanation
Exploitation requires the node operator to have OIDC authentication enabled (`NewOIDCAuthenticator` requires `ClientID`, `ClientSecret`, `ProviderURL`, `RedirectURL`, and role-claim names to be configured), and it requires the configured OIDC identity provider to return an ID token that omits the `email` claim while including claims sufficient for `IDClaimsToUserRole` to succeed. Any client completing (or partially completing) the OAuth2 authorization code exchange against `handleTokenExchange` reaches this path — no additional node-level privilege is required beyond having a valid authorization code from the configured IdP.

## Recommendation
Add `return` immediately after `c.String(http.StatusInternalServerError, "Failed to get email from claims")` at line 229 so the handler aborts before role mapping and session creation, matching the pattern used elsewhere in the function. Also correct the log statement at line 228, which references the stale `err` variable from the prior claims-parsing step rather than describing the failed type assertion. Additionally consider guarding the `oidc_sessions` insert error branch (lines 257-260), which has the same missing-`return` pattern.

## Proof of Concept
1. Configure the node with OIDC auth pointing at a test IdP that issues a valid, verifiable ID token containing the configured RBAC group claim (e.g., matching `AdminClaim()`) but without a top-level `email` claim.
2. Drive the OAuth2 authorization code flow to completion and POST the resulting `code`/`state` to the token-exchange endpoint served by `handleTokenExchange`.
3. Observe server-side: `claims["email"].(string)` assertion fails; `c.String(http.StatusInternalServerError, ...)` is written; execution continues (no `return`).
4. Observe an `oidc_sessions` row is inserted with `user_email=''`, `AuthLoginSuccessNo2FA` is audit-logged with an empty email, the response body contains both the 500 string write and the trailing `200 {"success": true}` JSON, and the session cookie set in that response is subsequently valid for authenticated requests. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L199-212)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L249-262)
```go
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
