Audit Report

## Title
Missing `return` after OIDC claim/session errors allows authentication to proceed despite failure - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `oidcAuthenticator.handleTokenExchange`, the `email` claim-extraction failure branch and the `oidc_sessions` INSERT failure branch both write an error response but omit the `return` statement present in every other error branch of the function. As a result, execution falls through and completes session creation, DB insert, audit logging, and cookie assignment even after a detected failure, ultimately overwriting the error response with a `200 OK` success response.

## Finding Description
The handler `handleTokenExchange` validates OIDC state, exchanges the code for a token, verifies the ID token, and extracts claims. All prior error branches correctly `return` after writing an error response (e.g. state mismatch, token exchange failure, verification failure, claim parsing/extraction failure) [1](#0-0) [2](#0-1) .

However, the `email` extraction block lacks the `return`: [3](#0-2) 

And the `oidc_sessions` INSERT failure block also lacks the `return`: [4](#0-3) 

In both cases execution continues into role mapping (already computed before the email check), audit logging via `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)`, `ginSession.Set(webauth.SessionIDKey, clSession.ID)`, `ginSession.Save()`, and finally a `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})` response that overwrites/follows the earlier error write [5](#0-4) . This confirms the exact code path and root cause described in the claim: a detected failure emits an error response but does not halt subsequent session-issuing side effects.

## Impact Explanation
This is a genuine logic defect in the authentication/session-issuance code path. The role assigned to the resulting session is derived from `idClaims`/group claims (which succeeded independently of the email check), so the missing `return` does not itself grant an attacker a role or session they wouldn't otherwise have obtained via a normal, successful OIDC login — the primary concrete effect is that the session's `user_email` in `oidc_sessions` and the audit log entry (`audit.AuthLoginSuccessNo2FA`) become corrupted (empty/incorrect email) when the email claim is malformed, and a `200 OK` "success" response can be returned to the client even when the DB insert genuinely failed (client believes it is logged in with a session row that doesn't exist). These are real correctness/audit-integrity defects but do not, on their own, demonstrate a concrete authentication bypass, privilege escalation, or unauthorized access to node APIs by an unprivileged attacker — reaching this code requires already completing a valid, provider-verified OIDC login (state check, token exchange, and signature verification all succeed) with a legitimate IdP-issued ID token that merely omits the `email` claim, which is a corner-case identity-provider response rather than an actor-controlled bypass of authorization.

## Likelihood Explanation
Triggering this requires OIDC to be enabled and a completed, cryptographically valid OIDC login flow from a legitimate identity provider whose ID token omits the `email` claim (or a transient DB failure for the second branch) — both plausible under real-world misconfiguration/edge cases, but not exploitable as an authentication or role bypass by an arbitrary unprivileged actor without already being an authorized principal at the configured OIDC provider.

## Recommendation
Add `return` immediately after both error-response writes, consistent with every other error branch in `handleTokenExchange`:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
```go
_, err = oi.ds.ExecContext(ctx, "INSERT INTO oidc_sessions ...", ...)
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```

## Proof of Concept
1. Enable OIDC auth (`config.OIDC`) against a test/mock OIDC provider.
2. Configure the provider to return a valid, signature-verifiable ID token containing the configured group claim (so claim extraction and role mapping succeed) but omitting the `email` claim.
3. Complete the front-end OAuth2 redirect flow and call the token-exchange endpoint that invokes `handleTokenExchange`.
4. Observe: server logs "Failed to get email from claims" and writes a `500` body, but the actual HTTP response received is `200 OK` with `Success: true`, a `clsession` cookie is set, and (if the DB insert succeeds) a row is written to `oidc_sessions` with an empty `user_email` but a valid `user_role`.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L177-183)
```go
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
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

**File:** core/sessions/oidcauth/oidc.go (L250-260)
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
```

**File:** core/sessions/oidcauth/oidc.go (L262-275)
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
```
