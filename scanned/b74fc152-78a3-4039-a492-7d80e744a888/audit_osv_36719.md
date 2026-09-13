# [M] PEAR is Vulnerable to SQL Injection in apidoc_queue Insert via Unescaped Filename

## Summary
Severity: Medium
Advisory: CVE-2026-25239
Aliases: GHSA-f9mg-x463-3vxg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25239
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, a SQL injection vulnerability in apidoc queue insertion can allow query manipulation if an attacker can influence the inserted filename value. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25239.json
- https://github.com/pear/pearweb/security/advisories/GHSA-f9mg-x463-3vxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25239
