# [C] PEAR is Vulnerable to SQL Injection in /get/<package>/<version> Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-25241
Aliases: GHSA-63fv-vpq5-gv8p
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25241
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, an unauthenticated SQL injection in the /get/<package>/<version> endpoint allows remote attackers to execute arbitrary SQL via a crafted package version. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25241.json
- https://github.com/pear/pearweb/security/advisories/GHSA-63fv-vpq5-gv8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-25241
