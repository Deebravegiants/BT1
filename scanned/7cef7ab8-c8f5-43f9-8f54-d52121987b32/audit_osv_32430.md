# [C] HestiaCP < 1.9.5 Authenticated OS Command Injection via DNS Record Management

## Summary
Severity: Critical
Advisory: CVE-2025-30007
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2025-30007
Type: osv

## Details
HestiaCP before 1.9.5 contains an authenticated OS command injection vulnerability that allows low-privilege authenticated users to execute arbitrary commands as root by injecting a single-quote character into unvalidated DNS record types. Attackers can exploit insufficient input validation in is_dns_record_format_valid() combined with unsafe eval-based parsing in update_domain_zone() to prematurely close a variable assignment string and achieve full root code execution on the underlying host in a single DNS record creation step.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30007.json
- https://github.com/hestiacp/hestiacp/releases/tag/1.9.5
- https://nvd.nist.gov/vuln/detail/CVE-2025-30007
- https://www.vulncheck.com/advisories/hestiacp-authenticated-os-command-injection-via-dns-record-management
- https://github.com/hestiacp/hestiacp/pull/5197
- https://github.com/hestiacp/hestiacp/commit/a74babb739aa92e52b12d6ef52b6b9428ffbbb67
- https://github.com/hestiacp/hestiacp
