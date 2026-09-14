### Title
Unchecked type-assertion error allows OIDC session creation to proceed with an empty/unattributed user identity - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
In `handleTokenExchange`, the internet-facing OIDC callback handler that processes an unauthenticated client's authorization-code exchange, the result of the `email` claim type assertion is not checked and execution is not aborted on failure, mirroring the "unchecked error / operation continues silently" bug class described in the source report (`ResetChurnableTopics` ignoring `Clear`'s error and letting the EndBlocker continue). [1](#0-0) 

### Finding Description
`handleTokenExchange` performs the OAuth2/OIDC code exchange, verifies the ID token, and extracts claims for RBAC role mapping:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
``` [2](#0-1) 

Unlike every other failure branch in this function (invalid state, exchange failure, missing `id_token`, verify failure, claim-parsing failure, role-mapping failure, session-save failure — all of which call `return` after writing an error response), this branch writes a `500` body but does **not** `return`. Execution falls through, `email` retains its zero value (`""`), and the function continues to:

1. Map the role from group claims (independent of email) at `IDClaimsToUserRole`. [3](#0-2) 
2. Insert a new row into `oidc_sessions` with `user_email = ""` and the resolved role. [4](#0-3) 
3. Emit an audit log entry (`AuthLoginSuccessNo2FA`) attributing the login to an empty email. [5](#0-4) 
4. Set the session cookie on the response and return `200 {"success": true}` to the client (the earlier `c.String(500, ...)` write is effectively overridden/ignored since gin allows multiple writes and the final `c.JSON(http.StatusOK, ...)` is reached). [6](#0-5) 

This creates a fully authenticated, cookie-backed session (`AuthorizedUserWithSession` will successfully resolve it from `oidc_sessions`) whose `user_email` column is empty. [7](#0-6) 

Because downstream authorization decisions (`RequiresRunRole`, `GetAuthenticatedUser`, per-role gating) key only on `Role`, not `Email`, a caller who can complete the OAuth code exchange with an identity-provider token lacking an `email` claim (but containing whichever group claim maps to Admin/Edit/Run) is granted a working, role-privileged session that carries no attributable identity. Audit logs (`AuthLoginSuccessNo2FA` and any subsequent per-request audit entries keyed on `sessionUser.Email`) will record an empty user, breaking accountability and enabling multiple distinct OIDC principals lacking an email claim to collapse into indistinguishable, unattributed sessions — a cross-user response/attribution confusion at the audit layer.

### Impact Explanation
The unchecked failure allows the request to complete "successfully" from the client's point of view (`200 OK`, valid session cookie) despite a claim-extraction error that the code clearly intended to be fatal (every sibling branch returns). The resulting session:
- Is persisted with an empty `user_email`, breaking session/user attribution used for auditing (`oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})`) and any admin UI/session listing (`Sessions()`), undermining accountability for privileged actions taken under that session. [8](#0-7) 
- Still carries a legitimate role derived from the IdP's group claims, so subsequent RBAC checks (`RequiresRunRole`, etc.) succeed normally, meaning the bad/incomplete session functions as a normal privileged session that cannot be traced back to a specific email/user.

This is a moderate-severity accountability/audit-integrity issue on the internet-facing OIDC login endpoint reachable by any client capable of driving the OAuth2 code-exchange flow, not a full authentication bypass (the role assignment mechanism itself is unaffected), but it does violate the intended fail-closed behavior of the handler and produces unattributable, non-reproducible sessions similar in nature to the reported "operation continues despite an unchecked failure" bug class.

### Likelihood Explanation
Exploitability depends on whether the configured OIDC identity provider can be made to omit the standard `email` claim while still returning a role-mapping group claim (`AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim`) — feasible for a malicious or misconfigured IdP, or an attacker who controls a subset of claim contents (e.g., via a compromised/rogue IdP client or a token replay where email is intentionally scrubbed). It does not require any special chainlink-node privilege; it only requires completing the standard `/oidc-login` → callback flow, which is otherwise reachable to any external actor able to reach the login endpoint.

### Recommendation
Add a `return` immediately after writing the error response in the `email` type-assertion failure branch, consistent with every other error branch in `handleTokenExchange`:

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```

Additionally, treat the `oi.ds.ExecContext` session-insert error at line 257 the same way — it currently logs and writes a `500` body but also falls through to set the cookie and respond `200 OK`; that branch should likewise `return` after the error response. [9](#0-8) 

### Proof of Concept
1. Configure an OIDC identity provider (or a controlled/rogue one used by a client under attacker influence) whose ID token issues a group claim matching `oi.config.RunClaim()` (or another configured role claim) but does not include an `email` claim.
2. Drive the standard flow: `GET /oidc-login` (handled by `handleSignIn`) to obtain `state`, complete the provider's consent, then `POST` the resulting `code`/`state` to the token-exchange endpoint handled by `handleTokenExchange`.
3. Observe that despite the server logging `"Failed to get email from claims"` and writing a `500` body, execution continues: `IDClaimsToUserRole` resolves a role from the group claim, `oidc_sessions` gets a new row with `user_email = ''`, the audit log records `{"email": ""}`, the gin session cookie is set, and the final response overwrites the earlier error with `200 {"success": true}`.
4. Using the returned session cookie, call any endpoint gated by `RequiresRunRole`/`AuthenticateBySession`; the request succeeds as an authenticated user with the mapped role but no attributable email, confirming the fail-open behavior caused by the missing `return`.

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

**File:** core/sessions/oidcauth/oidc.go (L350-391)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L561-569)
```go
// Sessions returns all sessions limited by the parameters.
func (oi *oidcAuthenticator) Sessions(ctx context.Context, offset, limit int) ([]clsessions.Session, error) {
	var sessions []clsessions.Session
	sql := `SELECT * FROM oidc_sessions ORDER BY created_at, id LIMIT $1 OFFSET $2;`
	if err := oi.ds.SelectContext(ctx, &sessions, sql, limit, offset); err != nil {
		return sessions, nil
	}
	return sessions, nil
}
```
