This confirms the bug. Two failure paths in `handleTokenExchange` write an error response via `c.String(...)` but **omit the `return` statement**, exactly mirroring the "ignored failure signal, execution continues" root cause from the report. [1](#0-0) [2](#0-1) 

### Title
Missing `return` after failed email-claim extraction and session-row insert lets OIDC login continue and issue an authenticated session cookie - (File: core/sessions/oidcauth/oidc.go)

### Summary
`oidcAuthenticator.handleTokenExchange` is the internet-facing OIDC callback handler that finishes the login flow for an unprivileged client (any browser completing the SSO redirect). After verifying the ID token, it extracts the `email` claim and later persists a row in `oidc_sessions`. Both of these steps have failure branches that call `c.String(http.StatusInternalServerError, ...)` to report the error, but neither branch contains a `return` statement — unlike every other error branch in the same function. Execution falls through and the handler still creates a valid, gateway-issued session cookie and finally overwrites the response with `c.JSON(http.StatusOK, ExchangeTokenResponse{Success: true})`.

### Finding Description
Compare the two "unchecked" branches: [3](#0-2) 
which correctly returns after a failure, to: [1](#0-0) 
which does not. The role, however, is still computed and a session is still created with the (possibly empty) email value: [4](#0-3) 

If `claims["email"]` is missing or not a string (e.g. an IdP misconfigured to omit `email`, or a token whose `email` claim is a non-string type), `email` silently becomes `""`. The code does not abort; it proceeds to compute `role` from the already-verified group claims, inserts a row into `oidc_sessions` with `user_email = ''` and the resolved `role`, then: [5](#0-4) 
sets `SessionIDKey` on the gin session cookie and saves it — establishing a fully authenticated session for the browser — before finally writing a `200 OK` / `Success: true` JSON body over the earlier `500` write.

The second unchecked path (`oi.ds.ExecContext` insert failure at lines 257-260) is equally dangerous: if the DB insert fails, the handler still proceeds to set the session cookie value to `clSession.ID`, an ID that was never persisted. Any later authorization check that looks up `oidc_sessions` by that ID (see `AuthorizedUserWithSession`) would then legitimately fail — but the more security-relevant issue is the first case, since it can result in an active, role-bearing session tied to an empty/incorrect email identity, breaking the invariant that every session in `oidc_sessions` maps to a distinct, correctly-attested user identity.

This is the same root-cause pattern as the reported `UDA.sol` finding: a call whose failure indicator is checked and logged, but whose control-flow consequence (aborting further state changes) is never applied, letting the system continue as if the operation had succeeded.

### Impact Explanation
An externally-facing, unprivileged actor completing the OIDC callback can end up with a browser session cookie tied to a session record with an empty/incorrect `user_email` while still carrying a role derived from the verified group claims. This undermines per-user audit trails (`audit.AuthLoginSuccessNo2FA` is logged with the empty email) and identity-to-role binding used throughout the node's authentication/authorization stack (`RequiresAdminRole`, `RequiresEditRole`, etc., which key off the `User` struct populated from this session row). Because the HTTP response is still eventually overwritten with `200 OK / Success: true`, the client has no visibility that an error occurred, so the broken session state is not surfaced or retried — it persists silently, analogous to the "funds permanently locked with no recovery" outcome in the original report, except here it is "a session persists in an inconsistent, non-recoverable identity state."

### Likelihood Explanation
Reaching this path only requires controlling or misconfiguring the upstream OIDC IdP's `email` claim (or hitting a transient DB failure on session insert) while otherwise presenting a validly signed ID token — something achievable by any client driving the standard, unprivileged `/oidc/callback`-style token exchange flow. No special privilege beyond completing a normal OIDC login round trip is required.

### Recommendation
Add `return` immediately after both `c.String(http.StatusInternalServerError, ...)` calls at lines 229 and 259, mirroring the pattern used everywhere else in this function (e.g. lines 195, 203, 211, 218, 224, 244, 270), so that any failure to extract the email claim or persist the session row aborts the handler instead of falling through to cookie issuance and the final success response.

### Proof of Concept
1. Configure the OIDC authenticator with an IdP (or a test OIDC provider) that issues a validly signed ID token containing the configured RBAC group claim but omitting the `email` claim (or returning it as a non-string, e.g. a number).
2. Drive the standard sign-in flow: `GET` the sign-in redirect, complete the IdP round trip, then `POST` the resulting `code`/`state` to the token-exchange endpoint backed by `handleTokenExchange`.
3. Observe server logs show `"Failed to get email from claims"` and an `http.StatusInternalServerError` write, yet the handler continues: `IDClaimsToUserRole` resolves a role, a row is inserted into `oidc_sessions` with `user_email = ''`, `SessionIDKey` is set on the gin session and saved, and the final response body is `{"success":true}`.
4. Use the returned session cookie against a role-protected endpoint (e.g. one wrapped by `RequiresAdminRole`/`RequiresEditRole`) and observe it is treated as a valid, role-bearing session despite the missing/invalid email identity.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L199-204)
```go
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
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

**File:** core/sessions/oidcauth/oidc.go (L247-256)
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
```

**File:** core/sessions/oidcauth/oidc.go (L257-260)
```go
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
