### Title
Missing `return` after failed email-claim extraction allows OIDC session creation with an empty/unverified email - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
In `oidcAuthenticator.handleTokenExchange`, the code validates that the OIDC `email` claim can be extracted as a string, but on failure it writes an error response and continues executing instead of returning, mirroring the CVE-2024-27040 bug class: a validated failure condition is checked and handled once, but the subsequent code path is executed anyway as if the check had succeeded.

### Finding Description
`handleTokenExchange` is the internet-reachable callback handler for the OIDC login flow at `core/sessions/oidcauth/oidc.go`. After verifying the ID token and extracting RBAC group claims, it attempts to pull the `email` claim: [1](#0-0) 

```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```

Unlike every other error branch in this function (state mismatch, exchange failure, missing `id_token`, verification failure, claims parse failure, role-mapping failure — all of which call `return` immediately after writing the error response), this branch omits the `return` statement. Execution falls through to role mapping and session creation: [2](#0-1) 

```go
role, err := oi.IDClaimsToUserRole(...)
...
clSession := clsessions.NewSession()
_, err = oi.ds.ExecContext(
    ctx,
    "INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
    clSession.ID,
    strings.ToLower(email),
    role,
)
```

Because `email` was never successfully assigned, it retains its zero value (`""`), and the code proceeds to create and persist a new `oidc_sessions` row bound to an empty/blank email with whatever role was derived from the group claims, then (per the HTTP handler's normal flow which persists past this point) sets the session cookie for the caller. This is directly analogous to the referenced Linux kernel CVE: a NULL/invalid condition is detected but the guard fails to stop the subsequent privileged use of the invalid value, and the flawed state is used downstream anyway.

### Impact Explanation
This path is reachable by any external, unauthenticated actor who can complete (or partially forge, depending on the identity provider's claim shaping) an OIDC token exchange against the configured `ExchangeTokenRequest` endpoint. If an IdP-issued ID token omits or malforms the `email` claim while still supplying admin/edit/run group claims, the request is not rejected — it results in a persisted session row and role in `oidc_sessions` with an empty owner identity. This blurs identity binding for session/role handling in the node's authentication layer (per the "session/token handling" analog scope): a session could be minted and returned to the client without an enforced, verified email tying it to a real user record, undermining the integrity of role-based access control for the node's admin API.

### Likelihood Explanation
Exploitability depends on whether an untrusted or misconfigured IdP response can omit/malform the `email` claim while still including group/role claims that pass `IDClaimsToUserRole`. This is plausible in multi-tenant or loosely configured OIDC setups, or if an attacker can influence claims returned during the exchange (e.g., a compromised or attacker-controlled IdP endpoint, or a race/config error). The missing `return` is a clear, deterministic code defect (not a timing or race condition), so once the precondition (missing/invalid `email` claim) is met, the flawed session-creation path is always taken.

### Recommendation
Add a `return` statement immediately after writing the error response in the `email` extraction failure branch, matching the pattern used by every other validation branch in `handleTokenExchange`:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
Additionally, consider validating that `email` is non-empty before the `oidc_sessions` INSERT as defense-in-depth, and add a regression test asserting that a claims payload lacking a usable `email` field results in no `oidc_sessions` row being created and no session cookie issued.

### Proof of Concept
1. Configure the node with OIDC auth enabled (`AuthenticationMethod = "oidc"`).
2. Drive the `/oidc/authenticate/callback` (`handleTokenExchange`) flow with a valid `state` and a `code` that exchanges for an ID token whose claims include valid group claims mapping to a role (e.g., `EditClaim`) but where the `email` claim is absent or is not a JSON string (e.g., `email: 12345` or omitted entirely).
3. Observe that the server logs `"Failed to get email from claims"` and writes a `500` body, but does not stop processing.
4. Observe a new row inserted into `oidc_sessions` with `user_email = ''` and the mapped role, and that the HTTP response/cookie flow proceeds as if authentication succeeded, because no `return` halted the handler. [3](#0-2)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-260)
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

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}

	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}

	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}

	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
		return
	}
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
		return
	}
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

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
