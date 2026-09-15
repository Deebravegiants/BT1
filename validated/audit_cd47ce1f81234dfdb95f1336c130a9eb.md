Audit Report

## Title
OIDC token exchange handler fails to abort on missing email claim, creating an authenticated session despite the detected validation failure - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `oidcAuthenticator.handleTokenExchange`, the missing/non-string `email` claim check at [1](#0-0)  logs an error and writes an HTTP 500 body but does not `return`, unlike every other error branch in the same function (e.g. the `id_token` extraction check and the token verification/claims parsing checks) which correctly `return` after writing their error responses. Execution therefore falls through to session creation and persistence with `email` left as the empty string, while the role derived independently from group claims is still applied and a valid session cookie is issued.

## Finding Description
The claim is accurate as verified against the actual source. `handleTokenExchange` reads the `email` claim and, on failure, only logs and calls `c.String(...)` without a `return` statement [1](#0-0) . This is inconsistent with the surrounding pattern in the same function, where every other validation failure (`id_token` missing, ID token verification failure, claims parsing failure, ID claim extraction failure, role mapping failure) properly `return`s immediately after writing the error response, e.g. [2](#0-1)  and [3](#0-2) .

Execution then proceeds to role mapping (independent of the email claim) and to session persistence, inserting a row into `oidc_sessions` with `user_email` set to the lowercased empty string and the mapped role [4](#0-3) , followed by saving the session cookie and returning `200 OK` [5](#0-4) . This session is later fully honored by `AuthorizedUserWithSession`, which trusts `user_role`/`user_email` stored at creation time without further correlation [6](#0-5) . No other check in the codebase re-validates that a non-empty email was associated with the session before honoring it, so the broken assumption ("an error response implies the request was rejected") is not compensated for elsewhere.

## Impact Explanation
This is a genuine node API authentication logic flaw: a detected identity-assertion validation failure does not abort issuance of a working, role-bearing session, contrary to the intended behavior mirrored by every sibling error branch in the function. The role attached to the resulting session is still derived from cryptographically verified group claims (via `IDClaimsToUserRole`), so this is not a full unauthenticated bypass, but it does allow a session to be created and persisted with a corrupted identity (`user_email = ""`) whenever the IdP's verified token/claims response omits or misencodes `email`. This can cause cross-session collisions on the empty-email value in `oidc_sessions` and incorrect data in audit logs (`AuthLoginSuccessNo2FA` recorded with an empty email), undermining the auditability and identity-correctness guarantees of the authentication subsystem.

## Likelihood Explanation
Reaching this path requires completing the real OIDC exchange flow (`handleSignIn` → `handleTokenExchange`) with a token that passes signature verification and includes a valid group claim mapped to a role, but omits or misencodes the `email` claim — a state achievable through legitimate IdP configurations where `email` is optional/unscoped, or IdP misconfiguration. This does not require attacker forgery of the signed token, but relies on completing a real authentication flow, which any user with valid IdP credentials satisfying the configured group/role claim can trigger without additional privilege.

## Recommendation
Add the missing `return` immediately after writing the error response in the `email` claim check:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally review the `oi.ds.ExecContext` error branch at [7](#0-6) , which also writes an error response without `return`, allowing the session cookie to be set even if the DB insert failed.

## Proof of Concept
1. Configure the OIDC provider such that the returned ID token includes a valid group claim used for role mapping (satisfying `ExtractIDClaimValues`/`IDClaimsToUserRole`) but omits or sets a non-string `email` claim.
2. Complete the OIDC flow: `GET` sign-in endpoint (state stored) → IdP redirect → `POST` to the token exchange endpoint handled by `handleTokenExchange` with the authorization code.
3. Observe the server logs `"Failed to get email from claims..."` and writes HTTP 500 body, but continues: inserts a row into `oidc_sessions` with `user_email = ''` and the mapped `user_role`, sets the session cookie via `ginSession.Save()`, then writes `200 OK` `{"success":true}`.
4. Use the resulting session cookie against an authenticated endpoint; `AuthorizedUserWithSession` returns a valid `User{Role: <mapped role>}` despite the earlier detected failure, confirmed at [8](#0-7) .

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

**File:** core/sessions/oidcauth/oidc.go (L220-225)
```go
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
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

**File:** core/sessions/oidcauth/oidc.go (L349-380)
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
```
