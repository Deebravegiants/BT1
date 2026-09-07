# [M] Nezha Monitoring: Authenticated users can claim the dashboard Host through NAT and preempt all dashboard routing

## Summary
Severity: Medium
Advisory: GHSA-x6fg-52vr-hj4w
CVE: CVE-2026-53520
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-x6fg-52vr-hj4w
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=2.0.14 <2.1.0

## Details
### Summary
An authenticated non-admin user who owns any server can create or update a NAT profile whose `domain` is equal to the dashboard's own HTTP Host (for example, `dashboard.example:8008`). The dashboard's top-level HTTP/gRPC multiplexer checks `NATShared.GetNATConfigByDomain(r.Host)` before dispatching requests to the dashboard API, frontend, or gRPC handler, so a member-controlled NAT profile for the dashboard Host takes precedence over the real dashboard.

A disabled claimed NAT profile blocks matching dashboard requests before they reach the dashboard handler. An enabled claimed NAT profile routes matching requests into `ServeNAT`, which sends a NAT task to the member's selected agent and wraps the original HTTP request into the NAT IO stream. This allows a low-privileged dashboard user to take over routing for a global host name that should be reserved for the dashboard operator.

Tested locally against commit `8b5e382fe217107c7b777ea9c6b4bc3d2e156202` of `github.com/nezhahq/nezha`.

### Details
The NAT management API is exposed to any authenticated user, not just administrators: `auth.POST("/nat", commonHandler(createNAT))` and `auth.PATCH("/nat/:id", commonHandler(updateNAT))` are registered in `cmd/dashboard/controller/controller.go:147-150`.

`createNAT` accepts the request body into `model.NATForm`, verifies only that the selected server exists and `server.HasPermission(c)` succeeds, then stores the caller-controlled `nf.Domain` directly into `n.Domain` and updates the shared NAT cache (`cmd/dashboard/controller/nat.go:48-80`). `updateNAT` performs the same assignment after checking ownership of the selected server and existing NAT record (`cmd/dashboard/controller/nat.go:96-140`). `NATForm.Domain` is an unconstrained string with no reserved-host or host-ownership validation (`model/nat_api.go:3-9`), and `model.NAT.Domain` is only globally unique in the database (`model/nat.go:3-10`).

The singleton NAT cache indexes persisted NAT profiles directly by `profile.Domain` in `NewNATClass` (`service/singleton/nat.go:17-25`) and writes updates into the same map with `c.list[n.Domain] = n` (`service/singleton/nat.go:37-45`). Runtime lookup is an exact map lookup of the incoming Host string (`service/singleton/nat.go:65-69`).

The routing boundary is global: `newHTTPandGRPCMux` checks `singleton.NATShared.GetNATConfigByDomain(r.Host)` before it checks for gRPC or invokes the dashboard HTTP handler (`cmd/dashboard/main.go:207-225`). If the NAT profile exists but is disabled, the router returns the WAF block page and never reaches the dashboard (`cmd/dashboard/main.go:209-214`). If it is enabled, the router calls `rpc.ServeNAT(w, r, natConfig)` and returns (`cmd/dashboard/main.go:216-217`).

`ServeNAT` selects the server from the NAT profile, requires that server's task stream to be online, sends a `TaskTypeNAT` task containing the NAT target host, then calls `utils.NewRequestWrapper(r, w)` and attaches the wrapped original request to the IO stream (`cmd/dashboard/rpc/rpc.go:142-204`). The request wrapper serializes the original request with `req.Write(buf)`, which includes the request line and headers, before streaming it over the hijacked connection (`pkg/utils/request_wrapper.go:19-31`). This is the intended NAT tunnel behavior, but it is unsafe when an ordinary user can bind the dashboard's own Host name.

Default/common exposure evidence: the dashboard binary is the primary shipped component of module `github.com/nezhahq/nezha` (`go.mod:1`), listens on port `8008` when `listen_port` is unset (`model/config.go:146-148`), and the Dockerfile exposes `8008` (`Dockerfile:14-18`). NAT management is part of the authenticated dashboard route set, so the vulnerable path is reachable in a default dashboard deployment with multiple users or any non-admin user who controls a server.

False-positive checks performed:

- The NAT routes are authenticated but not admin-only (`cmd/dashboard/controller/controller.go:147-150`).
- The only create-time authorization check is ownership of the selected server (`cmd/dashboard/controller/nat.go:56-65`), not authority over the claimed Host.
- The update path likewise accepts a caller-controlled replacement domain after ownership checks (`cmd/dashboard/controller/nat.go:109-139`).
- The NAT cache uses the domain string as the global dispatch key without reserving the dashboard Host (`service/singleton/nat.go:17-25`, `service/singleton/nat.go:37-45`, `service/singleton/nat.go:65-69`).
- The top-level mux checks NAT before dashboard/gRPC routing (`cmd/dashboard/main.go:207-225`).
- A control request using a different Host reaches the dashboard handler in the local reproduction, ruling out a generic handler failure.

Candidate score: 16/18.

- Reachability: 2 — authenticated NAT API and top-level mux are default dashboard paths.
- Attacker control: 2 — `NATForm.Domain` is directly controlled by the authenticated caller.
- Privilege required: 1 — requires an authenticated user with an owned server; no admin role is required.
- Sink impact: 2 — matching dashboard Host traffic is blocked or routed into the attacker's NAT stream instead of the dashboard.
- Mitigation weakness: 2 — no dashboard-host reservation, domain ownership validation, or post-parse host authorization was found.
- Default exposure: 2 — dashboard listens on/exposes port 8008 by default and NAT routes are registered in the default authenticated API.
- Safe reproduction feasibility: 2 — reproduced locally with a safe temporary unit-test harness and local SQLite database.
- Static certainty: 2 — source-to-sink chain is complete from JSON body to NAT cache to global router.
- False-positive resistance: 1 — disabled-route preemption is dynamically proven; enabled-route forwarding is supported by code path but was not exercised with a real agent binary in this repository checkout.

Exploitability gate result: confirmed for authenticated dashboard Host preemption and denial of service. Enabled-route request forwarding is included as impact rationale from the exact `ServeNAT` source path, but the reproducible proof uses a disabled NAT profile to avoid requiring a live agent.

### PoC
The following safe local reproduction adds only temporary test/stub files, uses a temporary SQLite database, runs the real unexported `newHTTPandGRPCMux`, and removes all temporary files on exit. It does not start a public listener or contact external systems.

Run from a clean checkout of commit `8b5e382fe217107c7b777ea9c6b4bc3d2e156202`:

```bash
cleanup() { rm -f cmd/dashboard/admin-dist/claude_nat_poc_placeholder.txt cmd/dashboard/user-dist/claude_nat_poc_placeholder.txt cmd/dashboard/docs/docs.go cmd/dashboard/nat_host_claim_tmp_test.go; rmdir cmd/dashboard/docs 2>/dev/null || true; }
cleanup
mkdir -p cmd/dashboard/docs
printf 'placeholder' > cmd/dashboard/admin-dist/claude_nat_poc_placeholder.txt
printf 'placeholder' > cmd/dashboard/user-dist/claude_nat_poc_placeholder.txt
cat > cmd/dashboard/docs/docs.go <<'EOF'
package docs

var SwaggerInfo = struct{ Version string }{Version: "test"}
EOF
cat > cmd/dashboard/nat_host_claim_tmp_test.go <<'EOF'
package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"github.com/nezhahq/nezha/model"
	"github.com/nezhahq/nezha/service/singleton"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func TestNATDomainPreemptsDashboardHost(t *testing.T) {
	dbPath := filepath.Join(t.TempDir(), "nezha-nat-host-poc.sqlite")
	db, err := gorm.Open(sqlite.Open(dbPath), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	singleton.DB = db
	if err := db.AutoMigrate(&model.User{}, &model.Server{}, &model.NAT{}); err != nil {
		t.Fatal(err)
	}

	member := model.User{Username: "member", Role: model.RoleMember, Password: "unused"}
	if err := db.Create(&member).Error; err != nil {
		t.Fatal(err)
	}
	server := model.Server{Common: model.Common{UserID: member.ID}, UUID: "11111111-1111-1111-1111-111111111111", Name: "member-agent"}
	if err := db.Create(&server).Error; err != nil {
		t.Fatal(err)
	}
	nat := model.NAT{Common: model.Common{UserID: member.ID}, Enabled: false, Domain: "dashboard.example:8008", Host: "127.0.0.1:18080", ServerID: server.ID, Name: "claim-dashboard-host"}
	if err := db.Create(&nat).Error; err != nil {
		t.Fatal(err)
	}
	singleton.NATShared = singleton.NewNATClass()

	httpHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusTeapot)
		_, _ = w.Write([]byte("dashboard handler reached"))
	})
	grpcHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusAccepted)
	})
	h := newHTTPandGRPCMux(httpHandler, grpcHandler)

	req := httptest.NewRequest(http.MethodGet, "http://dashboard.example:8008/api/v1/profile", nil)
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	if rec.Code == http.StatusTeapot || rec.Body.String() == "dashboard handler reached" {
		t.Fatalf("dashboard handler was reached despite claimed NAT host: code=%d body=%q", rec.Code, rec.Body.String())
	}
	fmt.Fprintf(os.Stdout, "positive: Host %s matched disabled member NAT id=%d and preempted dashboard handler with status=%d\n", req.Host, nat.ID, rec.Code)

	controlReq := httptest.NewRequest(http.MethodGet, "http://other.example:8008/api/v1/profile", nil)
	controlRec := httptest.NewRecorder()
	h.ServeHTTP(controlRec, controlReq)
	if controlRec.Code != http.StatusTeapot || controlRec.Body.String() != "dashboard handler reached" {
		t.Fatalf("control host did not reach dashboard handler: code=%d body=%q", controlRec.Code, controlRec.Body.String())
	}
	fmt.Fprintf(os.Stdout, "control: Host %s missed NAT and reached dashboard handler with status=%d\n", controlReq.Host, controlRec.Code)
}
EOF
trap cleanup EXIT
GOPROXY=off go test ./cmd/dashboard -run TestNATDomainPreemptsDashboardHost -count=1 -v
```

Observed vulnerable output in this environment:

```text
=== RUN   TestNATDomainPreemptsDashboardHost
positive: Host dashboard.example:8008 matched disabled member NAT id=1 and preempted dashboard handler with status=403
control: Host other.example:8008 missed NAT and reached dashboard handler with status=418
--- PASS: TestNATDomainPreemptsDashboardHost (0.11s)
PASS
ok  	github.com/nezhahq/nezha/cmd/dashboard	0.132s
```

Expected vulnerable output: the positive request for `dashboard.example:8008` must not return the dashboard handler's `418` response; it should be intercepted by the disabled NAT profile and return the WAF/block status. The control request for `other.example:8008` must reach the dashboard handler and return `418` with body `dashboard handler reached`.

Cleanup: the shell `trap cleanup EXIT` removes the temporary test file, temporary generated docs stub, and temporary embed placeholders. The SQLite database is created under `t.TempDir()` and removed by Go's test cleanup.

Final re-check: the reproduction above was run after source-to-sink analysis and before writing this draft; it passed with the exact output shown above.

### Impact
A non-admin authenticated user can bind a global routing key that belongs to the dashboard operator. If the attacker sets `enabled=false`, all requests carrying the claimed dashboard Host are blocked before reaching dashboard API, frontend, or gRPC handlers. This can deny access to the dashboard for all users who use that Host.

If the attacker sets `enabled=true` and keeps the selected owned agent online, the matching requests enter `ServeNAT`: the dashboard sends a NAT task to that agent and streams the serialized original HTTP request into the NAT IO stream. Because `utils.NewRequestWrapper` serializes the original request with headers, dashboard requests that should have been processed locally can be forwarded to infrastructure controlled by the low-privileged user. The local proof avoids this stronger enabled-agent path, but the source path is direct in `cmd/dashboard/rpc/rpc.go:142-204` and `pkg/utils/request_wrapper.go:19-31`.

### Suggested remediation
Do not allow ordinary NAT profiles to claim dashboard-owned hosts. Recommended fixes:

1. Canonicalize incoming Host values and NAT domain values consistently, including case and port handling.
2. Add a server-side reserved-host check in both `createNAT` and `updateNAT` that rejects the configured dashboard public host(s), listen host/port combinations, and any administrator-reserved domains.
3. Consider making NAT domain creation admin-approved unless the deployment can verify domain ownership for the requesting user.
4. In the top-level mux, route dashboard/gRPC hosts before NAT when the Host is known to belong to the dashboard.
5. Add regression tests covering create, update, cache reload, and mux behavior for dashboard-host collisions.

A useful regression test is the PoC above inverted: a member-created NAT with `Domain` equal to the configured dashboard Host should be rejected by the controller, and a request with the dashboard Host should continue to reach the dashboard handler.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-x6fg-52vr-hj4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-53520
- https://github.com/nezhahq/nezha
