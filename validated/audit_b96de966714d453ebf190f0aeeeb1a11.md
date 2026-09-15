Audit Report

## Title
Missing return after failed email-claim extraction allows session creation with empty email in OIDC exchange handler - (File: core/sessions/oidcauth/oidc.go)

## Summary
`handleTokenExchange` fails to `return` after failing to type-assert `claims["email"]` to a string, so execution falls through to role mapping and session persistence using the zero-value empty string for `email` while a legitimately derived role continues to be attached. This decouples authorization (role) from identity for the resulting session.

## Finding Description
At `core/sessions/oidcauth/oidc.go:226-230`, the handler does: [1](#0-0) 
`ok` being false only logs the error and calls `c.String(...)`, which in Gin does not abort the handler — execution proceeds. The code then computes `role` from group claims via `IDClaimsToUserRole` [2](#0-1)  and inserts a new session row keyed on `strings.ToLower(email)` (i.e., empty string) paired with that role: [3](#0-2) . The handler then still sets the session cookie and returns HTTP 200 success: [4](#0-3) . `AuthorizedUserWithSession` later resolves this session ID back into a `clsessions.User{Email: "", Role: <role>}` with no additional validation that email is non-empty: [5](#0-4) . All existing checks in the surrounding function (state check, oauth2 exchange, ID token verification, claims parsing, `ExtractIDClaimValues`) properly `return` on failure — only this one branch is missing it, confirming this is a genuine oversight rather than intended behavior.

## Impact Explanation
This produces a session with a role attached (potentially Admin, depending on group claim mapping) but no valid identity — a form of authentication/role bypass and cross-user response confusion, since every such session collapses to the same empty-email identity. This maps to the in-scope "node API authentication or role bypass" impact category.

## Likelihood Explanation
The path is reachable by any client that can drive the `/oidc-exchange` flow to completion, but it requires the configured (or attacker-controlled/misconfigured) identity provider to return an ID token whose claims include valid role-mapping group claims while omitting a string `email` claim — a provider/configuration-dependent condition, not something an unprivileged client can unilaterally force against an honestly-configured, standard OIDC provider that always includes email. This lowers exploitability from a general/unconditional bypass to a conditional one contingent on provider behavior. Regardless of likelihood constraints, the code defect itself — a missing `return` allowing session creation on validation failure — is real and independently verifiable in the code.

## Recommendation
Add `return` immediately after `c.String(http.StatusInternalServerError, "Failed to get email from claims")` at line 229, so the handler aborts before role mapping and session persistence, matching the pattern used by every other error branch in this function.

## Proof of Concept
1. Configure OIDC provider/mock IdP to return an ID token with valid group claims satisfying `AdminClaim`/etc. but without an `email` claim (or with a non-string `email` value).
2. Complete `/oidc-login` → `/oidc-exchange` as an unauthenticated client.
3. Observe that despite `handleTokenExchange` logging "Failed to get email from claims", it responds `200 OK` with `{"success": true}`, inserts a row into `oidc_sessions` with `user_email = ''` and the group-derived role, and sets a valid session cookie.
4. Use the returned session cookie against an authenticated endpoint; `AuthorizedUserWithSession` returns `User{Email: "", Role: <derived role>}`, granting access at that role level — demonstrable via a Go unit/integration test on `handleTokenExchange` with a mocked claims map missing `email`.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L233-245)
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
