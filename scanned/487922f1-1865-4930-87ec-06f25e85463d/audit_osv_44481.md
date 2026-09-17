# [M] Admidio before 5.0.12 SQL Injection via relation_type_list

## Summary
Severity: Medium
Advisory: CVE-2026-82655
Aliases: GHSA-p5cp-mhvx-w392
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82655
Type: osv

## Details
Admidio before 5.0.12 contains a blind SQL injection vulnerability in the relation_type_list parameter of lists_show.php that allows unauthenticated attackers to execute arbitrary SQL queries. Attackers can bypass authentication by providing a dummy UUID in role_list and inject SQL through relation_type_list to extract database contents including password hashes and user credentials.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-p5cp-mhvx-w392
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82655.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82655
- https://www.vulncheck.com/advisories/admidio-before-5.0.12-sql-injection-via-relation-type-list
