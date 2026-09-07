# [M] Vitess: Missing authorization on vttablet /debug/vrlog exposes live VReplication SQL data

## Summary
Severity: Medium
Advisory: GHSA-mhc4-g3wh-cw7m
CVE: CVE-2026-65959
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-mhc4-g3wh-cw7m
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0.24.0-rc1
- Go: `vitess.io/vitess` — affected >=0

## Details
## Vulnerability Details

**File**: `go/vt/vttablet/tabletmanager/vreplication/vrlog.go`

### Summary
`vttablet`'s `/debug/vrlog` HTTP endpoint streams live VReplication event data — including the literal SQL DML statements being replicated by MoveTables, Reshard, Materialize, and "vitess"-strategy Online DDL workflows — with no authorization check at all. Every comparable "debugging" HTTP endpoint in vttablet/vtgate (querylogz, queryz, txlogz, livequeryz, schemaz, debugenv, hotrows, tablet_plans, query_stats, query_rules) calls `acl.CheckAccessHTTP(r, acl.DEBUGGING)` before serving data, so that the cluster operator's configured `--security-policy` (e.g. `deny-all`, `read-only`, or a custom plugin) is actually honored. `vrlog.go` is the one exception: it has zero references to the `acl` package.

### Root Cause
`addHttpEndpoint()` registers `/debug/vrlog` via `servenv.HTTPHandleFunc`, and `vrlogStatsHandler()` immediately starts streaming subscribed `VrLogStats` events to the response writer without first calling `acl.CheckAccessHTTP(r, acl.DEBUGGING)`, unlike every sibling handler in the same family (see e.g. `go/vt/vttablet/tabletserver/querylogz.go`'s `querylogzHandler`, which calls the check first).

The data streamed is sensitive: `go/vt/vttablet/tabletmanager/vreplication/vplayer.go` calls `NewVrLogStats(...).Send(sql)` / `.Send(event.Statement)` for every row change and statement event flowing through a VReplication stream (vplayer.go:339, 700, 771, 785) — i.e. the literal SQL (including bound data values) being copied/replicated by MoveTables, Reshard, Materialize, and Online DDL.

### Attack Scenario
1. A cluster operator configures `--security-policy=deny-all` (or `read-only`, or a custom policy) specifically to lock down debugging/admin HTTP endpoints on vttablet, relying on this being uniformly enforced.
2. An attacker who can reach the vttablet debug HTTP port (common in Kubernetes/Prometheus-scraping deployments where this port is exposed beyond localhost) — but who does NOT have the `DEBUGGING`/admin role the policy requires — sends `GET /debug/vrlog`.
3. Every other debug endpoint correctly returns `403 Forbidden`. `/debug/vrlog` returns `200 OK` and streams live VReplication event data, including raw SQL DML statements containing application data values, for as long as the attacker keeps the connection open (bounded by `timeout`/`limit` query params, repeatable).

### Impact
Confidentiality impact: disclosure of live replicated application data (potentially including PII or other sensitive column values) to an unauthorized actor, bypassing an access control the operator explicitly configured. No write/modify capability; this is a read-only information-disclosure / access-control-bypass issue, scoped to the vttablet debug HTTP listener.

### Vulnerable Code
```go
// go/vt/vttablet/tabletmanager/vreplication/vrlog.go
func addHttpEndpoint() {
	servenv.HTTPHandleFunc("/debug/vrlog", func(w http.ResponseWriter, r *http.Request) {
		ch := vrLogStatsLogger.Subscribe("vrlogstats")
		defer vrLogStatsLogger.Unsubscribe(ch)
		vrlogStatsHandler(ch, w, r)
	})
}

func vrlogStatsHandler(ch chan *VrLogStats, w http.ResponseWriter, r *http.Request) {
	timeout, limit := parseTimeoutLimitParams(r)
	// no acl.CheckAccessHTTP(r, acl.DEBUGGING) call anywhere in this file
	...
```

### Recommended Fix
```go
import "vitess.io/vitess/go/acl"

func vrlogStatsHandler(ch chan *VrLogStats, w http.ResponseWriter, r *http.Request) {
	if err := acl.CheckAccessHTTP(r, acl.DEBUGGING); err != nil {
		acl.SendError(w, err)
		return
	}
	timeout, limit := parseTimeoutLimitParams(r)
	...
```
This mirrors the exact pattern already used by `querylogz.go`, `queryz.go`, `txlogz.go`, `livequeryz.go`, `schemaz.go`, `debugenv.go`, and `tx_serializer.go` (hotrows) in the same codebase.

### Verification
Built v24.0.1 from source and wrote a standalone Go test that: (1) activates the real `deny-all` security policy via `acl.RegisterFlags`, (2) registers `/debug/vrlog` via the real, unmodified `vreplication.NewVrLogStats(...)` call path (the same one `vplayer.go` uses for live replication traffic), (3) serves the real `servenv` HTTP mux on a loopback listener, and (4) issues a real `GET /debug/vrlog` while emitting a simulated replicated statement.

Result:
```
acl.CheckAccessHTTP(DEBUGGING) under deny-all => err=not allowed: deny-all security-policy enforced
GET /debug/vrlog under deny-all => status=200 body="ROWCHANGE Event\tINSERT INTO secret_table (ssn) VALUES ('leaked-via-vrlog')\t2026-06-22T11:01:55\t147101\n"
```
The identical ACL check that protects every sibling endpoint correctly rejected the request, while `/debug/vrlog` returned 200 and streamed the simulated sensitive content — confirming the bypass against real, unmodified v24.0.1 code.

Also confirmed via the GitHub Contents API that `vrlog.go` has zero references to the `acl` package on `main`, `release-23.0`, and `release-22.0` as well, so all currently supported release lines appear affected.

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-mhc4-g3wh-cw7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-65959
- https://github.com/vitessio/vitess/pull/20467
- https://github.com/vitessio/vitess/commit/4c58cd70edc6b03d61cb65842c342ac08341e64f
- https://github.com/vitessio/vitess/commit/657662e78bde1c82df680e9cc43a686d619f8094
- https://github.com/vitessio/vitess/commit/d929225a450027406687d27af8dca45620945ceb
- https://github.com/vitessio/vitess
