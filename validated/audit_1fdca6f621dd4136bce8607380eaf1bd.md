The code exactly matches the claim: at `core/sessions/oidcauth/oidc.go` lines 226-230, after `email, ok := claims["email"].(string)` fails, the handler writes an HTTP 500 via `c.String(...)` but does not `return`, so execution falls through to `IDClaimsToUserRole`, session creation via `INSERT INTO oidc_sessions`, `ginSession.Save()`, and a final `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.Audit Report

## Title
Missing `return` after failed email-claim extraction allows OIDC session creation for an unbound/empty identity - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `handleTokenExchange`, when the OIDC ID token's `email` claim is missing or not a string, the handler writes an HTTP 500 response but fails to `return`, unlike every other error branch in the function. Execution continues to `IDClaimsToUserRole`, inserts a row into `oidc_sessions` with `user_email = ''`, saves the session cookie, and finally overwrites the response with HTTP 200 `{Success: true}`.

## Finding Description
The claim accurately reflects the code. At [1](#0-0) , `email, ok := claims["email"].(string)` is checked, and on failure the code calls `c.String(http.StatusInternalServerError, "Failed to get email from claims")` but does not `return`, in contrast to every preceding error branch in the same function (e.g. [2](#0-1) ). Execution then proceeds to role mapping via `IDClaimsToUserRole` [3](#0-2)  and session persistence with `strings.ToLower(email)` (empty string) inserted into `oidc_sessions` [4](#0-3) , followed by cookie save and a final 200 JSON response [5](#0-4) . `AuthorizedUserWithSession` subsequently trusts `user_email`/`user_role` from `oidc_sessions` verbatim, with no cross-check against the `users` table [6](#0-5) .

The role granted to this empty-identity session is still derived from the token's group claims via `IDClaimsToUserRole`, which can grant Admin/Edit/Run/View roles [7](#0-6) . No existing middleware or check catches this — the ID token signature/expiry verification and claims-name extraction succeed independently of the `email` claim, so the only gate that should stop this flow (the missing-return) is broken.

I could not find a unit/integration test covering this specific failure branch (`TestHandleTokenExchange`-style tests were not found in `oidc_test.go`), consistent with this being an unremediated, untested defect rather than a documented/accepted behavior.

## Impact Explanation
This is a genuine control-flow bug that breaks the intended fail-closed behavior of the OIDC login-callback handler. Concretely, it causes:
- Session/identity binding corruption: every OIDC login whose token lacks an `email` claim produces a session identified by the same empty-string `user_email`, undermining per-user session invalidation logic that depends on `user_email` uniqueness.
- The server logs and intends to return a 500 (auth failure) but the client instead receives a 200 success with a valid, cookie-backed session whose role is fully attacker/IdP-claim-controlled.

This maps to the in-scope "cross-user response/session corruption" and "node API authentication/role bypass" impact categories, since a session not bound to a real, uniquely verifiable identity is created and granted a role purely from claims data.

## Likelihood Explanation
Exploitability requires the caller to complete a legitimate OIDC authorization-code exchange against the configured, valid identity provider — the ID token's cryptographic signature and expiry are still verified via `oi.provider.Verifier(...).Verify(...)`, so this is not exploitable by a fully unauthenticated/arbitrary client without IdP interaction. However, it is reachable by any client capable of completing the code exchange with a token that omits `email` while including a group claim matching one of `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim` — a realistic scenario with certain IdP configurations, scopes, or account types (e.g., service accounts, guest accounts) that omit email. This is a control-flow/logic defect in the node's own login handler, not a malicious-node/peer/host/operator-only issue, and is deterministically reproducible given such a token.

## Recommendation
Add `return` immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call at `core/sessions/oidcauth/oidc.go` line 229, so a missing/invalid `email` claim aborts the request before role mapping and session persistence occur. Consider also adding a regression test (`TestHandleTokenExchange_MissingEmailClaim`) asserting no row is inserted into `oidc_sessions` and no session cookie is set when `email` is absent.

## Proof of Concept
1. Configure `WebServer.OIDC` and complete the `/oidc-login` redirect flow to obtain a valid authorization `code` against a real or test IdP.
2. Arrange for the returned ID token to omit the `email` claim while including a group claim matching the configured `AdminClaim`/`EditClaim` (e.g., via a test/mock OIDC provider used in `oidc_test.go`'s test harness, or an IdP scope/claims configuration that doesn't emit `email`).
3. `POST /oidc/token-exchange` (bound to `handleTokenExchange`) with the valid `code`/`state`.
4. Observe: despite the server logging "Failed to get email from claims" and writing an initial 500 body, a row is inserted into `oidc_sessions` with `user_email = ''` and the mapped role, the session cookie is set, and the final HTTP response is `200 {"Success": true}` — i.e., the client obtains a working authenticated session at the mapped role despite the detected identity failure.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L207-211)
```go
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
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

**File:** core/sessions/oidcauth/oidc.go (L264-275)
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

**File:** core/sessions/oidcauth/oidc.go (L599-617)
```go
func (oi *oidcAuthenticator) IDClaimsToUserRole(idClaims []string, adminClaim string, editClaim string, runClaim string, readClaim string) (clsessions.UserRole, error) {
	// If defined Admin group name is present in id claims, return UserRoleAdmin
	if slices.Contains(idClaims, adminClaim) {
		return clsessions.UserRoleAdmin, nil
	}
	// Check edit role
	if slices.Contains(idClaims, editClaim) {
		return clsessions.UserRoleEdit, nil
	}
	// Check run role
	if slices.Contains(idClaims, runClaim) {
		return clsessions.UserRoleRun, nil
	}
	// Check view role
	if slices.Contains(idClaims, readClaim) {
		return clsessions.UserRoleView, nil
	}
	// No role group found, error
	return clsessions.UserRoleView, ErrUserNoOIDCGroups
```
