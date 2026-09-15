Audit Report

## Title
Missing `return` After Failed Email-Claim Extraction and DB Insert Errors Grants Authenticated Session in `handleTokenExchange` - (File: core/sessions/oidcauth/oidc.go)

## Summary
In `oidcAuthenticator.handleTokenExchange`, when the `email` claim cannot be type-asserted from the verified ID token claims map, the handler logs the error and writes an HTTP 500 body via `c.String(...)` but does not `return`, so execution falls through to role mapping, `oidc_sessions` row insertion, audit logging of `AuthLoginSuccessNo2FA`, and `ginSession.Save()` which commits a valid, functioning session cookie. The identical missing-`return` pattern exists on the subsequent `oidc_sessions` INSERT failure branch, allowing a session cookie to be issued even when the session was never durably persisted.

## Finding Description
The code at [1](#0-0)  shows:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
}
```
No `return` follows the error write, so control proceeds to `IDClaimsToUserRole` [2](#0-1) , the `INSERT INTO oidc_sessions` [3](#0-2)  (which has the same missing-`return` defect on its own error branch), the audit log call `oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, ...)`, and finally `ginSession.Set(webauth.SessionIDKey, clSession.ID)` followed by `ginSession.Save()` [4](#0-3) , which persists a valid session cookie on the response regardless of the earlier 500 write.

That cookie is not cosmetic: `AuthenticateBySession` in `core/web/auth/auth.go` reads `SessionIDKey` from the cookie and calls `authr.AuthorizedUserWithSession(ctx, sessionID)` [5](#0-4)  to look up the corresponding `oidc_sessions` row and grant a `clsessions.User` with the mapped `Role`, which is subsequently checked by `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` [6](#0-5) . Because `role` is derived independently from `idClaims` (via `ClaimName()`, e.g. a `groups` claim) rather than from `email`, a verified ID token that is missing the `email` claim but carries valid, signed group/role claims still yields a fully functional, role-bearing authenticated session — the missing `return` is not merely a redundant write, it is a broken authentication gate.

## Impact Explanation
This maps to the in-scope "node API authentication/role bypass" impact category: an OIDC login flow can complete and mint a real, cookie-backed session with the mapped RBAC role even though the identity-binding `email` claim was absent, and a false `AuthLoginSuccessNo2FA` audit entry is recorded. The `oidc_sessions` row is created with `user_email = ""` while a legitimately elevated role (e.g., admin, if the IdP's group claim maps that way) can still be attached and subsequently authorized by `AuthorizedUserWithSession`.

## Likelihood Explanation
Triggering this requires the configured, trusted OIDC provider to return a token that passes `oi.provider.Verifier(oi.oidcConfig).Verify(...)` (i.e., correctly signed by the trusted IdP) but whose claims lack `email` — a realistic scenario for IdPs/scopes not configured to include the `email` claim, or for group-only claim configurations, reachable through the standard, unprivileged `/oidc/callback`-style flow with no elevated credentials needed on the node side. The same reachable, unconditional flaw applies to the DB insert-failure branch.

## Recommendation
Add `return` immediately after both error-writing branches:
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
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```
Additionally, explicitly reject empty `email` before proceeding, and audit the file for other "log + write response + fall through" patterns.

## Proof of Concept
1. Stand up a test OIDC provider whose signing keys are trusted by the node's `oi.oidcConfig`/`oi.provider`, and configure it to issue an ID token that omits the `email` claim but includes a group claim mapped via `IDClaimsToUserRole` to a valid role (per `oi.config.AdminClaim()`/etc.).
2. Call `GET /oidc/login`-equivalent (`handleSignIn`) to establish `state` in the gin session and complete the redirect.
3. `POST` the resulting `code`/`state` to the token exchange endpoint bound to `handleTokenExchange`.
4. Observe the HTTP 500 body "Failed to get email from claims" is written, but the response also carries a `Set-Cookie` from `ginSession.Save()`.
5. Replay the cookie against any RBAC-protected endpoint (e.g., one wrapped by `RequiresAdminRole`) and confirm it is accepted, and inspect the `oidc_sessions` table/audit log for a row with `user_email = ''` and a false `AuthLoginSuccessNo2FA` entry.

A Go unit test on `handleTokenExchange` with a mocked `oi.provider`/`oi.oauth2Config` returning claims without `email` would deterministically demonstrate that `ginSession.Save()` is still called and `c.JSON(http.StatusOK, ...)`/cookie persistence occurs despite the earlier error write.

### Citations

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

**File:** core/web/auth/auth.go (L55-71)
```go
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/web/auth/auth.go (L200-253)
```go
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```
