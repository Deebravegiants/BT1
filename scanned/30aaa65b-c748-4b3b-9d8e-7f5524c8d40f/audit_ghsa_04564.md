# [C] Nezha vulnerable to cross-tenant terminal/file-manager session hijack via WebSocket stream UUID without ownership check

## Summary
Severity: Critical
Advisory: GHSA-q6xx-5vr8-p898
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-q6xx-5vr8-p898
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.14.13
- Go: `github.com/nezhahq/nezha` — affected >=2.0.0 <2.0.10

## Details
### Summary

In nezha **v1.14.13–v1.14.14** and **v2.0.0–v2.0.9**, the WebSocket endpoints `GET /ws/terminal/:id` and `GET /ws/file/:id` authenticate the caller only by the presence of a valid stream UUID, with no ownership check tying that UUID to the user who created the stream. Any authenticated dashboard user (including a `RoleMember`) who learns a live stream UUID can attach to the session and gain interactive shell access or full file-manager control on the target server — i.e. cross-tenant RCE.

This was silently fixed in commit [`6661d6a`](https://github.com/nezhahq/nezha/commit/6661d6a7fc1c269f55c7f4e775082ad23fbe0f54) (2026-05-18, shipped in v2.0.10). At submission time no public CVE/GHSA covers this fix, so operators of v1.14.x and pre-v2.0.10 v2.x deployments have no signal that they are running vulnerable code.

### Details

**Stream allocation — `service/rpc/io_stream.go` (v2.0.9):**

```go
func (s *NezhaHandler) CreateStream(streamId string) {
    s.ioStreamMutex.Lock()
    defer s.ioStreamMutex.Unlock()

    s.ioStreams[streamId] = &ioStreamContext{
        userIoConnectCh:  make(chan struct{}),
        agentIoConnectCh: make(chan struct{}),
    }
}
```

No creator is bound to the stream.

**Stream attach — `cmd/dashboard/controller/terminal.go` (v2.0.9):**

```go
// @Router /ws/terminal/{id} [get]
func terminalStream(c *gin.Context) (any, error) {
    streamId := c.Param("id")
    if _, err := rpc.NezhaHandlerSingleton.GetStream(streamId); err != nil {
        return nil, err
    }
    defer rpc.NezhaHandlerSingleton.CloseStream(streamId)
    // ... WebSocket upgrade and bidirectional pipe ...
}
```

The only authorization check is `GetStream(streamId)` — "does this UUID exist in the in-memory map". `getUid(c)` is never compared against the user who called `createTerminal`. The same pattern is present in `fmStream(c)` in `cmd/dashboard/controller/fm.go`.

**Where the UUID leaks:**

`createTerminal` returns the UUID to the legitimate client, which then opens `wss://<dashboard>/ws/terminal/<UUID>`. As a URL path component the UUID is exposed via:

- Reverse-proxy access logs (nginx, Caddy, Cloudflare).
- Referer headers when the page embeds external resources or error reporters.
- Browser history / bookmark sync.
- Frontend telemetry (Sentry, Bugsnag) breadcrumbs that include the WebSocket URL.
- Any shared-tenant or multi-operator log viewer.

Any authenticated user with access to one of these side channels can attach to a live session.

### PoC

1. Deploy nezha v2.0.9. Add at least one server. Configure two accounts: `admin` (RoleAdmin, owns the server) and `member` (RoleMember, no access to that server).
2. As `admin`, open the web terminal for the server. The browser opens `wss://<dashboard>/ws/terminal/<UUID>`. Capture this UUID from the network inspector, server access log, or `Referer` header.
3. From a separate session logged in as `member`, open `wss://<dashboard>/ws/terminal/<UUID>` (same UUID). The member's WebSocket attaches to the same `ioStreamContext` because `terminalStream` only checks `GetStream(streamId)` — no ownership check.
4. The member can now read the admin's shell output and inject keystrokes, achieving shell-level RCE on the target server, with no visible signal to the legitimate session owner.

Same flow works against `/ws/file/:id` (file-manager hijack: arbitrary read/write on the target server's filesystem).

### Impact

- **Severity**: Critical. Interactive RCE on a server administered by another user, with no audit signal to the rightful session owner.
- **Attack complexity**: Low. The attacker needs an authenticated dashboard account (which any `RoleMember` is) and one captured UUID from a side channel.
- **Confidentiality / Integrity / Availability**: all High. `/ws/file/:id` exposes arbitrary read+write on the target filesystem; `/ws/terminal/:id` is a full shell.

This is the same impact tier as CVE-2026-46716 (cross-tenant cron RCE) and arguably worse, because the entry point is a passively-leaked URL rather than an authenticated POST — attackers do not need direct dashboard interaction once the UUID is leaked through logs or telemetry.

### Fix reference

Already fixed in master by commit [`6661d6a`](https://github.com/nezhahq/nezha/commit/6661d6a7fc1c269f55c7f4e775082ad23fbe0f54) ("fix(rpc): bind io_stream sessions to creator to prevent terminal/fm hijack"):

- `CreateStream` now accepts a `creatorUserID uint64` and stores it on the `ioStreamContext`.
- New `IsStreamAuthorizedForUser(streamId, userID, isAdmin)` helper.
- `terminalStream` and `fmStream` call this helper **before** the WebSocket upgrade and **before** the `defer CloseStream(streamId)`, so a rejected attempt does not tear down a legitimate stream.

Shipped in v2.0.10 (2026-05-19). The v1.14 line has not received a backport.

### Why this advisory

The fix landed silently. The other May 17–21 fixes received public GHSAs (GHSA-99gv-2m7h-3hh9, GHSA-rxf6-wjh4-jfj6, GHSA-hvv7-hfrh-7gxj, GHSA-w4g9-mxgg-j532, GHSA-6x26-5727-rrm9, GHSA-4g6j-g789-rghm) covering cron RCE, AlertRule trigger, telemetry leak, notification SSRF, DDNS SSRF, and agent forge-results respectively — but none cover the terminal / file-manager session hijack. This advisory closes that gap so operators of v1.14.x and v2.0.0–v2.0.9 know to upgrade.

### Recommended action

- Publish this GHSA so v2.x operators below v2.0.10 see the alert in their dependency scanners.
- Either backport `6661d6a` to a v1.14.15 release, or mark the v1.14 line end-of-life in `SECURITY.md` so operators understand the support boundary.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-q6xx-5vr8-p898
- https://github.com/nezhahq/nezha
