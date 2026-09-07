# [M] Algernon: Auto-refresh SSE event server binds to all interfaces by default on Linux/macOS

## Summary
Severity: Medium
Advisory: GHSA-gj84-924c-48fx
CVE: CVE-2026-46430
CWE: CWE-1188, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-gj84-924c-48fx
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.7

## Details
### Summary

The SSE event server bound to `0.0.0.0:5553` on Linux/macOS by default because the platform-dependent host default in `engine/flags.go:39-46` set `host = ""` for non-Windows, and `utils.JoinHostPort("", ":5553")` resolves to `":5553"` — a Go `http.Server.Addr` of `":5553"` listens on every interface. On Windows the same code chose `"localhost"`, binding loopback only.

The result was a platform split where the OS Algernon's dev workflow is most often used on (Linux/macOS) got the network-exposed default, and only Windows users got the loopback-safe one. A LAN peer with no developer interaction could connect to `<dev-laptop-ip>:5553` and read the file-change stream.

This advisory covers the bind-address default in isolation. The fix is independent of authentication (#2a) and CORS (#2b) — switching the default to loopback can be done without touching either.

### Details

#### Root cause — platform-dependent `host` default in `handleFlags`

```go
// engine/flags.go:39-46  (1.17.6)
host := ""
if runtime.GOOS == "windows" {
    host = "localhost"
    // Default Bolt database file
    ac.defaultBoltFilename = filepath.Join(serverTempDir, "algernon.db")
    // Default log file
    ac.defaultLogFile = filepath.Join(serverTempDir, "algernon.log")
}
```

```go
// engine/config.go:388-391  (1.17.6, finalConfiguration)
if ac.eventAddr == "" {
    ac.eventAddr = utils.JoinHostPort(host, ac.defaultEventColonPort)
}
```

Result tabulated:

| Platform | `host` | `eventAddr` after `JoinHostPort` | Effective bind |
|---|---|---|---|
| Linux | `""` | `":5553"` | `0.0.0.0:5553` (all interfaces) |
| macOS | `""` | `":5553"` | `0.0.0.0:5553` (all interfaces) |
| Windows | `"localhost"` | `"localhost:5553"` | `127.0.0.1:5553` (loopback) |

The same `host` value also governs the main web server bind, so the platform split affects both ports. The web-server bind on Linux/macOS is a separate (defensible) design decision — a server intended to be reachable; the SSE port is *not* such a service and inherited the same default by accident.

#### Why this is an independent finding

The fix is a single line: change the default `host` value, or change the `eventAddr` default specifically, to `"localhost"` regardless of platform. No change to authentication or CORS is required to close the network-reach half of the original bundled advisory. A LAN peer can no longer connect — the listener is unreachable from another host — even if the SSE handler still has no authentication and still returns `Allow-Origin: *`.

### PoC (against 1.17.6 on Linux/macOS)

```bash
# Operator's laptop on a hotel/cafe/office WiFi:
algernon -a /path/to/project
# => SSE listener bound to 0.0.0.0:5553

# Any peer on the same subnet:
$ curl -sN http://<dev-laptop-ip>:5553/sse
id: 0
data: /path/to/project/secret-notes.md

id: 1
data: /path/to/project/.env.local
```

No interaction from the developer is required. The peer needs network reach and nothing else.

### Impact

- **Confidentiality:** medium. LAN-bounded continuous information disclosure of filenames and edit timing.
- **Integrity:** none.
- **Availability:** none directly.

The CVSS vector uses `AV:A` (adjacent network) to model the LAN-only reach. The vector for a misconfigured deployment behind a NAT-less or routed network would shift to `AV:N` and rise to 5.3.

### Suggestions to fix

**Primary fix — pick `localhost` as the SSE default on every platform.**

```go
// engine/flags.go -- platform-independent default for the event listener
// (keep the existing platform split for the WEB server if desired, but
// not for the event server)
host := "localhost"
```

Or, more surgically:

```go
// engine/config.go -- finalConfiguration
if ac.eventAddr == "" {
    ac.eventAddr = utils.JoinHostPort("localhost", ac.defaultEventColonPort)
}
```

An operator who genuinely wants LAN-reachable SSE can pass `--eventserver 0.0.0.0:5553` explicitly and accept the consequences.

**Stronger fix — eliminate the second listener entirely.** Mount the SSE handler on the main mux at `/sse`. The bind address is then whatever the main server uses; there is no second listener and therefore no second bind-address default to get wrong.

### Live verification

Audit-host bind check (Windows 10):

```
$ netstat -an | findstr 5553
  TCP    127.0.0.1:5553         0.0.0.0:0              LISTENING
```

Confirms the Windows default is `localhost`. The Linux/macOS bind to `0.0.0.0:5553` is documented in the code path above; it was not exercised on the audit machine because the audit host was Windows. A maintainer reproducing on a Linux host would see `0.0.0.0:5553 LISTENING` from `ss -tlnp`.

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-gj84-924c-48fx
- https://github.com/xyproto/algernon
