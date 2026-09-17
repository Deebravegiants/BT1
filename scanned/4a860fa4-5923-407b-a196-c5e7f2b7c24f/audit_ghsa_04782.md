# [H] Tilt: Unauthenticated pprof debug endpoints on the Tilt HUD server

## Summary
Severity: High
Advisory: GHSA-p749-9w62-w533
CVE: CVE-2026-55882
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p749-9w62-w533
Type: github-advisory

## Affected
- Go: `github.com/tilt-dev/tilt` — affected >=0.19.5 <0.37.4

## Details
## Summary
The Tilt HUD server mounts Go's `net/http/pprof` handlers under `/debug` with no access control. When the HUD is network-exposed, an attacker can read process memory — including session and apiserver tokens — and hold the process under profiling.

## Details
A blank import of `net/http/pprof` registers its handlers on `http.DefaultServeMux`, which the HUD controller mounts under `/debug` on both the web router and the apiserver listener. `/debug/pprof/heap` and `/goroutine` expose process memory, including the session token (also issued in the `Tilt-Token` cookie) and the apiserver loopback bearer token; `/profile` and `/trace` let a caller sample the process for an arbitrary duration.

## Impact
An unauthenticated caller who can reach the listener can extract process memory — including the session and apiserver tokens — and degrade performance by holding the process under CPU profiling or tracing. The leaked tokens compound the missing-authentication finding on the same server.

### Conditions for exploitation
- Affected version in `>= 0.19.5, <= 0.37.3`.
- HUD (or apiserver) listener bound to a non-loopback address (`tilt up --host 0.0.0.0`, or `TILT_HOST` set).
- Network reachability to the listener (default port `10350`).

### Not affected
- The default loopback-only bind is not reachable from the network.

## Workarounds
Use the default loopback bind (omit `--host`, unset `TILT_HOST`) so `/debug` is not remotely reachable. No complete workaround short of upgrading for non-loopback deployments.

## References
- https://github.com/tilt-dev/tilt/security/advisories/GHSA-p749-9w62-w533
- https://github.com/tilt-dev/tilt/pull/6776
- https://github.com/tilt-dev/tilt
- https://github.com/tilt-dev/tilt/releases/tag/v0.37.4
