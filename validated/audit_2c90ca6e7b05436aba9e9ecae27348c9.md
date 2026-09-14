### Title
Missing `return` after OIDC claim/session errors allows authentication to proceed despite failure - (File: core/sessions/oidcauth/oidc.go)

### Summary
In `oidcAuthenticator.handleTokenExchange`, two error branches write an error response to the client but do not `return`, so execution falls through and continues to create and persist an authenticated session even though a prior step failed. This mirrors the reported `SwapCallLib.call()` bug class: on failure the code should halt/"revert" all subsequent effects, but instead it behaves like `return()` in the Solidity report — the failure is logged/reported, yet state-changing operations continue to execute.

### Finding Description
`handleTokenExchange` performs the OIDC code-exchange callback flow: [1](#0-0) 

After validating claims and computing `idClaims`, the function extracts the email claim:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
``` [2](#0-1) 

There is no `return` statement in this `if !ok` block, unlike every other error branch in the same function (compare lines 166-172, 177-183, 189-196, 200-204, 208-212, 215-219, 221-225, 241-245, 267-271, all of which `return` after writing an error response). Execution therefore falls through to role mapping, session creation, DB insert, `audit.Audit(...)`, and finally `ginSession.Set(...) / Save()`, ultimately writing a second HTTP response (`c.JSON(http.StatusOK, ...)`) on top of the already-written `500` response. [3](#0-2) 

A second, related instance of the same pattern exists a few lines later: if the `INSERT INTO oidc_sessions` call fails, the error is logged and written to the response, but again there is no `return`, so the handler proceeds to set the session cookie (`ginSession.Set(webauth.SessionIDKey, clSession.ID)`) and returns `200 OK` with `Success: true`, even though the corresponding `oidc_sessions` row was never persisted: [4](#0-3) 

Both cases follow the exact anti-pattern flagged in the report: an error is detected, a "failure" signal is emitted (HTTP error write instead of Solidity `return()`), but the function keeps running and commits state changes (session cookie set, DB insert attempt, audit log entry) that should only happen on the success path.

### Impact Explanation
- In the `email` extraction failure path, a session is still created and the cookie (`clsession_id`) is set on the client with a role derived from `idClaims` (which succeeded) despite the identity information (`email`) being invalid/missing. This produces a session bound to an empty/undefined email but with a legitimate elevated role (admin/edit/run per the OIDC group mapping), corrupting the audit trail (`audit.AuthLoginSuccessNo2FA` is logged with the empty email) and the `oidc_sessions.user_email` column.
- In the DB-insert failure path, the client receives a `200 OK` "Success: true" response and a session cookie pointing to a `clSession.ID` that does not exist in `oidc_sessions`, which is a functional integrity failure (broken session state silently reported as success) rather than a privilege escalation by itself.
- Both are concrete "state changes persist despite failure" bugs in the authentication/session-issuance path, directly analogous to the reported bug class, though the most severe consequence (an authenticated session issued with a role but corrupted identity) applies to the first case.

### Likelihood Explanation
Reaching the vulnerable code requires only an unprivileged client to complete the standard OIDC front-end callback flow that any user goes through (`/sessions/oidc/exchange` type endpoint calling `handleTokenExchange`), so the reachable path from an unauthenticated actor is direct via the normal login flow. Triggering the specific missing-`return` branches requires an OIDC provider response whose ID token claims omit `email` as a string (first branch) or a transient DB failure during session insert (second branch) — both are plausible under normal OIDC misconfiguration/error conditions rather than requiring privileged or malicious infrastructure.

### Recommendation
Add `return` immediately after writing the error response in both branches:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
and
```go
_, err = oi.ds.ExecContext(ctx, "INSERT INTO oidc_sessions ...", ...)
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```
so that a detected failure halts all further session-issuing side effects, consistent with every other error branch in this function.

### Proof of Concept
1. Configure the node with OIDC auth enabled (`config.OIDC`), pointing at a test/mock OIDC provider.
2. Have the provider return a valid, verifiable ID token whose claims include the configured group claim (so `ExtractIDClaimValues`/`IDClaimsToUserRole` succeed) but omit the `email` claim (or supply a non-string value for it).
3. Complete the front-end OAuth2 redirect flow and call the token-exchange endpoint (`handleTokenExchange`) with the resulting `code`/`state`.
4. Observe: the server logs "Failed to get email from claims" and writes a `500` body, but the response actually returned to the client is `200 OK` with `Success: true` (from the later `c.JSON` call), a `clsession` cookie is set, and a row is inserted into `oidc_sessions` with an empty `user_email` but a valid `user_role` — i.e., an authenticated session was created despite the detected claim-extraction failure.

*Note:* I was not able to fully trace `AuthorizedUserWithSession`'s SQL query against `oidc_sessions` (to confirm whether an empty-email row could later be looked up/authenticated for an actual API call) within the available tool budget; this would need to be checked in a full session (e.g., in `core/sessions/oidcauth/oidc.go` for the `AuthorizedUserWithSession`/`FindUserByAPIToken` implementations) to determine whether the corrupted row is independently usable to authenticate further requests, or whether its effect is limited to a corrupted audit/session record.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-172)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
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

**File:** core/sessions/oidcauth/oidc.go (L233-275)
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
```
