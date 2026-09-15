Confirmed: `AuthorizedUserWithSession` in `core/sessions/oidcauth/oidc.go` queries `oidc_sessions` by `sessionID` to authorize subsequent requests [1](#0-0) , meaning if the `INSERT INTO oidc_sessions` fails at line 250-260 but the code doesn't `return`, the cookie is still issued with `clSession.ID`, but that ID won't exist in the DB — so subsequent authenticated requests using that cookie will fail with `ErrUserSessionExpired`/"no rows", not actually granting unauthorized access. This makes the DB-insert-failure branch a low-impact bug (misleading "success" response, but no working session is actually created). For the missing-email branch, the role is still derived from OIDC-verified claims via `IDClaimsToUserRole`, and the session row IS persisted successfully with `user_email=''`, so the session cookie *does* work with an empty-email identity.

Audit Report

## Title
Missing `return` after failed email-claim extraction in OIDC callback allows session issuance with corrupted (empty) identity - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, when the `email` claim is missing or not a string, the handler logs the error and writes an HTTP 500 body but does not `return`, unlike every other error branch in the function [2](#0-1) . Execution falls through, persists a valid `oidc_sessions` row with `user_email=''`, issues a working session cookie, and returns HTTP 200 `{"success": true}` [3](#0-2) .

## Finding Description
Every other failure branch in `handleTokenExchange` (e.g. token exchange failure, ID token verification failure, claims parsing failure) calls `return` immediately after writing the error response [4](#0-3) . The `email, ok := claims["email"].(string)` branch breaks this pattern: it logs the error and writes a 500 status via `c.String`, but does not return, so `c.String` is called and then subsequent `c.JSON` in the same handler overrides the response with `200 OK` [2](#0-1) . The role mapping via `IDClaimsToUserRole` proceeds using the already ID-token-verified group claims (independent of `email`), and the `INSERT INTO oidc_sessions` successfully persists a row keyed by `strings.ToLower(email)` == `""` together with a valid role [5](#0-4) . Because the DB row is created, `AuthorizedUserWithSession` will subsequently find and authorize this session on later requests, returning `clsessions.User{Email: "", Role: role}` [1](#0-0) . The audit log entry `AuthLoginSuccessNo2FA` is also recorded with `email: ""` [6](#0-5) .

By contrast, the separately-flagged `INSERT INTO oidc_sessions` failure branch (lines 257-260) is lower impact than described in the report: because `AuthorizedUserWithSession` looks up the session by ID in the `oidc_sessions` table [7](#0-6) , if the insert genuinely fails, the returned session cookie references a non-existent DB row and subsequent authenticated requests using that cookie will fail with `ErrUserSessionExpired`. This branch is a misleading-response bug (client told `Success: true` for a session that doesn't function), not a working unauthorized session.

## Impact Explanation
The email-claim omission path grants a legitimately-authenticated (valid, ID-token-verified) OIDC user a working, role-bearing session and DB record under an empty-string identity rather than their real email. This corrupts the audit trail (`AuthLoginSuccessNo2FA` with `email: ""`) and any downstream logic keyed by session email (e.g., per-user tracking, admin visibility into who holds edit/admin/run privileges) for a session that otherwise carries real privileges determined by `IDClaimsToUserRole`. This does not bypass authentication or elevate privilege beyond what the verified ID token's group claims already grant — the role itself is unaffected. The impact is accountability/traceability corruption on the auth boundary, not new access; it maps most closely to a low-severity audit/identity-integrity issue rather than authentication bypass or fund/job-run compromise.

## Likelihood Explanation
Reachable by any client that completes the OIDC exchange flow against an IdP/configuration where the `email` claim is absent or not a string (e.g., `email` scope not granted) — no special privilege is required, and this is plausible under legitimate IdP misconfiguration or non-standard OIDC providers, though not attacker-controlled arbitrarily (the ID token is cryptographically verified before claims are read, so an attacker cannot simply forge a token to omit email at will — the IdP must actually be configured to omit it).

## Recommendation
Add `return` immediately after the failed email-claim branch, matching the pattern used elsewhere in the function:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Also add `return` after the `INSERT INTO oidc_sessions` failure branch to avoid emitting a misleading `Success: true` response for a session that was never persisted.

## Proof of Concept
1. Stand up (or mock) an OIDC provider that issues a valid, signed ID token whose claims omit `email` (or set it to a non-string), while including valid group claims mapping to a role.
2. Complete the `/sessions/exchange`-equivalent flow driving `handleTokenExchange` with a valid `code`/`state`.
3. Observe: `claims["email"].(string)` assertion fails; the handler logs and writes a 500 body but does not return.
4. Observe the response is ultimately `200 OK {"success": true}`, a session cookie is set, and a corresponding `oidc_sessions` row exists with `user_email=''`.
5. Use the returned cookie against an authenticated endpoint and confirm `AuthorizedUserWithSession` succeeds, returning a `User{Email: "", Role: <role>}`.
6. A Go unit test invoking `handleTokenExchange` with a test `oidc.Provider`/`Verifier` stub returning claims without `email`, asserting the final response is 200-success and that an `oidc_sessions` row with empty `user_email` was created, would concretely prove this.

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L247-275)
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
```

**File:** core/sessions/oidcauth/oidc.go (L356-381)
```go
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
