### Title
Missing `return` on error/failure branches in OIDC token exchange handler allows session creation and success response after failed validation - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The unchecked-return-value bug class reported for `IComptroller.exitMarket()`/`enterMarkets()` (ignoring a failure signal and proceeding as if the call succeeded) has a direct analog in `oidcAuthenticator.handleTokenExchange` in `core/sessions/oidcauth/oidc.go`. Two failure conditions are detected, logged, and an error response is written, but execution is **not** halted with a `return`, so the handler falls through and completes the "successful login" code path anyway.

### Finding Description
In `handleTokenExchange` (`core/sessions/oidcauth/oidc.go:163-276`), reachable by any unauthenticated client hitting the OIDC callback endpoint with a validly-signed ID token from the configured IdP:

1. Email-claim extraction failure is not fatal: [1](#0-0) 
If `claims["email"]` is missing or not a string, the code logs an error and writes an HTTP 500 body via `c.String(...)`, but there is no `return`. Execution continues into role mapping and session creation using an empty `email` string.

2. The session-insert database error is not fatal either: [2](#0-1) 
If the `INSERT INTO oidc_sessions ...` fails, the code logs the error and writes an HTTP 500 body, but again omits `return`. Execution falls through to: [3](#0-2) 
which audits a successful login (`audit.AuthLoginSuccessNo2FA`), sets the session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`), saves the gin session, and finally writes a second, contradicting `http.StatusOK` JSON success response.

This mirrors the reported bug class exactly: a call that can signal failure (here, a type-assertion `ok` check and a SQL `err`) has its failure path partially handled (logged) but the caller does not enforce the "must be success/no-error" invariant before continuing privileged follow-on actions (setting an authenticated session cookie, auditing a successful login).

### Impact Explanation
- The client's browser receives conflicting writes to the same `ResponseWriter` (a 500 body followed by an attempted 200 JSON — Gin will typically only honor the first write, but a `Set-Cookie` header for an authenticated session is still attached to the response before the final write attempt is made).
- More importantly, in the email-extraction-failure case, a browser session cookie tied to `webauth.SessionIDKey` is issued and persisted via `ginSession.Save()` even though the server's own audit trail and logs recorded the login as failed/errored. If the DB insert for `oidc_sessions` succeeded (which is independent of the email-extraction check), that session row is now keyed to an empty `user_email` while carrying a real, attacker-influenced RBAC `role` derived from `IDClaimsToUserRole`. Because `AuthorizedUserWithSession` (`core/sessions/oidcauth/oidc.go:349-391`) trusts whatever `user_email`/`user_role` are stored against the session ID, a subsequently authenticated request using that cookie is granted the mapped role while being associated with an empty/incorrect identity, which breaks the assumption that every authenticated session correctly attributes actions to the OIDC-verified email. This is a correctness/authentication-integrity break (session issued despite a failed identity-claim check), rather than a full authentication bypass, since the attacker must still complete real OIDC token exchange and hold group-claim membership.
- The second finding (falling through after a failed DB insert) is lower impact: the client is told "Error creating session" (500) yet the server sets a cookie referencing a session row that may or may not actually exist, which can cause a confusing "half-authenticated" client state and inconsistent auditing.

### Likelihood Explanation
Reaching this code path only requires completing a normal OIDC `code`/`state` exchange against the configured identity provider — no special privilege is needed on the Chainlink node side, and it's part of the standard login flow (`/sessions/oidc/callback`-style handler wired via `handleTokenExchange`). The specific missing-claim condition depends on IdP/token contents (an ID token lacking an `email` claim, or one where the claim is not a JSON string), which is plausible for misconfigured or third-party IdP integrations, or a malicious/compromised IdP under the operator's OIDC trust chain.

### Recommendation
Add `return` immediately after both error-handling blocks in `handleTokenExchange`:
- After writing the 500 response for the missing/invalid `email` claim (`core/sessions/oidcauth/oidc.go:226-230`), add `return` before proceeding to role mapping/session creation.
- After writing the 500 response for the `oidc_sessions` insert failure (`core/sessions/oidcauth/oidc.go:257-260`), add `return` before the audit log, cookie set, and final success JSON response.

More generally, apply the same "must check and short-circuit on failure/non-nil-error" discipline that the original report recommends for `IComptroller.exitMarket`/`enterMarkets`: every error/`ok` check in an authentication or session-issuance code path must be immediately followed by a `return` (or equivalent abort), never merely logged.

### Proof of Concept
1. Configure OIDC login with a real IdP but craft/observe a scenario where the ID token's claims do not include an `email` field as a string (e.g., IdP configured without the `email` scope, or a token where `email` is `null`/an object).
2. Complete the normal `/sessions/oidc/...` sign-in redirect and callback flow with a valid `code` and matching `state`.
3. Observe in `handleTokenExchange` that:
   - `claims["email"].(string)` type assertion fails (`ok == false`),
   - the handler logs "Failed to get email from claims" and writes a 500 response,
   - execution nonetheless proceeds to `IDClaimsToUserRole`, inserts a row into `oidc_sessions` with `user_email = ''`, sets `ginSession.Set(webauth.SessionIDKey, clSession.ID)`, calls `ginSession.Save()`, and attempts a `200 OK` JSON response.
4. Inspect the response headers: a valid session cookie is present despite the logged failure, and a subsequent authenticated request using that cookie succeeds via `AuthorizedUserWithSession`, returning a `clsessions.User{Email: "", Role: <mapped role>}`. [4](#0-3) [5](#0-4)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-276)
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
