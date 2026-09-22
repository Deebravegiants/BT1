# [M] CVE-2026-8207

## Summary
Severity: Medium
Advisory: CVE-2026-8207
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-8207
Type: osv

## Details
Gibbon versions before v30.0.01 are affected by an authenticated SQL Injection vulnerability by abusing the  Tracking/graphing https://github.com/GibbonEdu/core/blob/c431e25fdc874adece5d2dc7e408e9aa2d1abadb/modules/Tracking/graphing.php#L145  feature. Successful exploitation requires Teacher or higher privileges. Exploitation could result in unintended read/write activities to the underlying database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8207.json
- https://github.com/GibbonEdu/core/releases/tag/v30.0.01
- https://nvd.nist.gov/vuln/detail/CVE-2026-8207
- https://projectblack.io/blog/gibbon-v30-authenticated-sql-injection-and-rce/#sql-injectiongetting-warmed-up
