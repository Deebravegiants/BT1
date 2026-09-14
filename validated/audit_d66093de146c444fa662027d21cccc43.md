### Title
Missing `return` after failed email-claim extraction lets OIDC login continue and create a valid session even when the client is told the request failed - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The reported issue is a "checked-but-ignored" class bug: code inspects a return/success indicator, logs that it failed, but then proceeds as though the operation succeeded — exactly mirroring the unchecked-ERC20-transfer pattern where a `false` return is not acted upon and the caller keeps going as if the transfer succeeded. The same anti-pattern exists in `core/sessions/oidcauth/oidc.go`'s `handleTokenExchange`, in the node's OIDC/SSO authentication handler that is reachable by any client hitting the SSO callback endpoint.

### Finding Description
In `handleTokenExchange`, after the ID token is verified and claims are parsed, the code attempts to type-assert the `email` claim: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```

Unlike every other error branch in this same function (which all `return` immediately after writing an error response, e.g. lines 166-172, 178-183, 189-196, 208-212, 216-219, 222-225, 241-245), this branch does **not** `return`. Execution falls through and continues with `email` holding its zero value (`""`).

The function then proceeds to:
1. Compute `role` from the (legitimately verified) group claims via `oi.IDClaimsToUserRole(...)`.
2. Insert a new row into `oidc_sessions` using the empty `email`: [2](#0-1) 
3. Call `oi.auditLogger.Audit(...)`.
4. Set the session cookie via `ginSession.Set(webauth.SessionIDKey, clSession.ID)` and `ginSession.Save()`: [3](#0-2) 
5. Finally write a second response `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.

Because Gin has already flushed a `500` status/body from the earlier `c.String` call, the later `c.JSON(200, ...)` call is a superfluous write (logged as a Gin warning) — but crucially, the `Set-Cookie` header for the session and the DB row insert (`INSERT INTO oidc_sessions ...`) still happen unconditionally. This means a legitimately authenticated OIDC/SSO exchange whose claims payload lacks (or has a malformed) `email` field — something an attacker can influence if they control or can trigger error/edge-case responses from the upstream IdP, or if the IdP's claim shape ever mismatches expectations — still results in the node minting and persisting a working session (with `Session-ID` cookie delivered to the client), even though the HTTP response visibly indicates failure (500).

This is the "unchecked/ignored failure signal" bug class: the failure indicator (`ok == false`) is detected and logged, but the operation that failure indicator was supposed to gate (creating and persisting a session) is not rolled back or aborted, so a caller who thinks the operation "failed" can still walk away with valid, usable session state — the login analog of "the transfer returned false but the deposit was credited anyway."

### Impact Explanation
An attacker who can drive the OIDC callback down this path obtains a valid, persisted `clsession` row and a `Set-Cookie` for `SessionIDKey`, which `AuthorizedUserWithSession` (used by `AuthenticateBySession` in `core/web/auth/auth.go`) will happily authenticate on every subsequent request, granting the role that was mapped from the (still-verified) group claims — all despite the front-end/client-visible response being an internal server error. This breaks the expectation that a `500`/failed exchange response means no session was created, and can result in orphaned, unaudited-as-successful sessions with attacker-influenced or ambiguous identity (empty email) still holding a role and full API access for that role.

### Likelihood Explanation
This requires the OIDC provider's claims payload to omit/misshape the `email` field on an otherwise-successful token exchange — a scenario within the influence of anyone who can affect claim shape via provider configuration edge cases, a malicious/compromised IdP, or a race/response manipulation at the IdP boundary. It doesn't require any privileged Chainlink-node capability, only interaction with the public `/oidc-login`/token-exchange endpoint, matching the "unprivileged client request" bar in scope.

### Recommendation
Add the missing `return` immediately after the `c.String(http.StatusInternalServerError, ...)` call in the `!ok` branch (matching every sibling error branch in the same function), so that a missing/invalid email claim aborts the session-creation flow instead of allowing it to complete.

### Proof of Concept
1. Configure/point the node at an OIDC provider (or a proxy impersonating one during the exchange) whose token response's ID-token claims omit the `email` field or return it as a non-string type.
2. Complete the normal OIDC redirect flow up to `/oidc-login/callback` (`handleTokenExchange`).
3. Observe: server logs `"Failed to get email from claims"` and responds with HTTP 500, but the response also carries a `Set-Cookie` for the session, and a new row appears in `oidc_sessions` with `user_email = ''` and the role mapped from the IdP group claims.
4. Replay the received session cookie against any authenticated `/v2/...` endpoint — the request is authenticated with the mapped role, despite the original exchange having reported failure to the client.

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

**File:** core/sessions/oidcauth/oidc.go (L264-271)
```go
	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}
```
