### Title
Missing `return` on OIDC email-claim extraction failure allows session creation with empty `user_email`, causing cross-user session confusion - (File: core/sessions/oidcauth/oidc.go)

### Summary
In `handleTokenExchange`, when the `email` claim cannot be extracted from the verified ID token, the handler logs an error and writes an HTTP 500 response, but does not `return`. Execution continues, and a new `oidc_sessions` row and authenticated session cookie are created using an empty (or attacker-influenced) email value, mirroring the reported bug class of a missing "receive"/reconciliation step that leaves state inconsistent after an operation.

### Finding Description
`handleTokenExchange` in `core/sessions/oidcauth/oidc.go` extracts the `email` claim from the OIDC provider's verified claims map: [1](#0-0) 

Unlike every other error branch in this function (invalid state, exchange failure, missing `id_token`, verification failure, claims parsing failure, role-mapping failure — all of which `return` immediately), this branch is missing a `return` statement. Execution falls through to role mapping and session persistence: [2](#0-1) 

The session row is inserted with `strings.ToLower(email)`, which — since `email` is the zero-value string `""` when the type assertion fails — writes `user_email = ''` into `oidc_sessions`. A valid session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`) is still issued to the client despite the HTTP 500 status being written first. [3](#0-2) 

Downstream, `AuthorizedUserWithSession` looks up the session purely by `sessionID` and trusts the `UserEmail`/`UserRole` values stored at creation time, without re-validating against the identity provider: [4](#0-3) 

If more than one authentication attempt hits this code path (e.g., an IdP misconfiguration, a malicious/compromised upstream claim source, or any client manipulating the callback flow so the `email` claim is absent while group claims are still present), multiple distinct sessions are created that all share `user_email = ''`. Because `ClearNonCurrentSessions` operates via `lower(user_email)` matching, one such session holder could delete/interact with all other same-empty-email sessions: [5](#0-4) 

### Impact Explanation
An authenticated `oidc_sessions` record can be created with an empty `user_email` while the client still receives a valid session cookie for a role derived from the group claims (`role, err := oi.IDClaimsToUserRole(...)`), even though the HTTP response reports failure. This produces state inconsistent with the intended "reject on incomplete claims" behavior, exactly analogous to the reported bug class (an operation that mutates persisted state without performing the corresponding validation/reconciliation step). It can lead to authenticated sessions with role privileges tied to an empty identity, cross-session collision between any two sign-ins missing an email claim, and audit-log entries (`AuthLoginSuccessNo2FA`) being recorded with an empty user identifier — undermining traceability and per-user session isolation guarantees relied upon by `ClearNonCurrentSessions` and password-change flows.

### Likelihood Explanation
This is reachable by any unprivileged client going through the standard OIDC login redirect/callback (`/oidc-login` → `handleSignIn` → `handleTokenExchange`), the internet-facing entry point for this authenticator. It does not require a malicious node/peer or operator privileges — only an IdP response, or crafted claims, lacking a top-level `email` field while retaining recognizable group claims. Likelihood depends on the IdP configuration reliably including `email` and is a code-correctness/defense-in-depth bug rather than a trivially exploitable end-to-end account takeover under normal correctly-configured providers, but it is a genuine reachable logic bug in the state-mutation path a background engineer should fix.

### Recommendation
Add `return` immediately after writing the error response in the missing-`email` branch:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
This ensures no `oidc_sessions` row or session cookie is created when the email claim cannot be extracted, keeping persisted authentication state consistent with the reported failure response.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L233-260)
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
```

**File:** core/sessions/oidcauth/oidc.go (L262-271)
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
```

**File:** core/sessions/oidcauth/oidc.go (L356-380)
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
```

**File:** core/sessions/oidcauth/oidc.go (L442-449)
```go
func (oi *oidcAuthenticator) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := oi.ds.GetContext(ctx, &email, "SELECT user_email FROM oidc_sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2", email, sessionID)
	return err
}
```
