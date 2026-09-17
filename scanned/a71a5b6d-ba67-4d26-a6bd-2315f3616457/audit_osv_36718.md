# [C] PEAR is Vulnerable to SQL Injection in Bug Subscription Deletion via Weak Email Validation

## Summary
Severity: Critical
Advisory: CVE-2026-25238
Aliases: GHSA-cv3c-27h5-7gmv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25238
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, a SQL injection vulnerability in bug subscription deletion may allow attackers to inject SQL via a crafted email value. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25238.json
- https://github.com/pear/pearweb/security/advisories/GHSA-cv3c-27h5-7gmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-25238
