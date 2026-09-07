# [C] Tilt: Missing authentication on the network-exposed Tilt HUD server

## Summary
Severity: Critical
Advisory: GHSA-c73q-8xxr-rgqm
CVE: CVE-2026-55884
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c73q-8xxr-rgqm
Type: github-advisory

## Affected
- Go: `github.com/tilt-dev/tilt` — affected >=0.20.8 <0.37.4

## Details
## Summary
The Tilt HUD HTTP server exposes state-changing and sensitive-read endpoints with no authentication. When the HUD is bound to a non-loopback address, a network attacker can trigger the developer's pre-defined Tiltfile resources, tamper with Tiltfile arguments, read full engine state including the session token, and reach the Tilt apiserver through a token-attaching proxy.

## Details
The HUD server registers its handlers on a `gorilla/mux` router with no authenticating middleware. The `cookieWrapper` helper emits the `Tilt-Token` cookie but never validates it, and is attached only to the static-asset prefix.

## Impact
An unauthenticated network caller can force any developer-defined resource to run on the host as the `tilt` user (choosing which and when, not the command text), set arbitrary Tiltfile arguments, disclose the session token and full engine state, and invoke apiserver resources via the loopback-token proxy. Because `tilt up` runs with the developer's privileges and credentials, the impact reaches the developer's environment and cluster.

### Conditions for exploitation
- Affected version in `>= 0.20.8, <= 0.37.3`.
- HUD bound to a non-loopback address (`tilt up --host 0.0.0.0`, or `TILT_HOST` set).
- Network reachability to the listener (default port `10350`).

### Not affected
- The default loopback-only bind is not reachable from the network.

## Workarounds
Use the default loopback bind (omit `--host`, unset `TILT_HOST`) and ensure nothing else proxies to `localhost:10350`. No complete workaround short of upgrading for non-loopback deployments.

## References
- https://github.com/tilt-dev/tilt/security/advisories/GHSA-c73q-8xxr-rgqm
- https://github.com/tilt-dev/tilt/pull/6776
- https://github.com/tilt-dev/tilt
- https://github.com/tilt-dev/tilt/releases/tag/v0.37.4
