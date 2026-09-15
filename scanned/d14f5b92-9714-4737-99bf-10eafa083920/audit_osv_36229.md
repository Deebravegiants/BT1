# [C] OpenViking Missing root_api_key Allows Anonymous ROOT Access

## Summary
Severity: Critical
Advisory: CVE-2026-22207
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-22207
Type: osv

## Details
OpenViking through version 0.1.18, prior to commit 0251c70, contains a broken access control vulnerability that allows unauthenticated attackers to gain ROOT privileges when the root_api_key configuration is omitted. Attackers can send requests to protected endpoints without authentication headers to access administrative functions including account management, resource operations, and system configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22207.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22207
- https://www.vulncheck.com/advisories/openviking-missing-root-api-key-allows-anonymous-root-access
- https://github.com/volcengine/OpenViking/issues/302
- https://github.com/volcengine/OpenViking/pull/310
- https://github.com/volcengine/OpenViking/commit/0251c7045b3f8092c4d2e1565115b1ba23db282f
