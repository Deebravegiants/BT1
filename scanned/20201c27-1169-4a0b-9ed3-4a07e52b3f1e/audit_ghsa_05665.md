# [M] Fleet Windows MDM endpoint has a Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gfpw-jgvr-cw4j
CVE: CVE-2026-22808
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-gfpw-jgvr-cw4j
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet` — affected >=4.78.0 <4.78.2
- Go: `github.com/fleetdm/fleet` — affected >=4.77.0 <4.77.1
- Go: `github.com/fleetdm/fleet` — affected >=4.76.0 <4.76.2
- Go: `github.com/fleetdm/fleet` — affected >=4.75.0 <4.75.2
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.43.5-0.20260111020427-0e6c790803d1

## Details
### Summary

A cross-site scripting (XSS) vulnerability in Fleet’s Windows MDM authentication flow could allow an attacker to compromise a Fleet user account. In certain cases, this could lead to administrative access and the ability to perform privileged actions on managed devices.

### Impact

If Windows MDM is enabled, an attacker could exploit a cross-site scripting (XSS) vulnerability by convincing an authenticated Fleet user to visit a malicious link. Successful exploitation could allow retrieval of the user’s Fleet authentication token from their browser.

A compromised authentication token may grant administrative access to the Fleet API, allowing an attacker to perform privileged actions such as deploying scripts to managed hosts.

This issue does not allow unauthenticated access and does not affect instances where Windows MDM is disabled.

### Patches

- 4.78.2
- 4.77.1
- 4.76.2
- 4.75.2
- 4.53.3

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Windows MDM.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-gfpw-jgvr-cw4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22808
- https://github.com/fleetdm/fleet/commit/0e6c790803d1b4407c5b4b41a67a37864a3d3573
- https://github.com/fleetdm/fleet
