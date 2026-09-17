# [C] Oxidized Web RANCID migration page allows unauthenticated user to gain control over Linux user account

## Summary
Severity: Critical
Advisory: GHSA-jx6p-9c26-g373
CVE: CVE-2025-27590
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-jx6p-9c26-g373
Type: github-advisory

## Affected
- RubyGems: `oxidized-web` — affected >=0 <0.15.0

## Details
In oxidized-web (aka Oxidized Web) before 0.15.0, the RANCID migration page allows an unauthenticated user to gain control over the Linux user account that is running oxidized-web.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27590
- https://github.com/ytti/oxidized-web/commit/a5220a0ddc57b85cd122bffee228d3ed4901668e
- https://github.com/ytti/oxidized-web
- https://github.com/ytti/oxidized-web/releases/tag/0.15.0
