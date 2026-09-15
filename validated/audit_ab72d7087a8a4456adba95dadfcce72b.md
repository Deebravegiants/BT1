Confirmed against the actual repository code. The exact behavior matches the claim precisely.

Audit Report

## Title
Missing `return` after email-claim validation failure allows OIDC session creation to proceed with an unvalidated/empty email - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `handleTokenExchange`, the type assertion `email, ok := claims["email"].(string)` at [1](#0-0)  fails to `return` on the `!ok` branch, unlike every other validation branch in the same function (state mismatch, exchange failure, missing `id_token`, verification failure, claim parsing failure, role-mapping failure), all of which correctly `return` after writing their error response. As a result, execution falls through to role mapping, session-row insertion with the empty-string `email`, and a fully successful `200 OK` authenticated session response.

## Finding Description
The function validates several inputs sequentially and returns immediately on each failure, as seen with the preceding `ExtractIDClaimValues` check at [2](#0-1)  and the subsequent `IDClaimsToUserRole` check at [3](#0-2) . The email claim check breaks this pattern — it logs an error and writes a `500` response via `c.String`, but does not call `return`, so control flow continues into role mapping and then into the session-creation logic at [4](#0-3) , which inserts `strings.ToLower(email)` (the empty string, since the assertion failed) into `oidc_sessions`, followed by `ginSession.Save()` and a `200 OK`/`Success: true` response at [5](#0-4) . Session lookup later in `AuthorizedUserWithSession` trusts whatever `user_email`/`user_role` is stored without re-validating identity, at [6](#0-5) . No other check in the function compensates for this, since role mapping (`IDClaimsToUserRole`) operates on group/claim data independent of the email field, meaning a valid role (including `admin`, if group claims map to it) can still be granted even when the email claim is malformed or absent.

## Impact Explanation
This is a genuine authentication/session-integrity defect: the server explicitly flags the request as invalid (`Failed to get email from claims`, HTTP 500) yet still creates and persists a valid, cookie-backed session for the caller, with a role determined solely by group claims and an empty-string email in `oidc_sessions`. This maps to the in-scope "node API authentication or role bypass" and "cross-user response corruption" categories, since multiple such callers would all be keyed to the same empty-string email in the sessions table, corrupting the per-user identity mapping and email-keyed session operations (e.g., `ClearNonCurrentSessions`).

## Likelihood Explanation
Exploitation requires an OIDC login flow to be configured on the node (a supported, documented feature, not an operator-only side channel) and an IdP response whose `email` claim is missing or not a JSON string, while group/role claims still resolve to a valid role. This is a plausible IdP-response condition (optional/absent claim, wrong type) reachable by any client completing the standard, unauthenticated `/oidc/callback`-style exchange flow — it does not require operator, admin, database, or host access, and is a simple, deterministic control-flow bug rather than a speculative exploit chain.

## Recommendation
Add the missing `return` immediately after the failed type assertion so the request stops processing on the same error path as every other check in the function:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```

## Proof of Concept
1. Configure OIDC auth on a local node with a mock/test OIDC provider (as done in `core/sessions/oidcauth/oidc_test.go`).
2. Craft an ID token whose claims include valid group/role claims (so `IDClaimsToUserRole` succeeds) but omit the `email` claim (or set it to a non-string JSON type, e.g. a number or array).
3. Drive the `/callback`/token-exchange endpoint through `handleTokenExchange` with this token.
4. Observe: despite the `500`/"Failed to get email from claims" log/response line executing, the response body ultimately returned is `HTTP 200 {"success": true}`, a `oidc_sessions` cookie is set, and a corresponding row with `user_email = ''` is inserted into `oidc_sessions` — confirming the fall-through. This can be directly written as a Go unit test extending the existing `oidc_test.go` suite, asserting both the final HTTP status/body and the DB row content.

### Citations

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
