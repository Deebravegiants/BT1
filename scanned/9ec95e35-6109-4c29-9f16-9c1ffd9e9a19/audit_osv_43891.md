# [C] Grav before 2.0.15 Arbitrary File Write via error_log

## Summary
Severity: Critical
Advisory: CVE-2026-75827
Aliases: GHSA-f8wv-xp27-6gq7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75827
Type: osv

## Details
Grav before 2.0.15 contains an arbitrary file write vulnerability in the Blueprint dynamic-data bare-function validation that uses an incomplete denylist instead of a positive allowlist. Attackers with page-edit or blueprint-config access can invoke the error_log function through a data directive to append PHP payloads to web-accessible files, achieving remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75827.json
- https://github.com/getgrav/grav/security/advisories/GHSA-f8wv-xp27-6gq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-75827
- https://www.vulncheck.com/advisories/grav-before-arbitrary-file-write-via-error-log
