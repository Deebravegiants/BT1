# [M] Vapor's Metrics integration could cause a system drain

## Summary
Severity: Medium
Advisory: GHSA-gcj9-jj38-hwmc
CVE: CVE-2021-21328
CWE: CWE-400
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-gcj9-jj38-hwmc
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=0 <4.40.1

## Details
### Impact
This is a DoS attack against anyone who Bootstraps a metrics backend for their Vapor app with the following attack vector:

1. send unlimited requests against a vapor instance with different paths. this will create “unlimited” counters and timers, which will eventually drain the system.
2. downstream services might suffer from this attack as well by being spammed with error paths

### Patches
This has been patched in 4.40.1. The `DefaultResponder` will rewrite any undefined route paths for to `vapor_route_undefined` to avoid unlimited counters.

### Workarounds
Don't bootstrap a metrics system or upgrade to 4.40.1

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Vapor](https://github.com/vapor/vapor)
* Ask in [Discord](http://vapor.team)

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-gcj9-jj38-hwmc
- https://nvd.nist.gov/vuln/detail/CVE-2021-21328
- https://github.com/vapor/vapor/commit/e3aa712508db2854ac0ab905696c65fd88fa7e23
- https://github.com/vapor/vapor
- https://github.com/vapor/vapor/releases/tag/4.40.1
- https://vapor.codes
