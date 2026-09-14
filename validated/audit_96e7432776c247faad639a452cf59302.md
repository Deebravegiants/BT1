### Title
Missing `return` after failed OIDC email claim extraction lets `handleTokenExchange` create an authenticated session with an empty user identity - ([File: core/sessions/oidcauth/oidc.go])

### Summary
In `oidcAuthenticator.handleTokenExchange`, when the `email` claim cannot be type-asserted from the verified ID token claims, the handler logs an error and writes an HTTP 500 status but fails to `return`, so execution falls through and continues to create a fully valid, authenticated session using the empty `email` string.

### Finding Description
`handleTokenExchange` verifies the OIDC ID token and extracts claims, then does: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

Unlike every other error branch in this function (e.g. the `oauth2Config.Exchange`, `idToken.Claims`, and `ExtractIDClaimValues` failure paths, all of which `return` immediately after writing the error response), this branch is missing the `return` statement. As a result, when the `email` claim is absent or not a string, `ok` is `false`, `email` remains the zero value (`""`), an HTTP 500 body is written to the client, but the function keeps executing: [2](#0-1) 

It proceeds to map the (already-fetched) group claims to a role via `IDClaimsToUserRole`, inserts a new row into `oidc_sessions` with `user_email = ""`, sets the session cookie via `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()`, and finally responds `c.JSON(http.StatusOK, ...)` — overwriting the earlier 500 status/body with a 200 success response. The net effect: the client ends up with a valid, server-set session cookie tied to a session row keyed by an empty email, even though the identity provider's email claim was missing/malformed.

This session is fully functional for subsequent requests: `AuthorizedUserWithSession` looks up `oidc_sessions` purely by session ID and returns whatever `user_email`/`user_role` was stored, without re-validating that email is non-empty or matches a real identity: [3](#0-2) 

The role assigned to this empty-email session is still derived from the OIDC provider's group claims (`IDClaimsToUserRole`), so the practical severity depends on group-claim membership, but the identity binding to a specific user is broken — the resulting session is not tied to any real user account, and subsequent flows keyed on user email (e.g. audit logging via `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})` at line 262, or password/user lookups elsewhere that assume a valid email) receive an empty string.

### Impact Explanation
This is an authentication/session-integrity defect reachable directly by an unprivileged actor completing (or partially completing) the OIDC authorization-code exchange flow — an internet-facing, unauthenticated endpoint (`handleTokenExchange`), which is exactly the class of unprivileged-actor session/token handling in scope. A malformed or attacker-influenced OIDC provider response (or a misconfigured/malicious upstream IdP under the operator's control, or a claim-name mismatch) causes the node to mint a live, cookie-backed session with no real user identity attached, while returning what looks like a generic failure. This breaks the invariant that every session in `oidc_sessions` corresponds to a verified, identifiable user, and could let a request proceed as an authenticated (non-view) role without a legitimate user record backing it — a session/identity-confusion condition consistent with "unauthorized job run" / "role bypass" class impact described in the validation criteria, driven directly by the code ignoring the claim-extraction failure signal instead of aborting the flow (directly analogous to the reported "ignoring return value can lead to silent failure" pattern, here manifesting as ignoring a type-assertion failure instead of an ERC20 `transfer()` return value).

### Likelihood Explanation
Likelihood is moderate: it requires the ID token's claims to lack a usable `email` string (e.g., IdP configuration returning email as a non-string, omitting the `email` scope/claim, or an attacker-controlled/compromised IdP flow), which is a plausible real-world misconfiguration or malicious-IdP scenario rather than requiring privileged internal access. The double-write to the response (`500` body followed by an overriding `200 OK` JSON `{"success":true}`) is also a clear symptom that would appear in production logs/telemetry, which increases the chance of it going unnoticed by developers testing only the happy path but makes it discoverable in review.

### Recommendation
Add the missing `return` statement immediately after writing the error response in the `email` claim extraction failure branch, mirroring every other error path in this function:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, treat an empty-string `email` (even if the type assertion succeeds) as a failure before proceeding to create the session, since `oidc_sessions.user_email` should never be persisted as an empty value.

### Proof of Concept
1. Configure (or compromise) an OIDC identity provider such that the ID token's claims payload omits the `email` claim, or returns it as a non-string JSON value (e.g., `null` or a number).
2. Initiate the OIDC login flow against the Chainlink node (`/sessions` OIDC sign-in → provider → callback), completing the state/code exchange so `handleTokenExchange` is invoked with a valid `code` and matching `state`.
3. `oauth2Config.Exchange`, `idToken.Claims`, and `ExtractIDClaimValues` all succeed (these depend on group/role claims, not `email`), so execution reaches the `email` extraction: `claims["email"].(string)` fails, `ok == false`.
4. The handler writes an HTTP 500 body but does not return; execution continues to `IDClaimsToUserRole`, `INSERT INTO oidc_sessions (... user_email='' ...)`, `ginSession.Set(...)`, `ginSession.Save()`, and finally overwrites the response with `c.JSON(http.StatusOK, {"success": true})`.
5. The client now holds a valid session cookie. Subsequent authenticated requests succeed via `AuthorizedUserWithSession`, returning a `User{Email: "", Role: <mapped role>}`, despite no real user/email having been validated for this session.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-231)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

**File:** core/sessions/oidcauth/oidc.go (L233-276)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L351-373)
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
```
