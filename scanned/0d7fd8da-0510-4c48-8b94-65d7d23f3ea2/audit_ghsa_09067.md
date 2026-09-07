# [M] Nezha Monitoring: Nezha WebSocket server stream discloses cross-tenant server telemetry to authenticated members

## Summary
Severity: Medium
Advisory: GHSA-hvv7-hfrh-7gxj
CVE: CVE-2026-47124
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-hvv7-hfrh-7gxj
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.4.0 <1.14.15-0.20260517034128-05e5da253519

## Details
### Summary

Any authenticated non-admin member can connect to the server-status WebSocket and receive telemetry for all servers, including servers owned by other users. The normal server list API filters objects by `HasPermission`, but the WebSocket stream treats the presence of any authenticated user as authorization for the full unfiltered server list.

### Details

The server WebSocket route is registered under the optional-auth group in `cmd/dashboard/controller/controller.go:71-73`:

```go
optionalAuth := api.Group("", optionalAuthMw)
optionalAuth.GET("/ws/server", commonHandler(serverStream))
```

`serverStream` treats any `CtxKeyAuthorizedUser` as a member, without checking admin role or per-server ownership, in `cmd/dashboard/controller/ws.go:123-139`:

```go
u, isMember := c.Get(model.CtxKeyAuthorizedUser)
var userId uint64
if isMember {
    userId = u.(*model.User).ID
}
...
stat, err := getServerStat(count == 0, isMember)
```

The authorization boolean is then used as a full/guest switch in `getServerStat` in `cmd/dashboard/controller/ws.go:160-184`:

```go
if authorized {
    serverList = singleton.ServerShared.GetSortedList()
} else {
    serverList = singleton.ServerShared.GetSortedListForGuest()
}
...
servers = append(servers, model.StreamServer{
    ID:           server.ID,
    Name:         server.Name,
    PublicNote:   utils.IfOr(withPublicNote, server.PublicNote, ""),
    DisplayIndex: server.DisplayIndex,
    Host:         utils.IfOr(authorized, server.Host, server.Host.Filter()),
    State:        server.State,
    CountryCode:  countryCode,
    LastActive:   server.LastActive,
})
```

For authenticated members, `GetSortedList()` returns all servers and `server.Host` is not filtered. There is no call to `server.HasPermission(c)`.

The streamed response model in `model/server_api.go:5-20` includes server ID/name, public note, host details, runtime state, country code, last active time, and global online count. Host and state fields include platform version, agent version, CPU/GPU names, memory/disk/swap totals, architecture, virtualization, boot time, CPU load, memory/disk/swap usage, network transfer/speed, uptime, TCP/UDP/process counts, temperatures, and GPU utilization, as defined in `model/host.go:20-38` and `model/host.go:100-112`.

The normal list endpoint has the expected object-level authorization. `GET /api/v1/server` is registered with `listHandler` in `cmd/dashboard/controller/controller.go:113`, and `listHandler` filters each returned object with `HasPermission` in `cmd/dashboard/controller/controller.go:263-291`:

```go
filtered := filter(c, data)
...
return slices.DeleteFunc(s, func(e E) bool {
    return !e.HasPermission(ctx)
})
```

The shared permission model in `model/common.go:44-56` allows admins to see all objects but restricts members to objects whose `UserID` matches their user ID:

```go
if user.Role == RoleAdmin {
    return true
}
return user.ID == c.UserID
```

Mitigations checked:

- Guests receive `GetSortedListForGuest()` and `Host.Filter()` output, but authenticated members bypass both guest restrictions.
- `HideForGuest` only affects unauthenticated guests, not members.
- The normal `/api/v1/server` list endpoint uses `listHandler` and is not affected in the same way.
- No owner/admin filter is applied in the WebSocket path.

Candidate score: 12/14

- Reachability: 2, default WebSocket API
- Attacker control: 1, attacker controls authentication state and connection
- Privilege required: 1, authenticated member
- Sink impact: 2, cross-tenant sensitive telemetry disclosure
- Mitigation weakness: 2, no object-level auth in the WebSocket path
- Default exposure: 2, endpoint is part of default dashboard
- Safe PoC feasibility: 2, can be verified with local users/servers or statically

Exploitability gate: statically confirmed

- Reachable source: `GET /api/v1/ws/server`
- Default/common configuration: dashboard API exposed by default
- Missing/bypassed mitigation: member-vs-guest check replaces object-level authorization
- Impact-bearing sink: WebSocket response includes unfiltered all-server telemetry
- Safe proof: static source-to-sink proof; full runtime test blocked locally by unavailable Go 1.26 toolchain
- Affected version evidence: confirmed at commit `85b0dd2992733037b019442caffc6c049ba937dd` (`v2.0.7-1-g85b0dd2`)
- Variant review: normal server list endpoint and guest filtering were checked

### PoC

Static local PoC steps:

1. Start Nezha with two non-admin users and at least one server assigned to each user.
2. Authenticate as user A.
3. Connect to the WebSocket endpoint with user A's token, for example:

```http
GET /api/v1/ws/server HTTP/1.1
Host: 127.0.0.1:8008
Cookie: nz-jwt=<user-a-token>
Upgrade: websocket
Connection: Upgrade
```

4. Observe that the JSON messages contain entries for all servers from `singleton.ServerShared.GetSortedList()`, including servers whose `UserID` does not match user A.
5. Compare with `GET /api/v1/server` using the same token; that route is filtered through `listHandler`/`HasPermission` and should only return user A's own servers.

Cleanup: no persistent state is created by the WebSocket connection.

Local dynamic confirmation note: the full project test/runtime could not be executed in this audit environment because the repository requires Go 1.26 and the local toolchain reported `go: download go1.26 for linux/amd64: toolchain not available`.

### Impact

This is an authenticated horizontal information disclosure. A low-privileged member can continuously monitor other users' server inventory and live telemetry, including host platform details, agent versions, CPU/GPU details, resource usage, traffic counters, country code, and last-active timestamps. This may expose infrastructure composition, usage patterns, and operational state across tenants.

## Suggested remediation

Apply object-level authorization in `getServerStat` for authenticated non-admin users. For each server in the stream, include it only if the current user is admin or `server.UserID` matches the authenticated user. Keep guest filtering and host redaction for unauthenticated users.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-hvv7-hfrh-7gxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47124
- https://github.com/nezhahq/nezha
