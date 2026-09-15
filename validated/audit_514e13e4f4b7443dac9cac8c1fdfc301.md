This confirms the code exactly as claimed. The two missing `return` statements are present in the actual code at lines 229 and 259.

Analysis of the claim:

1. **Line 226-230**: `claims["email"].(string)` assertion fails → error logged, `c.String(500, ...)` written, but no `return`. Execution continues to compute `role` (line 234, independent of `email`) and then inserts the session row using the empty `email` string.
2. **Line 247-260**: The `ExecContext` insert error is also swallowed without `return` — execution continues to set the session cookie and returns `Success: true`.
3. This is inconsistent with every other error branch in the same function, all of which correctly `return` after writing the error response (lines 195, 203, 211, 218, 224, 244, 270).
4. `AuthorizedUserWithSession` at lines 349-391 confirms sessions are looked up purely by session ID, so a session with an empty `user_email` still functions as a valid authenticated session bound to a `role`.
5. This is reachable by an unprivileged actor completing the OIDC exchange against a misconfigured or non-standard IdP response lacking an `email` claim — no operator/admin access required, and it's part of the public-facing `/oidc-login` token exchange endpoint.
6. The impact is concrete: authentication/session integrity corruption (session created with blank `user_email` but valid role-based access), silent masking of an internal error from the client (still returns HTTP 200 `Success: true`), and audit log corruption — this matches the "node API authentication" impact category.

The claim is well-supported by direct code inspection with no mitigating logic found elsewhere (e.g., no `c.Abort()`, no post-check on `ok`/`err` before proceeding).Confirmed — no `c.Abort()` calls exist anywhere in this file, so nothing stops gin's handler chain from proceeding after the missing `return` statements. The vulnerability is real and exactly as described.

Audit Report

## Title
Missing `return` after failed `email` claim assertion allows OIDC session creation with empty/wrong email and DB write error swallowed - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, the type assertion of the `email` claim at line 226 checks `ok` and logs/writes an HTTP error, but omits `return`, so execution falls through and creates a persisted OIDC session using an empty `email` string. A second identical pattern at line 257 swallows the `ExecContext` insert error the same way, after which the code still sets the session cookie and returns `Success: true`.

## Finding Description
`handleTokenExchange` extracts `email` via `claims["email"].(string)` and on failure only logs and writes a 500 body without `return` [1](#0-0) , unlike every other validation branch in the same function which correctly returns on failure [2](#0-1) . Execution proceeds to compute `role` (independent of `email`) and insert a new `oidc_sessions` row using the (possibly empty) `email`, and the `ExecContext` error branch also lacks a `return` [3](#0-2) . The handler then sets the session cookie and reports success regardless [4](#0-3) . No `c.Abort()` is used anywhere in this file to compensate for the missing `return`s, and `AuthorizedUserWithSession` looks up sessions purely by session ID, meaning a session row with a blank `user_email` still resolves to a fully functional authenticated `clsessions.User` bound to the mapped `role` [5](#0-4) .

## Impact Explanation
An externally authenticated but claim-malformed OIDC exchange results in a valid session cookie backed by a DB row with an empty/incorrect `user_email`, while the client still receives HTTP 200 `Success: true`. This corrupts the audit trail (`audit.AuthLoginSuccessNo2FA` logged with empty email) and the identity-to-session binding assumption relied on elsewhere in the authenticator, and silently masks internal errors (both the missing claim and a failed DB insert) from both the caller and error monitoring. This falls under node API authentication/session integrity — a legitimate in-scope impact class, though it does not directly enable privilege escalation beyond what the IdP-derived group claims already grant.

## Likelihood Explanation
Triggerable by any actor able to complete the OAuth2/OIDC code exchange against the configured provider when that provider's ID token claims omit `email` or return a non-string value — reachable via the public-facing `/oidc-login` token exchange endpoint without any special node/DON privilege. Likelihood is moderate since it depends on IdP claim behavior (e.g., certain provider configurations or claim-mapping quirks), but it requires no host, database, or operator access.

## Recommendation
Add `return` immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call, matching the pattern used by all other validation branches in this function. Likewise add `return` after the `ExecContext` error branch so a failed session insert does not proceed to set the session cookie and report `Success: true`.

## Proof of Concept
1. Configure OIDC login against an IdP that returns valid, verifiable ID token claims (passing `Verify`, `ExtractIDClaimValues`, `IDClaimsToUserRole`) but omits the `email` claim or returns a non-string value.
2. Complete the `/oidc-login` flow, invoking `handleTokenExchange` with a valid `code`/`state`.
3. `claims["email"].(string)` fails (`ok=false`); a 500 body is written but execution continues.
4. `role` is derived successfully from group claims; a row is inserted into `oidc_sessions` with `user_email=''`; the session cookie is set; the handler responds `200 {"success": true}`.
5. Verify via a follow-up authenticated request that `AuthorizedUserWithSession` returns a `clsessions.User{Email: "", Role: <mapped role>}` for the issued cookie, demonstrating a functioning session with corrupted identity data.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L199-224)
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

**File:** core/sessions/oidcauth/oidc.go (L247-260)
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

**File:** core/sessions/oidcauth/oidc.go (L349-382)
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
```
