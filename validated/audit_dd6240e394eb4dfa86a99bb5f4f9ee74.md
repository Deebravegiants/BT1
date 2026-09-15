Audit Report

## Title
Missing `return` after email-extraction failure allows OIDC session creation to proceed with an empty identity - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, when the `email` claim type-assertion fails, the handler writes an HTTP 500 response via `c.String(...)` but does not `return`, unlike every other error branch in this function [1](#0-0) . Execution falls through to compute the RBAC role, insert a new `oidc_sessions` row with `user_email=''`, and set a valid, authenticated session cookie with `Success: true`.

## Finding Description
Every other error path in `handleTokenExchange` returns immediately after writing the error response, e.g. the missing `id_token` check [2](#0-1)  and the token verification failure [3](#0-2) . The `email` extraction branch is the sole exception [1](#0-0) , so after a failed assertion `email` retains the zero value `""` and control flow continues into role mapping [4](#0-3) , session-row insertion [5](#0-4) , audit logging [6](#0-5) , and cookie issuance with a `200 OK` / `Success: true` response [7](#0-6) . Critically, `AuthorizedUserWithSession` resolves this session purely from the `oidc_sessions` row (`user_email`, `user_role`) without re-validating the email against the ID token, so the empty-email session is fully authenticated for whatever role was derived from the group claims [8](#0-7) . The role derivation in `IDClaimsToUserRole` is independent of the email claim, so a token lacking `email` (e.g., an IdP not configured to release the `email` scope) but containing valid group claims still yields a fully privileged, working session.

## Impact Explanation
This is an authentication/role bypass in the node's externally-facing OIDC callback: a failed identity-extraction step should reject the login but instead mints a live, cookie-backed session tied to an empty email while still carrying a legitimate RBAC role. This falls squarely into the in-scope "node API authentication or role bypass" impact category, since a client whose ID token omits `email` still ends up authenticated with `Success: true` rather than being rejected.

## Likelihood Explanation
No admin, operator, or host access is required by the client performing the callback flow — only that the configured/trusted OIDC IdP issues a signed ID token that passes verification but omits the `email` claim (a realistic scenario, e.g., an IdP not configured to release the `email` scope, or one where `email` is optional). The token signature is verified via `oi.provider.Verifier(...).Verify(...)`, so the attacker does not need to forge claims — only trigger a normal completion of the flow against an IdP that doesn't emit `email`, which is a plausible, non-privileged trigger path.

## Recommendation
Add `return` immediately after `c.String(http.StatusInternalServerError, "Failed to get email from claims")` so the handler aborts before creating any session, and correct the log statement to reference the actual assertion failure rather than the stale `err` variable from the prior claims-parsing step. Also fix the equivalent missing `return` after the `oidc_sessions` insert error handling at lines 257-260, which has the same fall-through defect.

## Proof of Concept
1. Configure the node's OIDC authenticator against an IdP that returns a valid, signature-verifiable ID token containing the configured RBAC group claim (e.g., matching `AdminClaim()`) but no `email` claim.
2. Drive the OAuth2 authorization-code flow to the node's `handleTokenExchange` endpoint with a valid `code` and matching `state`.
3. Observe: `claims["email"].(string)` fails, `c.String(http.StatusInternalServerError, "Failed to get email from claims")` is written, but execution continues past `oi.IDClaimsToUserRole`, inserts into `oidc_sessions` with `user_email=''`, and returns `HTTP 200 {"success": true}` along with a valid `webauth.SessionIDKey` cookie.
4. Use the returned cookie against an authenticated API route; `AuthorizedUserWithSession` resolves it to a `clsessions.User{Email: "", Role: <mapped role>}`, confirming the bypass.

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

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
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
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```
