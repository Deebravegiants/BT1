# [C] PEAR is Vulnerable to PHP Code Execution via preg_replace /e in Bug Update Emails

## Summary
Severity: Critical
Advisory: CVE-2026-25237
Aliases: GHSA-vhw6-hqh9-8r23
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25237
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, use of preg_replace() with the /e modifier in bug update email handling can enable PHP code execution if attacker-controlled content reaches the evaluated replacement. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25237.json
- https://github.com/pear/pearweb/security/advisories/GHSA-vhw6-hqh9-8r23
- https://nvd.nist.gov/vuln/detail/CVE-2026-25237
