# [M] Grafana OSS: Authorization bypass allows users with Editor role to modify protected webhook URLs without permissions

## Summary
Severity: Medium
Advisory: GHSA-7g92-g4vh-hp84
CVE: CVE-2026-21724
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-7g92-g4vh-hp84
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <1.9.2-0.20260323180334-daffe750de85

## Details
A vulnerability has been discovered in Grafana OSS where an authorization bypass in the provisioning contact points API allows users with Editor role to modify protected webhook URLs without the required alert.notifications.receivers.protected:write permission.

A patched version is available at https://github.com/grafana/grafana/releases/tag/v12.3.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21724
- https://github.com/grafana/grafana/commit/daffe750de85b0dbf79f206a35835cf66a83d6ca
- https://github.com/advisories/GHSA-7g92-g4vh-hp84
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v12.3.6
- https://grafana.com/security/security-advisories/cve-2026-21724
