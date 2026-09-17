# [C] Compass connection import allows to override OIDC browser open command (usually set through settings), allowing for arbitrary shell commands execution when connecting to cluster using OIDC auth flow

## Summary
Severity: Critical
Advisory: CVE-2026-14881
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-14881
Type: osv

## Details
When importing connections in Compass it is possible to override some connection options that are otherwise can't be changed via connection form. In particular it is possible to provide a custom browser open command for OIDC auth flow that is usually can be set only globally via Compass settings.

## References
- https://github.com/mongodb-js/compass/releases/tag/v1.49.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14881.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14881
