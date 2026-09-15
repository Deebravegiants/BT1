The code matches the claim exactly. Both missing `return` statements are confirmed at lines 226-230 (email claim check) and 257-260 (DB insert check), with execution falling through to session cookie issuance and `Success: true` response.

This is a genuine, verifiable bug in the code — not a false claim. The security assumption broken is that a checked error condition must halt sensitive follow-on actions (RBAC role persistence, session-cookie issuance, audit logging). Both branches log the error but don't `return`, so:
1. Missing/malformed `email` claim → session created with empty email but a valid role/cookie, and audit log records `email: ""`.
2. Failed DB insert → client still gets a working session cookie and `Success: true`, while no `oidc_sessions` row exists.

The exploit path is reachable by any client completing the OIDC exchange flow if the IdP omits the `email` claim (a legitimate OIDC configuration scenario, not attacker-controlled forgery, but the claims are parsed from the IdP-issued token so it's within the code's normal input space) — no privileged access needed, matching the "checked-but-ignored return value" pattern described. This maps to an in-scope Chainlink impact category: node API authentication bypass / corrupted identity in authenticated session.

Audit Report

## Title
Fail-open error handling in OIDC token exchange handler allows session creation despite failed email-claim extraction or DB persistence - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `handleTokenExchange`, two error checks (email claim extraction and `oidc_sessions` DB insert) log the failure and write an HTTP error body but omit the `return` statement that every other error branch in the function uses. As a result, execution falls through and completes the login flow — issuing a valid session cookie and returning `Success: true` — even though a security-relevant step failed. [1](#0-0) [2](#0-1) 

## Finding Description
Every other failure branch in the function calls `return` right after writing the error response, e.g. token exchange, `id_token` extraction, ID token verification, claims parsing, `ExtractIDClaimValues`, and role mapping all `return` on error. [3](#0-2) [4](#0-3) 

Two branches break this pattern:
- `email, ok := claims["email"].(string)`: if `ok` is `false`, the handler logs and writes a 500 body but does not `return`, so `email` remains `""` and execution proceeds to role mapping, DB insert, audit logging, and cookie issuance using the empty email. [5](#0-4) 
- The `INSERT INTO oidc_sessions` call: if it errors, the handler logs and writes a 500 body but does not `return`, so the audit log, session cookie set, and final 200 success response all still execute even though no session row was persisted. [6](#0-5) 

Immediately after, the code unconditionally sets the session cookie and returns success. [7](#0-6) 

## Impact Explanation
If the identity provider's claims omit or misencode `email`, the handler still derives a role via `IDClaimsToUserRole` from group claims, issues a valid authenticated session cookie, and logs `AuthLoginSuccessNo2FA` with `email: ""` — producing a working, role-bearing session tied to a corrupted/empty identity, which undermines audit trail integrity and per-user attribution for privileged (edit/admin/run) sessions. If the DB insert fails, the client still receives `Success: true` and a working session cookie for a session that was never durably persisted, misrepresenting authentication state. This is a concrete node authentication/session integrity defect, though it does not directly grant privilege escalation beyond what the IdP's own group claims would authorize.

## Likelihood Explanation
The email-claim gap is reachable whenever the configured/actual IdP response omits the `email` claim (a legitimate, non-adversarial OIDC configuration variance, e.g., missing `email` scope), and requires no operator/admin access — just completion of the standard `/sessions/exchange` OIDC callback flow with a valid `code`/`state`. The DB-insert failure path requires only a transient DB error, not attacker action, but is also silently fail-open.

## Recommendation
Add `return` immediately after both fail branches so they mirror the rest of the function's error handling:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
...
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```

## Proof of Concept
1. Configure or intercept the OIDC provider's token response so the ID token claims omit `email` (valid IdP behavior when `email` scope isn't granted).
2. Complete the OAuth2 code exchange via the route wired to `handleTokenExchange` with a valid `code`/`state`.
3. Observe the `claims["email"].(string)` assertion fails; the handler logs the error and writes a 500 body but does not return.
4. Execution continues: role is mapped from group claims, `oidc_sessions` row is inserted with `user_email = ''`, the session cookie is set via `ginSession.Save()`, and the handler emits `c.JSON(http.StatusOK, {"success": true})` — confirming a working authenticated session was minted despite the failed email-claim check. A parallel test can force the DB `ExecContext` call to error (e.g., via a mock datastore) to confirm the same fail-open behavior on the persistence check.

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

**File:** core/sessions/oidcauth/oidc.go (L226-231)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)
```

**File:** core/sessions/oidcauth/oidc.go (L241-245)
```go
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L250-262)
```go
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
