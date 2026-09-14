## Analysis

I found an analog matching the report's bug class: **a control-flow error where the error-handling branch fails to abort execution**, causing the code to proceed as if the error hadn't occurred — directly analogous to `SendDataWithRetry` continuing/returning success-like behavior when it shouldn't due to mishandled error checking.

### Title
Missing `return` after email-extraction failure allows OIDC session creation to proceed with an empty/attacker-influenced identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
In `handleTokenExchange`, after verifying the ID token and extracting claims, the code type-asserts the `email` claim: [1](#0-0) 
If the assertion fails (`!ok`), the handler logs an error and writes an HTTP 500 response via `c.String(...)`, but **does not `return`**. Execution falls through and continues to build the RBAC role, insert an `oidc_sessions` row, and set the session cookie using the empty `email` value.

### Finding Description
Every other error branch in this same function correctly returns after writing an error response (e.g., the `id_token` missing check at [2](#0-1) , the token verification failure at [3](#0-2) ). The email-extraction branch is the only one missing this `return`, structurally the same class of bug as the reported issue: an error path that is supposed to halt/alter control flow silently doesn't, letting the caller (or in this case, downstream logic) proceed as though the operation succeeded.

Because `ok` is false, `email` is the zero value `""`. The handler continues to:
1. Map the OIDC group claims to an RBAC role via `IDClaimsToUserRole` [4](#0-3) .
2. Insert a new row into `oidc_sessions` with `user_email = ""` [5](#0-4) .
3. Audit-log a successful login with an empty email [6](#0-5) .
4. Set the Gin session cookie to the newly created (empty-email) session ID and respond with HTTP 200 `Success: true` [7](#0-6) .

The double HTTP write (`c.String` followed later by `c.JSON`) is also a Gin anti-pattern that produces a corrupted/concatenated response body, but the more serious problem is the missing `return`.

### Impact Explanation
An externally-facing OIDC callback endpoint is reachable by any client completing (or attempting to complete) the OAuth2 code exchange. If an identity provider's ID token is missing/malformed with respect to the `email` claim (attacker-controlled or misconfigured IdP scenario), the handler creates a valid, authenticated `oidc_sessions` row and issues a working session cookie with `Success: true`, associated with `user_email = ""`. This is a request/authentication-flow confusion bug: a failed authentication step results in an apparently successful session being minted, tied to an empty identity rather than being rejected. Downstream authorization code that keys off `user_email` for role/session lookups (e.g., `FindUser`, `Sessions`) could behave unpredictably for this empty-email session, and it pollutes the sessions table with unauthenticated/incompletely-identified sessions.

### Likelihood Explanation
Requires an OIDC identity provider (or a compromised/misconfigured one) to return an ID token without a top-level `email` claim while other claims (e.g., the RBAC group claim) are present and valid enough to pass `IDClaimsToUserRole`. This is a plausible edge case for OIDC providers where `email` is optional or omitted by default, or where a malicious/compromised IdP is used, making this reachable without needing to be a privileged actor — it only requires control over, or a bug in, the ID token response reaching this unprivileged, internet-facing OIDC callback handler.

### Recommendation
Add the missing `return` statement immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call so the handler aborts before creating a session, matching the pattern used by every other error branch in this function. Also fix the log statement referencing a stale `err` variable (it logs the wrong/unrelated error since `err` at that point is from the previous claims-parsing step, not from the failed type assertion).

### Proof of Concept
1. Stand up (or control) an OIDC IdP that returns a valid, verifiable ID token containing the configured RBAC claim (e.g., `AdminClaim`) but omitting the `email` claim.
2. Complete the OAuth2 authorization code flow against the Chainlink node's `/sessions/oidc/callback`-style token exchange endpoint (`handleTokenExchange`).
3. Observe: `claims["email"].(string)` assertion fails, `c.String(http.StatusInternalServerError, ...)` is written, but execution continues.
4. The handler proceeds to insert a row into `oidc_sessions` with `user_email=''`, calls `ginSession.Save()`, and finally returns `c.JSON(http.StatusOK, {"success": true})` — the client receives a success response with a valid session cookie despite the intended failure path.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L199-204)
```go
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L207-212)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L234-245)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L249-260)
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
```

**File:** core/sessions/oidcauth/oidc.go (L262-262)
```go
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
