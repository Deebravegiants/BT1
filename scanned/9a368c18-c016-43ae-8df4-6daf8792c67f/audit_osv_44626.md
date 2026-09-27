# [C] SiYuan before v3.8.2 API Token Exposure via Log File

## Summary
Severity: Critical
Advisory: CVE-2026-85174
Aliases: GHSA-3wvc-5754-gp67
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85174
Type: osv

## Details
SiYuan before v3.8.2 logs API tokens from query parameters in plaintext to an accessible log file when full-text search requests exceed timing thresholds. Authenticated attackers can read the log file via the getFile endpoint to recover admin API tokens and gain permanent administrative access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85174.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-3wvc-5754-gp67
- https://nvd.nist.gov/vuln/detail/CVE-2026-85174
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-api-token-exposure-via-log-file
