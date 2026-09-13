# [C] LibreNMS before 26.8.0 Authentication Bypass via API Token Type Confusion

## Summary
Severity: Critical
Advisory: CVE-2026-86426
Aliases: GHSA-cvq8-gqfq-3mvg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86426
Type: osv

## Details
LibreNMS before 26.8.0 contains an authentication bypass vulnerability in the REST API that allows unauthenticated attackers to access protected endpoints by sending numeric values instead of string tokens. Attackers can exploit MySQL type coercion by sending small integers like 0 through 9 to match token hashes, gaining access to API functionality including device credentials and administrative features that enable remote code execution through alert templates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86426.json
- https://github.com/librenms/librenms/security/advisories/GHSA-cvq8-gqfq-3mvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-86426
- https://www.vulncheck.com/advisories/librenms-before-26.8.0-authentication-bypass-via-api-token-type-confusion
