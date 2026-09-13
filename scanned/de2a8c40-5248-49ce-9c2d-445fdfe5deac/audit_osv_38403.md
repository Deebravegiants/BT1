# [C] Lawnchair vulnerable to Command Injection via unquoted workflow dispatch input in release_update.yml

## Summary
Severity: Critical
Advisory: CVE-2026-39866
Aliases: GHSA-9prc-pp2c-3427
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-39866
Type: osv

## Details
Lawnchair is a free, open-source home app for Android. Prior to commit fcba413f55dd47f8a3921445252849126c6266b2, command injection in release_update.yml workflow dispatch input allows arbitrary code execution. Commit fcba413f55dd47f8a3921445252849126c6266b2 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39866.json
- https://github.com/LawnchairLauncher/lawnchair/security/advisories/GHSA-9prc-pp2c-3427
- https://nvd.nist.gov/vuln/detail/CVE-2026-39866
- https://github.com/LawnchairLauncher/lawnchair/commit/fcba413f55dd47f8a3921445252849126c6266b2
