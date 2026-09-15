I confirmed the exact code in the repository matches the claim precisely.Audit Report

## Title
Missing `return` after failed email-claim extraction lets OIDC login flow continue and issue a valid authenticated session - (File: `core/sessions/oidcauth/oidc.go`)

## Summary
In `oidcAuthenticator.handleTokenExchange`, when the `email` claim in a verified OIDC `id_token` is missing or not a string, the handler logs the error and writes an HTTP 500 response but fails to `return`, so execution falls through and completes the login flow anyway. This confirmed missing-`return` bug causes the server to both signal failure (500) and simultaneously grant a fully functional, cookie-backed session (200 `Success: true`) with a database row inserted into `oidc_sessions`.

## Finding Description
The code at [1](#0-0)  performs the type assertion `email, ok := claims["email"].(string)`. When `ok` is `false`, the `email` variable is left as the Go zero value (`""`), the error is logged, and `c.String(http.StatusInternalServerError, ...)` is called, but there is no `return` statement, unlike every other error branch in the same function (e.g. the `id_token` extraction failure at [2](#0-1) , verification failure at [3](#0-2) , and claim parsing failure at [4](#0-3) , all of which correctly `return` after writing an error response).

As a result, execution proceeds to role mapping via `IDClaimsToUserRole` [5](#0-4) , insertion into `oidc_sessions` with `strings.ToLower(email)` (an empty string) [6](#0-5) , an `audit.AuthLoginSuccessNo2FA` audit event recorded with an empty email [7](#0-6) , session cookie assignment via `ginSession.Set`/`ginSession.Save()` [8](#0-7) , and a final `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` response [9](#0-8) . The client thus receives contradictory signals (a written 500 body followed by a 200 JSON body) and, more importantly, ends up with a valid, cookie-authenticated session and a persisted `oidc_sessions` row despite the developer's evident intent to abort on this error path.

Note that role assignment itself is derived independently from group claims via `IDClaimsToUserRole` and is not weakened by the missing email; the token's cryptographic signature is also verified earlier via `oi.provider.Verifier(...).Verify(...)`. So this bug does not allow forging a session without ever authenticating against the real, configured IdP — the user must still complete the actual OIDC login with valid credentials and applicable group claims. The concrete consequence of the missing `return` is that the intended fail-closed behavior (reject login when email extraction fails) is bypassed: the login still succeeds, `AuthorizedUserWithSession` ( [10](#0-9) ) will subsequently return a `User{Email: ""}` for that session, corrupting per-user identity/audit records tied to that session while granting a working RBAC-scoped session.

## Impact Explanation
This is a genuine, reproducible code defect: the missing `return` breaks the intended fail-closed contract of the error branch and lets a login flow complete despite an internal validation failure, corrupting the persisted `user_email` value in `oidc_sessions` and the audit log entry for that login. This falls under the node API authentication-integrity impact class, since it demonstrates that an internal error/edge-case branch of the authentication callback does not actually gate session issuance as intended — mirroring the CVE-2016-3085 bug class cited. However, the practical severity is bounded: the session's RBAC role is still derived correctly and independently from the token's verified group claims, so this bug does not, by itself, allow escalation to a role the authenticated IdP account does not already hold, nor does it allow bypassing signature verification of the `id_token`.

## Likelihood Explanation
Triggering this requires successfully completing the real OIDC redirect/callback flow against the operator's configured IdP with a validly-signed `id_token` that omits (or malforms) the `email` claim — e.g., a scope/claims misconfiguration, a machine/service account without an email attribute, or an IdP that omits `email` for certain accounts. This is a realistic, not purely theoretical, edge case in production OIDC deployments and requires no privileged access to the Chainlink node itself.

## Recommendation
Add an explicit `return` immediately after the failed `email` claim extraction:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Also audit the other non-returning error branches in the same function (`oi.ds.ExecContext` insert failure at line 257-260 also lacks a `return`) for the same missing-`return` pattern, since this class of bug is easy to reintroduce across the OIDC/LDAP authenticators.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'oidc'` with a real OIDC provider whose issued `id_token` for the test account omits the `email` claim (or returns a non-string value), while including the configured role-mapping group claim (e.g., `AdminClaim`).
2. Complete the standard flow: `GET /oidc-login`-style redirect (via `handleSignIn`) → provider login → callback → `POST` the resulting `code`/`state` to the token-exchange endpoint (`handleTokenExchange`).
3. Observe the response body/behavior: the handler writes an HTTP 500 body for "Failed to get email from claims" but continues; a row is inserted into `oidc_sessions` with `user_email = ''`; the session cookie is set (`ginSession.Save()`); and the handler ultimately also writes `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.
4. Confirm the issued session cookie is valid for subsequent authenticated node API calls via `AuthorizedUserWithSession`, and that the corresponding audit log / `oidc_sessions.user_email` is empty/corrupted despite the earlier logged failure.

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

**File:** core/sessions/oidcauth/oidc.go (L214-219)
```go
	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
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

**File:** core/sessions/oidcauth/oidc.go (L264-271)
```go
	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L273-275)
```go
	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
```

**File:** core/sessions/oidcauth/oidc.go (L351-381)
```go
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
```
