# [M] React Router: Open redirect via backslash in <Link> and useNavigate (CVE-2025-68470 bypass)

## Summary
Severity: Medium
Advisory: GHSA-wrjc-x8rr-h8h6
CVE: CVE-2026-53669
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-wrjc-x8rr-h8h6
Type: github-advisory

## Affected
- npm: `react-router` — affected >=6.0.0 <7.18.0

## Details
This is a follow up to [CVE-2025-68470](https://github.com/remix-run/react-router/security/advisories/GHSA-9jcx-v3wj-wh4m).  React Router was alerted to certain scenarios in which the fix there was incomplete so there still existed some scenarios where attacker supplied paths passed to navigation mechanisms could result in unexpected external navigations.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-wrjc-x8rr-h8h6
- https://github.com/remix-run/react-router/pull/15176
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v7180
- https://github.com/remix-run/react-router/releases/tag/react-router@7.18.0
- http://github.com/remix-run/react-router/pull/15176
