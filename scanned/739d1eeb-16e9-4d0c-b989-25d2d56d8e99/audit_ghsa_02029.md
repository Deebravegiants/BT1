# [M] Improper input validation in CNCF Cortex

## Summary
Severity: Medium
Advisory: GHSA-m45g-f45x-vv22
CVE: CVE-2021-31232
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-m45g-f45x-vv22
Type: github-advisory

## Affected
- Go: `github.com/cortexproject/cortex` — affected >=0 <1.8.1

## Details
The Alertmanager in CNCF Cortex before 1.8.1 has a local file disclosure vulnerability when -experimental.alertmanager.enable-api is used. The HTTP basic auth password_file can be used as an attack vector to send any file content via a webhook. The alertmanager templates can be used as an attack vector to send any file content because the alertmanager can load any text file specified in the templates list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31232
- https://github.com/cortexproject/cortex/pull/4129/files
- https://community.grafana.com/c/security-announcements
- https://github.com/cortexproject/cortex
- https://lists.cncf.io/g/cortex-users/message/50
