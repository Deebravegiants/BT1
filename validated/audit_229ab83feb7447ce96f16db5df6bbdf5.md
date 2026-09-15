Audit Report

## Title
Missing `return` after failed checks in OIDC token exchange lets login continue on error, creating authenticated sessions with unvalidated/missing email - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `oidcAuthenticator.handleTokenExchange`, the email-claim type-assertion failure branch and the `oidc_sessions` INSERT error branch both write an HTTP error response but omit the `return` statement present in every other error check in this function, so execution falls through and completes session creation, cookie setting, and returns a `200 OK` success response regardless of the failure.

## Finding Description
The code at [1](#0-0)  type-asserts `claims["email"]` and, on failure, logs and writes `c.String(http.StatusInternalServerError, ...)` without a `return`, unlike the pattern used consistently elsewhere in the same function, e.g. [2](#0-1) . Execution proceeds to compute `role` via `IDClaimsToUserRole` and then unconditionally inserts a new row into `oidc_sessions` keyed on the (possibly empty) `email` at [3](#0-2) . The second bug is identical: the INSERT error branch at [4](#0-3)  also lacks a `return`. In both cases the handler subsequently sets the session cookie via `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and unconditionally returns `200 OK` with `Success: true` at [5](#0-4) .

## Impact Explanation
This produces a genuine authentication-hygiene defect: a session cookie can be issued and marked successful even though the email claim could not be extracted (stored as `""` in `oidc_sessions`) or even though the session row failed to persist at all (cookie references a `session_id` never written to `oidc_sessions`, breaking later lookups in `AuthorizedUserWithSession`). Notably, the RBAC `role` is still correctly derived from group claims via `IDClaimsToUserRole` independent of the email field, so this is not a full authentication/role bypass — it is a Medium-severity correctness bug that can corrupt session state and produce a misleading double HTTP response body, falling within the "cross-user response corruption" / session-integrity impact category.

## Likelihood Explanation
The path is reachable purely by an unprivileged client completing the standard OIDC callback (`state`/`code` exchange) at `handleTokenExchange`; it is triggered whenever the configured OIDC provider's ID token omits/mistypes the `email` claim, or when the `oidc_sessions` INSERT fails transiently (e.g., DB error) — both are realistic operational conditions rather than attacker-crafted exploitation, making the bug easy to hit unintentionally in a live deployment using OIDC auth.

## Recommendation
Add `return` immediately after both error branches:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
and
```go
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```

## Proof of Concept
1. Configure an OIDC provider/test IdP so the verified ID token's claims omit the `email` field.
2. Complete the standard OIDC login flow against `/exchange` with a valid `state` and authorization `code`.
3. Observe that despite the `Failed to get email from claims` error being written, the handler still inserts an `oidc_sessions` row with `user_email = ''`, calls `ginSession.Set(webauth.SessionIDKey, clSession.ID)` + `ginSession.Save()`, and finally emits `{"Success": true}` — yielding a cookie-backed session for a login step that failed. The same fall-through can be reproduced by forcing `oi.ds.ExecContext` to error (e.g., duplicate key or DB unavailability) at lines 250-256, resulting in a cookie referencing a `session_id` absent from `oidc_sessions`.

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

**File:** core/sessions/oidcauth/oidc.go (L249-256)
```go
	clSession := clsessions.NewSession()
	_, err = oi.ds.ExecContext(
		ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		clSession.ID,
		strings.ToLower(email),
		role,
	)
```

**File:** core/sessions/oidcauth/oidc.go (L257-260)
```go
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
